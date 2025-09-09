"""
Centralized logging utility for bio.tools annotation quality evaluation.

This module provides a unified logging configuration system that supports
both console and file logging with configurable levels and formatting.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import yaml


class Logger:
    """Centralized logging utility with configuration support."""
    
    _initialized = False
    _loggers: Dict[str, logging.Logger] = {}
    _config: Dict[str, Any] = {}
    
    # Default configuration
    DEFAULT_CONFIG = {
        'level': 'INFO',
        'file_logging': True,
        'console_logging': True,
        'log_file': 'biotools_quality_analysis.log',
        'log_dir': 'logs',
        'max_log_size': 10485760,  # 10MB
        'backup_count': 5,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S'
    }
    
    @classmethod
    def setup_logging(
        cls,
        level: str = "INFO",
        log_file: Optional[str] = None,
        console: bool = True,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set up application logging with unified configuration.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
            console: Whether to log to console
            config: Optional configuration dictionary
        """
        if cls._initialized:
            return
            
        # Merge configurations
        cls._config = cls.DEFAULT_CONFIG.copy()
        if config:
            cls._config.update(config)
            
        # Override with parameters
        if level:
            cls._config['level'] = level.upper()
        if log_file:
            cls._config['log_file'] = log_file
        if not console:
            cls._config['console_logging'] = False
            
        # Create log directory
        log_dir = Path(cls._config['log_dir'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, cls._config['level']))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # Set up formatters
        formatter = logging.Formatter(
            fmt=cls._config['format'],
            datefmt=cls._config['date_format']
        )
        
        # Console handler
        if cls._config['console_logging']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(getattr(logging, cls._config['level']))
            root_logger.addHandler(console_handler)
            
        # File handler with rotation
        log_file_path = None
        if cls._config['file_logging']:
            log_file_path = log_dir / cls._config['log_file']
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=cls._config['max_log_size'],
                backupCount=cls._config['backup_count']
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, cls._config['level']))
            root_logger.addHandler(file_handler)
            
        cls._initialized = True
        
        # Log initialization
        logger = cls.get_logger('Logger')
        logger.info("Logging system initialized")
        logger.info(f"Log level: {cls._config['level']}")
        logger.info(f"Console logging: {cls._config['console_logging']}")
        logger.info(f"File logging: {cls._config['file_logging']}")
        if cls._config['file_logging'] and log_file_path:
            logger.info(f"Log file: {log_file_path}")
    
    @classmethod
    def setup_from_config_file(cls, config_path: str) -> None:
        """
        Set up logging from a YAML configuration file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            # Extract logging configuration
            logging_config = config_data.get('system', {}).get('logging', {})
            
            cls.setup_logging(config=logging_config)
            
        except Exception as e:
            # Fallback to default configuration
            cls.setup_logging()
            logger = cls.get_logger('Logger')
            logger.warning(f"Failed to load logging config from {config_path}: {e}")
            logger.info("Using default logging configuration")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get logger instance for a module.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            Configured logger instance
        """
        if not cls._initialized:
            cls.setup_logging()
            
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
            
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Change logging level for all loggers.
        
        Args:
            level: New logging level (DEBUG, INFO, WARNING, ERROR)
        """
        level_obj = getattr(logging, level.upper())
        
        # Update root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level_obj)
        
        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(level_obj)
            
        cls._config['level'] = level.upper()
        
        logger = cls.get_logger('Logger')
        logger.info(f"Log level changed to: {level.upper()}")
    
    @classmethod
    def add_file_handler(cls, log_file: str, level: Optional[str] = None) -> None:
        """
        Add additional file handler for specific logging needs.
        
        Args:
            log_file: Path to additional log file
            level: Optional logging level for this handler
        """
        if not cls._initialized:
            cls.setup_logging()
            
        log_path = Path(cls._config['log_dir']) / log_file
        
        formatter = logging.Formatter(
            fmt=cls._config['format'],
            datefmt=cls._config['date_format']
        )
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=cls._config['max_log_size'],
            backupCount=cls._config['backup_count']
        )
        file_handler.setFormatter(formatter)
        
        if level:
            file_handler.setLevel(getattr(logging, level.upper()))
        else:
            file_handler.setLevel(getattr(logging, cls._config['level']))
            
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        
        logger = cls.get_logger('Logger')
        logger.info(f"Added file handler: {log_path}")
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Get current logging configuration.
        
        Returns:
            Current logging configuration dictionary
        """
        return cls._config.copy()
    
    @classmethod
    def create_analysis_logger(cls, analysis_name: str) -> logging.Logger:
        """
        Create a specialized logger for specific analysis runs.
        
        Args:
            analysis_name: Name of the analysis (used for log file naming)
            
        Returns:
            Specialized logger with its own file handler
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"{analysis_name}_{timestamp}.log"
        
        logger = cls.get_logger(f"analysis.{analysis_name}")
        
        # Add dedicated file handler for this analysis
        cls.add_file_handler(log_file, level=cls._config['level'])
        
        logger.info(f"Starting analysis: {analysis_name}")
        return logger


# Convenience functions for backward compatibility
def setup_logging(level: str = "INFO", log_file: Optional[str] = None, console: bool = True) -> None:
    """Convenience function for setting up logging."""
    Logger.setup_logging(level=level, log_file=log_file, console=console)


def get_logger(name: str) -> logging.Logger:
    """Convenience function for getting a logger."""
    return Logger.get_logger(name)


# Module-level logger for this utility
logger = Logger.get_logger(__name__)
