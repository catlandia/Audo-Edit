"""Style learning system for personal editing preferences (Phase 3)."""

import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import logging

from .clip_selector import Clip
from .signal_detector import SignalEvent

logger = logging.getLogger(__name__)


class StyleLearner:
    """
    Learns personal editing style from paired examples.

    Phase 3 implementation - learns from raw stream + human-edited pairs.
    """

    def __init__(self, config):
        """
        Initialize style learner.

        Args:
            config: Configuration object
        """
        self.config = config
        self.models_dir = config.get('paths.models_dir', Path('./models'))
        self.training_data_dir = config.get('paths.training_data_dir', Path('./training_data'))
        self.model = None
        self.is_trained = False

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load trained style model.

        Args:
            model_path: Optional path to model file

        Returns:
            True if model loaded successfully
        """
        if model_path is None:
            model_path = self.models_dir / 'personal_style.pkl'

        model_path = Path(model_path)

        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}")
            return False

        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)

            self.is_trained = True
            logger.info(f"Style model loaded from: {model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def save_model(self, model_path: Optional[str] = None) -> None:
        """
        Save trained model.

        Args:
            model_path: Optional path to save model
        """
        if model_path is None:
            model_path = self.models_dir / 'personal_style.pkl'

        model_path = Path(model_path)
        model_path.parent.mkdir(parents=True, exist_ok=True)

        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

        logger.info(f"Style model saved to: {model_path}")

    def add_training_example(self, raw_video: str, edited_video: str,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a training example pair.

        Args:
            raw_video: Path to raw stream VOD
            edited_video: Path to human-edited highlight video
            metadata: Optional metadata about the example

        Returns:
            True if added, False if already exists
        """
        # Check if this pair already exists
        if self.is_pair_trained(raw_video, edited_video):
            logger.info(f"Skipping already trained pair: {Path(raw_video).name}")
            return False

        logger.info(f"Adding training example:\n  Raw: {raw_video}\n  Edited: {edited_video}")

        # Store training example
        example_id = len(list(self.training_data_dir.glob('example_*.pkl')))
        example_path = self.training_data_dir / f'example_{example_id:04d}.pkl'

        example_data = {
            'raw_video': raw_video,
            'edited_video': edited_video,
            'metadata': metadata or {},
            'features': None  # Will be computed during training
        }

        with open(example_path, 'wb') as f:
            pickle.dump(example_data, f)

        logger.info(f"Training example saved: {example_path}")
        return True

    def is_pair_trained(self, raw_video: str, edited_video: str) -> bool:
        """
        Check if a video pair is already in training data.

        Args:
            raw_video: Path to raw video
            edited_video: Path to edited video

        Returns:
            True if pair already exists in training data
        """
        # Ensure training data dir exists
        if not self.training_data_dir.exists():
            return False

        raw_name = Path(raw_video).name
        edited_name = Path(edited_video).name

        # Check all existing training examples
        for example_file in self.training_data_dir.glob('example_*.pkl'):
            try:
                with open(example_file, 'rb') as f:
                    example = pickle.load(f)

                existing_raw = Path(example['raw_video']).name
                existing_edited = Path(example['edited_video']).name

                if existing_raw == raw_name and existing_edited == edited_name:
                    return True
            except Exception as e:
                logger.warning(f"Error reading {example_file}: {e}")
                continue

        return False

    def train(self, min_examples: Optional[int] = None) -> bool:
        """
        Train style model from examples.

        Args:
            min_examples: Minimum required examples

        Returns:
            True if training successful
        """
        if min_examples is None:
            min_examples = self.config.get('style_learning.min_examples_required', 5)

        # Load all training examples
        example_files = list(self.training_data_dir.glob('example_*.pkl'))

        if len(example_files) < min_examples:
            logger.warning(f"Not enough training examples. "
                         f"Have {len(example_files)}, need {min_examples}")
            return False

        logger.info(f"Training style model with {len(example_files)} examples...")

        # Extract features from all examples
        features = []
        for example_file in example_files:
            with open(example_file, 'rb') as f:
                example = pickle.load(f)

            # Extract features (Phase 3 implementation)
            example_features = self._extract_style_features(
                example['raw_video'],
                example['edited_video']
            )
            features.append(example_features)

        # Train model (placeholder - Phase 3)
        self.model = self._train_model(features)
        self.is_trained = True

        # Save model
        self.save_model()

        logger.info("Style model training complete")
        return True

    def _extract_style_features(self, raw_video: str, edited_video: str) -> Dict[str, Any]:
        """
        Extract style features from a training pair.

        Args:
            raw_video: Raw stream path
            edited_video: Edited highlights path

        Returns:
            Feature dictionary
        """
        # Phase 3 implementation will:
        # 1. Analyze edited video to find cut points
        # 2. Match edited clips back to raw stream
        # 3. Extract patterns:
        #    - Preferred clip lengths
        #    - Types of moments selected
        #    - Cutting rhythm
        #    - Context inclusion
        #    - Transition preferences
        #    - Pacing patterns

        logger.info("Extracting style features (Phase 3 placeholder)")

        # Placeholder features
        features = {
            'clip_duration_preferences': [],
            'moment_selection_patterns': [],
            'cutting_rhythm': [],
            'context_preferences': {},
            'transition_style': {},
            'pacing_metrics': {}
        }

        return features

    def _train_model(self, features: List[Dict[str, Any]]) -> Any:
        """
        Train model from extracted features.

        Args:
            features: List of feature dictionaries

        Returns:
            Trained model
        """
        # Phase 3 implementation will use ML to learn patterns
        # Possible approaches:
        # - Neural network to predict clip selection
        # - Decision tree for moment classification
        # - Clustering for style patterns
        # - Time series analysis for rhythm

        logger.info("Training model (Phase 3 placeholder)")

        model = {
            'version': '0.1.0',
            'features': features,
            'preferences': self._aggregate_preferences(features)
        }

        return model

    def _aggregate_preferences(self, features: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate preferences from all examples.

        Args:
            features: Feature list

        Returns:
            Aggregated preferences
        """
        # Placeholder aggregation
        preferences = {
            'avg_clip_length': 15.0,
            'preferred_signals': ['laughter', 'excitement'],
            'context_before': 5.0,
            'context_after': 3.0,
            'min_gap_between_clips': 30.0
        }

        return preferences

    def score_clip(self, clip: Clip, signals: List[SignalEvent]) -> float:
        """
        Score a clip based on learned style.

        Args:
            clip: Clip to score
            signals: Associated signals

        Returns:
            Style-based score (0-1)
        """
        if not self.is_trained or self.model is None:
            logger.warning("Model not trained, returning neutral score")
            return 0.5

        # Phase 3 implementation will use trained model
        # to predict how likely user is to select this clip

        preferences = self.model.get('preferences', {})

        score = 0.5

        # Adjust based on clip duration preference
        preferred_length = preferences.get('avg_clip_length', 15.0)
        if preferred_length <= 0:
            preferred_length = 15.0  # Default fallback
        length_diff = abs(clip.duration - preferred_length)
        length_score = max(0, 1.0 - length_diff / preferred_length)
        score += 0.3 * (length_score - 0.5)

        # Adjust based on signal preferences
        preferred_signals = preferences.get('preferred_signals', [])
        signal_types = [s.signal_type for s in signals]
        matching_signals = len(set(signal_types) & set(preferred_signals))
        if preferred_signals:
            signal_score = matching_signals / len(preferred_signals)
            score += 0.3 * (signal_score - 0.5)

        return np.clip(score, 0.0, 1.0)

    def get_adjusted_weights(self) -> Dict[str, float]:
        """
        Get signal weights adjusted for personal style.

        Returns:
            Dictionary of signal weights
        """
        if not self.is_trained or self.model is None:
            return {}

        # Return learned signal preferences
        preferences = self.model.get('preferences', {})
        preferred_signals = preferences.get('preferred_signals', [])

        weights = {}
        for signal in preferred_signals:
            weights[signal] = 1.2  # Boost preferred signals

        return weights

    def scan_learning_folder(self) -> List[Tuple[str, str]]:
        """
        Scan learning folder for matching original/edited pairs.

        Expected structure:
            learning/
                original/
                    video1.mp4
                    video2.mp4
                edited/
                    video1.mp4
                    video2.mp4

        Returns:
            List of (original_path, edited_path) tuples
        """
        learning_dir = Path('./learning')
        original_dir = learning_dir / 'original'
        edited_dir = learning_dir / 'edited'

        # Create directories if they don't exist
        original_dir.mkdir(parents=True, exist_ok=True)
        edited_dir.mkdir(parents=True, exist_ok=True)

        # Scan for video files in original folder
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.webm']
        pairs = []

        for original_file in original_dir.iterdir():
            if original_file.suffix.lower() in video_extensions:
                # Look for matching file in edited folder
                edited_file = edited_dir / original_file.name

                if edited_file.exists():
                    pairs.append((str(original_file), str(edited_file)))
                    logger.info(f"Found pair: {original_file.name}")
                else:
                    logger.warning(f"No edited version found for: {original_file.name}")

        logger.info(f"Found {len(pairs)} matching video pairs")
        return pairs

    def train_from_learning_folder(self) -> Dict[str, Any]:
        """
        Automatically train from videos in learning folder.

        Scans learning/original/ and learning/edited/ for matching pairs,
        adds them as training examples, then trains the model.
        Only adds NEW pairs that haven't been trained on yet.

        Returns:
            Dictionary with training results:
            {
                'success': bool,
                'total_pairs': int,
                'new_pairs': int,
                'already_trained': int,
                'new_pair_names': List[str]
            }
        """
        logger.info("Scanning learning folder for training pairs...")

        # Scan for pairs
        pairs = self.scan_learning_folder()

        if not pairs:
            logger.warning("No matching video pairs found in learning folder")
            logger.info("Add videos to learning/original/ and learning/edited/ with matching filenames")
            return {
                'success': False,
                'total_pairs': 0,
                'new_pairs': 0,
                'already_trained': 0,
                'new_pair_names': []
            }

        # Separate new vs already trained pairs
        new_pairs = []
        already_trained = []

        for original_path, edited_path in pairs:
            if self.is_pair_trained(original_path, edited_path):
                already_trained.append(Path(original_path).name)
            else:
                new_pairs.append((original_path, edited_path))

        logger.info(f"Found {len(pairs)} total pairs: {len(new_pairs)} new, {len(already_trained)} already trained")

        # Add only new pairs as training examples
        new_pair_names = []
        for original_path, edited_path in new_pairs:
            added = self.add_training_example(original_path, edited_path)
            if added:
                new_pair_names.append(Path(original_path).name)

        # Train model if we have enough examples
        if len(new_pairs) > 0:
            success = self.train()
        else:
            logger.info("No new pairs to train on")
            # Still return success if we have a trained model
            success = self.is_trained

        return {
            'success': success,
            'total_pairs': len(pairs),
            'new_pairs': len(new_pairs),
            'already_trained': len(already_trained),
            'new_pair_names': new_pair_names,
            'already_trained_names': already_trained
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about learned style.

        Returns:
            Statistics dictionary
        """
        if not self.is_trained or self.model is None:
            return {'trained': False}

        example_count = len(list(self.training_data_dir.glob('example_*.pkl')))

        stats = {
            'trained': True,
            'example_count': example_count,
            'model_version': self.model.get('version', 'unknown'),
            'preferences': self.model.get('preferences', {})
        }

        return stats
