"""
Auto Edit - Automated Stream VOD Highlight Editor
Converts long-form stream VODs into engaging highlight videos.
"""

__version__ = "0.2.0"
__author__ = "Auto Edit Team"

from .config import Config
from .video_processor import VideoProcessor
from .signal_detector import SignalDetector
from .clip_selector import ClipSelector
from .video_assembler import VideoAssembler
from .thumbnail_extractor import ThumbnailExtractor
from .sound_extractor import SoundExtractor

__all__ = [
    "Config",
    "VideoProcessor",
    "SignalDetector",
    "ClipSelector",
    "VideoAssembler",
    "ThumbnailExtractor",
    "SoundExtractor",
]
