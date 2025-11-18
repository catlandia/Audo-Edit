"""Signal detection for identifying interesting moments in streams."""

import cv2
import numpy as np
import librosa
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignalEvent:
    """Represents a detected signal event."""
    signal_type: str
    timestamp: float
    duration: float
    intensity: float  # 0-1 normalized intensity
    metadata: Dict[str, Any]


class SignalDetector:
    """Detects various signals that indicate interesting moments."""

    def __init__(self, config):
        """
        Initialize signal detector.

        Args:
            config: Configuration object
        """
        self.config = config
        self.enabled_signals = config.get_enabled_signals()

    def detect_all_signals(self, video_path: str, audio: np.ndarray, sr: int,
                          video_metadata: Dict[str, Any]) -> Dict[str, List[SignalEvent]]:
        """
        Run all enabled signal detectors.

        Args:
            video_path: Path to video file
            audio: Audio data
            sr: Sample rate
            video_metadata: Video metadata

        Returns:
            Dictionary mapping signal type to list of events
        """
        logger.info("Running signal detection...")
        all_signals = {}

        # Audio-based signals
        if 'audio_voice_analysis' in self.enabled_signals:
            all_signals['voice_activity'] = self.detect_voice_activity(audio, sr)

        if 'audio_game_peaks' in self.enabled_signals:
            all_signals['audio_peaks'] = self.detect_audio_peaks(audio, sr)

        if 'silence_to_chaos' in self.enabled_signals:
            all_signals['silence_to_chaos'] = self.detect_silence_to_chaos(audio, sr)

        # Visual signals
        if 'visual_activity' in self.enabled_signals:
            all_signals['visual_activity'] = self.detect_visual_activity(video_path, video_metadata)

        # Chat signals
        if 'chat_density' in self.enabled_signals:
            chat_config = self.enabled_signals['chat_density']
            region = chat_config.get('region', [0.7, 0.0, 1.0, 1.0])
            all_signals['chat_density'] = self.detect_chat_activity(video_path, video_metadata, region)

        # Facecam signals
        if 'facecam_emotion' in self.enabled_signals:
            facecam_config = self.enabled_signals['facecam_emotion']
            region = facecam_config.get('facecam_region', [0.0, 0.7, 0.25, 1.0])
            all_signals['facecam_emotion'] = self.detect_facecam_activity(video_path, video_metadata, region)

        logger.info(f"Signal detection complete. Found {sum(len(events) for events in all_signals.values())} events")
        return all_signals

    def detect_audio_peaks(self, audio: np.ndarray, sr: int) -> List[SignalEvent]:
        """
        Detect audio peaks/loud moments.

        Args:
            audio: Audio data
            sr: Sample rate

        Returns:
            List of peak events
        """
        logger.info("Detecting audio peaks...")

        # Mix to mono if stereo
        if len(audio.shape) == 2:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio.flatten()

        if len(audio_mono) == 0:
            return []

        # Calculate RMS energy in windows
        window_length = int(0.5 * sr)  # 0.5 second windows
        hop_length = int(0.1 * sr)  # 0.1 second hop

        rms = librosa.feature.rms(y=audio_mono, frame_length=window_length, hop_length=hop_length)[0]

        if len(rms) == 0:
            return []

        # Convert to dB (handle zero RMS)
        max_rms = np.max(rms)
        if max_rms == 0:
            max_rms = 1e-10
        rms_db = librosa.amplitude_to_db(rms, ref=max_rms)

        # Get threshold from config
        threshold = self.config.get('signals.audio_game_peaks.peak_threshold', -20)

        # Find peaks above threshold
        events = []
        times = librosa.frames_to_time(np.arange(len(rms_db)), sr=sr, hop_length=hop_length)

        i = 0
        while i < len(rms_db):
            if rms_db[i] > threshold:
                # Found a peak, find the extent
                start_idx = i
                peak_value = rms_db[i]

                while i < len(rms_db) and rms_db[i] > threshold - 10:  # Allow 10dB drop
                    peak_value = max(peak_value, rms_db[i])
                    i += 1

                end_idx = i

                # Calculate intensity (0-1)
                intensity = min(1.0, (peak_value - threshold) / 20.0)

                # Safely get timestamps
                if end_idx < len(times):
                    duration = float(times[end_idx] - times[start_idx])
                elif start_idx < len(times):
                    duration = float(times[-1] - times[start_idx])
                else:
                    duration = 0.0

                events.append(SignalEvent(
                    signal_type='audio_peak',
                    timestamp=float(times[start_idx]) if start_idx < len(times) else 0.0,
                    duration=duration,
                    intensity=float(intensity),
                    metadata={'peak_db': float(peak_value)}
                ))
            else:
                i += 1

        logger.info(f"Found {len(events)} audio peaks")
        return events

    def detect_voice_activity(self, audio: np.ndarray, sr: int) -> List[SignalEvent]:
        """
        Detect voice activity, laughter, shouting, excitement.

        Args:
            audio: Audio data
            sr: Sample rate

        Returns:
            List of voice activity events
        """
        logger.info("Detecting voice activity...")

        # Mix to mono
        if len(audio.shape) == 2:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio.flatten()

        # Extract features
        # 1. Zero crossing rate (higher for unvoiced sounds, laughter)
        zcr = librosa.feature.zero_crossing_rate(audio_mono, frame_length=2048, hop_length=512)[0]

        # 2. Spectral centroid (brightness - higher for excitement)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_mono, sr=sr, hop_length=512)[0]

        # 3. RMS energy
        rms = librosa.feature.rms(y=audio_mono, frame_length=2048, hop_length=512)[0]

        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)

        events = []

        # Normalize features
        zcr_norm = (zcr - np.mean(zcr)) / (np.std(zcr) + 1e-8)
        centroid_norm = (spectral_centroid - np.mean(spectral_centroid)) / (np.std(spectral_centroid) + 1e-8)
        rms_norm = (rms - np.mean(rms)) / (np.std(rms) + 1e-8)

        # Detect moments of high activity
        # Laughter: high ZCR + high energy
        # Shouting: very high energy + high centroid
        # Excitement: high energy + high centroid + variable ZCR

        activity_score = 0.3 * zcr_norm + 0.4 * rms_norm + 0.3 * centroid_norm

        # Find high activity segments
        threshold = 1.5  # Standard deviations above mean
        i = 0
        while i < len(activity_score):
            if activity_score[i] > threshold:
                start_idx = i
                peak_score = activity_score[i]

                while i < len(activity_score) and activity_score[i] > 0.5:
                    peak_score = max(peak_score, activity_score[i])
                    i += 1

                end_idx = i

                # Classify type based on features (handle empty segments)
                if end_idx > start_idx:
                    segment_zcr = np.mean(zcr_norm[start_idx:end_idx])
                    segment_energy = np.mean(rms_norm[start_idx:end_idx])
                    segment_centroid = np.mean(centroid_norm[start_idx:end_idx])
                else:
                    segment_zcr = zcr_norm[start_idx] if start_idx < len(zcr_norm) else 0
                    segment_energy = rms_norm[start_idx] if start_idx < len(rms_norm) else 0
                    segment_centroid = centroid_norm[start_idx] if start_idx < len(centroid_norm) else 0

                event_type = 'voice_activity'
                if segment_zcr > 1.5 and segment_energy > 1.0:
                    event_type = 'laughter'
                elif segment_energy > 2.0:
                    event_type = 'shouting'
                elif segment_centroid > 1.5:
                    event_type = 'excitement'

                intensity = min(1.0, peak_score / 3.0)

                # Safely calculate duration
                if end_idx < len(times):
                    duration = float(times[end_idx] - times[start_idx])
                elif start_idx < len(times):
                    duration = float(times[-1] - times[start_idx])
                else:
                    duration = 0.0

                events.append(SignalEvent(
                    signal_type=event_type,
                    timestamp=float(times[start_idx]) if start_idx < len(times) else 0.0,
                    duration=duration,
                    intensity=float(intensity),
                    metadata={
                        'zcr': float(segment_zcr),
                        'energy': float(segment_energy),
                        'centroid': float(segment_centroid)
                    }
                ))
            else:
                i += 1

        logger.info(f"Found {len(events)} voice activity events")
        return events

    def detect_silence_to_chaos(self, audio: np.ndarray, sr: int) -> List[SignalEvent]:
        """
        Detect transitions from silence to loud/chaotic moments.

        Args:
            audio: Audio data
            sr: Sample rate

        Returns:
            List of silence-to-chaos events
        """
        logger.info("Detecting silence-to-chaos patterns...")

        if len(audio.shape) == 2:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio.flatten()

        # Calculate RMS in small windows
        hop_length = int(0.1 * sr)
        rms = librosa.feature.rms(y=audio_mono, frame_length=2048, hop_length=hop_length)[0]

        if len(rms) == 0:
            return []

        max_rms = np.max(rms)
        if max_rms == 0:
            max_rms = 1e-10
        rms_db = librosa.amplitude_to_db(rms, ref=max_rms)

        times = librosa.frames_to_time(np.arange(len(rms_db)), sr=sr, hop_length=hop_length)

        silence_threshold = self.config.get('signals.silence_to_chaos.silence_threshold', -40)
        chaos_threshold = self.config.get('signals.silence_to_chaos.chaos_threshold', -15)

        events = []
        i = 0

        while i < len(rms_db) - 20:  # Need lookahead
            # Check for silence period (at least 2 seconds)
            if rms_db[i] < silence_threshold:
                silence_start = i
                silence_duration = 0

                while i < len(rms_db) and rms_db[i] < silence_threshold:
                    silence_duration += 1
                    i += 1

                # Check if silence is followed by chaos
                if i < len(rms_db) - 10 and silence_duration >= 20:  # At least 2 seconds
                    # Look ahead for chaos within next 3 seconds
                    lookahead = min(30, len(rms_db) - i)

                    if lookahead > 0:
                        max_next = np.max(rms_db[i:i + lookahead])

                        if max_next > chaos_threshold:
                            # Found silence-to-chaos transition
                            chaos_idx = i + np.argmax(rms_db[i:i + lookahead])
                            intensity = min(1.0, (max_next - chaos_threshold) / 20.0)

                            # Safely get timestamps
                            if chaos_idx < len(times) and silence_start < len(times):
                                events.append(SignalEvent(
                                    signal_type='silence_to_chaos',
                                    timestamp=float(times[silence_start]),
                                    duration=float(times[chaos_idx] - times[silence_start]),
                                    intensity=float(intensity),
                                    metadata={
                                        'silence_db': float(rms_db[silence_start]),
                                        'chaos_db': float(max_next),
                                        'silence_duration': float(silence_duration * 0.1)
                                    }
                                ))
            i += 1

        logger.info(f"Found {len(events)} silence-to-chaos events")
        return events

    def detect_visual_activity(self, video_path: str, video_metadata: Dict[str, Any]) -> List[SignalEvent]:
        """
        Detect visual activity, scene changes, and motion.

        Args:
            video_path: Path to video file
            video_metadata: Video metadata

        Returns:
            List of visual activity events
        """
        logger.info("Detecting visual activity...")

        cap = cv2.VideoCapture(str(video_path))
        fps = video_metadata['fps']
        total_frames = video_metadata['frame_count']

        # Sample frames (not every frame for efficiency)
        sample_rate = max(1, int(fps / 5))  # Sample 5 frames per second

        events = []
        prev_frame = None
        prev_hist = None

        frame_idx = 0
        motion_scores = []
        scene_changes = []

        pbar = tqdm(total=total_frames // sample_rate, desc="Analyzing video")

        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                break

            timestamp = frame_idx / fps

            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate histogram for scene change detection
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_frame is not None:
                # Motion detection using frame difference
                diff = cv2.absdiff(prev_frame, gray)
                motion_score = np.mean(diff) / 255.0

                motion_scores.append((timestamp, motion_score))

                # Scene change detection using histogram comparison
                if prev_hist is not None:
                    hist_diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CHISQR)
                    scene_threshold = self.config.get('signals.visual_activity.scene_change_threshold', 30)

                    if hist_diff > scene_threshold:
                        scene_changes.append((timestamp, hist_diff))

            prev_frame = gray.copy()
            prev_hist = hist.copy()
            frame_idx += sample_rate
            pbar.update(1)

        pbar.close()
        cap.release()

        # Process motion scores to find high activity periods
        if motion_scores:
            motion_threshold = self.config.get('signals.visual_activity.motion_threshold', 0.3)
            times, scores = zip(*motion_scores)
            scores = np.array(scores)

            # Find periods of high motion
            i = 0
            while i < len(scores):
                if scores[i] > motion_threshold:
                    start_idx = i
                    peak_score = scores[i]

                    while i < len(scores) and scores[i] > motion_threshold * 0.7:
                        peak_score = max(peak_score, scores[i])
                        i += 1

                    end_idx = i

                    if end_idx - start_idx >= 2:  # At least 0.4 seconds
                        # Safely access times array
                        end_time_idx = min(end_idx - 1, len(times) - 1)
                        if start_idx < len(times) and end_time_idx >= start_idx:
                            events.append(SignalEvent(
                                signal_type='high_motion',
                                timestamp=float(times[start_idx]),
                                duration=float(times[end_time_idx] - times[start_idx]),
                                intensity=float(min(1.0, peak_score / motion_threshold)),
                                metadata={'peak_motion': float(peak_score)}
                            ))
                else:
                    i += 1

        # Add scene changes as events
        for timestamp, intensity in scene_changes:
            events.append(SignalEvent(
                signal_type='scene_change',
                timestamp=float(timestamp),
                duration=0.1,
                intensity=float(min(1.0, intensity / 100.0)),
                metadata={'hist_diff': float(intensity)}
            ))

        logger.info(f"Found {len(events)} visual activity events")
        return events

    def detect_chat_activity(self, video_path: str, video_metadata: Dict[str, Any],
                            region: List[float]) -> List[SignalEvent]:
        """
        Detect chat activity using motion detection in chat region.

        Args:
            video_path: Path to video file
            video_metadata: Video metadata
            region: Chat region as [x1, y1, x2, y2] (normalized 0-1)

        Returns:
            List of chat activity events
        """
        logger.info("Detecting chat activity...")

        cap = cv2.VideoCapture(str(video_path))
        fps = video_metadata['fps']
        width = video_metadata['width']
        height = video_metadata['height']

        # Convert normalized region to pixel coordinates
        x1 = int(region[0] * width)
        y1 = int(region[1] * height)
        x2 = int(region[2] * width)
        y2 = int(region[3] * height)

        # Sample frames
        sample_rate = max(1, int(fps))  # 1 frame per second for chat

        events = []
        prev_roi = None
        frame_idx = 0
        activity_scores = []

        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                break

            timestamp = frame_idx / fps

            # Extract chat region
            roi = frame[y1:y2, x1:x2]
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            if prev_roi is not None:
                # Detect motion/changes in chat area
                diff = cv2.absdiff(prev_roi, gray_roi)
                activity = np.mean(diff) / 255.0
                activity_scores.append((timestamp, activity))

            prev_roi = gray_roi.copy()
            frame_idx += sample_rate

        cap.release()

        # Analyze activity scores to find chat bursts
        if activity_scores and len(activity_scores) > 0:
            times, scores = zip(*activity_scores)
            scores = np.array(scores)

            if len(scores) == 0:
                logger.info(f"Found {len(events)} chat activity events")
                return events

            # Smooth scores
            window = 5
            scores_smooth = np.convolve(scores, np.ones(window) / window, mode='same')

            # Find high activity periods
            threshold = np.percentile(scores_smooth, 75)  # Top 25%

            i = 0
            while i < len(scores_smooth):
                if scores_smooth[i] > threshold:
                    start_idx = i
                    peak_score = scores_smooth[i]

                    while i < len(scores_smooth) and scores_smooth[i] > threshold * 0.5:
                        peak_score = max(peak_score, scores_smooth[i])
                        i += 1

                    end_idx = i

                    if end_idx - start_idx >= 3:  # At least 3 seconds
                        # Safely access times array
                        end_time_idx = min(end_idx - 1, len(times) - 1)
                        if start_idx < len(times) and end_time_idx >= start_idx:
                            events.append(SignalEvent(
                                signal_type='chat_activity',
                                timestamp=float(times[start_idx]),
                                duration=float(times[end_time_idx] - times[start_idx]),
                                intensity=float(min(1.0, peak_score * 10)),
                                metadata={'peak_activity': float(peak_score)}
                            ))
                else:
                    i += 1

        logger.info(f"Found {len(events)} chat activity events")
        return events

    def detect_facecam_activity(self, video_path: str, video_metadata: Dict[str, Any],
                               region: List[float]) -> List[SignalEvent]:
        """
        Detect facecam activity/emotion changes.

        Args:
            video_path: Path to video file
            video_metadata: Video metadata
            region: Facecam region as [x1, y1, x2, y2] (normalized 0-1)

        Returns:
            List of facecam activity events
        """
        logger.info("Detecting facecam activity...")

        # Similar to chat detection but focused on facecam region
        # In a full implementation, this could use face detection and emotion recognition
        # For now, we'll use motion detection as a proxy

        cap = cv2.VideoCapture(str(video_path))
        fps = video_metadata['fps']
        width = video_metadata['width']
        height = video_metadata['height']

        x1 = int(region[0] * width)
        y1 = int(region[1] * height)
        x2 = int(region[2] * width)
        y2 = int(region[3] * height)

        sample_rate = max(1, int(fps / 5))  # 5 fps

        events = []
        prev_roi = None
        frame_idx = 0
        activity_scores = []

        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()

            if not ret:
                break

            timestamp = frame_idx / fps

            roi = frame[y1:y2, x1:x2]
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            if prev_roi is not None:
                diff = cv2.absdiff(prev_roi, gray_roi)
                activity = np.mean(diff) / 255.0
                activity_scores.append((timestamp, activity))

            prev_roi = gray_roi.copy()
            frame_idx += sample_rate

        cap.release()

        # Process activity scores
        if activity_scores and len(activity_scores) > 0:
            times, scores = zip(*activity_scores)
            scores = np.array(scores)

            if len(scores) == 0:
                logger.info(f"Found {len(events)} facecam activity events")
                return events

            # Find sudden changes (reactions)
            threshold = np.percentile(scores, 80)

            i = 0
            while i < len(scores):
                if scores[i] > threshold:
                    start_idx = i
                    peak_score = scores[i]

                    while i < len(scores) and scores[i] > threshold * 0.6:
                        peak_score = max(peak_score, scores[i])
                        i += 1

                    end_idx = i

                    # Safely calculate duration
                    if end_idx > start_idx and end_idx - 1 < len(times) and start_idx < len(times):
                        duration = float(times[end_idx - 1] - times[start_idx])
                    else:
                        duration = 0.2

                    if start_idx < len(times):
                        events.append(SignalEvent(
                            signal_type='facecam_reaction',
                            timestamp=float(times[start_idx]),
                            duration=duration,
                            intensity=float(min(1.0, peak_score * 5)),
                            metadata={'peak_activity': float(peak_score)}
                        ))
                else:
                    i += 1

        logger.info(f"Found {len(events)} facecam activity events")
        return events
