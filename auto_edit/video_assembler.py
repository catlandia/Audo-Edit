"""Video assembly and export for Auto Edit."""

import ffmpeg
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from tqdm import tqdm
import json
import numpy as np

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
                      output_path: Optional[str] = None,
                      audio: Optional[np.ndarray] = None,
                      sr: int = 22050,
                      signals: Optional[List[Dict[str, Any]]] = None) -> Tuple[str, Optional[List], Optional[List]]:
        """
        Assemble clips into final highlight video.

        Args:
            input_video: Path to source video
            clips: List of selected clips
            output_path: Optional output path
            audio: Optional audio data for sound extraction
            sr: Sample rate for audio
            signals: Optional list of detected signals for asset placement

        Returns:
            Tuple of (output_path, thumbnails, sound_clips)
        """
        if not clips:
            raise ValueError("No clips provided for assembly")

        # Ensure output_path is a Path object
        if output_path is None:
            video_name = Path(input_video).stem
            output_path = self.output_dir / f"{video_name}_highlights.mp4"
        else:
            output_path = Path(output_path)

        logger.info(f"Assembling {len(clips)} clips into: {output_path}")

        # Create concat file for ffmpeg
        concat_file = self._create_concat_file(input_video, clips)

        try:
            # Assemble video using ffmpeg
            self._run_ffmpeg_concat(concat_file, output_path)

            # Apply user assets if enabled (music, sounds, images)
            assets_enabled = self.config.get('assets.enabled', False)
            if assets_enabled:
                output_path = self._apply_user_assets(output_path, clips, signals or [])

            # Create metadata file
            self._create_metadata_file(clips, output_path)

            # Extract thumbnails if enabled
            thumbnails = None
            if self.config.get('output.extract_thumbnails', True):
                thumbnails = self._extract_thumbnails_auto(input_video, clips)

            # Extract sound clips if enabled
            sound_clips = None
            if self.config.get('output.extract_sounds', True):
                sound_clips = self._extract_sounds_auto(input_video, clips, audio, sr)

            logger.info("Video assembly complete")
            return str(output_path), thumbnails, sound_clips

        finally:
            # Cleanup temp files
            if concat_file.exists():
                concat_file.unlink()

    def _extract_thumbnails_auto(self, video_path: str, clips: List[Clip]) -> Optional[List]:
        """
        Automatically extract thumbnails from clips.

        Args:
            video_path: Path to video
            clips: List of clips

        Returns:
            List of thumbnails or None
        """
        try:
            from .thumbnail_extractor import ThumbnailExtractor

            logger.info("Extracting thumbnails...")
            extractor = ThumbnailExtractor(self.config)
            thumbnails = extractor.extract_thumbnails(video_path, clips)

            # Export thumbnail list
            extractor.export_thumbnail_list(thumbnails)

            # Create grid if we have thumbnails
            if len(thumbnails) >= 4:
                try:
                    extractor.create_thumbnail_grid(thumbnails)
                except Exception as e:
                    logger.warning(f"Could not create thumbnail grid: {e}")

            logger.info(f"✓ Extracted {len(thumbnails)} thumbnails")
            return thumbnails

        except Exception as e:
            logger.error(f"Error extracting thumbnails: {e}")
            return None

    def _extract_sounds_auto(self, video_path: str, clips: List[Clip],
                            audio: Optional[np.ndarray], sr: int) -> Optional[List]:
        """
        Automatically extract sound clips.

        Args:
            video_path: Path to video
            clips: List of clips
            audio: Audio data (optional)
            sr: Sample rate

        Returns:
            List of sound clips or None
        """
        try:
            from .sound_extractor import SoundExtractor

            logger.info("Extracting sound clips...")
            extractor = SoundExtractor(self.config)

            max_clips = self.config.get('output.max_sound_clips', 10)
            sound_clips = extractor.extract_sound_clips(video_path, clips, max_clips)

            # Export sound list
            extractor.export_sound_list(sound_clips)

            logger.info(f"✓ Extracted {len(sound_clips)} sound clips")
            return sound_clips

        except Exception as e:
            logger.error(f"Error extracting sounds: {e}")
            return None

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

        # Check if memes are enabled
        memes_enabled = self.config.get('memes.enabled', False)

        if memes_enabled:
            # Use meme-enhanced clip extraction
            return self._create_concat_file_with_memes(input_video, clips)

        # Standard clip extraction
        with open(concat_file, 'w') as f:
            for i, clip in enumerate(clips):
                # Extract clip to temp file
                temp_clip = self.temp_dir / f"clip_{i:04d}.mp4"

                logger.info(f"Extracting clip {i + 1}/{len(clips)}: "
                           f"{clip.start_time:.1f}s - {clip.end_time:.1f}s")

                self._extract_clip(input_video, clip.start_time, clip.end_time, temp_clip)

                # Add to concat file (use absolute path to avoid path doubling)
                f.write(f"file '{temp_clip.absolute()}'\n")

        return concat_file

    def _create_concat_file_with_memes(self, input_video: str, clips: List[Clip]) -> Path:
        """
        Create concat file with meme-enhanced clips.

        Args:
            input_video: Source video path
            clips: List of clips

        Returns:
            Path to concat file
        """
        from .meme_generator import MemeGenerator
        from .video_effects import VideoEffects

        concat_file = self.temp_dir / "concat_list.txt"

        # Initialize meme generator
        meme_gen = MemeGenerator(self.config)
        video_fx = VideoEffects(self.config)

        # Analyze clips for meme opportunities
        logger.info("Analyzing clips for meme insertions...")
        all_meme_inserts = meme_gen.analyze_meme_opportunities(clips)

        # Group memes by clip
        memes_by_clip = {}
        for meme in all_meme_inserts:
            memes_by_clip.setdefault(meme.clip_index, []).append(meme)

        # Export meme list
        if all_meme_inserts:
            meme_gen.export_meme_list(all_meme_inserts)
            logger.info(f"✓ {len(all_meme_inserts)} memes will be inserted")

        # Extract clips with memes
        with open(concat_file, 'w') as f:
            for i, clip in enumerate(clips):
                temp_clip = self.temp_dir / f"clip_meme_{i:04d}.mp4"

                logger.info(f"Processing clip {i + 1}/{len(clips)}: "
                           f"{clip.start_time:.1f}s - {clip.end_time:.1f}s")

                # Get memes for this clip
                clip_memes = memes_by_clip.get(i, [])

                if clip_memes:
                    # Apply memes to clip
                    video_fx.apply_memes_to_clip(input_video, clip, clip_memes, str(temp_clip))
                else:
                    # Standard extraction
                    self._extract_clip(input_video, clip.start_time, clip.end_time, temp_clip)

                # Use absolute path to avoid path doubling issues
                f.write(f"file '{temp_clip.absolute()}'\n")

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

    def _apply_user_assets(self, video_path: Path, clips: List[Clip],
                          signals: List[Dict[str, Any]]) -> Path:
        """
        Apply user-provided assets (music, sounds, images) to the video.

        Args:
            video_path: Path to the assembled video
            clips: List of clips in the video
            signals: List of detected signals

        Returns:
            Path to the enhanced video
        """
        from .asset_manager import AssetManager
        import cv2

        logger.info("Applying user assets...")

        # Initialize asset manager
        asset_mgr = AssetManager(self.config)
        asset_mgr.load_assets()

        # Calculate video statistics
        total_duration = sum(c.duration for c in clips)
        avg_intensity = sum(c.score for c in clips) / len(clips) if clips else 0

        # Plan all asset placements
        all_placements = []

        # Music overlay
        if asset_mgr.music_pool or asset_mgr.music_required:
            music_placements = asset_mgr.plan_music_overlay(total_duration, len(clips), avg_intensity)
            all_placements.extend(music_placements)
            asset_mgr.placements.extend(music_placements)

        # Sound effects
        if asset_mgr.sounds_pool or asset_mgr.sounds_required:
            sound_placements = asset_mgr.plan_sound_effects(signals, total_duration)
            all_placements.extend(sound_placements)
            asset_mgr.placements.extend(sound_placements)

        # Image overlays
        if asset_mgr.images_pool or asset_mgr.images_required:
            image_placements = asset_mgr.plan_image_overlays(signals, total_duration)
            all_placements.extend(image_placements)
            asset_mgr.placements.extend(image_placements)

        if not all_placements:
            logger.info("No assets to apply")
            return video_path

        # Save asset report
        asset_mgr.save_placement_report(self.output_dir / "asset_placements.txt")

        # Apply assets to video
        enhanced_path = video_path.parent / f"{video_path.stem}_with_assets{video_path.suffix}"

        # Separate placements by type
        music_placements = [p for p in all_placements if p.asset_type == 'music']
        sound_placements = [p for p in all_placements if p.asset_type == 'sound']
        image_placements = [p for p in all_placements if p.asset_type == 'image']

        # Apply in stages
        current_video = video_path

        # Stage 1: Apply music overlay
        if music_placements:
            current_video = self._apply_music_overlay(current_video, music_placements, total_duration)

        # Stage 2: Apply sound effects
        if sound_placements:
            current_video = self._apply_sound_effects(current_video, sound_placements)

        # Stage 3: Apply image overlays
        if image_placements:
            current_video = self._apply_image_overlays(current_video, image_placements)

        # Rename to final output
        if current_video != enhanced_path:
            import shutil
            shutil.move(str(current_video), str(enhanced_path))

        logger.info(f"✓ Assets applied successfully: {enhanced_path.name}")
        return enhanced_path

    def _apply_music_overlay(self, video_path: Path, music_placements: List,
                            total_duration: float) -> Path:
        """Apply background music overlay to video."""
        logger.info(f"Applying {len(music_placements)} music track(s)...")

        output_path = video_path.parent / f"{video_path.stem}_music{video_path.suffix}"

        # Get music volume from config
        music_volume = self.config.get('assets.music.volume', 0.3)

        try:
            # Build ffmpeg filter for music overlay
            # Start with video
            video_input = ffmpeg.input(str(video_path))

            # For simplicity, use the first music track (can be extended for multiple)
            music = music_placements[0]
            music_input = ffmpeg.input(str(music.asset_path), ss=0, t=music.duration)

            # Mix audio: lower music volume, keep original audio
            mixed_audio = ffmpeg.filter([video_input.audio, music_input], 'amix',
                                       inputs=2, duration='first',
                                       weights=f'1.0 {music_volume}')

            # Output with mixed audio
            output = ffmpeg.output(video_input.video, mixed_audio, str(output_path),
                                  vcodec='copy', acodec='aac', audio_bitrate='192k')

            output.overwrite_output().run(capture_stdout=True, capture_stderr=True, quiet=True)

            logger.info(f"✓ Music overlay applied")
            return output_path

        except Exception as e:
            logger.error(f"Error applying music overlay: {e}")
            return video_path

    def _apply_sound_effects(self, video_path: Path, sound_placements: List) -> Path:
        """Apply sound effects at specific timestamps."""
        logger.info(f"Applying {len(sound_placements)} sound effect(s)...")

        output_path = video_path.parent / f"{video_path.stem}_sounds{video_path.suffix}"

        # Get sound volume from config
        sound_volume = self.config.get('assets.sounds.volume', 0.7)

        try:
            # This is complex for multiple sounds at different timestamps
            # For now, we'll use a simpler approach with adelay filter

            video_input = ffmpeg.input(str(video_path))
            audio_streams = [video_input.audio]

            # Add each sound effect with delay
            for sound in sound_placements:
                delay_ms = int(sound.timestamp * 1000)
                sound_input = ffmpeg.input(str(sound.asset_path))

                # Delay the sound to the correct timestamp
                delayed = sound_input.filter('adelay', f'{delay_ms}|{delay_ms}')
                delayed = delayed.filter('volume', sound_volume)

                audio_streams.append(delayed)

            # Mix all audio streams
            if len(audio_streams) > 1:
                mixed = ffmpeg.filter(audio_streams, 'amix',
                                    inputs=len(audio_streams),
                                    duration='first')
            else:
                mixed = audio_streams[0]

            # Output
            output = ffmpeg.output(video_input.video, mixed, str(output_path),
                                  vcodec='copy', acodec='aac', audio_bitrate='192k')

            output.overwrite_output().run(capture_stdout=True, capture_stderr=True, quiet=True)

            logger.info(f"✓ Sound effects applied")
            return output_path

        except Exception as e:
            logger.error(f"Error applying sound effects: {e}")
            return video_path

    def _apply_image_overlays(self, video_path: Path, image_placements: List) -> Path:
        """Apply image overlays at specific timestamps."""
        logger.info(f"Applying {len(image_placements)} image overlay(s)...")

        output_path = video_path.parent / f"{video_path.stem}_images{video_path.suffix}"

        try:
            import cv2
            from PIL import Image
            import numpy as np

            # Open video
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            temp_video = video_path.parent / f"{video_path.stem}_temp_images.mp4"
            out = cv2.VideoWriter(str(temp_video), fourcc, fps, (width, height))

            # Process frames
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                current_time = frame_idx / fps

                # Apply image overlays for this timestamp
                for img_placement in image_placements:
                    start_time = img_placement.timestamp
                    end_time = start_time + img_placement.duration

                    if start_time <= current_time < end_time:
                        frame = self._overlay_image(frame, img_placement, width, height)

                out.write(frame)
                frame_idx += 1

            cap.release()
            out.release()

            # Copy audio from original
            video_only = ffmpeg.input(str(temp_video))
            audio_only = ffmpeg.input(str(video_path)).audio

            output = ffmpeg.output(video_only, audio_only, str(output_path),
                                  vcodec='libx264', acodec='copy')
            output.overwrite_output().run(capture_stdout=True, capture_stderr=True, quiet=True)

            # Cleanup temp
            temp_video.unlink()

            logger.info(f"✓ Image overlays applied")
            return output_path

        except Exception as e:
            logger.error(f"Error applying image overlays: {e}")
            return video_path

    def _overlay_image(self, frame: np.ndarray, img_placement, frame_width: int,
                      frame_height: int) -> np.ndarray:
        """Overlay a single image on a frame."""
        try:
            from PIL import Image

            # Load overlay image
            overlay = Image.open(img_placement.asset_path)

            # Calculate overlay size
            size_fraction = img_placement.properties.get('size', 0.2)
            overlay_width = int(frame_width * size_fraction)
            aspect_ratio = overlay.size[1] / overlay.size[0]
            overlay_height = int(overlay_width * aspect_ratio)

            # Resize overlay
            overlay = overlay.resize((overlay_width, overlay_height), Image.Resampling.LANCZOS)

            # Convert to RGBA if needed
            if overlay.mode != 'RGBA':
                overlay = overlay.convert('RGBA')

            # Calculate position
            position = img_placement.properties.get('position', 'auto')
            padding = 20

            if position == 'top-left':
                x, y = padding, padding
            elif position == 'top-right':
                x, y = frame_width - overlay_width - padding, padding
            elif position == 'bottom-left':
                x, y = padding, frame_height - overlay_height - padding
            elif position == 'bottom-right':
                x, y = frame_width - overlay_width - padding, frame_height - overlay_height - padding
            elif position == 'center':
                x = (frame_width - overlay_width) // 2
                y = (frame_height - overlay_height) // 2
            else:  # auto - random corner
                import random
                positions = [
                    (padding, padding),
                    (frame_width - overlay_width - padding, padding),
                    (padding, frame_height - overlay_height - padding),
                    (frame_width - overlay_width - padding, frame_height - overlay_height - padding)
                ]
                x, y = random.choice(positions)

            # Convert overlay to numpy array
            overlay_array = np.array(overlay)

            # Get global opacity setting from config (0-100%)
            global_opacity = self.config.get('assets', {}).get('image_opacity', 100) / 100.0

            # Extract alpha channel
            if overlay_array.shape[2] == 4:
                alpha = (overlay_array[:, :, 3] / 255.0) * global_opacity
                overlay_rgb = overlay_array[:, :, :3]
            else:
                alpha = np.ones((overlay_height, overlay_width)) * global_opacity
                overlay_rgb = overlay_array

            # Extract region of interest from frame
            y1, y2 = y, y + overlay_height
            x1, x2 = x, x + overlay_width

            # Bounds checking
            if y1 < 0 or y2 > frame_height or x1 < 0 or x2 > frame_width:
                return frame

            roi = frame[y1:y2, x1:x2]

            # Alpha blending
            for c in range(3):
                roi[:, :, c] = (alpha * overlay_rgb[:, :, c] +
                               (1 - alpha) * roi[:, :, c])

            # Put blended region back
            frame[y1:y2, x1:x2] = roi

            return frame

        except Exception as e:
            logger.warning(f"Could not overlay image: {e}")
            return frame

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
