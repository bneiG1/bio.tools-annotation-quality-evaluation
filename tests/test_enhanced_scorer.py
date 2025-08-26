#!/usr/bin/env python3
"""
Test the enhanced group-based scorer with real bio.tools data.
"""

import json
from pathlib import Path
from src.scoring.group_based_scorer import GroupBasedScorer


def test_enhanced_scorer():
    """Test the enhanced group-based scorer."""
    
    print("Testing Enhanced Group-Based Scorer")
    print("=" * 50)
    
    # Initialize scorer
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    # Load sample data
    with open('config/Untitled-1.json', 'r') as f:
        api_data = json.load(f)
    
    # Test with a few representative tools
    test_tools = [
        api_data['list'][0],  # nf-CBRA-snvs - well annotated
        api_data['list'][4],  # MacSyLib - different profile  
        {   # Minimal tool for comparison
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
    ]
    
    for i, tool in enumerate(test_tools, 1):
        tool_name = tool.get('name', f'Tool {i}')
        print(f"\n{i}. Testing: {tool_name}")
        print("-" * 60)
        
        # Score with groups
        result = scorer.score_with_groups(tool)
        
        print(f"Base Score: {result['total_score']:.1f}%")
        print(f"Tier: {result['tier']}")
        
        # Show group evaluation
        group_eval = result.get('group_evaluation', {})
        print(f"\nGroup Evaluation:")
        print(f"  Group Score: {group_eval.get('total_group_score', 0)}/{group_eval.get('max_group_score', 0)} ({group_eval.get('group_percentage', 0):.1f}%)")
        
        if 'combined_score' in result:
            print(f"  Combined Score: {result['combined_score']:.1f}%")
        
        # Show individual group results
        groups = group_eval.get('groups', {})
        for group_name, group_details in groups.items():
            status = "✅" if group_details['satisfied'] else "❌"
            print(f"  {group_name}: {status}")
            if group_details['present_fields']:
                print(f"    Present: {', '.join(group_details['present_fields'])}")
        
        # Test tier requirements
        print(f"\nTier Requirements Check:")
        for tier_num in range(1, 6):
            tier_name = f'tier_{tier_num}'
            meets_req, req_details = scorer.check_tier_requirements(tool, tier_name)
            status = "✅" if meets_req else "❌"
            met_count = len(req_details['met_requirements'])
            total_count = req_details['total_requirements']
            print(f"  {tier_name.upper()}: {status} ({met_count}/{total_count} requirements)")
            
            if not meets_req and tier_num <= 3:  # Show missing for lower tiers
                missing = req_details['missing_requirements']
                if missing:
                    print(f"    Missing: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}")


if __name__ == "__main__":
    test_enhanced_scorer()
