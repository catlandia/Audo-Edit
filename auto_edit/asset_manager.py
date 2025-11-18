"""
Asset Manager for Auto Edit

Manages user-provided assets (music, sounds, images) with two modes:
1. POOL mode: Assets the system can intelligently choose from
2. REQUIRED mode: Assets that MUST be included in the final output

Author: Auto Edit Team
Version: 0.4.0
"""

import logging
import random
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MusicAsset:
    """Represents a music file asset"""
    path: Path
    name: str
    duration: Optional[float] = None
    required: bool = False
    energy_level: str = 'medium'  # 'low', 'medium', 'high'
    used: bool = False


@dataclass
class SoundAsset:
    """Represents a sound effect asset"""
    path: Path
    name: str
    duration: Optional[float] = None
    required: bool = False
    trigger_type: Optional[str] = None  # 'laughter', 'excitement', 'shouting', etc.
    used: bool = False


@dataclass
class ImageAsset:
    """Represents an image asset"""
    path: Path
    name: str
    required: bool = False
    position: str = 'auto'  # 'top-left', 'top-right', 'bottom-left', 'bottom-right', 'center', 'auto'
    size: float = 0.2  # Fraction of screen size
    duration: float = 2.0  # How long to show if required
    timestamp: Optional[float] = None  # When to show if required
    used: bool = False


@dataclass
class AssetPlacement:
    """Represents a planned asset placement"""
    asset_type: str  # 'music', 'sound', 'image'
    asset_path: Path
    timestamp: float
    duration: float
    properties: Dict[str, Any]


class AssetManager:
    """
    Manages user-provided assets for video enhancement

    Supports two modes for each asset type:
    - Pool mode: Assets in pool/ subdirectory - system chooses intelligently
    - Required mode: Assets in required/ subdirectory - MUST be included
    """

    def __init__(self, config: Dict[str, Any], base_dir: Optional[Path] = None):
        """
        Initialize the asset manager

        Args:
            config: Configuration dictionary
            base_dir: Base directory for the project (default: current directory)
        """
        self.config = config
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

        # Asset directories
        self.music_dir = self.base_dir / "music"
        self.sounds_dir = self.base_dir / "sounds"
        self.images_dir = self.base_dir / "images"

        # Asset storage
        self.music_pool: List[MusicAsset] = []
        self.music_required: List[MusicAsset] = []
        self.sounds_pool: List[SoundAsset] = []
        self.sounds_required: List[SoundAsset] = []
        self.images_pool: List[ImageAsset] = []
        self.images_required: List[ImageAsset] = []

        # Placement tracking
        self.placements: List[AssetPlacement] = []

        logger.info("Asset Manager initialized")

    def load_assets(self) -> None:
        """Load all assets from their respective directories"""
        logger.info("Loading assets...")

        # Load music
        self._load_music()

        # Load sounds
        self._load_sounds()

        # Load images
        self._load_images()

        logger.info(
            f"Assets loaded: "
            f"{len(self.music_pool)} music pool, {len(self.music_required)} music required, "
            f"{len(self.sounds_pool)} sounds pool, {len(self.sounds_required)} sounds required, "
            f"{len(self.images_pool)} images pool, {len(self.images_required)} images required"
        )

    def _load_music(self) -> None:
        """Load music assets from music directory"""
        if not self.music_dir.exists():
            logger.debug(f"Music directory does not exist: {self.music_dir}")
            return

        # Load pool music
        pool_dir = self.music_dir / "pool"
        if pool_dir.exists():
            for file in pool_dir.glob("*"):
                if file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                    asset = self._parse_music_asset(file, required=False)
                    self.music_pool.append(asset)
                    logger.debug(f"Loaded music pool: {asset.name}")

        # Load required music
        required_dir = self.music_dir / "required"
        if required_dir.exists():
            for file in required_dir.glob("*"):
                if file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                    asset = self._parse_music_asset(file, required=True)
                    self.music_required.append(asset)
                    logger.debug(f"Loaded music required: {asset.name}")

    def _parse_music_asset(self, file: Path, required: bool) -> MusicAsset:
        """Parse a music file and extract metadata from filename"""
        name = file.stem
        energy_level = 'medium'

        # Parse energy level from filename (e.g., "epic_high.mp3", "chill_low.mp3")
        name_lower = name.lower()
        if 'high' in name_lower or 'epic' in name_lower or 'intense' in name_lower:
            energy_level = 'high'
        elif 'low' in name_lower or 'chill' in name_lower or 'calm' in name_lower:
            energy_level = 'low'

        return MusicAsset(
            path=file,
            name=name,
            required=required,
            energy_level=energy_level
        )

    def _load_sounds(self) -> None:
        """Load sound effect assets from sounds directory"""
        if not self.sounds_dir.exists():
            logger.debug(f"Sounds directory does not exist: {self.sounds_dir}")
            return

        # Load pool sounds
        pool_dir = self.sounds_dir / "pool"
        if pool_dir.exists():
            for file in pool_dir.glob("*"):
                if file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                    asset = self._parse_sound_asset(file, required=False)
                    self.sounds_pool.append(asset)
                    logger.debug(f"Loaded sound pool: {asset.name}")

        # Load required sounds
        required_dir = self.sounds_dir / "required"
        if required_dir.exists():
            for file in required_dir.glob("*"):
                if file.suffix.lower() in ['.mp3', '.wav', '.ogg', '.m4a']:
                    asset = self._parse_sound_asset(file, required=True)
                    self.sounds_required.append(asset)
                    logger.debug(f"Loaded sound required: {asset.name}")

    def _parse_sound_asset(self, file: Path, required: bool) -> SoundAsset:
        """Parse a sound file and extract metadata from filename"""
        name = file.stem
        trigger_type = None

        # Parse trigger type from filename
        name_lower = name.lower()
        if 'laugh' in name_lower or 'lol' in name_lower:
            trigger_type = 'laughter'
        elif 'excite' in name_lower or 'hype' in name_lower or 'pog' in name_lower:
            trigger_type = 'excitement'
        elif 'shout' in name_lower or 'scream' in name_lower:
            trigger_type = 'shouting'
        elif 'wow' in name_lower or 'amaze' in name_lower:
            trigger_type = 'excitement'
        elif 'fail' in name_lower or 'sad' in name_lower:
            trigger_type = 'negative'

        return SoundAsset(
            path=file,
            name=name,
            required=required,
            trigger_type=trigger_type
        )

    def _load_images(self) -> None:
        """Load image assets from images directory"""
        if not self.images_dir.exists():
            logger.debug(f"Images directory does not exist: {self.images_dir}")
            return

        # Load pool images
        pool_dir = self.images_dir / "pool"
        if pool_dir.exists():
            for file in pool_dir.glob("*"):
                if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    asset = self._parse_image_asset(file, required=False)
                    self.images_pool.append(asset)
                    logger.debug(f"Loaded image pool: {asset.name}")

        # Load required images
        required_dir = self.images_dir / "required"
        if required_dir.exists():
            for file in required_dir.glob("*"):
                if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    asset = self._parse_image_asset(file, required=True)
                    self.images_required.append(asset)
                    logger.debug(f"Loaded image required: {asset.name}")

    def _parse_image_asset(self, file: Path, required: bool) -> ImageAsset:
        """Parse an image file and extract metadata from filename"""
        name = file.stem
        position = 'auto'
        size = 0.2
        duration = 2.0
        timestamp = None

        # Parse position from filename (e.g., "logo_top-left.png")
        name_lower = name.lower()
        if 'top-left' in name_lower or 'topleft' in name_lower:
            position = 'top-left'
        elif 'top-right' in name_lower or 'topright' in name_lower:
            position = 'top-right'
        elif 'bottom-left' in name_lower or 'bottomleft' in name_lower:
            position = 'bottom-left'
        elif 'bottom-right' in name_lower or 'bottomright' in name_lower:
            position = 'bottom-right'
        elif 'center' in name_lower:
            position = 'center'

        # Parse size from filename (e.g., "logo_small.png", "banner_large.png")
        if 'small' in name_lower or 'tiny' in name_lower:
            size = 0.1
        elif 'large' in name_lower or 'big' in name_lower:
            size = 0.3
        elif 'huge' in name_lower or 'full' in name_lower:
            size = 0.5

        # Parse duration from filename (e.g., "logo_5s.png")
        import re
        duration_match = re.search(r'(\d+)s', name_lower)
        if duration_match:
            duration = float(duration_match.group(1))

        # Parse timestamp from filename (e.g., "logo_at30.png" = show at 30 seconds)
        timestamp_match = re.search(r'at(\d+)', name_lower)
        if timestamp_match:
            timestamp = float(timestamp_match.group(1))

        return ImageAsset(
            path=file,
            name=name,
            required=required,
            position=position,
            size=size,
            duration=duration,
            timestamp=timestamp
        )

    def plan_music_overlay(self, total_duration: float, clip_count: int,
                          avg_intensity: float) -> List[AssetPlacement]:
        """
        Plan music overlay for the entire video

        Args:
            total_duration: Total duration of the final video in seconds
            clip_count: Number of clips in the video
            avg_intensity: Average intensity of the video (0-1)

        Returns:
            List of music placements
        """
        placements = []

        # First, handle required music
        current_time = 0.0
        for music in self.music_required:
            if music.used:
                continue

            # Get duration from config or estimate
            duration = music.duration or self.config.get('assets', {}).get('music', {}).get('default_duration', 30.0)

            # Make sure we don't exceed video duration
            if current_time + duration > total_duration:
                duration = total_duration - current_time

            if duration > 0:
                placements.append(AssetPlacement(
                    asset_type='music',
                    asset_path=music.path,
                    timestamp=current_time,
                    duration=duration,
                    properties={'energy_level': music.energy_level, 'required': True}
                ))
                music.used = True
                current_time += duration

        # Then, fill remaining time with pool music if available
        if current_time < total_duration and self.music_pool:
            # Choose music based on video intensity
            if avg_intensity > 0.7:
                target_energy = 'high'
            elif avg_intensity > 0.4:
                target_energy = 'medium'
            else:
                target_energy = 'low'

            # Filter by energy level
            suitable_music = [m for m in self.music_pool if m.energy_level == target_energy and not m.used]
            if not suitable_music:
                suitable_music = [m for m in self.music_pool if not m.used]

            if suitable_music:
                music = random.choice(suitable_music)
                duration = total_duration - current_time

                placements.append(AssetPlacement(
                    asset_type='music',
                    asset_path=music.path,
                    timestamp=current_time,
                    duration=duration,
                    properties={'energy_level': music.energy_level, 'required': False}
                ))
                music.used = True

        logger.info(f"Planned {len(placements)} music overlays")
        return placements

    def plan_sound_effects(self, signals: List[Dict[str, Any]],
                          video_duration: float) -> List[AssetPlacement]:
        """
        Plan sound effect insertions based on detected signals

        Args:
            signals: List of detected signals with timestamps and types
            video_duration: Total video duration in seconds

        Returns:
            List of sound effect placements
        """
        placements = []

        # First, handle required sounds (place at random high-intensity moments)
        high_intensity_signals = [s for s in signals if s.get('intensity', 0) > 0.7]

        for sound in self.sounds_required:
            if sound.used:
                continue

            # Place at a high-intensity moment if available
            if high_intensity_signals:
                signal = random.choice(high_intensity_signals)
                timestamp = signal.get('timestamp', 0)
                high_intensity_signals.remove(signal)  # Don't reuse the same moment
            else:
                # Place randomly if no high-intensity moments
                timestamp = random.uniform(0, max(0.1, video_duration - 1))

            duration = sound.duration or 2.0

            placements.append(AssetPlacement(
                asset_type='sound',
                asset_path=sound.path,
                timestamp=timestamp,
                duration=duration,
                properties={'trigger_type': sound.trigger_type, 'required': True}
            ))
            sound.used = True

        # Then, intelligently place pool sounds based on signal types
        for signal in signals:
            signal_type = signal.get('type', '')
            signal_intensity = signal.get('intensity', 0)
            signal_timestamp = signal.get('timestamp', 0)

            # Only place sounds at moderately intense moments
            if signal_intensity < 0.5:
                continue

            # Find suitable sounds for this signal type
            suitable_sounds = [
                s for s in self.sounds_pool
                if not s.used and (s.trigger_type == signal_type or s.trigger_type is None)
            ]

            if suitable_sounds and random.random() < 0.3:  # 30% chance to add a sound
                sound = random.choice(suitable_sounds)
                duration = sound.duration or 1.5

                placements.append(AssetPlacement(
                    asset_type='sound',
                    asset_path=sound.path,
                    timestamp=signal_timestamp,
                    duration=duration,
                    properties={'trigger_type': sound.trigger_type, 'required': False}
                ))
                # Don't mark as used so it can be reused

        logger.info(f"Planned {len(placements)} sound effect insertions")
        return placements

    def plan_image_overlays(self, signals: List[Dict[str, Any]],
                           video_duration: float) -> List[AssetPlacement]:
        """
        Plan image overlay placements

        Args:
            signals: List of detected signals with timestamps and types
            video_duration: Total video duration in seconds

        Returns:
            List of image placements
        """
        placements = []

        # First, handle required images
        for image in self.images_required:
            if image.used:
                continue

            # Use specified timestamp or place randomly
            if image.timestamp is not None:
                timestamp = min(image.timestamp, video_duration - image.duration)
            else:
                timestamp = random.uniform(0, max(0.1, video_duration - image.duration))

            placements.append(AssetPlacement(
                asset_type='image',
                asset_path=image.path,
                timestamp=timestamp,
                duration=image.duration,
                properties={
                    'position': image.position,
                    'size': image.size,
                    'required': True
                }
            ))
            image.used = True

        # Then, place pool images at interesting moments
        max_pool_images = self.config.get('assets', {}).get('images', {}).get('max_pool_per_video', 3)
        placed_count = 0

        high_intensity_signals = sorted(
            [s for s in signals if s.get('intensity', 0) > 0.6],
            key=lambda x: x.get('intensity', 0),
            reverse=True
        )

        for signal in high_intensity_signals:
            if placed_count >= max_pool_images:
                break

            if not self.images_pool:
                break

            # Random chance to place an image
            if random.random() < 0.2:  # 20% chance
                image = random.choice([img for img in self.images_pool if not img.used])
                timestamp = signal.get('timestamp', 0)

                placements.append(AssetPlacement(
                    asset_type='image',
                    asset_path=image.path,
                    timestamp=timestamp,
                    duration=image.duration,
                    properties={
                        'position': image.position,
                        'size': image.size,
                        'required': False
                    }
                ))
                placed_count += 1

        logger.info(f"Planned {len(placements)} image overlays")
        return placements

    def get_all_placements(self) -> List[AssetPlacement]:
        """Get all planned asset placements"""
        return sorted(self.placements, key=lambda p: p.timestamp)

    def save_placement_report(self, output_path: Path) -> None:
        """
        Save a report of all asset placements to a file

        Args:
            output_path: Path to save the report
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("ASSET PLACEMENT REPORT\n")
            f.write("=" * 80 + "\n\n")

            # Group by asset type
            by_type = {}
            for placement in self.placements:
                asset_type = placement.asset_type
                if asset_type not in by_type:
                    by_type[asset_type] = []
                by_type[asset_type].append(placement)

            # Write each type
            for asset_type, placements_list in sorted(by_type.items()):
                f.write(f"\n{asset_type.upper()} ({len(placements_list)} total)\n")
                f.write("-" * 80 + "\n")

                for p in sorted(placements_list, key=lambda x: x.timestamp):
                    required = p.properties.get('required', False)
                    req_str = " [REQUIRED]" if required else ""

                    f.write(f"  @ {p.timestamp:.2f}s - {p.duration:.2f}s duration{req_str}\n")
                    f.write(f"    File: {p.asset_path.name}\n")

                    # Add type-specific properties
                    if asset_type == 'music':
                        f.write(f"    Energy: {p.properties.get('energy_level', 'N/A')}\n")
                    elif asset_type == 'sound':
                        f.write(f"    Trigger: {p.properties.get('trigger_type', 'N/A')}\n")
                    elif asset_type == 'image':
                        f.write(f"    Position: {p.properties.get('position', 'N/A')}\n")
                        f.write(f"    Size: {p.properties.get('size', 0.2):.1%}\n")

                    f.write("\n")

            f.write("=" * 80 + "\n")

        logger.info(f"Saved asset placement report to {output_path}")
