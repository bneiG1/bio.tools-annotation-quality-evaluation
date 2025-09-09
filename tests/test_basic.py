"""
Basic test for the bio.tools quality evaluation system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import json
from src.validators.standards_scorer import ToolInformationStandardsScorer, Tier

def test_standards_scorer():
    """Test the Tool Information Standards scorer"""
    scorer = ToolInformationStandardsScorer()
    
    # Test minimal tool data
    minimal_tool = {
        "biotoolsID": "test-tool",
        "name": "Test Tool",
        "description": "A test tool for analysis",
        "homepage": "https://example.com",
        "topic": [{"term": "Sequence analysis", "uri": "http://edamontology.org/topic_0080"}],
        "toolType": ["Command-line tool"],
        "function": [{"operation": [{"term": "Sequence alignment", "uri": "http://edamontology.org/operation_0292"}]}]
    }
    
    result = scorer.score_tool(minimal_tool)
    
    # Should achieve at least MINIMAL tier
    assert result["tier"] in [Tier.MINIMAL, Tier.DETAILED, Tier.COMPLETE, Tier.COMPREHENSIVE]
    assert result["score"] >= 20.0  # Minimal threshold
    assert result["score"] <= 100.0
    
    print(f"Test passed: Tool scored {result['score']:.1f} points and achieved {result['tier'].name} tier")

def test_sparse_tool():
    """Test a tool that should be SPARSE tier"""
    scorer = ToolInformationStandardsScorer()
    
    sparse_tool = {
        "biotoolsID": "sparse-tool",
        "name": "Sparse Tool",
        "description": "Basic tool",
        "homepage": "https://example.com"
    }
    
    result = scorer.score_tool(sparse_tool)
    
    # Should be SPARSE tier
    assert result["tier"] == Tier.SPARSE
    assert result["score"] < 40.0  # Adjusted threshold
    
    print(f"Sparse test passed: Tool scored {result['score']:.1f} points and achieved {result['tier'].name} tier")

if __name__ == "__main__":
    test_standards_scorer()
    test_sparse_tool()
    print("All tests passed!")

if __name__ == "__main__":
    test_standards_scorer()
    test_sparse_tool()
    print("All tests passed!")
