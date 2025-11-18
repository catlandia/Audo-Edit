"""Meme and image insertion for video enhancement."""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import random

from .clip_selector import Clip
from .signal_detector import SignalEvent

logger = logging.getLogger(__name__)


@dataclass
class MemeInsert:
    """Represents a meme insertion point."""
    clip_index: int
    timestamp: float
    duration: float
    meme_type: str
    image_path: Optional[str]
    text: Optional[str]
    position: str  # 'top', 'bottom', 'center', 'corner'
    size: float  # Scale factor 0-1
    opacity: float  # 0-1


class MemeGenerator:
    """Generates and inserts memes and images into videos."""

    # Meme type mappings based on signal types
    MEME_MAPPINGS = {
        'laughter': ['laughing', 'lmao', 'dead', 'crying_laughing'],
        'shouting': ['screaming', 'intense', 'angry', 'shocked'],
        'excitement': ['hype', 'poggers', 'excited', 'epic'],
        'audio_peak': ['loud', 'boom', 'explosion', 'intense'],
        'silence_to_chaos': ['surprised', 'shocked', 'what', 'ohno'],
        'facecam_reaction': ['reaction', 'surprised', 'shocked'],
        'chat_activity': ['chat', 'spam', 'kekw'],
        'scene_change': ['transition', 'new_scene'],
    }

    # Text templates for different moment types
    TEXT_TEMPLATES = {
        'laughter': ['LMAO', 'DEAD', '💀', 'IM DYING', 'CANT BREATHE'],
        'shouting': ['AHHH!', 'WHAT!?', 'NO WAY!', 'OMG!', 'BRUH'],
        'excitement': ['LETS GO!', 'POGGERS', 'HYPE!', 'SHEESH', 'W'],
        'audio_peak': ['LOUD', 'RIP HEADPHONES', '🔊', 'BASS BOOSTED'],
        'silence_to_chaos': ['WAIT WHAT', 'SUDDENLY', '?!', 'UH OH'],
        'epic': ['EPIC', 'LEGENDARY', 'INSANE', 'GODLIKE', '🔥'],
    }

    def __init__(self, config):
        """
        Initialize meme generator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.output_dir = config.get('paths.output_dir', Path('./output'))
        self.memes_dir = Path('memes')  # User-provided meme library
        self.memes_dir.mkdir(parents=True, exist_ok=True)

        # Default meme positions
        self.positions = {
            'top': (0.5, 0.15),
            'bottom': (0.5, 0.85),
            'center': (0.5, 0.5),
            'top_left': (0.15, 0.15),
            'top_right': (0.85, 0.15),
            'bottom_left': (0.15, 0.85),
            'bottom_right': (0.85, 0.85),
        }

    def analyze_meme_opportunities(self, clips: List[Clip]) -> List[MemeInsert]:
        """
        Analyze clips to find good moments for meme insertion.

        Args:
            clips: List of clips

        Returns:
            List of meme insertion points
        """
        logger.info("Analyzing meme insertion opportunities...")

        meme_inserts = []

        for i, clip in enumerate(clips):
            # Determine if this clip is meme-worthy based on signals
            if not clip.signals:
                continue

            # Get dominant signal type
            top_signal = max(clip.signals, key=lambda s: s.intensity)
            signal_type = top_signal.signal_type

            # Check if we should add a meme
            if self._should_add_meme(clip, top_signal):
                meme = self._create_meme_insert(i, clip, top_signal)
                if meme:
                    meme_inserts.append(meme)

        logger.info(f"Found {len(meme_inserts)} meme insertion opportunities")
        return meme_inserts

    def _should_add_meme(self, clip: Clip, signal: SignalEvent) -> bool:
        """
        Determine if a meme should be added to this clip.

        Args:
            clip: Clip object
            signal: Top signal

        Returns:
            True if meme should be added
        """
        # High intensity moments are meme-worthy
        if signal.intensity > 0.7:
            return True

        # Multiple strong signals
        strong_signals = [s for s in clip.signals if s.intensity > 0.6]
        if len(strong_signals) >= 2:
            return True

        # Specific signal types that are inherently meme-worthy
        meme_worthy_types = ['laughter', 'shouting', 'silence_to_chaos', 'facecam_reaction']
        if signal.signal_type in meme_worthy_types and signal.intensity > 0.5:
            return True

        return False

    def _create_meme_insert(self, clip_index: int, clip: Clip,
                           signal: SignalEvent) -> Optional[MemeInsert]:
        """
        Create a meme insert specification.

        Args:
            clip_index: Index of the clip
            clip: Clip object
            signal: Top signal

        Returns:
            MemeInsert object or None
        """
        signal_type = signal.signal_type

        # Determine meme style based on configuration
        meme_style = self.config.get('memes.style', 'text')  # 'text', 'image', 'both'

        # Choose position based on signal type
        position = self._choose_position(signal_type)

        # Duration for meme display
        duration = min(2.0, clip.duration * 0.3)  # Max 2 seconds or 30% of clip

        # Get meme text
        text = self._get_meme_text(signal_type, signal.intensity)

        # Try to find matching image if using images
        image_path = None
        if meme_style in ['image', 'both']:
            image_path = self._find_meme_image(signal_type)

        # Size and opacity based on intensity
        size = 0.15 + (signal.intensity * 0.15)  # 15-30% of screen
        opacity = 0.7 + (signal.intensity * 0.3)  # 70-100% opacity

        return MemeInsert(
            clip_index=clip_index,
            timestamp=clip.start_time + (clip.duration * 0.2),  # 20% into clip
            duration=duration,
            meme_type=signal_type,
            image_path=image_path,
            text=text if meme_style in ['text', 'both'] else None,
            position=position,
            size=min(1.0, size),
            opacity=min(1.0, opacity)
        )

    def _choose_position(self, signal_type: str) -> str:
        """
        Choose appropriate position for meme based on signal type.

        Args:
            signal_type: Type of signal

        Returns:
            Position string
        """
        position_map = {
            'laughter': 'bottom',
            'shouting': 'center',
            'excitement': 'top',
            'audio_peak': 'top',
            'silence_to_chaos': 'center',
            'facecam_reaction': 'top_right',
            'chat_activity': 'bottom_right',
        }

        return position_map.get(signal_type, 'bottom')

    def _get_meme_text(self, signal_type: str, intensity: float) -> str:
        """
        Get appropriate meme text for signal type.

        Args:
            signal_type: Type of signal
            intensity: Signal intensity

        Returns:
            Meme text
        """
        # Map signal types to text template categories
        text_category_map = {
            'laughter': 'laughter',
            'shouting': 'shouting',
            'excitement': 'excitement',
            'audio_peak': 'audio_peak',
            'silence_to_chaos': 'silence_to_chaos',
            'high_motion': 'excitement',
            'scene_change': 'epic',
        }

        category = text_category_map.get(signal_type, 'excitement')
        templates = self.TEXT_TEMPLATES.get(category, ['EPIC'])

        # Choose text based on intensity
        if intensity > 0.9:
            # Super intense - use all caps, multiple exclamation marks
            text = random.choice(templates)
            if not any(emoji in text for emoji in ['💀', '🔊', '🔥', '?!']):
                text += '!!!'
        elif intensity > 0.7:
            text = random.choice(templates)
            if '!' not in text and '💀' not in text:
                text += '!'
        else:
            text = random.choice(templates)

        return text

    def _find_meme_image(self, signal_type: str) -> Optional[str]:
        """
        Find appropriate meme image for signal type.

        Args:
            signal_type: Type of signal

        Returns:
            Path to meme image or None
        """
        # Check user's meme library
        meme_categories = self.MEME_MAPPINGS.get(signal_type, [])

        for category in meme_categories:
            # Look for images matching this category
            pattern = f"{category}*"
            matches = list(self.memes_dir.glob(f"{pattern}.png")) + \
                     list(self.memes_dir.glob(f"{pattern}.jpg"))

            if matches:
                return str(random.choice(matches))

        # Check default memes folder
        default_memes = list(self.memes_dir.glob("*.png")) + \
                       list(self.memes_dir.glob("*.jpg"))

        if default_memes:
            return str(random.choice(default_memes))

        return None

    def create_text_overlay(self, frame: np.ndarray, text: str,
                           position: Tuple[float, float], size: float,
                           opacity: float) -> np.ndarray:
        """
        Create text overlay on frame.

        Args:
            frame: Video frame
            text: Text to overlay
            position: Position as (x, y) normalized coordinates
            size: Size factor
            opacity: Opacity 0-1

        Returns:
            Frame with text overlay
        """
        # Convert to PIL for better text rendering
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        # Create drawing context
        draw = ImageDraw.Draw(pil_image, 'RGBA')

        # Calculate font size based on frame size and size factor
        frame_height = frame.shape[0]
        font_size = int(frame_height * size * 0.15)  # Scale with frame

        try:
            # Try to load a bold font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Fallback to default
                font = ImageFont.load_default()

        # Calculate text position
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = int(position[0] * frame.shape[1] - text_width / 2)
        y = int(position[1] * frame.shape[0] - text_height / 2)

        # Draw text with outline for readability
        outline_color = (0, 0, 0, int(255 * opacity))
        text_color = (255, 255, 255, int(255 * opacity))

        # Draw outline
        for offset_x in [-2, 0, 2]:
            for offset_y in [-2, 0, 2]:
                if offset_x != 0 or offset_y != 0:
                    draw.text((x + offset_x, y + offset_y), text, font=font, fill=outline_color)

        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color)

        # Convert back to OpenCV
        frame_with_text = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return frame_with_text

    def create_image_overlay(self, frame: np.ndarray, image_path: str,
                            position: Tuple[float, float], size: float,
                            opacity: float) -> np.ndarray:
        """
        Overlay an image on the frame.

        Args:
            frame: Video frame
            image_path: Path to overlay image
            position: Position as (x, y) normalized coordinates
            size: Size factor
            opacity: Opacity 0-1

        Returns:
            Frame with image overlay
        """
        # Load image
        overlay_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if overlay_img is None:
            logger.warning(f"Could not load image: {image_path}")
            return frame

        # Resize image based on size factor
        frame_height = frame.shape[0]
        target_height = int(frame_height * size)

        aspect_ratio = overlay_img.shape[1] / overlay_img.shape[0]
        target_width = int(target_height * aspect_ratio)

        overlay_img = cv2.resize(overlay_img, (target_width, target_height))

        # Calculate position
        x = int(position[0] * frame.shape[1] - target_width / 2)
        y = int(position[1] * frame.shape[0] - target_height / 2)

        # Ensure image fits in frame
        x = max(0, min(x, frame.shape[1] - target_width))
        y = max(0, min(y, frame.shape[0] - target_height))

        # Apply overlay with alpha blending
        if overlay_img.shape[2] == 4:  # Has alpha channel
            # Extract alpha channel
            alpha = overlay_img[:, :, 3] / 255.0 * opacity
            alpha = alpha[:, :, np.newaxis]

            # Get overlay region
            overlay_region = frame[y:y+target_height, x:x+target_width]

            # Blend
            overlay_rgb = overlay_img[:, :, :3]
            blended = (overlay_rgb * alpha + overlay_region * (1 - alpha)).astype(np.uint8)

            frame[y:y+target_height, x:x+target_width] = blended
        else:
            # No alpha channel, use simple overlay with opacity
            overlay_region = frame[y:y+target_height, x:x+target_width]
            blended = cv2.addWeighted(overlay_img, opacity, overlay_region, 1 - opacity, 0)
            frame[y:y+target_height, x:x+target_width] = blended

        return frame

    def create_meme_template(self, text_top: str, text_bottom: str,
                            background_color: Tuple[int, int, int] = (0, 0, 0),
                            text_color: Tuple[int, int, int] = (255, 255, 255),
                            width: int = 600, height: int = 600) -> str:
        """
        Create a classic meme template image with text.

        Args:
            text_top: Top text
            text_bottom: Bottom text
            background_color: Background RGB color
            text_color: Text RGB color
            width: Image width
            height: Image height

        Returns:
            Path to created meme image
        """
        # Create image
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)

        try:
            font_size = int(height * 0.1)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Draw top text
        if text_top:
            bbox = draw.textbbox((0, 0), text_top, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = int(height * 0.1)

            # Outline
            for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                draw.text((x + offset[0], y + offset[1]), text_top, font=font, fill=(0, 0, 0))
            draw.text((x, y), text_top, font=font, fill=text_color)

        # Draw bottom text
        if text_bottom:
            bbox = draw.textbbox((0, 0), text_bottom, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = int(height * 0.85)

            # Outline
            for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                draw.text((x + offset[0], y + offset[1]), text_bottom, font=font, fill=(0, 0, 0))
            draw.text((x, y), text_bottom, font=font, fill=text_color)

        # Save
        output_path = self.memes_dir / f"meme_{text_top[:10]}_{text_bottom[:10]}.png"
        img.save(output_path)

        return str(output_path)

    def export_meme_list(self, meme_inserts: List[MemeInsert],
                        output_path: Optional[str] = None) -> str:
        """
        Export list of meme insertions.

        Args:
            meme_inserts: List of meme inserts
            output_path: Optional output path

        Returns:
            Path to exported file
        """
        if output_path is None:
            output_path = self.output_dir / "meme_inserts.txt"

        with open(output_path, 'w') as f:
            f.write("Auto Edit - Meme Insertions\n")
            f.write("=" * 80 + "\n\n")

            for i, meme in enumerate(meme_inserts, 1):
                f.write(f"Meme {i} (Clip {meme.clip_index}):\n")
                f.write(f"  Timestamp: {meme.timestamp:.2f}s\n")
                f.write(f"  Duration: {meme.duration:.2f}s\n")
                f.write(f"  Type: {meme.meme_type}\n")
                f.write(f"  Text: {meme.text or 'N/A'}\n")
                f.write(f"  Image: {Path(meme.image_path).name if meme.image_path else 'N/A'}\n")
                f.write(f"  Position: {meme.position}\n")
                f.write(f"  Size: {meme.size:.2f}\n")
                f.write(f"  Opacity: {meme.opacity:.2f}\n")
                f.write("\n")

            f.write("=" * 80 + "\n")
            f.write(f"Total memes: {len(meme_inserts)}\n")

        logger.info(f"Meme list exported: {output_path}")
        return str(output_path)

    def create_example_memes(self):
        """Create example meme images for users to start with."""
        logger.info("Creating example meme templates...")

        examples = [
            ("WHEN THE", "IMPOSTER IS SUS", (255, 0, 0)),
            ("TOP TEXT", "BOTTOM TEXT", (0, 0, 0)),
            ("POV:", "YOU JUST CLUTCHED", (0, 100, 255)),
            ("NOBODY:", "LITERALLY NOBODY:", (0, 0, 0)),
        ]

        for top, bottom, color in examples:
            try:
                self.create_meme_template(top, bottom, background_color=color)
            except Exception as e:
                logger.warning(f"Could not create example meme: {e}")

        logger.info("Example memes created in memes/ folder")
