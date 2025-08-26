#!/usr/bin/env python3
"""
Simple test for documentation type checking.
"""

from src.scoring.group_based_scorer import GroupBasedScorer
import json

def main():
    # Load scorer and data
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    with open('config/Untitled-1.json', 'r') as f:
        data = json.load(f)
    
    # Test with first tool that has documentation
    tool = data['list'][0]  # nf-CBRA-snvs
    print(f'Testing: {tool["name"]}')
    print(f'Documentation: {tool["documentation"]}')
    
    # Test documentation group specifically
    config = scorer.config
    print(f"Config keys: {list(config.keys())}")
    
    # Access the field_groups correctly
    doc_group_config = config['field_groups']['documentation_group']
    is_satisfied, details = scorer.evaluate_field_group(tool, 'documentation_group', doc_group_config)
    
    print(f'Documentation group satisfied: {is_satisfied}')
    print(f'Type matches: {details.get("type_matches", [])}')
    print(f'Types required: {details.get("types_required", [])}')
    
    # Test with synthetic data
    print('\n--- Testing synthetic data ---')
    
    synthetic_tool = {
        "name": "Test Tool",
        "documentation": [
            {
                "url": "https://example.com/api",
                "type": ["API documentation"],
                "note": "API docs"
            }
        ]
    }
    
    print(f'Testing: {synthetic_tool["name"]}')
    print(f'Documentation: {synthetic_tool["documentation"]}')
    
    is_satisfied2, details2 = scorer.evaluate_field_group(synthetic_tool, 'documentation_group', doc_group_config)
    
    print(f'Documentation group satisfied: {is_satisfied2}')
    print(f'Type matches: {details2.get("type_matches", [])}')
    print(f'Types required: {details2.get("types_required", [])}')

if __name__ == "__main__":
    main()
