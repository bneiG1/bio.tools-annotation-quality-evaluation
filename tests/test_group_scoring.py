#!/usr/bin/env python3
"""
Test script to validate the updated group-based scoring configuration.
"""

import yaml
import json
from pathlib import Path


def load_config():
    """Load the updated scoring configuration."""
    config_path = Path('config/scoring_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def evaluate_field_group(tool_data, group_name, group_config, field_mappings):
    """
    Evaluate if a field group requirement is met (at least one field present).
    
    Args:
        tool_data: Tool data dictionary
        group_name: Name of the group to evaluate
        group_config: Group configuration
        field_mappings: Field mapping configuration
        
    Returns:
        Tuple of (is_satisfied, details)
    """
    fields = group_config.get('fields', [])
    mapping = field_mappings.get(group_name, {})
    primary_fields = mapping.get('primary_fields', fields)
    secondary_fields = mapping.get('secondary_fields', [])
    all_fields = primary_fields + secondary_fields
    
    satisfied = False
    present_fields = []
    checked_content = {}
    
    for field in all_fields:
        if field in tool_data:
            value = tool_data[field]
            checked_content[field] = value
            
            # Check if field has meaningful content
            if value is not None and value != "":
                if isinstance(value, list):
                    if len(value) > 0:
                        satisfied = True
                        present_fields.append(field)
                elif isinstance(value, str):
                    if value.strip():  # Non-empty string
                        satisfied = True
                        present_fields.append(field)
                elif isinstance(value, dict):
                    if value:  # Non-empty dict
                        satisfied = True
                        present_fields.append(field)
                else:
                    # Other truthy values
                    satisfied = True
                    present_fields.append(field)
    
    return satisfied, {
        'present_fields': present_fields,
        'checked_fields': all_fields,
        'checked_content': checked_content,
        'group_weight': group_config.get('weight', 0),
        'description': group_config.get('description', '')
    }


def test_group_based_scoring():
    """Test the group-based scoring system."""
    
    print("Testing Group-Based Scoring System")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    scoring_config = config['scoring']
    
    # Load sample tools from the JSON file
    with open('config/Untitled-1.json', 'r') as f:
        api_data = json.load(f)
    
    # Test with first few tools and add a minimal test case
    sample_tools = api_data['list'][:2]  # Use first 2 from API
    
    # Add a minimal tool for testing
    minimal_tool = {
        "name": "MinimalTool",
        "description": "Basic tool with minimal metadata",
        "homepage": "https://example.com/minimal", 
        "biotoolsID": "minimal-tool",
        "toolType": ["Command-line tool"],
        "topic": [],
        "publication": [],
        "credit": [],
        "link": [],
        "download": [],
        "documentation": [],
        "function": [],
        "operatingSystem": [],
        "language": [],
        "license": None,
        "accessibility": None,
        "cost": None,
        "maturity": None,
        "version": []
    }
    
    sample_tools.append(minimal_tool)
    
    print(f"\nField Groups Configuration:")
    print("-" * 30)
    for group_name, group_config in scoring_config['field_groups'].items():
        print(f"\n{group_name}:")
        print(f"  Weight: {group_config['weight']}")
        print(f"  Fields: {group_config['fields']}")
        print(f"  Description: {group_config['description']}")
    
    print(f"\n\nTool Evaluation Results:")
    print("=" * 50)
    
    for i, tool in enumerate(sample_tools, 1):
        tool_name = tool.get('name', f'Tool {i}')
        print(f"\n{i}. {tool_name}")
        print("-" * 50)
        
        total_group_score = 0
        max_group_score = 0
        
        # Evaluate each field group
        for group_name, group_config in scoring_config['field_groups'].items():
            is_satisfied, details = evaluate_field_group(
                tool, group_name, group_config, 
                scoring_config.get('field_mappings', {})
            )
            
            group_weight = group_config['weight']
            max_group_score += group_weight
            
            if is_satisfied:
                total_group_score += group_weight
                status = "✅ SATISFIED"
            else:
                status = "❌ NOT SATISFIED"
            
            print(f"  {group_name}: {status}")
            print(f"    Weight: {group_weight} points")
            print(f"    Present fields: {details['present_fields']}")
            if details['present_fields']:
                for field in details['present_fields']:
                    content = details['checked_content'].get(field, 'N/A')
                    if isinstance(content, list):
                        print(f"      {field}: {len(content)} items")
                    elif isinstance(content, str):
                        print(f"      {field}: '{content[:50]}{'...' if len(str(content)) > 50 else ''}'")
                    else:
                        print(f"      {field}: {content}")
            print()
        
        # Calculate individual field scores for non-grouped fields
        individual_fields = ['name', 'description', 'homepage', 'biotoolsID', 
                           'toolType', 'topic', 'publication', 'function',
                           'operatingSystem', 'language', 'license', 
                           'version', 'maturity']
        
        individual_score = 0
        max_individual_score = 0
        
        for field in individual_fields:
            field_weight = scoring_config['field_weights'].get(field, 0)
            max_individual_score += field_weight
            
            if field in tool and tool[field] and tool[field] not in ["", [], None]:
                if isinstance(tool[field], list):
                    if len(tool[field]) > 0:
                        individual_score += field_weight
                else:
                    individual_score += field_weight
        
        total_score = total_group_score + individual_score
        max_total_score = max_group_score + max_individual_score
        
        percentage = (total_score / max_total_score * 100) if max_total_score > 0 else 0
        
        print(f"\n  Scoring Summary:")
        print(f"    Group score: {total_group_score}/{max_group_score}")
        print(f"    Individual score: {individual_score}/{max_individual_score}")
        print(f"    Total score: {total_score}/{max_total_score} ({percentage:.1f}%)")
        
        # Determine tier
        tiers = scoring_config['tiers']
        assigned_tier = 'tier_1'
        for tier, (min_score, max_score) in tiers.items():
            if min_score <= percentage <= max_score:
                assigned_tier = tier
                break
        
        tier_desc = scoring_config['tier_descriptions'].get(assigned_tier, '')
        print(f"    Assigned tier: {assigned_tier.upper()}")
        print(f"    Tier description: {tier_desc}")


if __name__ == "__main__":
    test_group_based_scoring()
