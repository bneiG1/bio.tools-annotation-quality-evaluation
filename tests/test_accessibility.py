#!/usr/bin/env python3
"""
Test accessibility type checking functionality.
"""

from src.scoring.group_based_scorer import GroupBasedScorer
import json

def main():
    print("=== Accessibility Type Checking Test ===\n")
    
    # Load scorer
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    # Load real data to check existing patterns
    with open('config/Untitled-1.json', 'r') as f:
        data = json.load(f)
    
    print("Checking real tools for accessibility patterns:\n")
    
    # Check for accessibility, cost, and terms of use patterns
    tools_with_accessibility = []
    tools_with_cost = []
    tools_with_terms_docs = []
    
    for i, tool in enumerate(data['list'][:50]):
        # Check accessibility field
        if 'accessibility' in tool and tool['accessibility']:
            tools_with_accessibility.append((tool.get('name', f'Tool_{i}'), tool['accessibility']))
        
        # Check cost field
        if 'cost' in tool and tool['cost']:
            tools_with_cost.append((tool.get('name', f'Tool_{i}'), tool['cost']))
        
        # Check for Terms of use in documentation
        if 'documentation' in tool and tool['documentation']:
            for doc in tool['documentation']:
                if 'type' in doc and isinstance(doc['type'], list):
                    if 'Terms of use' in doc['type']:
                        tools_with_terms_docs.append((tool.get('name', f'Tool_{i}'), doc))
                elif 'type' in doc and doc['type'] == 'Terms of use':
                    tools_with_terms_docs.append((tool.get('name', f'Tool_{i}'), doc))
    
    print(f"Found {len(tools_with_accessibility)} tools with accessibility field")
    for name, accessibility in tools_with_accessibility[:3]:
        print(f"  {name}: {accessibility}")
    
    print(f"\nFound {len(tools_with_cost)} tools with cost field")  
    for name, cost in tools_with_cost[:3]:
        print(f"  {name}: {cost}")
    
    print(f"\nFound {len(tools_with_terms_docs)} tools with Terms of use documentation")
    for name, doc in tools_with_terms_docs[:3]:
        print(f"  {name}: {doc.get('type', 'No type')}")
    
    print("\n=== Testing Accessibility Group ===\n")
    
    # Test with synthetic data representing all types
    test_cases = [
        {
            "name": "Tool with accessibility field",
            "accessibility": "Open access"
        },
        {
            "name": "Tool with cost information",
            "cost": "Free of charge"
        },
        {
            "name": "Tool with Terms of use documentation",
            "documentation": [
                {"url": "https://example.com/terms", "type": ["Terms of use"]}
            ]
        },
        {
            "name": "Tool with multiple accessibility options",
            "accessibility": "Open access",
            "cost": "Free of charge",
            "documentation": [
                {"url": "https://example.com/terms", "type": ["Terms of use"]}
            ]
        },
        {
            "name": "Tool with documentation but wrong type",
            "documentation": [
                {"url": "https://example.com/manual", "type": ["User manual"]}
            ]
        },
        {
            "name": "Tool with no accessibility information"
        }
    ]
    
    # Get the accessibility group configuration
    accessibility_group_config = scorer.config['field_groups']['accessibility_group']
    print(f"Accessibility types required: {accessibility_group_config.get('types_required', [])}")
    print(f"Accessibility fields: {accessibility_group_config.get('fields', [])}")
    print()
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        is_satisfied, details = scorer.evaluate_field_group(test_case, 'accessibility_group', accessibility_group_config)
        
        print(f"  Satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"  Type matches: {details['type_matches']}")
        if details.get('present_fields'):
            print(f"  Present fields: {details['present_fields']}")
        if details.get('checked_content'):
            print(f"  Checked content: {details['checked_content']}")
        print()
    
    # Test with real tool that has Terms of use documentation
    if tools_with_terms_docs:
        real_tool_name, _ = tools_with_terms_docs[0]
        real_tool = next(tool for tool in data['list'] if tool.get('name') == real_tool_name)
        
        print(f"=== Testing Real Tool with Terms of Use: {real_tool_name} ===")
        print(f"Accessibility: {real_tool.get('accessibility', 'None')}")
        print(f"Cost: {real_tool.get('cost', 'None')}")
        print(f"Documentation: {real_tool.get('documentation', [])}")
        
        is_satisfied, details = scorer.evaluate_field_group(real_tool, 'accessibility_group', accessibility_group_config)
        print(f"Accessibility group satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"Type matches: {details['type_matches']}")
        if details.get('present_fields'):
            print(f"Present fields: {details['present_fields']}")
        print()
    
    # Also test with a tool that has cost information
    if tools_with_cost:
        real_tool_name, _ = tools_with_cost[0]
        real_tool = next(tool for tool in data['list'] if tool.get('name') == real_tool_name)
        
        print(f"=== Testing Real Tool with Cost: {real_tool_name} ===")
        print(f"Accessibility: {real_tool.get('accessibility', 'None')}")
        print(f"Cost: {real_tool.get('cost', 'None')}")
        print(f"Documentation: {real_tool.get('documentation', [])}")
        
        is_satisfied, details = scorer.evaluate_field_group(real_tool, 'accessibility_group', accessibility_group_config)
        print(f"Accessibility group satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"Type matches: {details['type_matches']}")
        if details.get('present_fields'):
            print(f"Present fields: {details['present_fields']}"))

if __name__ == "__main__":
    main()
