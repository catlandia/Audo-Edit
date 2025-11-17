"""Configuration management for Auto Edit."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Manages application configuration from YAML and environment variables."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        load_dotenv()
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Override with environment variables if present
        config['paths'] = {
            'input_dir': Path(os.getenv('INPUT_DIR', './input')),
            'output_dir': Path(os.getenv('OUTPUT_DIR', './output')),
            'models_dir': Path(os.getenv('MODELS_DIR', './models')),
            'training_data_dir': Path(os.getenv('TRAINING_DATA_DIR', './training_data')),
            'temp_dir': Path(os.getenv('TEMP_DIR', './temp')),
        }

        # Create directories if they don't exist
        for path in config['paths'].values():
            path.mkdir(parents=True, exist_ok=True)

        return config

    def get(self, key: str, default=None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value

    def get_enabled_signals(self) -> Dict[str, Dict[str, Any]]:
        """Get all enabled signal sources."""
        signals = self.config.get('signals', {})
        return {name: config for name, config in signals.items() if config.get('enabled', False)}

    def get_active_mode(self) -> str:
        """Get the currently active editing mode."""
        return self.config.get('active_mode', 'general_interest')

    def update(self, key: str, value: Any) -> None:
        """Update a configuration value."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        config[keys[-1]] = value

    def save(self) -> None:
        """Save current configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def __repr__(self) -> str:
        return f"Config(active_mode='{self.get_active_mode()}', signals={len(self.get_enabled_signals())})"
