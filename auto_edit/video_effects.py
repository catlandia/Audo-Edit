"""Video effects and meme application for Auto Edit."""

import cv2
import numpy as np
import ffmpeg
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import logging
from tqdm import tqdm

from .meme_generator import MemeInsert, MemeGenerator
from .clip_selector import Clip

logger = logging.getLogger(__name__)


class VideoEffects:
    """Applies effects and memes to video clips."""

    def __init__(self, config):
        """
        Initialize video effects processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.temp_dir = config.get('paths.temp_dir', Path('./temp'))
        self.meme_generator = MemeGenerator(config)

    def apply_memes_to_clip(self, input_video: str, clip: Clip,
                           meme_inserts: List[MemeInsert],
                           output_path: str) -> str:
        """
        Apply meme overlays to a video clip.

        Args:
            input_video: Source video path
            clip: Clip object
            meme_inserts: List of meme inserts for this clip
            output_path: Output path for processed clip

        Returns:
            Path to processed clip
        """
        if not meme_inserts:
            # No memes to apply, just extract clip normally
            return self._extract_clip_simple(input_video, clip, output_path)

        logger.info(f"Applying {len(meme_inserts)} memes to clip at {clip.start_time:.1f}s")

        # Extract clip frames and process
        cap = cv2.VideoCapture(str(input_video))
        out = None
        temp_video = None

        try:
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {input_video}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0:
                raise ValueError(f"Invalid FPS: {fps}")

            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Prepare output video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            temp_video = self.temp_dir / f"temp_meme_{clip.start_time:.0f}.mp4"
            out = cv2.VideoWriter(str(temp_video), fourcc, fps, (width, height))

            # Calculate frame range
            start_frame = int(clip.start_time * fps)
            end_frame = int(clip.end_time * fps)

            # Process frames
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

            for frame_idx in tqdm(range(start_frame, end_frame),
                                 desc=f"Processing clip", leave=False):
                ret, frame = cap.read()
                if not ret:
                    break

                # Calculate current timestamp
                current_time = frame_idx / fps

                # Check if any memes should be displayed at this timestamp
                for meme in meme_inserts:
                    if meme.timestamp <= current_time < meme.timestamp + meme.duration:
                        frame = self._apply_meme_to_frame(frame, meme)

                out.write(frame)
        finally:
            cap.release()
            if out is not None:
                out.release()

        # Re-encode with audio
        self._add_audio_to_video(input_video, temp_video, output_path,
                                clip.start_time, clip.duration)

        # Cleanup temp file
        if temp_video.exists():
            temp_video.unlink()

        return str(output_path)

    def _apply_meme_to_frame(self, frame: np.ndarray, meme: MemeInsert) -> np.ndarray:
        """
        Apply a single meme to a frame.

        Args:
            frame: Video frame
            meme: Meme insert specification

        Returns:
            Frame with meme applied
        """
        # Get position coordinates
        position = self.meme_generator.positions.get(meme.position, (0.5, 0.5))

        # Apply image overlay if present
        if meme.image_path:
            frame = self.meme_generator.create_image_overlay(
                frame, meme.image_path, position, meme.size, meme.opacity
            )

        # Apply text overlay if present
        if meme.text:
            frame = self.meme_generator.create_text_overlay(
                frame, meme.text, position, meme.size, meme.opacity
            )

        return frame

    def _extract_clip_simple(self, input_video: str, clip: Clip,
                            output_path: str) -> str:
        """
        Extract clip without effects using FFmpeg.

        Args:
            input_video: Source video
            clip: Clip object
            output_path: Output path

        Returns:
            Path to extracted clip
        """
        try:
            (
                ffmpeg
                .input(str(input_video), ss=clip.start_time, t=clip.duration)
                .output(
                    str(output_path),
                    vcodec='libx264',
                    acodec='aac',
                    preset='medium',
                    crf=23
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            return str(output_path)
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise

    def _add_audio_to_video(self, source_video: str, video_file: str,
                           output_file: str, start_time: float, duration: float):
        """
        Add audio track to video file.

        Args:
            source_video: Original video with audio
            video_file: Video file without audio
            output_file: Output path
            start_time: Start time for audio extraction
            duration: Duration of audio
        """
        try:
            input_video = ffmpeg.input(str(video_file))
            input_audio = ffmpeg.input(str(source_video), ss=start_time, t=duration).audio

            (
                ffmpeg
                .output(input_video, input_audio, str(output_file),
                       vcodec='libx264', acodec='aac', preset='medium', crf=23)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error adding audio: {e.stderr.decode()}")
            raise

    def create_transition_effect(self, clip1_path: str, clip2_path: str,
                                 output_path: str, transition_type: str = 'fade',
                                 duration: float = 0.5) -> str:
        """
        Create transition between two clips.

        Args:
            clip1_path: First clip
            clip2_path: Second clip
            output_path: Output path
            transition_type: Type of transition ('fade', 'wipe', 'slide')
            duration: Transition duration in seconds

        Returns:
            Path to output file with transition
        """
        logger.info(f"Creating {transition_type} transition...")

        try:
            if transition_type == 'fade':
                # Use xfade filter for crossfade
                input1 = ffmpeg.input(clip1_path)
                input2 = ffmpeg.input(clip2_path)

                # Get duration of first clip
                probe = ffmpeg.probe(clip1_path)
                duration1 = float(probe['format']['duration'])

                (
                    ffmpeg
                    .filter([input1, input2], 'xfade',
                           transition='fade',
                           duration=duration,
                           offset=duration1 - duration)
                    .output(str(output_path), vcodec='libx264', acodec='aac')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
            else:
                # For other transitions, just concatenate for now
                (
                    ffmpeg
                    .concat(
                        ffmpeg.input(clip1_path),
                        ffmpeg.input(clip2_path),
                        v=1, a=1
                    )
                    .output(str(output_path), vcodec='libx264', acodec='aac')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )

            return str(output_path)

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg transition error: {e.stderr.decode()}")
            raise

    def apply_zoom_effect(self, frame: np.ndarray, zoom_factor: float,
                         center: Optional[Tuple[float, float]] = None) -> np.ndarray:
        """
        Apply zoom effect to frame.

        Args:
            frame: Input frame
            zoom_factor: Zoom factor (1.0 = no zoom, 2.0 = 2x zoom)
            center: Center point for zoom (normalized coordinates)

        Returns:
            Zoomed frame
        """
        if zoom_factor == 1.0:
            return frame

        height, width = frame.shape[:2]

        if center is None:
            center = (0.5, 0.5)

        # Calculate crop region
        new_width = int(width / zoom_factor)
        new_height = int(height / zoom_factor)

        x = int(center[0] * width - new_width / 2)
        y = int(center[1] * height - new_height / 2)

        # Ensure crop is within bounds
        x = max(0, min(x, width - new_width))
        y = max(0, min(y, height - new_height))

        # Crop and resize
        cropped = frame[y:y+new_height, x:x+new_width]
        zoomed = cv2.resize(cropped, (width, height))

        return zoomed

    def apply_shake_effect(self, frame: np.ndarray, intensity: float = 10.0) -> np.ndarray:
        """
        Apply camera shake effect to frame.

        Args:
            frame: Input frame
            intensity: Shake intensity in pixels

        Returns:
            Shaken frame
        """
        import random

        height, width = frame.shape[:2]

        # Random offset
        dx = random.randint(-int(intensity), int(intensity))
        dy = random.randint(-int(intensity), int(intensity))

        # Translation matrix
        M = np.float32([[1, 0, dx], [0, 1, dy]])

        # Apply transformation
        shaken = cv2.warpAffine(frame, M, (width, height), borderMode=cv2.BORDER_REPLICATE)

        return shaken

    def add_vignette_effect(self, frame: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """
        Add vignette (darkened edges) effect to frame.

        Args:
            frame: Input frame
            intensity: Vignette intensity (0-1)

        Returns:
            Frame with vignette
        """
        height, width = frame.shape[:2]

        # Create radial gradient mask
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)

        # Calculate distance from center
        radius = np.sqrt(X**2 + Y**2)

        # Create vignette mask
        vignette = 1 - (radius * intensity)
        vignette = np.clip(vignette, 0, 1)

        # Apply to each channel
        for i in range(3):
            frame[:, :, i] = (frame[:, :, i] * vignette).astype(np.uint8)

        return frame
