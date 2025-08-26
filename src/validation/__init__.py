"""
Validation module for bio.tools metadata quality evaluation.

This module provides various validation utilities including URL accessibility checking,
schema validation, and data integrity checks.
"""

from .url_checker import URLChecker

__all__ = ['URLChecker']
