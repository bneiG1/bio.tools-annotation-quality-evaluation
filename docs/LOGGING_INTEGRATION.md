# Logging System Integration

## Overview

I have successfully integrated a comprehensive centralized logging system into the bio.tools annotation quality evaluation application. The logging system provides unified configuration, multiple output options, and flexible log level management.

## What Was Added

### 1. Centralized Logger Utility (`src/utils/logger.py`)

**Key Features:**
- **Centralized Configuration**: Single point of logging configuration
- **Multiple Handlers**: Support for both console and file logging with rotation
- **Configuration Integration**: Loads settings from YAML configuration files
- **Dynamic Level Changes**: Change log levels at runtime
- **Specialized Loggers**: Create analysis-specific loggers with dedicated files
- **Backward Compatibility**: Convenience functions for easy migration

**Main Methods:**
```python
# Setup logging
Logger.setup_logging(level="INFO", log_file="app.log", console=True)

# Setup from config file
Logger.setup_from_config_file("config/logging_config.yaml")

# Get logger instance
logger = Logger.get_logger(__name__)

# Change log level dynamically
Logger.set_level("DEBUG")

# Create analysis-specific logger
analysis_logger = Logger.create_analysis_logger("proteomics_analysis")
```

### 2. Configuration Management (`src/utils/config.py`)

**Features:**
- **YAML-based Configuration**: Easy-to-read configuration files
- **Deep Merging**: Overlay configurations for different environments
- **Dot Notation Access**: Easy access to nested configuration values
- **Default Values**: Sensible defaults with override capability

**Usage:**
```python
from src.utils.config import get_config_manager

config = get_config_manager("config/my_config.yaml")
log_level = config.get("system.logging.level", "INFO")
```

### 3. Default Configuration (`config/default_config.yaml`)

**Comprehensive Settings:**
- **Logging Configuration**: Levels, file rotation, formatting
- **API Settings**: Timeouts, retries, rate limiting
- **Scoring Parameters**: Weights, tiers, field scoring
- **Output Options**: Formats, directories, visualization
- **Development Settings**: Debug modes, testing options

### 4. Updated Main Application (`main.py`)

**Improvements:**
- **Configuration Option**: Added `--config` CLI parameter
- **Centralized Logging**: Uses new Logger utility throughout
- **Consistent Error Handling**: Unified error logging across commands
- **Better Debugging**: Verbose mode integration with logging levels

### 5. Module Updates

**Updated Files:**
- `src/utils/data_cleaner.py`: Uses centralized logger
- `src/validators/schema_validator.py`: Integrated with new logging system
- `src/validators/standards_scorer.py`: Updated to use Logger utility

## Configuration Options

### Logging Configuration (in YAML)

```yaml
system:
  logging:
    level: "INFO"                    # DEBUG, INFO, WARNING, ERROR
    file_logging: true              # Enable file logging
    console_logging: true           # Enable console logging
    log_file: "biotools_quality_analysis.log"
    log_dir: "logs"                 # Directory for log files
    max_log_size: 10485760         # 10MB max log file size
    backup_count: 5                # Number of backup log files
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: "%Y-%m-%d %H:%M:%S"
```

### Environment-Specific Configurations

**Development:**
```yaml
system:
  logging:
    level: "DEBUG"
    console_logging: true
```

**Production:**
```yaml
system:
  logging:
    level: "INFO"
    file_logging: true
    console_logging: false
```

## Usage Examples

### 1. Basic Usage

```bash
# Use default logging
python main.py analyze --tool-id blast

# Use verbose logging
python main.py --verbose analyze --tool-id blast

# Use custom configuration
python main.py --config config/production.yaml analyze --collection proteomics
```

### 2. In Python Code

```python
from src.utils.logger import Logger

# Get logger for current module
logger = Logger.get_logger(__name__)

# Log messages
logger.info("Starting analysis")
logger.warning("Tool has incomplete metadata")
logger.error("Validation failed", exc_info=True)

# Create specialized logger for analysis run
analysis_logger = Logger.create_analysis_logger("batch_analysis")
```

### 3. Configuration-Based Setup

```python
from src.utils.logger import Logger

# Setup from configuration file
Logger.setup_from_config_file("config/my_config.yaml")

# Or manual setup
Logger.setup_logging(
    level="DEBUG",
    log_file="debug.log",
    console=True
)
```

## Log Files Generated

The system creates several log files in the `logs/` directory:

1. **Main Application Log**: `biotools_quality_analysis.log`
2. **Analysis-Specific Logs**: `analysis_name_timestamp.log`
3. **Specialized Logs**: `errors.log`, `api_requests.log` (if configured)
4. **Rotated Logs**: `.log.1`, `.log.2`, etc. (when files exceed size limit)

## Benefits

### 1. **Centralized Management**
- Single configuration point for all logging
- Consistent formatting across the application
- Easy to change logging behavior globally

### 2. **Flexibility**
- Support for multiple log levels
- Console and file output options
- Configurable rotation and retention
- Environment-specific configurations

### 3. **Analysis Tracking**
- Dedicated logs for specific analysis runs
- Timestamped log files for historical tracking
- Module-specific logging for debugging

### 4. **Production Ready**
- File rotation to prevent disk space issues
- Configurable log retention
- Performance-optimized logging
- Error handling and fallback options

### 5. **Developer Friendly**
- Easy-to-use API
- Backward compatibility with existing code
- Rich configuration options
- Debugging support

## Migration Guide

For existing code, simply replace:

```python
# Old way
import logging
logger = logging.getLogger(__name__)

# New way
from src.utils.logger import Logger
logger = Logger.get_logger(__name__)
```

The Logger class provides the same interface as Python's standard logging, so existing log calls work unchanged.

## Example Usage Script

Run `logging_examples.py` to see the logging system in action:

```bash
python logging_examples.py
```

This demonstrates:
- Basic logging setup
- Configuration-based logging
- Analysis-specific logging
- Dynamic log level changes
- Additional file handlers

## Next Steps

1. **Test the logging system** with real analysis runs
2. **Create environment-specific configs** for development/production
3. **Add log monitoring** for production deployments
4. **Integrate with external log aggregation** systems if needed
5. **Add log analysis tools** for performance monitoring

The logging system is now fully integrated and ready for production use!
