#!/usr/bin/env python3
"""
Auto Edit - Automated Stream Highlight Editor
Main CLI interface
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from auto_edit import Config, VideoProcessor, SignalDetector, ClipSelector, VideoAssembler
from auto_edit.style_learner import StyleLearner
from auto_edit.utils import (
    setup_logging, print_header, print_success, print_error,
    print_info, print_video_info, print_signals_summary,
    print_clips_summary, validate_video_file, format_duration
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='0.4.0')
def cli():
    """Auto Edit - Automated Stream VOD Highlight Editor"""
    pass


@cli.command()
@click.argument('input_video', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output video path')
@click.option('--duration', '-d', type=int, default=20, help='Target duration in minutes')
@click.option('--mode', '-m', type=click.Choice(['general', 'my_style', 'hybrid']),
              default='general', help='Editing mode')
@click.option('--config', '-c', type=click.Path(), default='config.yaml',
              help='Configuration file path')
@click.option('--preview', is_flag=True, help='Generate preview with top 5 clips only')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def edit(input_video: str, output: Optional[str], duration: int, mode: str,
         config: str, preview: bool, verbose: bool):
    """
    Edit a stream VOD into highlights.

    INPUT_VIDEO: Path to the stream VOD file
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)

    print_header("AUTO EDIT - Stream Highlight Editor")

    try:
        # Validate input
        video_path = validate_video_file(input_video)
        print_success(f"Input video: {video_path}")

        # Load configuration
        cfg = Config(config)
        print_success(f"Configuration loaded: {config}")

        # Override mode if specified
        if mode:
            cfg.update('active_mode', mode)
            print_info(f"Editing mode: {mode}")

        # Initialize components
        print_info("Initializing components...")
        video_processor = VideoProcessor(cfg)
        signal_detector = SignalDetector(cfg)
        clip_selector = ClipSelector(cfg)
        video_assembler = VideoAssembler(cfg)

        # Load video metadata
        print_info("Loading video...")
        metadata = video_processor.load_video(str(video_path))
        print_video_info(metadata)

        # Extract audio
        print_info("Extracting audio...")
        audio_path = video_processor.extract_audio(str(video_path))
        audio, sr = video_processor.load_audio(audio_path)
        print_success("Audio extracted")

        # Detect signals
        print_header("Signal Detection")
        signals = signal_detector.detect_all_signals(
            str(video_path),
            audio,
            sr,
            metadata
        )
        print_signals_summary(signals)

        # Select clips
        print_header("Clip Selection")
        clips = clip_selector.select_clips(
            signals,
            metadata['duration_seconds'],
            target_duration=duration
        )
        print_clips_summary(clips, metadata['duration_seconds'])

        if not clips:
            print_error("No clips selected. Try adjusting signal settings or threshold.")
            sys.exit(1)

        # Assemble video
        print_header("Video Assembly")

        if preview:
            print_info("Creating preview with top 5 clips...")
            output_path = video_assembler.create_preview_video(
                str(video_path),
                clips,
                max_clips=5
            )
        else:
            print_info(f"Assembling {len(clips)} clips...")
            output_path, thumbnails, sound_clips = video_assembler.assemble_video(
                str(video_path),
                clips,
                output_path=output,
                audio=audio,
                sr=sr
            )

            # Report on extracted thumbnails and sounds
            if thumbnails:
                print_success(f"✓ {len(thumbnails)} thumbnails extracted → output/thumbnails/")
            if sound_clips:
                print_success(f"✓ {len(sound_clips)} sound clips extracted → output/sounds/")

        # Export clip list
        clip_list_path = video_assembler.export_clip_list(clips)
        print_success(f"Clip list exported: {clip_list_path}")

        # Final summary
        print_header("Complete!")
        print_success(f"Output video: {output_path}")

        total_duration = sum(c.duration for c in clips)
        compression_ratio = (metadata['duration_seconds'] / total_duration) if total_duration > 0 else 0
        print_info(f"Compression ratio: {compression_ratio:.1f}x "
                  f"({format_duration(metadata['duration_seconds'])} → "
                  f"{format_duration(total_duration)})")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


@cli.command()
@click.argument('input_video', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def analyze(input_video: str, config: str):
    """
    Analyze a video and show detected signals without editing.

    INPUT_VIDEO: Path to the stream VOD file
    """
    setup_logging(level="INFO")

    print_header("AUTO EDIT - Video Analysis")

    try:
        video_path = validate_video_file(input_video)
        cfg = Config(config)

        video_processor = VideoProcessor(cfg)
        signal_detector = SignalDetector(cfg)

        # Load video
        metadata = video_processor.load_video(str(video_path))
        print_video_info(metadata)

        # Extract audio
        print_info("Extracting audio...")
        audio_path = video_processor.extract_audio(str(video_path))
        audio, sr = video_processor.load_audio(audio_path)

        # Detect signals
        print_header("Signal Detection")
        signals = signal_detector.detect_all_signals(
            str(video_path),
            audio,
            sr,
            metadata
        )
        print_signals_summary(signals)

        # Show statistics
        clip_selector = ClipSelector(cfg)
        stats = clip_selector.calculate_signal_statistics(signals)

        print_header("Statistics")
        print(f"Total events: {stats['total_events']}")
        print(f"\nAverage intensity by type:")
        for signal_type, intensity in stats['avg_intensity'].items():
            print(f"  {signal_type:.<30} {intensity:.3f}")

        print_success("Analysis complete")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def config_show(config: str):
    """Show current configuration."""
    setup_logging(level="INFO")

    try:
        cfg = Config(config)

        print_header("Current Configuration")

        print(f"Active mode: {cfg.get_active_mode()}")
        print(f"\nEnabled signals:")
        for name, config in cfg.get_enabled_signals().items():
            weight = config.get('weight', 1.0)
            print(f"  {name:.<30} (weight: {weight})")

        print(f"\nOutput settings:")
        print(f"  Target duration: {cfg.get('output.target_duration_minutes')} minutes")
        print(f"  Resolution: {cfg.get('output.resolution')}")
        print(f"  FPS: {cfg.get('output.fps')}")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('signal_name')
@click.argument('enabled', type=click.Choice(['on', 'off']))
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def signal(signal_name: str, enabled: str, config: str):
    """
    Toggle a signal source on or off.

    SIGNAL_NAME: Name of the signal (e.g., audio_voice_analysis, chat_density)
    ENABLED: 'on' or 'off'
    """
    setup_logging(level="INFO")

    try:
        cfg = Config(config)

        enabled_bool = (enabled == 'on')
        cfg.update(f'signals.{signal_name}.enabled', enabled_bool)
        cfg.save()

        status = "enabled" if enabled_bool else "disabled"
        print_success(f"Signal '{signal_name}' {status}")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('mode', type=click.Choice(['general_interest', 'my_style', 'hybrid']))
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def set_mode(mode: str, config: str):
    """
    Set the active editing mode.

    MODE: Editing mode (general_interest, my_style, or hybrid)
    """
    setup_logging(level="INFO")

    try:
        cfg = Config(config)
        cfg.update('active_mode', mode)
        cfg.save()

        print_success(f"Active mode set to: {mode}")

        if mode == 'my_style':
            print_info("Note: my_style mode requires a trained model. "
                      "Use 'auto_edit.py train' to train from examples.")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('raw_video', type=click.Path(exists=True))
@click.argument('edited_video', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def add_example(raw_video: str, edited_video: str, config: str):
    """
    Add a training example for style learning (Phase 3).

    RAW_VIDEO: Path to raw stream VOD
    EDITED_VIDEO: Path to your edited highlight video
    """
    setup_logging(level="INFO")

    print_header("Add Training Example")

    try:
        cfg = Config(config)
        style_learner = StyleLearner(cfg)

        style_learner.add_training_example(raw_video, edited_video)

        print_success("Training example added")
        print_info("Use 'auto_edit.py train' to update the model with new examples")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def train(config: str):
    """
    Train style model from examples (Phase 3).
    """
    setup_logging(level="INFO")

    print_header("Train Style Model")

    try:
        cfg = Config(config)
        style_learner = StyleLearner(cfg)

        success = style_learner.train()

        if success:
            print_success("Style model trained successfully")

            stats = style_learner.get_statistics()
            print_info(f"Trained on {stats['example_count']} examples")
            print_info("You can now use 'my_style' or 'hybrid' mode")
        else:
            print_error("Training failed. Check that you have enough examples.")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', type=click.Path(), default='config.yaml')
def style_info(config: str):
    """Show information about trained style model."""
    setup_logging(level="INFO")

    try:
        cfg = Config(config)
        style_learner = StyleLearner(cfg)

        # Try to load model
        loaded = style_learner.load_model()

        print_header("Style Model Information")

        if loaded:
            stats = style_learner.get_statistics()

            print(f"Status: {stats['trained']}")
            print(f"Example count: {stats['example_count']}")
            print(f"Model version: {stats['model_version']}")

            if 'preferences' in stats:
                print("\nLearned preferences:")
                for key, value in stats['preferences'].items():
                    print(f"  {key}: {value}")

            print_success("Style model is trained and ready")
        else:
            print_info("No trained style model found")
            print_info("Add training examples with 'auto_edit.py add-example'")
            print_info("Then train with 'auto_edit.py train'")

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
