#!/usr/bin/env python3
"""
Test script for the new Tool Information Standards completeness scorer.

This script tests the completeness scorer on cached bio.tools data to verify
it correctly identifies the fields shown in the Tool Information Standards diagram.
"""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.validators.completeness_scorer import ToolCompletenessScorer


def test_completeness_scorer():
    """Test the completeness scorer on a sample tool."""
    
    # Initialize the scorer
    scorer = ToolCompletenessScorer()
    
    # Load a sample tool from cache
    cache_dir = Path("data/cache")
    sample_files = list(cache_dir.glob("*.json"))[:3]  # Test first 3 files
    
    print("="*80)
    print("TOOL INFORMATION STANDARDS COMPLETENESS TEST")
    print("="*80)
    print()
    
    for file_path in sample_files:
        print(f"Testing file: {file_path.name}")
        print("-" * 60)
        
        try:
            # Load tool data
            with open(file_path, 'r', encoding='utf-8') as f:
                tool_data = json.load(f)
            
            # Score the tool
            result = scorer.score_tool(tool_data)
            
            # Display results
            print(f"Tool ID: {tool_data.get('biotoolsID', 'unknown')}")
            print(f"Tool Name: {tool_data.get('name', 'Unknown')}")
            print(f"Achieved Tier: {result['achieved_tier_name']}")
            print(f"Completeness Score: {result['completeness_score']:.1f}%")
            print()
            
            # Show tier breakdown
            print("Tier Achievement:")
            for tier_name, tier_result in result['tier_results'].items():
                status = "✅ PASSED" if tier_result['satisfied'] else "❌ FAILED"
                print(f"  {tier_name}: {status}")
                if not tier_result['satisfied'] and tier_result['missing_fields']:
                    print(f"    Missing: {', '.join(tier_result['missing_fields'])}")
            print()
            
            # Show field analysis for key fields
            print("Key Fields Analysis:")
            key_fields = ['name', 'description', 'homepage', 'biotoolsID', 'toolType', 'topic', 
                         'publication', 'support', 'function', 'documentation', 'license']
            
            for field in key_fields:
                field_data = result['field_analysis'].get(field, {})
                status = "✅" if field_data.get('present', False) else "❌"
                quality = field_data.get('quality', 'unknown')
                print(f"  {field}: {status} ({quality})")
                if field_data.get('issues'):
                    for issue in field_data['issues']:
                        print(f"    ⚠️  {issue}")
            print()
            
            # Show recommendations
            if result['recommendations']:
                print("Recommendations:")
                for rec in result['recommendations']:
                    print(f"  💡 {rec}")
            print()
            
        except Exception as e:
            print(f"Error testing {file_path}: {e}")
        
        print("=" * 60)
        print()


def test_specific_fields():
    """Test specific field detection logic."""
    
    print("TESTING SPECIFIC FIELD DETECTION LOGIC")
    print("=" * 50)
    
    scorer = ToolCompletenessScorer()
    
    # Test with BLAST tool data from cache
    blast_file = Path("data/cache/tool_BLAST__-1179062606671494878.json")
    if blast_file.exists():
        with open(blast_file, 'r', encoding='utf-8') as f:
            blast_data = json.load(f)
        
        print(f"Testing BLAST tool fields:")
        print("-" * 30)
        
        # Test individual field checkers
        field_checkers = [
            ('name', scorer._check_name),
            ('description', scorer._check_description),
            ('homepage', scorer._check_homepage),
            ('biotoolsID', scorer._check_biotools_id),
            ('toolType', scorer._check_tool_type),
            ('topic', scorer._check_scientific_topics),
            ('publication', scorer._check_publications),
            ('support', scorer._check_support),
            ('function', scorer._check_scientific_operations),
            ('documentation', scorer._check_documentation),
            ('operatingSystem', scorer._check_operating_system),
            ('language', scorer._check_language),
            ('license', scorer._check_license),
            ('input_output', scorer._check_input_output_data),
            ('accessibility', scorer._check_accessibility),
            ('code_availability', scorer._check_code_availability),
            ('downloads', scorer._check_downloads),
            ('supported_data_formats', scorer._check_supported_data_formats)
        ]
        
        for field_name, checker_func in field_checkers:
            try:
                result = checker_func(blast_data)
                status = "✅" if result['present'] else "❌"
                quality = result.get('quality', 'unknown')
                value_info = ""
                
                if 'count' in result:
                    value_info = f" (count: {result['count']})"
                elif 'types_found' in result:
                    value_info = f" (types: {len(result['types_found'])})"
                    
                print(f"{field_name}: {status} {quality}{value_info}")
                
                if result.get('issues'):
                    for issue in result['issues']:
                        print(f"  ⚠️  {issue}")
                        
            except Exception as e:
                print(f"{field_name}: ❌ Error - {e}")
        
        print()


if __name__ == "__main__":
    test_completeness_scorer()
    test_specific_fields()
