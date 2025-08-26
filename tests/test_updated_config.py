#!/usr/bin/env python3
"""
Test script to validate the updated scoring configuration.
"""

from src.scoring.completeness_scorer import CompletenessScorer
from src.scoring.tier_classifier import TierClassifier

def test_updated_config():
    """Test the updated scoring configuration with sample tools."""
    
    # Initialize with updated config
    scorer = CompletenessScorer('config/scoring_config.yaml')
    classifier = TierClassifier()  # TierClassifier uses default tiers
    
    # Test cases representing different tier levels
    test_tools = [
        {
            'name': 'Minimal Tool',
            'description': 'Basic tool description',
            'homepage': 'https://example.com',
            'biotoolsID': 'minimal-tool',
            'expected_tier': 'tier_1'
        },
        {
            'name': 'nf-CBRA-snvs',
            'description': 'Workflow optimized for the analysis of rare diseases, designed to detect SNVs and INDELs in targeted sequencing data (CES/WES) and whole genome sequencing (WGS), built on Nextflow.',
            'homepage': 'https://github.com/CIBERER/nf-CBRA-snvs',
            'biotoolsID': 'nf-cbra-snvs',
            'toolType': ['Workflow'],
            'topic': [],  # Empty but present
            'operatingSystem': ['Linux'],
            'license': 'MIT',
            'maturity': 'Emerging',
            'cost': 'Free of charge',
            'accessibility': 'Open access',
            'publication': [],
            'credit': [],
            'link': [],
            'download': [],
            'documentation': [],
            'expected_tier': 'tier_1_or_2'
        }
    ]
    
    print("Testing Updated Scoring Configuration")
    print("=" * 50)
    
    for i, tool in enumerate(test_tools, 1):
        print(f"\nTest {i}: {tool['name']}")
        print("-" * 30)
        
        # Remove expected_tier from tool data for scoring
        expected = tool.pop('expected_tier', 'unknown')
        
        try:
            result = scorer.score_tool(tool)
            score = result['total_score'] 
            tier = result['tier']
            
            print(f"Score: {score:.2f}%")
            print(f"Assigned Tier: {tier}")
            print(f"Expected: {expected}")
            
            # Show score breakdown
            print("Score breakdown:")
            for category, cat_score in result['scores'].items():
                print(f"  {category}: {cat_score:.2f}")
            
            # Count available fields
            available_fields = []
            for field, value in tool.items():
                if value:
                    if isinstance(value, list):
                        if len(value) > 0:
                            available_fields.append(field)
                    else:
                        available_fields.append(field)
            
            field_list = ', '.join(available_fields)
            print(f"Available fields ({len(available_fields)}): {field_list}")
            
        except Exception as e:
            print(f"Error scoring tool: {e}")
            import traceback
            traceback.print_exc()
    
    # Display tier requirements
    print(f"\n\nTier Requirements Summary")
    print("=" * 50)
    
    # Load config directly to access tier requirements
    import yaml
    with open('config/scoring_config.yaml', 'r') as f:
        full_config = yaml.safe_load(f)
    
    scoring_config = full_config['scoring']
    for tier_name, requirements in scoring_config['tier_requirements'].items():
        description = scoring_config['tier_descriptions'].get(tier_name, '')
        print(f"\n{tier_name.upper()}: {len(requirements)} fields required")
        print(f"Description: {description}")
        print(f"Fields: {', '.join(requirements)}")

if __name__ == "__main__":
    test_updated_config()
