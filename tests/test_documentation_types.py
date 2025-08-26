#!/usr/bin/env python3
"""
Test the type-specific documentation group checking.
"""

import json
from pathlib import Path
from src.scoring.group_based_scorer import GroupBasedScorer


def test_documentation_types():
    """Test documentation type-specific checking."""
    
    print("Testing Documentation Type-Specific Checking")
    print("=" * 60)
    
    # Initialize scorer
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    # Load sample data
    with open('config/Untitled-1.json', 'r') as f:
        api_data = json.load(f)
    
    # Find tools with documentation to test
    tools_with_docs = []
    for tool in api_data['list']:
        if 'documentation' in tool and tool['documentation']:
            tools_with_docs.append(tool)
        if len(tools_with_docs) >= 3:  # Get first 3 tools with documentation
            break
    
    # Add test cases with different documentation types
    test_cases = [
        {
            "name": "Tool with General Documentation",
            "description": "Test tool with general documentation",
            "homepage": "https://example.com",
            "biotoolsID": "test-general-docs",
            "documentation": [
                {
                    "url": "https://example.com/docs",
                    "type": ["General"],
                    "note": "General documentation"
                }
            ]
        },
        {
            "name": "Tool with User Manual", 
            "description": "Test tool with user manual",
            "homepage": "https://example.com",
            "biotoolsID": "test-user-manual",
            "documentation": [
                {
                    "url": "https://example.com/manual",
                    "type": ["User manual"],
                    "note": "User manual"
                }
            ]
        },
        {
            "name": "Tool with API Documentation",
            "description": "Test tool with API documentation", 
            "homepage": "https://example.com",
            "biotoolsID": "test-api-docs",
            "documentation": [
                {
                    "url": "https://example.com/api",
                    "type": ["API documentation"],
                    "note": "API documentation"
                }
            ]
        },
        {
            "name": "Tool with API Specification",
            "description": "Test tool with API specification",
            "homepage": "https://example.com", 
            "biotoolsID": "test-api-spec",
            "documentation": [
                {
                    "url": "https://example.com/spec",
                    "type": ["API specification"],
                    "note": "API specification"
                }
            ]
        },
        {
            "name": "Tool with Other Documentation Type",
            "description": "Test tool with non-matching documentation type",
            "homepage": "https://example.com",
            "biotoolsID": "test-other-docs", 
            "documentation": [
                {
                    "url": "https://example.com/other",
                    "type": ["Tutorial"],
                    "note": "Tutorial documentation"
                }
            ]
        },
        {
            "name": "Tool with Multiple Documentation Types",
            "description": "Test tool with multiple documentation types",
            "homepage": "https://example.com",
            "biotoolsID": "test-multi-docs",
            "documentation": [
                {
                    "url": "https://example.com/manual",
                    "type": ["User manual"],
                    "note": "User manual"
                },
                {
                    "url": "https://example.com/api",
                    "type": ["API documentation"],
                    "note": "API documentation"  
                }
            ]
        }
    ]
    
    # Test with real tools first
    print("\nReal Tools from bio.tools:")
    print("-" * 40)
    
    for i, tool in enumerate(tools_with_docs, 1):
        tool_name = tool.get('name', f'Tool {i}')
        print(f"\n{i}. {tool_name}")
        print(f"Documentation entries: {len(tool.get('documentation', []))}")
        
        # Show documentation details
        for j, doc in enumerate(tool.get('documentation', []), 1):
            doc_type = doc.get('type', ['Unknown'])
            doc_url = doc.get('url', 'No URL')
            print(f"   Doc {j}: Type: {doc_type}, URL: {doc_url[:50]}...")
        
        # Test documentation group evaluation
        result = scorer.score_with_groups(tool)
        group_eval = result.get('group_evaluation', {})
        doc_group = group_eval.get('groups', {}).get('documentation_group', {})
        
        status = "✅" if doc_group.get('satisfied', False) else "❌"
        print(f"   Documentation Group: {status}")
        
        if doc_group.get('type_matches'):
            print(f"   Type matches: {doc_group['type_matches']}")
    
    # Test with synthetic test cases
    print(f"\n\nSynthetic Test Cases:")
    print("-" * 40)
    
    for i, tool in enumerate(test_cases, 1):
        print(f"\n{i}. {tool['name']}")
        
        # Show documentation details
        for j, doc in enumerate(tool.get('documentation', []), 1):
            doc_type = doc.get('type', ['Unknown'])
            print(f"   Doc {j}: Type: {doc_type}")
        
        # Test documentation group evaluation
        result = scorer.score_with_groups(tool)
        group_eval = result.get('group_evaluation', {})
        doc_group = group_eval.get('groups', {}).get('documentation_group', {})
        
        status = "✅" if doc_group.get('satisfied', False) else "❌"
        print(f"   Documentation Group: {status}")
        
        if doc_group.get('type_matches'):
            print(f"   Type matches: {doc_group['type_matches']}")
        elif doc_group.get('types_required'):
            print(f"   Required types: {doc_group['types_required']}")
            print(f"   No matches found")


if __name__ == "__main__":
    test_documentation_types()
