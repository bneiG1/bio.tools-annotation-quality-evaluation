"""
Configuration management for bio.tools annotation quality evaluation.

This module provides configuration loading and management capabilities
with support for logging configuration integration.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class ConfigManager:
    """Configuration manager with logging integration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_default_config()
        
        if config_path and Path(config_path).exists():
            self._load_config_file(config_path)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration."""
        return {
            'system': {
                'logging': {
                    'level': 'INFO',
                    'file_logging': True,
                    'console_logging': True,
                    'log_file': 'biotools_quality_analysis.log',
                    'log_dir': 'logs',
                    'max_log_size': 10485760,  # 10MB
                    'backup_count': 5,
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    'date_format': '%Y-%m-%d %H:%M:%S'
                },
                'api': {
                    'base_url': 'https://bio.tools/api',
                    'timeout': 30,
                    'max_retries': 3,
                    'rate_limit_delay': 0.1
                },
                'output': {
                    'base_dir': 'data/processed',
                    'create_subdirs': True,
                    'formats': {
                        'json': True,
                        'csv': True,
                        'html': True
                    }
                }
            },
            'scoring': {
                'weights': {
                    'basic_info': 15,
                    'core_metadata': 25,
                    'technical_info': 20,
                    'accessibility': 20,
                    'advanced_features': 15,
                    'community': 5
                },
                'tiers': {
                    'tier_1': [0, 15],
                    'tier_2': [16, 40],
                    'tier_3': [41, 65],
                    'tier_4': [66, 85],
                    'tier_5': [86, 100]
                }
            }
        }
    
    def _load_config_file(self, config_path: str) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f)
            
            # Deep merge configurations
            self._deep_merge(self.config, file_config)
            
        except Exception as e:
            # Use logging if available, otherwise print
            try:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to load config from {config_path}: {e}")
            except:
                print(f"Warning: Failed to load config from {config_path}: {e}")
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary to update
            update: Dictionary with updates
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'system.logging.level')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'system.logging.level')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Logging configuration dictionary
        """
        return self.get('system.logging', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """
        Get API configuration.
        
        Returns:
            API configuration dictionary
        """
        return self.get('system.api', {})
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """
        Get scoring configuration.
        
        Returns:
            Scoring configuration dictionary
        """
        return self.get('scoring', {})
    
    def save_config(self, output_path: str) -> None:
        """
        Save current configuration to file.
        
        Args:
            output_path: Path to save configuration
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
                
        except Exception as e:
            try:
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to save config to {output_path}: {e}")
            except:
                print(f"Error: Failed to save config to {output_path}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global configuration manager instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration manager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    
    return _config_manager


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    manager = get_config_manager(config_path)
    return manager.to_dict()
