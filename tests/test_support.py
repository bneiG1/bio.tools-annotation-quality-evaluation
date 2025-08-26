#!/usr/bin/env python3
"""
Test support type checking functionality.
"""

from src.scoring.group_based_scorer import GroupBasedScorer
import json

def main():
    print("=== Support Type Checking Test ===\n")
    
    # Load scorer
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    # Load real data to check existing patterns
    with open('config/Untitled-1.json', 'r') as f:
        data = json.load(f)
    
    print("Checking real tools for support patterns:\n")
    
    # Check for different support patterns
    tools_with_support_links = []
    tools_with_primary_contacts = []
    
    for i, tool in enumerate(data['list'][:50]):
        # Check link types for support
        if 'link' in tool and tool['link']:
            support_links = []
            for link in tool['link']:
                if 'type' in link:
                    link_types = link['type'] if isinstance(link['type'], list) else [link['type']]
                    support_types = ['Helpdesk', 'Issue tracker', 'Mailing list']
                    for support_type in support_types:
                        if support_type in link_types:
                            support_links.append((support_type, link))
            if support_links:
                tools_with_support_links.append((tool.get('name', f'Tool_{i}'), support_links))
        
        # Check credit for primary contacts
        if 'credit' in tool and tool['credit']:
            primary_contacts = []
            for credit in tool['credit']:
                if 'typeRole' in credit:
                    type_roles = credit['typeRole'] if isinstance(credit['typeRole'], list) else [credit['typeRole']]
                    if 'Primary contact' in type_roles:
                        primary_contacts.append(credit)
            if primary_contacts:
                tools_with_primary_contacts.append((tool.get('name', f'Tool_{i}'), primary_contacts))
    
    print(f"Found {len(tools_with_support_links)} tools with support links")
    for name, support_links in tools_with_support_links[:3]:
        print(f"  {name}: {[(stype, link['type']) for stype, link in support_links]}")
    
    print(f"\nFound {len(tools_with_primary_contacts)} tools with primary contacts")  
    for name, contacts in tools_with_primary_contacts[:3]:
        print(f"  {name}: {[contact.get('typeRole', 'No role') for contact in contacts]}")
    
    print("\n=== Testing Support Group ===\n")
    
    # Test with synthetic data representing all support types
    test_cases = [
        {
            "name": "Tool with Helpdesk link",
            "link": [
                {"url": "https://example.com/help", "type": ["Helpdesk"]}
            ]
        },
        {
            "name": "Tool with Issue tracker link",
            "link": [
                {"url": "https://github.com/example/issues", "type": ["Issue tracker"]}
            ]
        },
        {
            "name": "Tool with Mailing list link",
            "link": [
                {"url": "mailto:help@example.com", "type": ["Mailing list"]}
            ]
        },
        {
            "name": "Tool with Primary contact credit",
            "credit": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "typeRole": ["Primary contact"]
                }
            ]
        },
        {
            "name": "Tool with multiple support options",
            "link": [
                {"url": "https://github.com/example/issues", "type": ["Issue tracker"]}
            ],
            "credit": [
                {
                    "name": "John Doe", 
                    "email": "john@example.com",
                    "typeRole": ["Primary contact", "Developer"]
                }
            ]
        },
        {
            "name": "Tool with unsupported link type",
            "link": [
                {"url": "https://example.com/docs", "type": ["Documentation"]}
            ]
        },
        {
            "name": "Tool with credit but wrong role",
            "credit": [
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com", 
                    "typeRole": ["Developer"]
                }
            ]
        }
    ]
    
    # Get the support group configuration
    support_group_config = scorer.config['field_groups']['support_group']
    print(f"Support types required: {support_group_config.get('types_required', [])}")
    print(f"Support fields: {support_group_config.get('fields', [])}")
    print()
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        is_satisfied, details = scorer.evaluate_field_group(test_case, 'support_group', support_group_config)
        
        print(f"  Satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"  Type matches: {details['type_matches']}")
        if details.get('present_fields'):
            print(f"  Present fields: {details['present_fields']}")
        print()
    
    # Test with real tools
    if tools_with_support_links:
        real_tool_name, _ = tools_with_support_links[0]
        real_tool = next(tool for tool in data['list'] if tool.get('name') == real_tool_name)
        
        print(f"=== Testing Real Tool with Support Links: {real_tool_name} ===")
        print(f"Links: {[link.get('type') for link in real_tool.get('link', [])]}")
        print(f"Credits: {[credit.get('typeRole') for credit in real_tool.get('credit', [])]}")
        
        is_satisfied, details = scorer.evaluate_field_group(real_tool, 'support_group', support_group_config)
        print(f"Support group satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"Type matches: {details['type_matches']}")
        print()
    
    if tools_with_primary_contacts:
        real_tool_name, _ = tools_with_primary_contacts[0]
        real_tool = next(tool for tool in data['list'] if tool.get('name') == real_tool_name)
        
        print(f"=== Testing Real Tool with Primary Contact: {real_tool_name} ===")
        print(f"Links: {[link.get('type') for link in real_tool.get('link', [])]}")
        print(f"Credits: {[credit.get('typeRole') for credit in real_tool.get('credit', [])]}")
        
        is_satisfied, details = scorer.evaluate_field_group(real_tool, 'support_group', support_group_config)
        print(f"Support group satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"Type matches: {details['type_matches']}")

if __name__ == "__main__":
    main()
