#!/usr/bin/env python3
"""
Comprehensive test of the enhanced group-based scoring system.
"""

from src.scoring.group_based_scorer import GroupBasedScorer
import json

def main():
    print("=== Comprehensive Group-Based Scoring Test ===\n")
    
    # Load scorer and data
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    with open('config/Untitled-1.json', 'r') as f:
        data = json.load(f)
    
    # Test scoring on multiple tools
    print("Testing enhanced scoring on sample tools:\n")
    
    for i, tool in enumerate(data['list'][:5]):  # Test first 5 tools
        print(f"--- Tool {i+1}: {tool['name']} ---")
        
        # Get score details
        score_result = scorer.score_tool(tool)
        score = score_result.get('total_score', 0) if isinstance(score_result, dict) else score_result
        
        print(f"Score: {score:.1f}")
        
        if isinstance(score_result, dict):
            print(f"Details: {score_result.get('breakdown', {})}")
        
        # Show documentation details if present
        if 'documentation' in tool and tool['documentation']:
            doc_types = []
            for doc in tool['documentation']:
                if 'type' in doc:
                    doc_types.extend(doc['type'])
            print(f"Documentation types: {doc_types}")
        
        print()
    
    print("\n=== Field Group Evaluation Test ===\n")
    
    # Test specific field groups
    test_tool = data['list'][0]  # Use first tool
    print(f"Testing field groups on: {test_tool['name']}\n")
    
    field_groups = [
        'basic_info_group',
        'core_metadata_group', 
        'technical_info_group',
        'accessibility_group',
        'documentation_group',
        'community_group'
    ]
    
    for group_name in field_groups:
        if group_name in scorer.config['field_groups']:
            group_config = scorer.config['field_groups'][group_name]
            is_satisfied, details = scorer.evaluate_field_group(test_tool, group_name, group_config)
            
            print(f"{group_name}: {'✓' if is_satisfied else '✗'} ({details.get('satisfied_count', 0)}/{details.get('total_fields', 0)} satisfied)")
            
            if 'type_matches' in details and details['type_matches']:
                print(f"  Type matches: {details['type_matches']}")
            
    print("\n=== Testing Different Documentation Types ===\n")
    
    # Test with synthetic tools having different documentation types
    test_cases = [
        {
            "name": "Tool with General docs",
            "documentation": [{"url": "https://example.com", "type": ["General"]}]
        },
        {
            "name": "Tool with User manual",
            "documentation": [{"url": "https://example.com", "type": ["User manual"]}]
        },
        {
            "name": "Tool with API docs",
            "documentation": [{"url": "https://example.com", "type": ["API documentation"]}]
        },
        {
            "name": "Tool with API spec",
            "documentation": [{"url": "https://example.com", "type": ["API specification"]}]
        },
        {
            "name": "Tool with multiple types",
            "documentation": [
                {"url": "https://example.com/manual", "type": ["User manual"]},
                {"url": "https://example.com/api", "type": ["API documentation"]}
            ]
        },
        {
            "name": "Tool with unsupported type",
            "documentation": [{"url": "https://example.com", "type": ["Training material"]}]
        }
    ]
    
    doc_group_config = scorer.config['field_groups']['documentation_group']
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        is_satisfied, details = scorer.evaluate_field_group(test_case, 'documentation_group', doc_group_config)
        
        print(f"  Satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"  Matches: {details['type_matches']}")
        print()

if __name__ == "__main__":
    main()
