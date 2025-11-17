"""Video assembly and export for Auto Edit."""

import ffmpeg
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm
import json

from .clip_selector import Clip

logger = logging.getLogger(__name__)


class VideoAssembler:
    """Assembles selected clips into final highlight video."""

    def __init__(self, config):
        """
        Initialize video assembler.

        Args:
            config: Configuration object
        """
        self.config = config
        self.temp_dir = config.get('paths.temp_dir', Path('./temp'))
        self.output_dir = config.get('paths.output_dir', Path('./output'))

    def assemble_video(self, input_video: str, clips: List[Clip],
                      output_path: Optional[str] = None) -> str:
        """
        Assemble clips into final highlight video.

        Args:
            input_video: Path to source video
            clips: List of selected clips
            output_path: Optional output path

        Returns:
            Path to output video
        """
        if not clips:
            raise ValueError("No clips provided for assembly")

        if output_path is None:
            video_name = Path(input_video).stem
            output_path = self.output_dir / f"{video_name}_highlights.mp4"

        logger.info(f"Assembling {len(clips)} clips into: {output_path}")

        # Create concat file for ffmpeg
        concat_file = self._create_concat_file(input_video, clips)

        try:
            # Assemble video using ffmpeg
            self._run_ffmpeg_concat(concat_file, output_path)

            # Create metadata file
            self._create_metadata_file(clips, output_path)

            logger.info("Video assembly complete")
            return str(output_path)

        finally:
            # Cleanup temp files
            if concat_file.exists():
                concat_file.unlink()

    def _create_concat_file(self, input_video: str, clips: List[Clip]) -> Path:
        """
        Create ffmpeg concat file for clips.

        Args:
            input_video: Source video path
            clips: List of clips

        Returns:
            Path to concat file
        """
        concat_file = self.temp_dir / "concat_list.txt"

        with open(concat_file, 'w') as f:
            for i, clip in enumerate(clips):
                # Extract clip to temp file
                temp_clip = self.temp_dir / f"clip_{i:04d}.mp4"

                logger.info(f"Extracting clip {i + 1}/{len(clips)}: "
                           f"{clip.start_time:.1f}s - {clip.end_time:.1f}s")

                self._extract_clip(input_video, clip.start_time, clip.end_time, temp_clip)

                # Add to concat file
                f.write(f"file '{temp_clip}'\n")

        return concat_file

    def _extract_clip(self, input_video: str, start_time: float,
                     end_time: float, output_path: Path) -> None:
        """
        Extract a single clip from source video.

        Args:
            input_video: Source video path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Output path for clip
        """
        duration = end_time - start_time

        try:
            # Get output settings from config
            fps = self.config.get('output.fps', 30)
            codec = self.config.get('output.codec', 'libx264')
            audio_codec = self.config.get('output.audio_codec', 'aac')
            bitrate = self.config.get('output.bitrate', '4M')

            (
                ffmpeg
                .input(str(input_video), ss=start_time, t=duration)
                .output(
                    str(output_path),
                    vcodec=codec,
                    acodec=audio_codec,
                    video_bitrate=bitrate,
                    r=fps,
                    preset='medium',
                    crf=23
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error extracting clip: {e.stderr.decode()}")
            raise

    def _run_ffmpeg_concat(self, concat_file: Path, output_path: Path) -> None:
        """
        Run ffmpeg concat to merge clips.

        Args:
            concat_file: Path to concat file
            output_path: Output video path
        """
        logger.info("Concatenating clips...")

        try:
            (
                ffmpeg
                .input(str(concat_file), format='concat', safe=0)
                .output(
                    str(output_path),
                    c='copy'  # Copy codec (no re-encoding)
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg concat error: {e.stderr.decode()}")
            raise

    def assemble_video_with_transitions(self, input_video: str, clips: List[Clip],
                                       output_path: Optional[str] = None) -> str:
        """
        Assemble clips with transitions (more advanced, slower).

        Args:
            input_video: Path to source video
            clips: List of selected clips
            output_path: Optional output path

        Returns:
            Path to output video
        """
        if not clips:
            raise ValueError("No clips provided for assembly")

        if output_path is None:
            video_name = Path(input_video).stem
            output_path = self.output_dir / f"{video_name}_highlights.mp4"

        logger.info(f"Assembling {len(clips)} clips with transitions")

        # Extract all clips first
        clip_files = []
        for i, clip in enumerate(tqdm(clips, desc="Extracting clips")):
            temp_clip = self.temp_dir / f"clip_trans_{i:04d}.mp4"
            self._extract_clip(input_video, clip.start_time, clip.end_time, temp_clip)
            clip_files.append(temp_clip)

        # Build complex filter for transitions
        transition_duration = self.config.get('output.transition_duration_seconds', 0.5)

        # For simplicity, we'll use xfade filter
        # This is complex for many clips, so we'll do it iteratively
        current_output = clip_files[0]

        for i in range(1, len(clip_files)):
            next_clip = clip_files[i]
            temp_output = self.temp_dir / f"merged_{i:04d}.mp4"

            self._add_crossfade(current_output, next_clip, temp_output, transition_duration)
            current_output = temp_output

        # Copy final result to output path
        import shutil
        shutil.copy(current_output, output_path)

        # Cleanup
        for clip_file in clip_files:
            if clip_file.exists():
                clip_file.unlink()

        logger.info("Video assembly with transitions complete")
        return str(output_path)

    def _add_crossfade(self, clip1: Path, clip2: Path, output: Path,
                      duration: float) -> None:
        """
        Add crossfade transition between two clips.

        Args:
            clip1: First clip path
            clip2: Second clip path
            output: Output path
            duration: Transition duration in seconds
        """
        # This is a simplified version
        # A full implementation would use xfade filter
        try:
            # For now, just concatenate without transition
            (
                ffmpeg
                .concat(
                    ffmpeg.input(str(clip1)),
                    ffmpeg.input(str(clip2)),
                    v=1, a=1
                )
                .output(str(output), vcodec='libx264', acodec='aac')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg crossfade error: {e.stderr.decode()}")
            raise

    def _create_metadata_file(self, clips: List[Clip], output_path: Path) -> None:
        """
        Create metadata file with clip information.

        Args:
            clips: List of clips
            output_path: Output video path
        """
        metadata_path = output_path.with_suffix('.json')

        metadata = {
            'clips': [
                {
                    'index': i,
                    'start_time': clip.start_time,
                    'end_time': clip.end_time,
                    'duration': clip.duration,
                    'score': clip.score,
                    'reason': clip.reason,
                    'signal_count': len(clip.signals),
                    'signal_types': clip.metadata.get('signal_types', [])
                }
                for i, clip in enumerate(clips)
            ],
            'summary': {
                'total_clips': len(clips),
                'total_duration': sum(c.duration for c in clips),
                'avg_clip_duration': sum(c.duration for c in clips) / len(clips) if clips else 0,
                'avg_score': sum(c.score for c in clips) / len(clips) if clips else 0
            }
        }

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to: {metadata_path}")

    def create_preview_video(self, input_video: str, clips: List[Clip],
                           max_clips: int = 5) -> str:
        """
        Create a quick preview with top clips.

        Args:
            input_video: Source video path
            clips: All selected clips
            max_clips: Maximum clips for preview

        Returns:
            Path to preview video
        """
        # Select top clips by score
        preview_clips = sorted(clips, key=lambda x: x.score, reverse=True)[:max_clips]
        preview_clips.sort(key=lambda x: x.start_time)  # Sort by time

        video_name = Path(input_video).stem
        output_path = self.output_dir / f"{video_name}_preview.mp4"

        return self.assemble_video(input_video, preview_clips, output_path)

    def export_clip_list(self, clips: List[Clip], output_path: Optional[str] = None) -> str:
        """
        Export clip list to file (for review/editing).

        Args:
            clips: List of clips
            output_path: Optional output path

        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.output_dir / "clip_list.txt"

        with open(output_path, 'w') as f:
            f.write("Auto Edit - Selected Clips\n")
            f.write("=" * 80 + "\n\n")

            for i, clip in enumerate(clips, 1):
                f.write(f"Clip {i}:\n")
                f.write(f"  Time: {clip.start_time:.2f}s - {clip.end_time:.2f}s "
                       f"({clip.duration:.2f}s)\n")
                f.write(f"  Score: {clip.score:.3f}\n")
                f.write(f"  Reason: {clip.reason}\n")
                f.write(f"  Signals: {', '.join(clip.metadata.get('signal_types', []))}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write(f"Total clips: {len(clips)}\n")
            f.write(f"Total duration: {sum(c.duration for c in clips):.2f}s "
                   f"({sum(c.duration for c in clips) / 60:.2f} minutes)\n")

        logger.info(f"Clip list exported to: {output_path}")
        return str(output_path)
