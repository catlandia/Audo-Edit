"""Clip selection and scoring for highlight generation."""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import logging

from .signal_detector import SignalEvent

logger = logging.getLogger(__name__)


@dataclass
class Clip:
    """Represents a selected clip for the highlight video."""
    start_time: float
    end_time: float
    score: float
    signals: List[SignalEvent]
    reason: str
    metadata: Dict[str, Any]

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class ClipSelector:
    """Selects and scores clips for highlight generation."""

    def __init__(self, config):
        """
        Initialize clip selector.

        Args:
            config: Configuration object
        """
        self.config = config
        self.mode = config.get_active_mode()
        self.enabled_signals = config.get_enabled_signals()

    def select_clips(self, signals: Dict[str, List[SignalEvent]],
                    video_duration: float,
                    target_duration: float = None) -> List[Clip]:
        """
        Select clips based on signals and mode.

        Args:
            signals: Dictionary of detected signals
            video_duration: Total video duration in seconds
            target_duration: Target highlight duration in minutes

        Returns:
            List of selected clips
        """
        if target_duration is None:
            target_duration = self.config.get('output.target_duration_minutes', 20)

        target_duration_seconds = target_duration * 60

        logger.info(f"Selecting clips in {self.mode} mode")
        logger.info(f"Target duration: {target_duration} minutes")

        # Score all potential moments
        scored_moments = self._score_all_moments(signals, video_duration)

        # Cluster nearby moments
        if self.config.get('selection.cluster_nearby_moments', True):
            scored_moments = self._cluster_moments(scored_moments)

        # Select top moments
        selected_clips = self._select_top_clips(
            scored_moments,
            target_duration_seconds,
            video_duration
        )

        logger.info(f"Selected {len(selected_clips)} clips "
                   f"({sum(c.duration for c in selected_clips) / 60:.1f} minutes)")

        return selected_clips

    def _score_all_moments(self, signals: Dict[str, List[SignalEvent]],
                          video_duration: float) -> List[Tuple[float, float, List[SignalEvent]]]:
        """
        Score all moments in the video.

        Args:
            signals: Dictionary of detected signals
            video_duration: Total video duration

        Returns:
            List of (timestamp, score, contributing_signals)
        """
        # Create a timeline of signal strengths
        resolution = 1.0  # 1 second resolution
        num_bins = int(video_duration / resolution) + 1
        timeline = np.zeros(num_bins)
        signal_map = {i: [] for i in range(num_bins)}

        # Weight signals based on configuration
        for signal_type, events in signals.items():
            # Find weight from config
            weight = 1.0
            for sig_name, sig_config in self.enabled_signals.items():
                if signal_type in sig_name or sig_name in signal_type:
                    weight = sig_config.get('weight', 1.0)
                    break

            # Add signal events to timeline
            for event in events:
                start_bin = int(event.timestamp / resolution)
                end_bin = min(int((event.timestamp + event.duration) / resolution) + 1, num_bins)

                for bin_idx in range(start_bin, end_bin):
                    if bin_idx < num_bins:
                        score = event.intensity * weight
                        timeline[bin_idx] += score
                        signal_map[bin_idx].append(event)

        # Find peaks in timeline
        scored_moments = []
        threshold = self.config.get('selection.interest_threshold', 0.6)

        for i in range(num_bins):
            timestamp = i * resolution
            score = timeline[i]

            if score >= threshold:
                scored_moments.append((timestamp, score, signal_map[i]))

        logger.info(f"Found {len(scored_moments)} scored moments above threshold")
        return scored_moments

    def _cluster_moments(self, moments: List[Tuple[float, float, List[SignalEvent]]]) -> List[Tuple[float, float, List[SignalEvent]]]:
        """
        Cluster nearby moments together.

        Args:
            moments: List of (timestamp, score, signals)

        Returns:
            Clustered moments
        """
        if not moments:
            return []

        cluster_window = self.config.get('selection.cluster_window_seconds', 60)
        clustered = []

        # Sort by timestamp
        moments = sorted(moments, key=lambda x: x[0])

        current_cluster_start = moments[0][0]
        current_cluster_signals = moments[0][2].copy()
        current_cluster_score = moments[0][1]
        current_cluster_count = 1

        for i in range(1, len(moments)):
            timestamp, score, signals = moments[i]

            # Check if within cluster window
            if timestamp - current_cluster_start <= cluster_window:
                # Add to current cluster
                current_cluster_score = max(current_cluster_score, score)
                current_cluster_signals.extend(signals)
                current_cluster_count += 1
            else:
                # Save current cluster and start new one
                avg_score = current_cluster_score
                clustered.append((
                    current_cluster_start,
                    avg_score,
                    current_cluster_signals
                ))

                current_cluster_start = timestamp
                current_cluster_signals = signals.copy()
                current_cluster_score = score
                current_cluster_count = 1

        # Add last cluster
        clustered.append((
            current_cluster_start,
            current_cluster_score,
            current_cluster_signals
        ))

        logger.info(f"Clustered {len(moments)} moments into {len(clustered)} clusters")
        return clustered

    def _select_top_clips(self, scored_moments: List[Tuple[float, float, List[SignalEvent]]],
                         target_duration: float,
                         video_duration: float) -> List[Clip]:
        """
        Select top clips to meet target duration.

        Args:
            scored_moments: List of (timestamp, score, signals)
            target_duration: Target total duration in seconds
            video_duration: Total video duration

        Returns:
            List of selected clips
        """
        if not scored_moments:
            return []

        # Sort by score (descending)
        sorted_moments = sorted(scored_moments, key=lambda x: x[1], reverse=True)

        min_clip_length = self.config.get('output.min_clip_length_seconds', 3)
        max_clip_length = self.config.get('output.max_clip_length_seconds', 45)
        context_before = self.config.get('selection.include_context_before_seconds', 5)
        context_after = self.config.get('selection.include_context_after_seconds', 3)

        selected_clips = []
        total_duration = 0.0
        used_ranges = []  # Track used time ranges to avoid overlap

        for timestamp, score, signals in sorted_moments:
            if total_duration >= target_duration:
                break

            # Determine clip boundaries
            # Find extent of high activity
            clip_start = max(0, timestamp - context_before)
            clip_end = min(video_duration, timestamp + max_clip_length)

            # Adjust based on signal durations
            if signals:
                signal_end = max(s.timestamp + s.duration for s in signals)
                clip_end = min(clip_end, signal_end + context_after)

            clip_duration = clip_end - clip_start

            # Enforce duration constraints
            if clip_duration < min_clip_length:
                clip_end = min(video_duration, clip_start + min_clip_length)
                clip_duration = clip_end - clip_start

            if clip_duration > max_clip_length:
                clip_end = clip_start + max_clip_length
                clip_duration = max_clip_length

            # Check for overlap with existing clips
            overlaps = False
            for used_start, used_end in used_ranges:
                if not (clip_end <= used_start or clip_start >= used_end):
                    overlaps = True
                    break

            if overlaps:
                continue

            # Create clip
            reason = self._generate_clip_reason(signals)
            clip = Clip(
                start_time=clip_start,
                end_time=clip_end,
                score=score,
                signals=signals,
                reason=reason,
                metadata={
                    'signal_count': len(signals),
                    'signal_types': list(set(s.signal_type for s in signals))
                }
            )

            selected_clips.append(clip)
            used_ranges.append((clip_start, clip_end))
            total_duration += clip_duration

        # Sort clips by timestamp for final video
        selected_clips.sort(key=lambda x: x.start_time)

        return selected_clips

    def _generate_clip_reason(self, signals: List[SignalEvent]) -> str:
        """
        Generate human-readable reason for clip selection.

        Args:
            signals: Contributing signals

        Returns:
            Reason string
        """
        if not signals:
            return "General interest"

        signal_types = [s.signal_type for s in signals]
        type_counts = {}
        for st in signal_types:
            type_counts[st] = type_counts.get(st, 0) + 1

        # Find dominant signal type
        dominant = max(type_counts.items(), key=lambda x: x[1])
        dominant_type = dominant[0]

        # Generate reason
        reason_map = {
            'audio_peak': 'Loud audio moment',
            'laughter': 'Laughter detected',
            'shouting': 'High energy shouting',
            'excitement': 'Excited reaction',
            'voice_activity': 'Strong voice activity',
            'high_motion': 'High visual activity',
            'scene_change': 'Scene transition',
            'chat_activity': 'Active chat',
            'facecam_reaction': 'Visible reaction',
            'silence_to_chaos': 'Dramatic moment',
        }

        reason = reason_map.get(dominant_type, 'Interesting moment')

        # Add context if multiple signal types
        if len(type_counts) > 1:
            other_types = [t for t in type_counts.keys() if t != dominant_type]
            if other_types:
                reason += f" + {len(other_types)} other signals"

        return reason

    def calculate_signal_statistics(self, signals: Dict[str, List[SignalEvent]]) -> Dict[str, Any]:
        """
        Calculate statistics about detected signals.

        Args:
            signals: Dictionary of detected signals

        Returns:
            Statistics dictionary
        """
        stats = {
            'total_events': sum(len(events) for events in signals.values()),
            'by_type': {},
            'avg_intensity': {},
            'total_duration': {}
        }

        for signal_type, events in signals.items():
            stats['by_type'][signal_type] = len(events)

            if events:
                intensities = [e.intensity for e in events]
                stats['avg_intensity'][signal_type] = np.mean(intensities)

                durations = [e.duration for e in events]
                stats['total_duration'][signal_type] = sum(durations)

        return stats
