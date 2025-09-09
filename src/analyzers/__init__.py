"""
Analysis modules for bio.tools quality evaluation.

This package contains modules for quality analysis, linting,
and parallel processing of bio.tools entries.
"""

# Import core analyzer
try:
    from .quality_analyzer import QualityAnalyzer, QualityReport, QualityMetrics
    QUALITY_ANALYZER_AVAILABLE = True
except ImportError:
    QUALITY_ANALYZER_AVAILABLE = False

# Import linter
try:
    from .linter import BiotoolsLinter, LintIssue, IssueLevel
    LINTER_AVAILABLE = True
except ImportError:
    LINTER_AVAILABLE = False

# Import parallel processor
try:
    from .parallel_processor import ParallelQualityProcessor, ProcessingResult, BatchProcessingStats, create_parallel_processor
    PARALLEL_PROCESSOR_AVAILABLE = True
except ImportError:
    PARALLEL_PROCESSOR_AVAILABLE = False

__all__ = []

if QUALITY_ANALYZER_AVAILABLE:
    __all__.extend([
        'QualityAnalyzer',
        'QualityReport', 
        'QualityMetrics'
    ])

if LINTER_AVAILABLE:
    __all__.extend([
        'BiotoolsLinter',
        'LintIssue',
        'IssueLevel'
    ])

if PARALLEL_PROCESSOR_AVAILABLE:
    __all__.extend([
        'ParallelQualityProcessor',
        'ProcessingResult',
        'BatchProcessingStats',
        'create_parallel_processor'
    ])
