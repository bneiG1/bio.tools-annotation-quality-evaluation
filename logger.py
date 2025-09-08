import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "biotools_evaluator",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up a comprehensive logger for the bio.tools quality evaluation pipeline.
    
    This logger is configured for bioinformatics data processing workflows with
    appropriate formatting for debugging API calls, data validation, and scoring operations.
    
    Args:
        name (str): Logger name (default: "biotools_evaluator")
        log_level (str): Logging level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        log_file (str, optional): Path to log file. If None, creates default in logs/
        console_output (bool): Whether to output logs to console (default: True)
        max_file_size (int): Maximum log file size in bytes before rotation (default: 10MB)
        backup_count (int): Number of backup log files to keep (default: 5)
    
    Returns:
        logging.Logger: Configured logger instance
        
    Example:
        >>> logger = setup_logger("data_collector", "DEBUG", "logs/collector.log")
        >>> logger.info("Starting bio.tools API data collection")
        >>> logger.debug(f"Fetching page {page_num} with {len(tools)} tools")
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Set up file logging
    if log_file is None:
        # Create default log file path
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d")
        # Ensure log_file is a string to match the declared type Optional[str]
        log_file = str(log_dir / f"{name}_{timestamp}.log")
    
    # Create rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_file_size,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # File gets all messages
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Set up console logging
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Log initial setup message
    logger.info(f"Logger '{name}' initialized with level {log_level}")
    logger.debug(f"Log file: {log_file}")
    
    return logger


def get_logger(name: str = "biotools_evaluator") -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


# Pre-configured loggers for different pipeline components
def get_collector_logger() -> logging.Logger:
    """Get logger for data collection operations (API calls, caching)."""
    return setup_logger("collector", "INFO", "logs/collector.log")


def get_validator_logger() -> logging.Logger:
    """Get logger for schema validation and data quality checks."""
    return setup_logger("validator", "INFO", "logs/validator.log")


def get_analyzer_logger() -> logging.Logger:
    """Get logger for scoring and analysis operations."""
    return setup_logger("analyzer", "INFO", "logs/analyzer.log")


def get_reporter_logger() -> logging.Logger:
    """Get logger for report generation and visualization."""
    return setup_logger("reporter", "INFO", "logs/reporter.log")


# Context manager for temporary log level changes
class LogLevel:
    """
    Context manager for temporarily changing log level.
    
    Example:
        >>> logger = get_logger()
        >>> with LogLevel(logger, "DEBUG"):
        ...     logger.debug("This debug message will be shown")
        >>> logger.debug("This debug message will be hidden")
    """
    
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.new_level = getattr(logging, level.upper())
        self.original_level = logger.level
    
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


# Helper function for logging API responses
def log_api_response(logger: logging.Logger, response, url: str, params: Optional[dict] = None):
    """
    Log API response details in a standardized format for bio.tools API calls.
    
    Args:
        logger: Logger instance
        response: requests.Response object
        url: Request URL
        params: Request parameters (optional)
    """
    params_str = f" with params {params}" if params else ""
    
    logger.info(f"API Request: {response.request.method} {url}{params_str}")
    logger.info(f"Response: {response.status_code} - {len(response.content)} bytes")
    
    if response.status_code != 200:
        logger.warning(f"Non-200 status code: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
    
    # Log rate limiting info if present
    if 'x-ratelimit-remaining' in response.headers:
        remaining = response.headers['x-ratelimit-remaining']
        logger.debug(f"Rate limit remaining: {remaining}")


if __name__ == "__main__":
    # Example usage and testing
    print("Testing logger setup...")
    
    # Test basic logger
    logger = setup_logger("test_logger", "DEBUG")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test specialized loggers
    collector_log = get_collector_logger()
    collector_log.info("Testing collector logger")
    
    # Test log level context manager
    with LogLevel(logger, "ERROR"):
        logger.info("This info message should not appear")
        logger.error("This error message should appear")
    
    logger.info("Back to normal log level")
    
    print("Logger testing complete. Check logs/ directory for output files.")
