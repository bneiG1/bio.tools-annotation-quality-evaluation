#!/usr/bin/env python3
"""
Test code availability type checking functionality.
"""

from src.scoring.group_based_scorer import GroupBasedScorer
import json

def main():
    print("=== Code Availability Type Checking Test ===\n")
    
    # Load scorer
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    # Load real data to check existing patterns
    with open('config/Untitled-1.json', 'r') as f:
        data = json.load(f)
    
    print("Checking real tools for code availability patterns:\n")
    
    # Check first few tools for code availability examples
    tools_with_links = []
    tools_with_downloads = []
    
    for i, tool in enumerate(data['list'][:20]):
        if 'link' in tool and tool['link']:
            repo_links = []
            for link in tool['link']:
                if 'type' in link and 'Repository' in link.get('type', []):
                    repo_links.append(link)
            if repo_links:
                tools_with_links.append((tool['name'], repo_links))
        
        if 'download' in tool and tool['download']:
            source_downloads = []
            for download in tool['download']:
                download_type = download.get('type', '')
                if 'Source code' in download_type or 'Software package' in download_type:
                    source_downloads.append(download)
            if source_downloads:
                tools_with_downloads.append((tool['name'], source_downloads))
    
    print(f"Found {len(tools_with_links)} tools with Repository links")
    for name, links in tools_with_links[:3]:
        print(f"  {name}: {[link['type'] for link in links]}")
    
    print(f"\nFound {len(tools_with_downloads)} tools with Source/Package downloads")
    for name, downloads in tools_with_downloads[:3]:
        print(f"  {name}: {[download['type'] for download in downloads]}")
    
    print("\n=== Testing Code Availability Group ===\n")
    
    # Test with synthetic data representing all three types
    test_cases = [
        {
            "name": "Tool with Repository link",
            "link": [
                {"url": "https://github.com/example/tool", "type": ["Repository"]}
            ]
        },
        {
            "name": "Tool with Source code download",
            "download": [
                {"url": "https://example.com/source.zip", "type": "Source code"}
            ]
        },
        {
            "name": "Tool with Software package download", 
            "download": [
                {"url": "https://example.com/package.zip", "type": "Software package"}
            ]
        },
        {
            "name": "Tool with multiple code availability options",
            "link": [
                {"url": "https://github.com/example/tool", "type": ["Repository"]}
            ],
            "download": [
                {"url": "https://example.com/source.zip", "type": "Source code"},
                {"url": "https://example.com/package.zip", "type": "Software package"}
            ]
        },
        {
            "name": "Tool with unsupported download type",
            "download": [
                {"url": "https://example.com/data.zip", "type": "Biological data"}
            ]
        },
        {
            "name": "Tool with link but wrong type",
            "link": [
                {"url": "https://example.com/docs", "type": ["Documentation"]}
            ]
        }
    ]
    
    # Get the code availability group configuration
    code_group_config = scorer.config['field_groups']['code_availability_group']
    print(f"Code availability types required: {code_group_config.get('types_required', [])}")
    print()
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        is_satisfied, details = scorer.evaluate_field_group(test_case, 'code_availability_group', code_group_config)
        
        print(f"  Satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"  Type matches: {details['type_matches']}")
        if details.get('present_fields'):
            print(f"  Present fields: {details['present_fields']}")
        
        # Debug: Show what was checked
        if details.get('checked_content'):
            print(f"  Checked content: {details['checked_content']}")
        print()
    
    # Test with real tool that should have code availability
    if tools_with_downloads:
        real_tool_name, _ = tools_with_downloads[0]
        real_tool = next(tool for tool in data['list'] if tool.get('name') == real_tool_name)
        
        print(f"=== Testing Real Tool with Downloads: {real_tool_name} ===")
        print(f"Links: {real_tool.get('link', [])}")
        print(f"Downloads: {real_tool.get('download', [])}")
        
        is_satisfied, details = scorer.evaluate_field_group(real_tool, 'code_availability_group', code_group_config)
        print(f"Code availability satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"Type matches: {details['type_matches']}")
        print()
    
    if tools_with_links:
        real_tool_name, _ = tools_with_links[0]
        real_tool = next(tool for tool in data['list'] if tool.get('name') == real_tool_name)
        
        print(f"=== Testing Real Tool with Links: {real_tool_name} ===")
        print(f"Links: {real_tool.get('link', [])}")
        print(f"Downloads: {real_tool.get('download', [])}")
        
        is_satisfied, details = scorer.evaluate_field_group(real_tool, 'code_availability_group', code_group_config)
        print(f"Code availability satisfied: {'✓' if is_satisfied else '✗'}")
        if details.get('type_matches'):
            print(f"Type matches: {details['type_matches']}")
        print()

if __name__ == "__main__":
    main()
