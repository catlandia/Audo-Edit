"""Thumbnail extraction for key moments."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
import logging
from dataclasses import dataclass

from .clip_selector import Clip

logger = logging.getLogger(__name__)


@dataclass
class Thumbnail:
    """Represents an extracted thumbnail."""
    clip_index: int
    timestamp: float
    file_path: str
    score: float
    reason: str
    resolution: Tuple[int, int]


class ThumbnailExtractor:
    """Extracts thumbnail images from key moments in clips."""

    def __init__(self, config):
        """
        Initialize thumbnail extractor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.output_dir = config.get('paths.output_dir', Path('./output'))
        self.thumbnails_dir = self.output_dir / 'thumbnails'
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)

    def extract_thumbnails(self, video_path: str, clips: List[Clip],
                          output_prefix: str = "thumbnail") -> List[Thumbnail]:
        """
        Extract thumbnails from clips.

        Args:
            video_path: Path to source video
            clips: List of clips
            output_prefix: Prefix for thumbnail filenames

        Returns:
            List of extracted thumbnails
        """
        logger.info(f"Extracting thumbnails from {len(clips)} clips...")

        thumbnails = []

        for i, clip in enumerate(clips):
            try:
                # Extract thumbnail at the middle of the clip (often most representative)
                mid_timestamp = clip.start_time + (clip.duration / 2)

                thumbnail = self._extract_single_thumbnail(
                    video_path, mid_timestamp, i, clip, output_prefix
                )

                if thumbnail:
                    thumbnails.append(thumbnail)

            except Exception as e:
                logger.error(f"Error extracting thumbnail for clip {i}: {e}")
                continue

        logger.info(f"Extracted {len(thumbnails)} thumbnails")
        return thumbnails

    def _extract_single_thumbnail(self, video_path: str, timestamp: float,
                                  clip_index: int, clip: Clip,
                                  output_prefix: str) -> Optional[Thumbnail]:
        """
        Extract a single thumbnail.

        Args:
            video_path: Path to video
            timestamp: Timestamp to extract
            clip_index: Index of the clip
            clip: Clip object
            output_prefix: Filename prefix

        Returns:
            Thumbnail object or None
        """
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            logger.error(f"Could not open video: {video_path}")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            cap.release()
            return None

        frame_number = int(timestamp * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return None

        # Save thumbnail
        filename = f"{output_prefix}_{clip_index:04d}_{timestamp:.2f}s.jpg"
        output_path = self.thumbnails_dir / filename

        # Resize if needed (optional)
        target_width = self.config.get('thumbnails.width', 1280)
        target_height = self.config.get('thumbnails.height', 720)

        if frame.shape[1] != target_width or frame.shape[0] != target_height:
            frame = cv2.resize(frame, (target_width, target_height))

        # Save with quality setting
        quality = self.config.get('thumbnails.quality', 90)
        cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, quality])

        return Thumbnail(
            clip_index=clip_index,
            timestamp=timestamp,
            file_path=str(output_path),
            score=clip.score,
            reason=clip.reason,
            resolution=(target_width, target_height)
        )

    def extract_best_frame(self, video_path: str, clip: Clip) -> Optional[Thumbnail]:
        """
        Extract the BEST frame from a clip (most visually interesting).

        Args:
            video_path: Path to video
            clip: Clip to analyze

        Returns:
            Thumbnail of best frame
        """
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            cap.release()
            return None

        start_frame = int(clip.start_time * fps)
        end_frame = int(clip.end_time * fps)

        # Sample frames throughout the clip
        sample_rate = max(1, int(fps / 2))  # Sample 2 frames per second

        best_frame = None
        best_score = -1
        best_timestamp = clip.start_time

        for frame_idx in range(start_frame, end_frame, sample_rate):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                break

            # Score frame based on visual interest
            score = self._score_frame_quality(frame)

            if score > best_score:
                best_score = score
                best_frame = frame.copy()
                best_timestamp = frame_idx / fps

        cap.release()

        if best_frame is None:
            return None

        # Save best frame
        filename = f"best_frame_clip_{clip.start_time:.2f}s.jpg"
        output_path = self.thumbnails_dir / filename

        target_width = self.config.get('thumbnails.width', 1280)
        target_height = self.config.get('thumbnails.height', 720)

        if best_frame.shape[1] != target_width or best_frame.shape[0] != target_height:
            best_frame = cv2.resize(best_frame, (target_width, target_height))

        quality = self.config.get('thumbnails.quality', 90)
        cv2.imwrite(str(output_path), best_frame, [cv2.IMWRITE_JPEG_QUALITY, quality])

        return Thumbnail(
            clip_index=-1,
            timestamp=best_timestamp,
            file_path=str(output_path),
            score=best_score,
            reason=f"Best frame from: {clip.reason}",
            resolution=(target_width, target_height)
        )

    def _score_frame_quality(self, frame: np.ndarray) -> float:
        """
        Score a frame based on visual interest.

        Uses multiple metrics:
        - Sharpness (Laplacian variance)
        - Color variance
        - Brightness distribution

        Args:
            frame: Frame to score

        Returns:
            Quality score (higher is better)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 1. Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()

        # 2. Color variance
        color_variance = np.var(frame)

        # 3. Brightness distribution (prefer well-distributed histograms)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_variance = np.var(hist)

        # Combine scores (normalized)
        sharpness_norm = min(1.0, sharpness / 1000.0)
        color_norm = min(1.0, color_variance / 10000.0)
        hist_norm = min(1.0, hist_variance / 1000000.0)

        total_score = (0.5 * sharpness_norm +
                      0.3 * color_norm +
                      0.2 * hist_norm)

        return total_score

    def create_thumbnail_grid(self, thumbnails: List[Thumbnail],
                             output_path: Optional[str] = None) -> str:
        """
        Create a grid of thumbnails.

        Args:
            thumbnails: List of thumbnails
            output_path: Optional output path

        Returns:
            Path to grid image
        """
        if not thumbnails:
            raise ValueError("No thumbnails to create grid")

        if output_path is None:
            output_path = self.thumbnails_dir / "thumbnail_grid.jpg"

        # Load all thumbnail images
        images = []
        for thumb in thumbnails[:16]:  # Max 16 thumbnails in grid
            img = cv2.imread(thumb.file_path)
            if img is not None:
                images.append(img)

        if not images:
            raise ValueError("Could not load any thumbnail images")

        # Calculate grid dimensions
        n_images = len(images)
        cols = int(np.ceil(np.sqrt(n_images)))
        rows = int(np.ceil(n_images / cols))

        # Get image dimensions
        img_height, img_width = images[0].shape[:2]

        # Create grid
        grid = np.zeros((rows * img_height, cols * img_width, 3), dtype=np.uint8)

        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols

            y1 = row * img_height
            y2 = y1 + img_height
            x1 = col * img_width
            x2 = x1 + img_width

            # Resize if needed
            if img.shape != images[0].shape:
                img = cv2.resize(img, (img_width, img_height))

            grid[y1:y2, x1:x2] = img

        # Save grid
        cv2.imwrite(str(output_path), grid)

        logger.info(f"Created thumbnail grid: {output_path}")
        return str(output_path)

    def export_thumbnail_list(self, thumbnails: List[Thumbnail],
                             output_path: Optional[str] = None) -> str:
        """
        Export thumbnail list to text file.

        Args:
            thumbnails: List of thumbnails
            output_path: Optional output path

        Returns:
            Path to text file
        """
        if output_path is None:
            output_path = self.thumbnails_dir / "thumbnails.txt"

        with open(output_path, 'w') as f:
            f.write("Auto Edit - Extracted Thumbnails\n")
            f.write("=" * 80 + "\n\n")

            for thumb in thumbnails:
                f.write(f"Thumbnail {thumb.clip_index + 1}:\n")
                f.write(f"  Timestamp: {thumb.timestamp:.2f}s\n")
                f.write(f"  Score: {thumb.score:.3f}\n")
                f.write(f"  Reason: {thumb.reason}\n")
                f.write(f"  File: {Path(thumb.file_path).name}\n")
                f.write(f"  Resolution: {thumb.resolution[0]}x{thumb.resolution[1]}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write(f"Total thumbnails: {len(thumbnails)}\n")

        logger.info(f"Thumbnail list exported: {output_path}")
        return str(output_path)
