"""Video and audio processing for Auto Edit."""

import cv2
import numpy as np
import ffmpeg
import librosa
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from tqdm import tqdm
import tempfile
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video and audio extraction and analysis."""

    def __init__(self, config):
        """
        Initialize video processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.temp_dir = config.get('paths.temp_dir', Path('./temp'))
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def load_video(self, video_path: str) -> Dict[str, Any]:
        """
        Load video and extract metadata.

        Args:
            video_path: Path to input video file

        Returns:
            Dictionary with video metadata
        """
        logger.info(f"Loading video: {video_path}")
        video_path = Path(video_path)

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Open video with OpenCV for metadata
        cap = cv2.VideoCapture(str(video_path))

        metadata = {
            'path': str(video_path),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        }

        metadata['duration_seconds'] = metadata['frame_count'] / metadata['fps']
        metadata['duration_hours'] = metadata['duration_seconds'] / 3600

        cap.release()

        logger.info(f"Video loaded: {metadata['duration_hours']:.2f}h, "
                   f"{metadata['width']}x{metadata['height']}, "
                   f"{metadata['fps']} fps")

        return metadata

    def extract_audio(self, video_path: str, output_path: Optional[str] = None) -> str:
        """
        Extract audio from video file.

        Args:
            video_path: Path to input video
            output_path: Optional output path for audio file

        Returns:
            Path to extracted audio file
        """
        if output_path is None:
            output_path = self.temp_dir / f"{Path(video_path).stem}_audio.wav"

        logger.info(f"Extracting audio to: {output_path}")

        try:
            (
                ffmpeg
                .input(str(video_path))
                .output(str(output_path), acodec='pcm_s16le', ac=2, ar='44100')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise

        logger.info("Audio extraction complete")
        return str(output_path)

    def load_audio(self, audio_path: str, sr: int = 22050) -> Tuple[np.ndarray, int]:
        """
        Load audio file.

        Args:
            audio_path: Path to audio file
            sr: Sample rate

        Returns:
            Tuple of (audio data, sample rate)
        """
        logger.info(f"Loading audio: {audio_path}")
        audio, sample_rate = librosa.load(audio_path, sr=sr, mono=False)

        # If stereo, keep both channels
        if len(audio.shape) == 1:
            audio = audio.reshape(1, -1)

        logger.info(f"Audio loaded: {audio.shape[1] / sample_rate:.2f}s, "
                   f"{audio.shape[0]} channels, {sample_rate} Hz")

        return audio, sample_rate

    def get_frame_at_time(self, video_path: str, timestamp: float) -> np.ndarray:
        """
        Extract a single frame at specific timestamp.

        Args:
            video_path: Path to video file
            timestamp: Time in seconds

        Returns:
            Frame as numpy array (BGR)
        """
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp * fps)

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise ValueError(f"Could not read frame at timestamp {timestamp}")

        return frame

    def extract_frames(self, video_path: str, start_time: float, end_time: float,
                      step: int = 1) -> np.ndarray:
        """
        Extract frames from video between timestamps.

        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            end_time: End time in seconds
            step: Frame step (1 = every frame, 2 = every other frame, etc.)

        Returns:
            Array of frames
        """
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)

        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)

        frames = []
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        for frame_idx in range(start_frame, end_frame, step):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()
        return np.array(frames)

    def analyze_audio_segments(self, audio: np.ndarray, sr: int,
                              segment_length: float = 1.0) -> np.ndarray:
        """
        Analyze audio in segments and compute energy.

        Args:
            audio: Audio data
            sr: Sample rate
            segment_length: Length of each segment in seconds

        Returns:
            Array of energy values per segment
        """
        # If stereo, mix to mono for analysis
        if len(audio.shape) == 2 and audio.shape[0] == 2:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio.flatten()

        segment_samples = int(segment_length * sr)
        num_segments = len(audio_mono) // segment_samples

        energy = np.array([
            np.sqrt(np.mean(audio_mono[i * segment_samples:(i + 1) * segment_samples] ** 2))
            for i in range(num_segments)
        ])

        return energy

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get detailed video information using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information
        """
        try:
            probe = ffmpeg.probe(str(video_path))
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)

            info = {
                'format': probe['format'],
                'video': video_info,
                'audio': audio_info,
            }

            return info
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}

    def create_preview_thumbnail(self, video_path: str, timestamp: float,
                                output_path: Optional[str] = None) -> str:
        """
        Create a thumbnail preview at specific timestamp.

        Args:
            video_path: Path to video file
            timestamp: Time in seconds
            output_path: Optional output path

        Returns:
            Path to thumbnail image
        """
        if output_path is None:
            output_path = self.temp_dir / f"preview_{timestamp:.2f}.jpg"

        frame = self.get_frame_at_time(video_path, timestamp)
        cv2.imwrite(str(output_path), frame)

        return str(output_path)
