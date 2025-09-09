"""
Parallel Processing Configuration

Configuration classes and settings for controlling concurrent operations
in the bio.tools quality analysis pipeline.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ParallelProcessingConfig:
    """Configuration for parallel processing operations."""
    
    # API fetching concurrency
    max_concurrent_api_requests: int = 5
    api_rate_limit_delay: float = 0.5  # seconds between requests
    api_timeout: int = 30
    api_max_retries: int = 3
    
    # Analysis processing concurrency  
    max_concurrent_analyses: int = 4
    analysis_batch_size: int = 10
    
    # Pipeline settings
    pipeline_buffer_size: int = 50
    enable_pipeline_mode: bool = True
    
    # Resource limits
    max_memory_usage_mb: int = 2048
    enable_memory_monitoring: bool = True
    
    # Progress and logging
    progress_update_interval: int = 5  # seconds
    enable_detailed_logging: bool = False
    
    @classmethod
    def create_default(cls) -> 'ParallelProcessingConfig':
        """Create default configuration."""
        return cls()
    
    @classmethod
    def create_conservative(cls) -> 'ParallelProcessingConfig':
        """Create conservative configuration for slower systems or rate-limited APIs."""
        return cls(
            max_concurrent_api_requests=2,
            api_rate_limit_delay=1.0,
            max_concurrent_analyses=2,
            analysis_batch_size=5,
            pipeline_buffer_size=20
        )
    
    @classmethod
    def create_aggressive(cls) -> 'ParallelProcessingConfig':
        """Create aggressive configuration for fast systems and APIs."""
        return cls(
            max_concurrent_api_requests=10,
            api_rate_limit_delay=0.2,
            max_concurrent_analyses=8,
            analysis_batch_size=20,
            pipeline_buffer_size=100
        )
    
    @classmethod
    def create_from_environment(cls) -> 'ParallelProcessingConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Read from environment variables with fallbacks
        config.max_concurrent_api_requests = int(
            os.getenv('BIOTOOLS_MAX_CONCURRENT_API', config.max_concurrent_api_requests)
        )
        config.api_rate_limit_delay = float(
            os.getenv('BIOTOOLS_API_RATE_LIMIT', config.api_rate_limit_delay)
        )
        config.max_concurrent_analyses = int(
            os.getenv('BIOTOOLS_MAX_CONCURRENT_ANALYSIS', config.max_concurrent_analyses)
        )
        config.analysis_batch_size = int(
            os.getenv('BIOTOOLS_ANALYSIS_BATCH_SIZE', config.analysis_batch_size)
        )
        config.pipeline_buffer_size = int(
            os.getenv('BIOTOOLS_PIPELINE_BUFFER_SIZE', config.pipeline_buffer_size)
        )
        config.enable_pipeline_mode = os.getenv('BIOTOOLS_ENABLE_PIPELINE', 'true').lower() == 'true'
        config.enable_detailed_logging = os.getenv('BIOTOOLS_DETAILED_LOGGING', 'false').lower() == 'true'
        
        return config
    
    def auto_tune_for_system(self) -> 'ParallelProcessingConfig':
        """Auto-tune configuration based on system capabilities."""
        try:
            import psutil
            
            # Get system info
            cpu_count = psutil.cpu_count(logical=True) or 4  # fallback to 4 if None
            memory_gb = psutil.virtual_memory().total / (1024**3)
            
        except ImportError:
            logger.warning("psutil not available, using default system assumptions")
            cpu_count = 4  # reasonable default
            memory_gb = 8.0  # reasonable default
        
        # Adjust based on system resources
        if cpu_count >= 8 and memory_gb >= 16:
            # High-end system
            self.max_concurrent_api_requests = min(10, cpu_count)
            self.max_concurrent_analyses = min(8, cpu_count - 2)
            self.analysis_batch_size = 20
        elif cpu_count >= 4 and memory_gb >= 8:
            # Mid-range system
            self.max_concurrent_api_requests = min(5, cpu_count)
            self.max_concurrent_analyses = min(4, cpu_count - 1)
            self.analysis_batch_size = 10
        else:
            # Lower-end system
            self.max_concurrent_api_requests = 2
            self.max_concurrent_analyses = 2
            self.analysis_batch_size = 5
        
        # Adjust memory limits
        self.max_memory_usage_mb = min(2048, int(memory_gb * 1024 * 0.5))  # Use up to 50% of RAM
        
        logger.info(f"Auto-tuned config for {cpu_count} CPUs, {memory_gb:.1f}GB RAM")
        logger.info(f"API concurrency: {self.max_concurrent_api_requests}, "
                   f"Analysis concurrency: {self.max_concurrent_analyses}")
        
        return self
    
    def validate(self) -> bool:
        """Validate configuration values."""
        errors = []
        
        if self.max_concurrent_api_requests <= 0:
            errors.append("max_concurrent_api_requests must be positive")
        
        if self.api_rate_limit_delay < 0:
            errors.append("api_rate_limit_delay must be non-negative")
        
        if self.max_concurrent_analyses <= 0:
            errors.append("max_concurrent_analyses must be positive")
        
        if self.analysis_batch_size <= 0:
            errors.append("analysis_batch_size must be positive")
        
        if self.pipeline_buffer_size <= 0:
            errors.append("pipeline_buffer_size must be positive")
        
        if errors:
            logger.error(f"Configuration validation errors: {'; '.join(errors)}")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'max_concurrent_api_requests': self.max_concurrent_api_requests,
            'api_rate_limit_delay': self.api_rate_limit_delay,
            'api_timeout': self.api_timeout,
            'api_max_retries': self.api_max_retries,
            'max_concurrent_analyses': self.max_concurrent_analyses,
            'analysis_batch_size': self.analysis_batch_size,
            'pipeline_buffer_size': self.pipeline_buffer_size,
            'enable_pipeline_mode': self.enable_pipeline_mode,
            'max_memory_usage_mb': self.max_memory_usage_mb,
            'enable_memory_monitoring': self.enable_memory_monitoring,
            'progress_update_interval': self.progress_update_interval,
            'enable_detailed_logging': self.enable_detailed_logging
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParallelProcessingConfig':
        """Create configuration from dictionary."""
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return (
            f"ParallelProcessingConfig("
            f"API: {self.max_concurrent_api_requests} concurrent, "
            f"{self.api_rate_limit_delay}s delay; "
            f"Analysis: {self.max_concurrent_analyses} concurrent, "
            f"batch_size={self.analysis_batch_size}; "
            f"Pipeline: {'enabled' if self.enable_pipeline_mode else 'disabled'}, "
            f"buffer={self.pipeline_buffer_size})"
        )


def create_optimal_config(
    system_type: str = "auto",
    priority: str = "balanced"
) -> ParallelProcessingConfig:
    """
    Create an optimal configuration based on system type and priority.
    
    Args:
        system_type: "auto", "desktop", "server", "cloud", "laptop"
        priority: "speed", "stability", "balanced", "resource_saving"
        
    Returns:
        Optimized ParallelProcessingConfig
    """
    if system_type == "auto":
        config = ParallelProcessingConfig.create_from_environment()
        config.auto_tune_for_system()
    elif system_type == "server":
        config = ParallelProcessingConfig.create_aggressive()
    elif system_type == "laptop":
        config = ParallelProcessingConfig.create_conservative()
    else:
        config = ParallelProcessingConfig.create_default()
    
    # Adjust based on priority
    if priority == "speed":
        config.max_concurrent_api_requests *= 2
        config.max_concurrent_analyses = min(16, config.max_concurrent_analyses * 2)
        config.api_rate_limit_delay *= 0.5
    elif priority == "stability":
        config.max_concurrent_api_requests = max(1, config.max_concurrent_api_requests // 2)
        config.max_concurrent_analyses = max(1, config.max_concurrent_analyses // 2)
        config.api_rate_limit_delay *= 2
    elif priority == "resource_saving":
        config.max_concurrent_api_requests = min(2, config.max_concurrent_api_requests)
        config.max_concurrent_analyses = min(2, config.max_concurrent_analyses)
        config.analysis_batch_size = min(5, config.analysis_batch_size)
        config.max_memory_usage_mb = min(1024, config.max_memory_usage_mb)
    
    config.validate()
    return config
