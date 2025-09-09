"""
Data collection modules for bio.tools quality analysis.

This package contains the unified bio.tools API client that supports both
synchronous and asynchronous operations for different use cases.
"""

# Import unified API client from the async module (which now contains both sync and async)
try:
    from .async_biotools_api import (
        UnifiedBioToolsAPIClient, 
        AsyncBioToolsAPIClient,
        FetchResult, 
        create_async_client
    )
    API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Bio.tools API client not available: {e}")
    API_AVAILABLE = False

__all__ = []

if API_AVAILABLE:
    __all__.extend([
        'UnifiedBioToolsAPIClient',
        'AsyncBioToolsAPIClient', 
        'FetchResult',
        'create_async_client'
    ])
