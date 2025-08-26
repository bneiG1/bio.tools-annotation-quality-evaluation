"""
Integration with the bio.tools linter for real-time quality assessment.
Based on: https://github.com/3top1a/biotools-linter
"""

import subprocess
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile
import os
from dataclasses import dataclass


@dataclass
class LinterResult:
    """Structured representation of linter output for a single tool."""
    biotoolsID: str
    errors: List[str]
    warnings: List[str] 
    info: List[str]
    error_count: int
    warning_count: int
    info_count: int
    linter_score: float
    raw_output: str


class BioToolsLinter:
    """
    Integration with the bio.tools linter CLI tool.
    
    Requires bio.tools linter to be installed:
    https://github.com/3top1a/biotools-linter
    """
    
    def __init__(self, linter_path: Optional[str] = None, cache_results: bool = True):
        """
        Initialize the bio.tools linter integration.
        
        Args:
            linter_path: Path to the bio.tools linter CLI (linter/cli.py)
            cache_results: Whether to cache linter results to avoid repeated calls
        """
        self.logger = logging.getLogger(__name__)
        self.linter_path = linter_path or self._find_linter_path()
        self.cache_results = cache_results
        self._result_cache: Dict[str, LinterResult] = {}
        
        # Error type severity mapping - updated based on actual linter output
        self.error_severity = {
            # Major errors - 15 points penalty each
            'URL_SSL_ERROR': 'error',        # SSL certificate issues
            'URL_NOT_FOUND': 'error',        # 404 errors, DNS failures
            'URL_TIMEOUT': 'error',          # Timeout issues
            'MISSING_REQUIRED_FIELD': 'error',  # Critical metadata missing
            'SCHEMA_VALIDATION_ERROR': 'error',  # Schema violations
            
            # Warnings - 5 points penalty each  
            'EDAM_OBSOLETE': 'warning',      # Obsolete EDAM terms
            'INVALID_FORMAT': 'warning',     # Format issues
            'DEPRECATED_FIELD': 'warning',   # Outdated fields
            'INCONSISTENT_DATA': 'warning',  # Data inconsistencies
            'URL_REDIRECT': 'warning',       # URL redirects
            
            # Info - 1 point penalty each
            'DOI_BUT_NOT_PMCID': 'info',     # Missing PMC IDs
            'DOI_BUT_NOT_PMID': 'info',      # Missing PMID
            'PUBLICATION_ENHANCEMENT': 'info',  # Publication improvements
            'METADATA_SUGGESTION': 'info'    # Optional metadata suggestions
        }
    
    def _find_linter_path(self) -> Optional[str]:
        """Attempt to find the bio.tools linter CLI path."""
        possible_paths = [
            'linter/cli.py',
            '../biotools-linter/linter/cli.py',
            '../../biotools-linter/linter/cli.py',
            os.path.expanduser('~/biotools-linter/linter/cli.py')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"Found bio.tools linter at: {path}")
                return path
        
        self.logger.warning("Bio.tools linter not found. Please install from: https://github.com/3top1a/biotools-linter")
        return None
    
    def is_available(self) -> bool:
        """Check if the bio.tools linter is available."""
        if not self.linter_path:
            return False
        
        try:
            # Test if we can run the linter
            result = subprocess.run(
                ['python3', self.linter_path, '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def lint_tool(self, biotoolsID: str, use_cache: bool = True) -> LinterResult:
        """
        Lint a single tool by its biotoolsID.
        
        Args:
            biotoolsID: The bio.tools ID of the tool to lint
            use_cache: Whether to use cached results if available
            
        Returns:
            LinterResult object with structured linter output
        """
        if use_cache and self.cache_results and biotoolsID in self._result_cache:
            self.logger.debug(f"Using cached linter result for {biotoolsID}")
            return self._result_cache[biotoolsID]
        
        if not self.linter_path:
            self.logger.error("Bio.tools linter not available")
            return self._create_empty_result(biotoolsID, "Linter not available")
        
        try:
            # Run the linter
            self.logger.debug(f"Running linter for tool: {biotoolsID}")
            result = subprocess.run(
                ['python3', self.linter_path, biotoolsID],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                self.logger.warning(f"Linter returned non-zero exit code for {biotoolsID}: {result.stderr}")
            
            # Parse the output
            linter_result = self._parse_linter_output(biotoolsID, result.stdout, result.stderr)
            
            # Cache the result
            if self.cache_results:
                self._result_cache[biotoolsID] = linter_result
            
            return linter_result
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Linter timeout for tool: {biotoolsID}")
            return self._create_empty_result(biotoolsID, "Linter timeout")
        
        except Exception as e:
            self.logger.error(f"Error running linter for {biotoolsID}: {e}")
            return self._create_empty_result(biotoolsID, f"Linter error: {str(e)}")
    
    def lint_tools_batch(self, biotoolsIDs: List[str], max_workers: int = 4) -> List[LinterResult]:
        """
        Lint multiple tools in batch with optional parallel processing.
        
        Args:
            biotoolsIDs: List of bio.tools IDs to lint
            max_workers: Maximum number of parallel workers (set to 1 for sequential)
            
        Returns:
            List of LinterResult objects
        """
        results = []
        
        if max_workers == 1:
            # Sequential processing
            for i, biotoolsID in enumerate(biotoolsIDs):
                self.logger.info(f"Linting tool {i+1}/{len(biotoolsIDs)}: {biotoolsID}")
                result = self.lint_tool(biotoolsID)
                results.append(result)
        else:
            # Parallel processing (if needed in future)
            # For now, use sequential to avoid overwhelming the bio.tools API
            self.logger.info("Using sequential processing to avoid API rate limits")
            for i, biotoolsID in enumerate(biotoolsIDs):
                if i % 10 == 0:
                    self.logger.info(f"Progress: {i}/{len(biotoolsIDs)} tools linted")
                result = self.lint_tool(biotoolsID)
                results.append(result)
        
        return results
    
    def _parse_linter_output(self, biotoolsID: str, stdout: str, stderr: str) -> LinterResult:
        """
        Parse the raw linter output into structured format.
        
        Args:
            biotoolsID: The tool ID that was linted
            stdout: Standard output from linter
            stderr: Standard error from linter
            
        Returns:
            LinterResult object
        """
        errors = []
        warnings = []
        info = []
        
        # Combine stdout and stderr for parsing
        full_output = stdout + "\n" + stderr
        
        # Parse each line for error patterns
        for line in full_output.split('\n'):
            if not line.strip():
                continue
                
            # Updated pattern to match actual linter output: "toolname [ERROR_TYPE]: description"
            match = re.match(r'^(\w+)\s+\[([^\]]+)\]:\s*(.+)$', line.strip())
            if match:
                tool_name, error_type, description = match.groups()
                
                # Categorize by severity
                severity = self.error_severity.get(error_type, 'warning')
                
                error_entry = f"[{error_type}] {description}"
                
                if severity == 'error':
                    errors.append(error_entry)
                elif severity == 'warning':
                    warnings.append(error_entry)
                else:
                    info.append(error_entry)
        
        # Calculate linter score (100 - penalty for issues)
        error_penalty = len(errors) * 15      # 15 points per error
        warning_penalty = len(warnings) * 5   # 5 points per warning  
        info_penalty = len(info) * 1          # 1 point per info
        
        linter_score = max(0, 100 - error_penalty - warning_penalty - info_penalty)
        
        return LinterResult(
            biotoolsID=biotoolsID,
            errors=errors,
            warnings=warnings,
            info=info,
            error_count=len(errors),
            warning_count=len(warnings),
            info_count=len(info),
            linter_score=linter_score,
            raw_output=full_output
        )
    
    def _create_empty_result(self, biotoolsID: str, error_message: str) -> LinterResult:
        """Create an empty result when linting fails."""
        return LinterResult(
            biotoolsID=biotoolsID,
            errors=[error_message],
            warnings=[],
            info=[],
            error_count=1,
            warning_count=0,
            info_count=0,
            linter_score=0,
            raw_output=error_message
        )
    
    def get_error_summary(self, results: List[LinterResult]) -> Dict[str, Any]:
        """
        Generate a summary of error patterns across linter results.
        
        Args:
            results: List of LinterResult objects
            
        Returns:
            Dictionary with error summary statistics
        """
        error_types = {}
        warning_types = {}
        total_errors = 0
        total_warnings = 0
        total_info = 0
        
        for result in results:
            total_errors += result.error_count
            total_warnings += result.warning_count
            total_info += result.info_count
            
            # Count error types
            for error in result.errors:
                error_type = self._extract_error_type(error)
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            # Count warning types
            for warning in result.warnings:
                warning_type = self._extract_error_type(warning)
                warning_types[warning_type] = warning_types.get(warning_type, 0) + 1
        
        return {
            'total_tools': len(results),
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_info': total_info,
            'avg_linter_score': sum(r.linter_score for r in results) / len(results) if results else 0,
            'tools_with_errors': sum(1 for r in results if r.error_count > 0),
            'tools_with_warnings': sum(1 for r in results if r.warning_count > 0),
            'most_common_errors': sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_common_warnings': sorted(warning_types.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def _extract_error_type(self, error_message: str) -> str:
        """Extract error type from error message."""
        match = re.match(r'^\[([^\]]+)\]', error_message)
        return match.group(1) if match else 'UNKNOWN'
    
    def export_results(self, results: List[LinterResult], output_path: str) -> None:
        """Export linter results to JSON file."""
        export_data = []
        for result in results:
            export_data.append({
                'biotoolsID': result.biotoolsID,
                'error_count': result.error_count,
                'warning_count': result.warning_count,
                'info_count': result.info_count,
                'linter_score': result.linter_score,
                'errors': result.errors,
                'warnings': result.warnings,
                'info': result.info
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Exported {len(results)} linter results to {output_path}")


def demo_linter_integration():
    """Demonstrate the bio.tools linter integration."""
    logging.basicConfig(level=logging.INFO)
    
    linter = BioToolsLinter()
    
    if not linter.is_available():
        print("❌ Bio.tools linter not available!")
        print("Please install from: https://github.com/3top1a/biotools-linter")
        return
    
    print("✅ Bio.tools linter is available")
    
    # Test with a single tool
    test_tool = "MetExplore"
    print(f"\n🔍 Testing linter with tool: {test_tool}")
    
    result = linter.lint_tool(test_tool)
    print(f"Errors: {result.error_count}")
    print(f"Warnings: {result.warning_count}")
    print(f"Linter Score: {result.linter_score}/100")
    
    if result.errors:
        print("\nErrors found:")
        for error in result.errors[:3]:  # Show first 3
            print(f"  • {error}")
    
    if result.warnings:
        print("\nWarnings found:")
        for warning in result.warnings[:3]:  # Show first 3
            print(f"  • {warning}")


if __name__ == "__main__":
    demo_linter_integration()
