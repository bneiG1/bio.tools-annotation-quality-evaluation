"""
Bio.tools linter integration module.

This module provides integration with the bio.tools linter (3top1a/biotools-linter)
to detect metadata quality issues in bio.tools entries.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from queue import Queue

logger = logging.getLogger(__name__)


class IssueLevel(Enum):
    """Severity levels for linter issues, mapped from bio.tools linter levels."""
    CRITICAL = "CRITICAL"  # Security problems or severe errors
    ERROR = "ERROR"        # High priority issues  
    WARNING = "WARNING"    # Medium priority issues
    INFO = "INFO"          # Low priority issues
    INTERNAL = "INTERNAL"  # Linter internal messages


@dataclass
class LintIssue:
    """Represents a linting issue found by the bio.tools linter."""
    
    code: str           # Issue code (e.g., "EDAM_OBSOLETE", "URL_SSL_ERROR")
    message: str        # Human-readable description
    location: str       # JSON path where issue was found
    level: IssueLevel   # Severity level
    tool_id: str        # bio.tools ID of the tool
    suggestion: Optional[str] = None  # Optional fix suggestion
    
    @classmethod
    def from_linter_message(cls, linter_message) -> 'LintIssue':
        """Create LintIssue from bio.tools linter Message object."""
        # Map linter levels to our levels
        level_mapping = {
            1: IssueLevel.INFO,      # Report
            2: IssueLevel.ERROR,     # LinterError  
            3: IssueLevel.INTERNAL,  # LinterInternal
            5: IssueLevel.ERROR,     # ReportHigh
            6: IssueLevel.WARNING,   # ReportMedium
            7: IssueLevel.INFO,      # ReportLow
            8: IssueLevel.CRITICAL,  # ReportCritical
        }
        
        level = level_mapping.get(linter_message.level.value, IssueLevel.WARNING)
        
        return cls(
            code=linter_message.code,
            message=linter_message.body,
            location=linter_message.location,
            level=level,
            tool_id=linter_message.tool or "unknown",
            suggestion=None  # bio.tools linter doesn't provide suggestions
        )


class BiotoolsLinter:
    """
    Integration wrapper for the bio.tools linter.
    
    This class provides a clean interface to the bio.tools linter
    while handling the complexities of the underlying implementation.
    """
    
    def __init__(self):
        """Initialize the linter with proper path setup."""
        self._setup_linter_path()
        self._linter_available = self._check_linter_availability()
        self._warning_message = None
        
        if not self._linter_available:
            self._warning_message = (
                "Bio.tools linter not available. Linting functionality will be disabled. "
                "Make sure the biotools-linter directory is present in the project root."
            )
            logger.warning(self._warning_message)
    
    def _setup_linter_path(self):
        """Add the linter directory to Python path for imports."""
        project_root = Path(__file__).parent.parent.parent
        linter_path = project_root / "biotools-linter" / "linter"
        
        if linter_path.exists():
            sys.path.insert(0, str(linter_path))
            self._linter_path = linter_path
        else:
            self._linter_path = None
            logger.warning(f"Linter path not found: {linter_path}")
    
    def _check_linter_availability(self) -> bool:
        """Check if the linter modules can be imported."""
        if not self._linter_path:
            return False
            
        try:
            # Try importing the main linter modules using importlib for dynamic imports
            import importlib.util
            
            # Check if main modules exist
            lib_spec = importlib.util.find_spec("lib")
            message_spec = importlib.util.find_spec("message")
            rules_spec = importlib.util.find_spec("rules")
            utils_spec = importlib.util.find_spec("utils")
            
            if not all([lib_spec, message_spec, rules_spec, utils_spec]):
                return False
                
            # Try actual imports
            import lib  # type: ignore
            import message  # type: ignore
            from rules import delegate_key_value_filter, delegate_whole_json_filter  # type: ignore
            from utils import flatten_json_to_single_dict, sanity_check_json  # type: ignore
            return True
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"Failed to import linter modules: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if the linter is available for use."""
        return self._linter_available
    
    def get_warning_message(self) -> Optional[str]:
        """Get the warning message if linter is not available."""
        return self._warning_message
    
    def lint_tool(self, tool_data: Dict) -> List[LintIssue]:
        """
        Lint a single bio.tools entry.
        
        Args:
            tool_data: Tool metadata from bio.tools API
            
        Returns:
            List of linting issues found
        """
        if not self._linter_available:
            logger.debug("Linter not available, returning empty issue list")
            return []
        
        try:
            return asyncio.run(self._lint_tool_async(tool_data))
        except Exception as e:
            logger.error(f"Error during linting: {e}")
            return []
    
    async def _lint_tool_async(self, tool_data: Dict) -> List[LintIssue]:
        """Async implementation of tool linting."""
        if not self._linter_available:
            return []
            
        try:
            # Import here to avoid issues if linter is not available
            from lib import Session  # type: ignore
            from utils import sanity_check_json, flatten_json_to_single_dict  # type: ignore
            from rules import delegate_key_value_filter, delegate_whole_json_filter  # type: ignore
            from message import Message  # type: ignore
        except (ImportError, ModuleNotFoundError) as e:
            logger.warning(f"Failed to import linter modules in async function: {e}")
            return []
        
        issues = []
        
        # Sanity check the JSON
        if sanity_check_json(tool_data):
            logger.warning("Tool data failed sanity check")
            return issues
        
        tool_name = tool_data.get("name", "Unknown")
        tool_id = tool_data.get("biotoolsID", "unknown")
        
        logger.debug(f"Linting tool: {tool_name} ({tool_id})")
        
        # Use a queue to collect messages
        message_queue = Queue()
        
        # Create session and lint the tool
        session = Session()
        try:
            await session.lint_specific_tool_json(tool_data, message_queue)
            
            # Collect all messages from the queue
            while not message_queue.empty():
                message = message_queue.get()
                if isinstance(message, Message):
                    # Skip internal linter messages
                    if message.code == "LINT-F":
                        continue
                    
                    # Convert to our LintIssue format
                    issue = LintIssue.from_linter_message(message)
                    issues.append(issue)
                    
        except Exception as e:
            logger.error(f"Error during async linting of {tool_id}: {e}")
        
        logger.debug(f"Found {len(issues)} linting issues for {tool_id}")
        return issues
    
    def lint_tools_batch(self, tools_data: List[Dict]) -> Dict[str, List[LintIssue]]:
        """
        Lint multiple bio.tools entries in batch.
        
        Args:
            tools_data: List of tool metadata from bio.tools API
            
        Returns:
            Dictionary mapping tool IDs to their linting issues
        """
        if not self._linter_available:
            logger.debug("Linter not available, returning empty results")
            return {}
        
        try:
            return asyncio.run(self._lint_tools_batch_async(tools_data))
        except Exception as e:
            logger.error(f"Error during batch linting: {e}")
            return {}
    
    async def _lint_tools_batch_async(self, tools_data: List[Dict]) -> Dict[str, List[LintIssue]]:
        """Async implementation of batch tool linting."""
        results = {}
        
        # Process tools in parallel with limited concurrency
        semaphore = asyncio.Semaphore(5)  # Limit concurrent linting operations
        
        async def lint_single_tool(tool_data: Dict) -> tuple[str, List[LintIssue]]:
            async with semaphore:
                tool_id = tool_data.get("biotoolsID", "unknown")
                issues = await self._lint_tool_async(tool_data)
                return tool_id, issues
        
        # Create tasks for all tools
        tasks = [lint_single_tool(tool_data) for tool_data in tools_data]
        
        # Wait for all tasks to complete
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for result in completed_tasks:
            if isinstance(result, Exception):
                logger.error(f"Error in batch linting task: {result}")
                continue
            
            # Ensure result is a tuple with two elements
            if not isinstance(result, tuple) or len(result) != 2:
                logger.error(f"Invalid result format: {result}")
                continue
                
            tool_id, issues = result
            results[tool_id] = issues
        
        logger.info(f"Completed batch linting of {len(results)} tools")
        return results
    
    def get_issue_summary(self, issues: List[LintIssue]) -> Dict[str, int]:
        """
        Get a summary of issues by type and severity.
        
        Args:
            issues: List of linting issues
            
        Returns:
            Summary dictionary with counts by level and type
        """
        summary = {
            "total": len(issues),
            "by_level": {},
            "by_code": {},
            "top_issues": []
        }
        
        # Count by level
        for level in IssueLevel:
            summary["by_level"][level.value] = sum(
                1 for issue in issues if issue.level == level
            )
        
        # Count by code
        code_counts = {}
        for issue in issues:
            code_counts[issue.code] = code_counts.get(issue.code, 0) + 1
        
        summary["by_code"] = code_counts
        
        # Get top 5 most common issues
        sorted_codes = sorted(code_counts.items(), key=lambda x: x[1], reverse=True)
        summary["top_issues"] = sorted_codes[:5]
        
        return summary
    
    def get_available_rules(self) -> List[str]:
        """
        Get list of available linting rules.
        
        Returns:
            List of rule names/codes that the linter can detect
        """
        if not self._linter_available:
            return []
        
        # Common rule codes from the bio.tools linter
        # This could be extended by actually inspecting the rules modules
        return [
            "EDAM_OBSOLETE",
            "EDAM_INVALID",
            "URL_SSL_ERROR", 
            "URL_INVALID",
            "URL_404",
            "URL_TIMEOUT",
            "URL_WITH_SPACES",
            "SUSPICIOUS_DOMAIN",
            "PUBLICATION_INVALID_DOI",
            "PUBLICATION_INVALID_PMID",
            "PUBLICATION_INVALID_PMCID",
            "MISSING_REQUIRED_FIELD",
            "EMPTY_FIELD"
        ]


# Convenience function for single tool linting
def lint_single_tool(tool_data: Dict) -> List[LintIssue]:
    """
    Convenience function to lint a single tool.
    
    Args:
        tool_data: Tool metadata from bio.tools API
        
    Returns:
        List of linting issues
    """
    linter = BiotoolsLinter()
    return linter.lint_tool(tool_data)


# Convenience function for batch linting
def lint_tools_batch(tools_data: List[Dict]) -> Dict[str, List[LintIssue]]:
    """
    Convenience function to lint multiple tools.
    
    Args:
        tools_data: List of tool metadata from bio.tools API
        
    Returns:
        Dictionary mapping tool IDs to their issues
    """
    linter = BiotoolsLinter()
    return linter.lint_tools_batch(tools_data)
