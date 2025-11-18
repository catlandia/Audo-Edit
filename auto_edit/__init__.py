"""
Auto Edit - Automated Stream VOD Highlight Editor
Converts long-form stream VODs into engaging highlight videos.
"""

__version__ = "0.4.0"
__author__ = "Auto Edit Team"

from .config import Config
from .video_processor import VideoProcessor
from .signal_detector import SignalDetector
from .clip_selector import ClipSelector
from .video_assembler import VideoAssembler
from .thumbnail_extractor import ThumbnailExtractor
from .sound_extractor import SoundExtractor
from .meme_generator import MemeGenerator
from .video_effects import VideoEffects
from .asset_manager import AssetManager

__all__ = [
    "Config",
    "VideoProcessor",
    "SignalDetector",
    "ClipSelector",
    "VideoAssembler",
    "ThumbnailExtractor",
    "SoundExtractor",
    "MemeGenerator",
    "VideoEffects",
    "AssetManager",
]
