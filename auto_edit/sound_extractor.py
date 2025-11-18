"""Sound extraction for best audio moments."""

import ffmpeg
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import List, Optional, Tuple
import logging
from dataclasses import dataclass

from .clip_selector import Clip
from .signal_detector import SignalEvent

logger = logging.getLogger(__name__)


@dataclass
class SoundClip:
    """Represents an extracted sound clip."""
    clip_index: int
    timestamp: float
    duration: float
    file_path: str
    signal_type: str
    intensity: float
    reason: str


class SoundExtractor:
    """Extracts sound clips from best audio moments."""

    def __init__(self, config):
        """
        Initialize sound extractor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.output_dir = config.get('paths.output_dir', Path('./output'))
        self.sounds_dir = self.output_dir / 'sounds'
        self.sounds_dir.mkdir(parents=True, exist_ok=True)

    def extract_sound_clips(self, video_path: str, clips: List[Clip],
                           max_clips: int = 10) -> List[SoundClip]:
        """
        Extract audio clips from best moments.

        Args:
            video_path: Path to source video
            clips: List of clips
            max_clips: Maximum number of sound clips to extract

        Returns:
            List of extracted sound clips
        """
        logger.info(f"Extracting sound clips from {len(clips)} clips...")

        # Sort clips by score to get best moments
        sorted_clips = sorted(clips, key=lambda x: x.score, reverse=True)[:max_clips]

        sound_clips = []

        for i, clip in enumerate(sorted_clips):
            try:
                # Extract audio for the clip
                sound_clip = self._extract_single_sound(video_path, clip, i)

                if sound_clip:
                    sound_clips.append(sound_clip)

            except Exception as e:
                logger.error(f"Error extracting sound for clip {i}: {e}")
                continue

        logger.info(f"Extracted {len(sound_clips)} sound clips")
        return sound_clips

    def _extract_single_sound(self, video_path: str, clip: Clip,
                             clip_index: int) -> Optional[SoundClip]:
        """
        Extract a single sound clip.

        Args:
            video_path: Path to video
            clip: Clip object
            clip_index: Index of the clip

        Returns:
            SoundClip object or None
        """
        # Determine signal type for naming
        signal_type = "mixed"
        if clip.signals:
            # Get the highest intensity signal
            top_signal = max(clip.signals, key=lambda s: s.intensity)
            signal_type = top_signal.signal_type

        # Create output filename
        filename = f"sound_{clip_index:04d}_{signal_type}_{clip.start_time:.2f}s.wav"
        output_path = self.sounds_dir / filename

        try:
            # Extract audio segment using FFmpeg
            (
                ffmpeg
                .input(str(video_path), ss=clip.start_time, t=clip.duration)
                .output(str(output_path), acodec='pcm_s16le', ac=2, ar='44100')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )

            # Get intensity from top signal
            intensity = max((s.intensity for s in clip.signals), default=0.5) if clip.signals else 0.5

            return SoundClip(
                clip_index=clip_index,
                timestamp=clip.start_time,
                duration=clip.duration,
                file_path=str(output_path),
                signal_type=signal_type,
                intensity=intensity,
                reason=clip.reason
            )

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error extracting sound: {e.stderr.decode()}")
            return None

    def extract_best_sounds_by_type(self, video_path: str, clips: List[Clip],
                                   sound_type: str, max_count: int = 5) -> List[SoundClip]:
        """
        Extract best sounds of a specific type (e.g., 'laughter', 'shouting').

        Args:
            video_path: Path to source video
            clips: List of clips
            sound_type: Type of sound to extract
            max_count: Maximum number to extract

        Returns:
            List of sound clips of specified type
        """
        logger.info(f"Extracting {max_count} best '{sound_type}' sounds...")

        # Filter clips that have signals of the requested type
        matching_clips = []
        for clip in clips:
            if any(s.signal_type == sound_type for s in clip.signals):
                # Get intensity of this signal type in the clip
                type_signals = [s for s in clip.signals if s.signal_type == sound_type]
                max_intensity = max(s.intensity for s in type_signals)

                matching_clips.append((clip, max_intensity))

        # Sort by intensity
        matching_clips.sort(key=lambda x: x[1], reverse=True)

        sound_clips = []

        for i, (clip, intensity) in enumerate(matching_clips[:max_count]):
            try:
                filename = f"{sound_type}_{i:02d}_{clip.start_time:.2f}s.wav"
                output_path = self.sounds_dir / filename

                (
                    ffmpeg
                    .input(str(video_path), ss=clip.start_time, t=clip.duration)
                    .output(str(output_path), acodec='pcm_s16le', ac=2, ar='44100')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )

                sound_clips.append(SoundClip(
                    clip_index=i,
                    timestamp=clip.start_time,
                    duration=clip.duration,
                    file_path=str(output_path),
                    signal_type=sound_type,
                    intensity=intensity,
                    reason=clip.reason
                ))

            except Exception as e:
                logger.error(f"Error extracting {sound_type} sound {i}: {e}")
                continue

        logger.info(f"Extracted {len(sound_clips)} '{sound_type}' sounds")
        return sound_clips

    def create_soundboard(self, sound_clips: List[SoundClip],
                         output_path: Optional[str] = None) -> str:
        """
        Create a single audio file with all sounds (soundboard).

        Args:
            sound_clips: List of sound clips
            output_path: Optional output path

        Returns:
            Path to soundboard file
        """
        if not sound_clips:
            raise ValueError("No sound clips to create soundboard")

        if output_path is None:
            output_path = self.sounds_dir / "soundboard.wav"

        # Load all audio files
        audio_segments = []
        sample_rate = 44100

        for sound_clip in sound_clips:
            try:
                audio, sr = librosa.load(sound_clip.file_path, sr=sample_rate, mono=False)
                audio_segments.append(audio)

                # Add 0.5 second silence between clips
                silence = np.zeros((audio.shape[0], int(0.5 * sample_rate)))
                audio_segments.append(silence)

            except Exception as e:
                logger.error(f"Error loading sound: {e}")
                continue

        if not audio_segments:
            raise ValueError("Could not load any sound clips")

        # Concatenate all audio
        combined_audio = np.concatenate(audio_segments, axis=1)

        # Save soundboard
        sf.write(output_path, combined_audio.T, sample_rate)

        logger.info(f"Created soundboard: {output_path}")
        return str(output_path)

    def export_sound_list(self, sound_clips: List[SoundClip],
                         output_path: Optional[str] = None) -> str:
        """
        Export sound clip list to text file.

        Args:
            sound_clips: List of sound clips
            output_path: Optional output path

        Returns:
            Path to text file
        """
        if output_path is None:
            output_path = self.sounds_dir / "sounds.txt"

        with open(output_path, 'w') as f:
            f.write("Auto Edit - Extracted Sound Clips\n")
            f.write("=" * 80 + "\n\n")

            # Group by signal type
            by_type = {}
            for sound in sound_clips:
                by_type.setdefault(sound.signal_type, []).append(sound)

            for signal_type, sounds in sorted(by_type.items()):
                f.write(f"\n{signal_type.upper()}\n")
                f.write("-" * 40 + "\n")

                for sound in sounds:
                    f.write(f"  Sound {sound.clip_index + 1}:\n")
                    f.write(f"    Timestamp: {sound.timestamp:.2f}s\n")
                    f.write(f"    Duration: {sound.duration:.2f}s\n")
                    f.write(f"    Intensity: {sound.intensity:.3f}\n")
                    f.write(f"    Reason: {sound.reason}\n")
                    f.write(f"    File: {Path(sound.file_path).name}\n")
                    f.write("\n")

            f.write("=" * 80 + "\n")
            f.write(f"Total sound clips: {len(sound_clips)}\n")
            f.write(f"Types: {', '.join(sorted(by_type.keys()))}\n")

        logger.info(f"Sound list exported: {output_path}")
        return str(output_path)

    def extract_peak_moments(self, video_path: str, audio: np.ndarray,
                            sr: int, top_n: int = 10) -> List[SoundClip]:
        """
        Extract the top N peak audio moments.

        Args:
            video_path: Path to video
            audio: Audio data
            sr: Sample rate
            top_n: Number of peaks to extract

        Returns:
            List of peak sound clips
        """
        logger.info(f"Finding top {top_n} peak audio moments...")

        # Mix to mono
        if len(audio.shape) == 2:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio.flatten()

        # Find peaks
        hop_length = int(0.1 * sr)
        rms = librosa.feature.rms(y=audio_mono, hop_length=hop_length)[0]

        # Find local maxima
        from scipy.signal import find_peaks

        peaks, properties = find_peaks(rms, distance=int(5 * sr / hop_length), prominence=0.1)

        # Get top N peaks
        if len(peaks) == 0:
            logger.warning("No peaks found in audio")
            return []

        # Sort by prominence
        prominences = properties['prominences']
        top_indices = np.argsort(prominences)[-top_n:][::-1]
        top_peaks = peaks[top_indices]

        sound_clips = []

        for i, peak_idx in enumerate(top_peaks):
            # Convert to timestamp
            timestamp = librosa.frames_to_time(peak_idx, sr=sr, hop_length=hop_length)

            # Extract 3-second clip around peak
            start_time = max(0, timestamp - 1.5)
            duration = 3.0

            filename = f"peak_{i:02d}_{timestamp:.2f}s.wav"
            output_path = self.sounds_dir / filename

            try:
                (
                    ffmpeg
                    .input(str(video_path), ss=start_time, t=duration)
                    .output(str(output_path), acodec='pcm_s16le', ac=2, ar='44100')
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )

                sound_clips.append(SoundClip(
                    clip_index=i,
                    timestamp=start_time,
                    duration=duration,
                    file_path=str(output_path),
                    signal_type='audio_peak',
                    intensity=float(prominences[top_indices[i]]),
                    reason=f"Peak audio moment"
                ))

            except Exception as e:
                logger.error(f"Error extracting peak {i}: {e}")
                continue

        logger.info(f"Extracted {len(sound_clips)} peak moments")
        return sound_clips
