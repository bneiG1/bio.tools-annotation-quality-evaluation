"""
Tool data cleaning utilities.

This module provides functionality to clean bio.tools data by removing
empty values, null fields, and other unwanted elements, following the
same approach used in the official bio.tools registry.
"""

import logging
from typing import Any, Dict, List, Union
from boltons.iterutils import remap
from .logger import Logger

logger = Logger.get_logger(__name__)


class ToolDataCleaner:
    """
    Cleans bio.tools data by removing empty/null values.
    
    Based on the cleaning logic from the bio.tools registry:
    https://github.com/bio-tools/biotoolsRegistry/blob/main/backend/elixir/renderers.py
    """
    
    def __init__(self, 
                 remove_empty_strings: bool = True,
                 remove_empty_lists: bool = True,
                 remove_empty_dicts: bool = True,
                 remove_null_values: bool = True,
                 remove_false_values: bool = False):
        """
        Initialize the cleaner with configuration options.
        
        Args:
            remove_empty_strings: Remove empty string values
            remove_empty_lists: Remove empty list values
            remove_empty_dicts: Remove empty dictionary values
            remove_null_values: Remove None/null values
            remove_false_values: Remove False boolean values
        """
        self.remove_empty_strings = remove_empty_strings
        self.remove_empty_lists = remove_empty_lists
        self.remove_empty_dicts = remove_empty_dicts
        self.remove_null_values = remove_null_values
        self.remove_false_values = remove_false_values
    
    def clean_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single tool entry by removing empty/unwanted values.
        
        Args:
            tool_data: Raw tool data from bio.tools API
            
        Returns:
            Cleaned tool data with empty values removed
        """
        logger.debug(f"Cleaning tool data for: {tool_data.get('biotoolsID', 'unknown')}")
        
        # Create a custom visit function based on configuration
        def should_keep_value(path, key, value):
            """Determine if a value should be kept during cleaning."""
            
            # Always keep if None for required navigation
            if key is None:
                return True
                
            # Remove null values if configured
            if self.remove_null_values and value is None:
                return False
                
            # Remove empty strings if configured
            if self.remove_empty_strings and value == "":
                return False
                
            # Remove empty lists if configured
            if self.remove_empty_lists and isinstance(value, list) and len(value) == 0:
                return False
                
            # Remove empty dictionaries if configured
            if self.remove_empty_dicts and isinstance(value, dict) and len(value) == 0:
                return False
                
            # Remove false values if configured (but keep 0)
            if self.remove_false_values and value is False:
                return False
                
            return True
        
        # Use boltons.remap to traverse and clean the data structure
        cleaned_data = remap(tool_data, visit=should_keep_value)
        
        # Log cleaning statistics
        original_fields = self._count_fields(tool_data)
        cleaned_fields = self._count_fields(cleaned_data)
        removed_fields = original_fields - cleaned_fields
        
        if removed_fields > 0:
            logger.info(f"Cleaned tool {tool_data.get('biotoolsID', 'unknown')}: "
                       f"removed {removed_fields} empty fields "
                       f"({original_fields} -> {cleaned_fields})")
        
        return cleaned_data
    
    def clean_tools_batch(self, tools_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean a batch of tool entries.
        
        Args:
            tools_data: List of raw tool data from bio.tools API
            
        Returns:
            List of cleaned tool data
        """
        logger.info(f"Cleaning batch of {len(tools_data)} tools")
        
        cleaned_tools = []
        total_removed = 0
        
        for tool_data in tools_data:
            cleaned_tool = self.clean_tool(tool_data)
            cleaned_tools.append(cleaned_tool)
            
            # Track total fields removed
            original_fields = self._count_fields(tool_data)
            cleaned_fields = self._count_fields(cleaned_tool)
            total_removed += (original_fields - cleaned_fields)
        
        logger.info(f"Batch cleaning complete: removed {total_removed} empty fields total")
        return cleaned_tools
    
    def _count_fields(self, data: Any, count: int = 0) -> int:
        """
        Recursively count the number of fields in a data structure.
        
        Args:
            data: Data structure to count
            count: Current count (for recursion)
            
        Returns:
            Total number of fields/values
        """
        if isinstance(data, dict):
            count += len(data)
            for value in data.values():
                count = self._count_fields(value, count)
        elif isinstance(data, list):
            for item in data:
                count = self._count_fields(item, count)
        return count
    
    @staticmethod
    def create_biotools_standard_cleaner() -> 'ToolDataCleaner':
        """
        Create a cleaner with settings that match bio.tools registry behavior.
        
        Returns:
            ToolDataCleaner configured for bio.tools standard cleaning
        """
        return ToolDataCleaner(
            remove_empty_strings=True,
            remove_empty_lists=True,
            remove_empty_dicts=True,
            remove_null_values=True,
            remove_false_values=False  # Keep False values as they might be meaningful
        )
    
    @staticmethod
    def create_aggressive_cleaner() -> 'ToolDataCleaner':
        """
        Create a cleaner with more aggressive settings for maximum cleanup.
        
        Returns:
            ToolDataCleaner configured for aggressive cleaning
        """
        return ToolDataCleaner(
            remove_empty_strings=True,
            remove_empty_lists=True,
            remove_empty_dicts=True,
            remove_null_values=True,
            remove_false_values=True
        )


def clean_tool_data(tool_data: Dict[str, Any], 
                   aggressive: bool = False) -> Dict[str, Any]:
    """
    Convenience function to clean tool data with default settings.
    
    Args:
        tool_data: Raw tool data from bio.tools API
        aggressive: Use aggressive cleaning settings
        
    Returns:
        Cleaned tool data
    """
    if aggressive:
        cleaner = ToolDataCleaner.create_aggressive_cleaner()
    else:
        cleaner = ToolDataCleaner.create_biotools_standard_cleaner()
    
    return cleaner.clean_tool(tool_data)


def clean_tools_batch(tools_data: List[Dict[str, Any]], 
                     aggressive: bool = False) -> List[Dict[str, Any]]:
    """
    Convenience function to clean a batch of tools with default settings.
    
    Args:
        tools_data: List of raw tool data from bio.tools API
        aggressive: Use aggressive cleaning settings
        
    Returns:
        List of cleaned tool data
    """
    if aggressive:
        cleaner = ToolDataCleaner.create_aggressive_cleaner()
    else:
        cleaner = ToolDataCleaner.create_biotools_standard_cleaner()
    
    return cleaner.clean_tools_batch(tools_data)
