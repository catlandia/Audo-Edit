"""Utility functions for Auto Edit."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import timedelta
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    """
    Setup logging configuration.

    Args:
        level: Logging level
        log_file: Optional log file path
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=handlers
    )


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 15m 30s")
    """
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_timestamp(seconds: float) -> str:
    """
    Format timestamp in HH:MM:SS format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def print_header(text: str) -> None:
    """Print colored header."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 80}")
    print(f"{text:^80}")
    print(f"{'=' * 80}{Style.RESET_ALL}\n")


def print_success(text: str) -> None:
    """Print success message."""
    try:
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"{Fore.GREEN}[OK] {text}{Style.RESET_ALL}")


def print_error(text: str) -> None:
    """Print error message."""
    try:
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"{Fore.RED}[ERROR] {text}{Style.RESET_ALL}")


def print_warning(text: str) -> None:
    """Print warning message."""
    try:
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"{Fore.YELLOW}[WARNING] {text}{Style.RESET_ALL}")


def print_info(text: str) -> None:
    """Print info message."""
    try:
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")
    except UnicodeEncodeError:
        print(f"{Fore.BLUE}[INFO] {text}{Style.RESET_ALL}")


def print_clips_summary(clips, video_duration: float) -> None:
    """
    Print summary of selected clips.

    Args:
        clips: List of clips
        video_duration: Total video duration
    """
    if not clips:
        print_warning("No clips selected")
        return

    print_header("Selected Clips Summary")

    total_duration = sum(c.duration for c in clips)
    coverage = (total_duration / video_duration) * 100 if video_duration > 0 else 0

    print(f"{Fore.CYAN}Total clips:{Style.RESET_ALL} {len(clips)}")
    print(f"{Fore.CYAN}Total duration:{Style.RESET_ALL} "
          f"{format_duration(total_duration)} ({total_duration / 60:.1f} minutes)")
    print(f"{Fore.CYAN}Coverage:{Style.RESET_ALL} {coverage:.1f}% of original video")
    print(f"{Fore.CYAN}Average clip length:{Style.RESET_ALL} "
          f"{format_duration(total_duration / len(clips))}")

    print(f"\n{Fore.YELLOW}Top 5 clips by score:{Style.RESET_ALL}")
    top_clips = sorted(clips, key=lambda x: x.score, reverse=True)[:5]

    for i, clip in enumerate(top_clips, 1):
        print(f"  {i}. {format_timestamp(clip.start_time)} - "
              f"{format_timestamp(clip.end_time)} "
              f"({format_duration(clip.duration)}) - "
              f"Score: {clip.score:.3f} - {clip.reason}")


def print_signals_summary(signals: Dict[str, Any]) -> None:
    """
    Print summary of detected signals.

    Args:
        signals: Dictionary of signals
    """
    print_header("Detected Signals Summary")

    total_events = sum(len(events) for events in signals.values())
    print(f"{Fore.CYAN}Total events:{Style.RESET_ALL} {total_events}")

    print(f"\n{Fore.YELLOW}By signal type:{Style.RESET_ALL}")
    for signal_type, events in sorted(signals.items(), key=lambda x: len(x[1]), reverse=True):
        if events:
            avg_intensity = sum(e.intensity for e in events) / len(events)
            print(f"  {signal_type:.<30} {len(events):>4} events "
                  f"(avg intensity: {avg_intensity:.2f})")


def sanitize_path(path: str, base_dir: Optional[Path] = None, must_exist: bool = False) -> Path:
    """
    Sanitize and validate a file path for security.

    Args:
        path: Path to sanitize
        base_dir: Optional base directory to validate path is within
        must_exist: Whether path must exist

    Returns:
        Resolved, validated Path object

    Raises:
        ValueError: If path is invalid or outside base_dir
    """
    try:
        # Resolve to absolute canonical path
        resolved_path = Path(path).resolve(strict=False)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")

    # If base_dir specified, ensure path is within it
    if base_dir is not None:
        base_dir = Path(base_dir).resolve()
        try:
            resolved_path.relative_to(base_dir)
        except ValueError:
            raise ValueError(f"Path {path} is outside allowed directory {base_dir}")

    # Check existence if required
    if must_exist and not resolved_path.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved_path}")

    return resolved_path


def validate_video_file(path: str) -> Path:
    """
    Validate video file exists and is readable.

    Args:
        path: Path to video file

    Returns:
        Resolved Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a video or path is invalid
    """
    # Security: Resolve path to absolute canonical path (prevents ../ attacks)
    try:
        path = Path(path).resolve(strict=False)
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")

    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    # Check extension
    valid_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', '.ts'}
    if path.suffix.lower() not in valid_extensions:
        raise ValueError(f"Invalid video file extension: {path.suffix}")

    return path


def get_file_size_mb(path: Path) -> float:
    """Get file size in MB."""
    return path.stat().st_size / (1024 * 1024)


def print_video_info(metadata: Dict[str, Any]) -> None:
    """
    Print video information.

    Args:
        metadata: Video metadata
    """
    print_header("Video Information")

    print(f"{Fore.CYAN}Duration:{Style.RESET_ALL} "
          f"{format_duration(metadata['duration_seconds'])} "
          f"({metadata['duration_hours']:.2f} hours)")
    print(f"{Fore.CYAN}Resolution:{Style.RESET_ALL} "
          f"{metadata['width']}x{metadata['height']}")
    print(f"{Fore.CYAN}FPS:{Style.RESET_ALL} {metadata['fps']:.2f}")
    print(f"{Fore.CYAN}Total frames:{Style.RESET_ALL} {metadata['frame_count']:,}")

    file_size = get_file_size_mb(Path(metadata['path']))
    print(f"{Fore.CYAN}File size:{Style.RESET_ALL} {file_size:.1f} MB")


def create_progress_callback(description: str = "Processing"):
    """
    Create a progress callback for long-running operations.

    Args:
        description: Description of operation

    Returns:
        Callback function
    """
    from tqdm import tqdm

    pbar = None

    def callback(current: int, total: int):
        nonlocal pbar
        if pbar is None:
            pbar = tqdm(total=total, desc=description)
        pbar.update(current - pbar.n)

        if current >= total:
            pbar.close()
            pbar = None

    return callback
