"""
Test script to verify biotools-linter integration.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analyzers.linter import BiotoolsLinter, lint_single_tool


def test_linter_availability():
    """Test if the linter is available and can be imported."""
    print("Testing linter availability...")
    
    linter = BiotoolsLinter()
    print(f"Linter available: {linter.is_available()}")
    
    if linter.is_available():
        print("Available rules:", linter.get_available_rules()[:5])  # Show first 5
    
    return linter.is_available()


def test_sample_tool_linting():
    """Test linting with a sample tool from our cache."""
    print("\nTesting tool linting...")
    
    # Try to find a cached tool to test with
    cache_dir = Path("data/cache")
    if not cache_dir.exists():
        print("No cache directory found, skipping tool linting test")
        return
    
    # Find the first JSON file in cache
    json_files = list(cache_dir.glob("*.json"))
    if not json_files:
        print("No cached tools found, skipping tool linting test")
        return
    
    # Load a sample tool
    sample_file = json_files[0]
    print(f"Testing with: {sample_file.name}")
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            tool_data = json.load(f)
        
        # Try linting
        issues = lint_single_tool(tool_data)
        print(f"Found {len(issues)} linting issues")
        
        # Show first few issues
        for i, issue in enumerate(issues[:3]):
            print(f"  {i+1}. [{issue.level.value}] {issue.code}: {issue.message}")
            if issue.location:
                print(f"      Location: {issue.location}")
        
        if len(issues) > 3:
            print(f"  ... and {len(issues) - 3} more issues")
            
    except Exception as e:
        print(f"Error during linting test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Bio.tools Linter Integration Test")
    print("=" * 40)
    
    available = test_linter_availability()
    
    if available:
        test_sample_tool_linting()
    else:
        print("Linter not available, skipping further tests")
    
    print("\nTest completed!")
