# Utils package initialization

# Add biotools-linter constants to avoid import conflicts
REPORT = 25  # Report log level from biotools-linter

def flatten_json_to_single_dict(json_data, parent_key="", separator="/"):
    """Placeholder function for biotools-linter compatibility"""
    return {}

def array_without_value(arr, value):
    """Placeholder function for biotools-linter compatibility"""
    return [item for item in arr if item != value]

def sanity_check_json(json_data):
    """Placeholder function for biotools-linter compatibility"""
    return isinstance(json_data, dict)

# Import parallel processing modules if available
try:
    from .parallel_config import ParallelProcessingConfig, create_optimal_config
    from .processing_pipeline import ProcessingPipeline, PipelineProgress, PipelineStats
    PARALLEL_PROCESSING_AVAILABLE = True
except ImportError:
    PARALLEL_PROCESSING_AVAILABLE = False

# Import utility modules
try:
    from .data_cleaner import ToolDataCleaner
    from .logger import Logger
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

__all__ = []

if UTILS_AVAILABLE:
    __all__.extend(['ToolDataCleaner', 'Logger'])

if PARALLEL_PROCESSING_AVAILABLE:
    __all__.extend([
        'ParallelProcessingConfig',
        'create_optimal_config', 
        'ProcessingPipeline',
        'PipelineProgress',
        'PipelineStats'
    ])
