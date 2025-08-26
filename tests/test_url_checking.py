#!/usr/bin/env python3
"""
Test script for URL accessibility checking functionality.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from validation.url_checker import URLChecker
from scoring.completeness_scorer import CompletenessScorer

def test_url_checker():
    """Test the URL checker with sample URLs."""
    print("Testing URL Checker...")
    print("=" * 50)
    
    checker = URLChecker(timeout=5, delay_between_requests=0.2)
    
    # Test URLs
    test_urls = [
        "https://github.com",
        "https://google.com", 
        "https://nonexistent-site-12345.com",
        "http://httpbin.org/status/404",
        "https://bio.tools"
    ]
    
    print("Checking individual URLs:")
    for url in test_urls:
        result = checker.check_url(url)
        status = "✓" if result['is_accessible'] else "✗"
        print(f"{status} {url}: {result['status_code']} - {result.get('error_message', 'OK')}")
    
    print("\nChecking URLs in batch:")
    batch_results = checker.check_urls_batch(test_urls)
    accessible_count = sum(1 for r in batch_results.values() if r['is_accessible'])
    print(f"Batch results: {accessible_count}/{len(test_urls)} accessible")
    
    # Test with sample bio.tools data
    print("\nTesting with sample bio.tools data...")
    sample_tool = {
        'name': 'Sample Tool',
        'homepage': 'https://github.com',
        'link': [
            {'type': 'Repository', 'url': 'https://github.com/example/repo'},
            {'type': 'Issue tracker', 'url': 'https://github.com/example/repo/issues'}
        ],
        'documentation': [
            {'type': 'General', 'url': 'https://example.com/docs'}
        ]
    }
    
    tool_results = checker.check_tool_urls(sample_tool)
    print(f"Tool URL check summary:")
    print(f"- Total URLs found: {tool_results['summary']['total_urls']}")
    print(f"- Accessible URLs: {tool_results['summary']['accessible_urls']}")
    print(f"- Homepage accessible: {tool_results['summary']['homepage_accessible']}")
    print(f"- Accessibility rate: {tool_results['summary']['accessibility_rate']:.2%}")

def test_enhanced_scorer():
    """Test the enhanced completeness scorer with URL checking."""
    print("\n\nTesting Enhanced Scorer...")
    print("=" * 50)
    
    # Load sample tool data
    data_file = Path('data/biotools/all/aa-score.json')
    if data_file.exists():
        print(f"Loading sample data from {data_file}")
        with open(data_file, 'r') as f:
            sample_tool = json.load(f)
    else:
        print("Using synthetic sample data")
        sample_tool = {
            'name': 'Test Tool',
            'description': 'A test tool for demonstration',
            'homepage': 'https://github.com',
            'biotoolsID': 'test-tool',
            'toolType': ['Command-line tool'],
            'topic': [{'term': 'Bioinformatics'}],
            'link': [
                {'type': 'Repository', 'url': 'https://github.com/example/repo'}
            ]
        }
    
    # Test without URL checking
    print("\n1. Scoring WITHOUT URL checking:")
    scorer_basic = CompletenessScorer(enable_url_checking=False)
    result_basic = scorer_basic.score_tool(sample_tool)
    print(f"   Total Score: {result_basic['total_score']}")
    print(f"   Accessibility Score: {result_basic['scores']['accessibility']}")
    if 'accessibility' in result_basic['details']:
        acc_details = result_basic['details']['accessibility']
        print(f"   URL Checking: {'Enabled' if acc_details.get('url_checking_enabled', False) else 'Disabled'}")
    
    # Test with URL checking
    print("\n2. Scoring WITH URL checking:")
    scorer_enhanced = CompletenessScorer(enable_url_checking=True)
    result_enhanced = scorer_enhanced.score_tool(sample_tool)
    print(f"   Total Score: {result_enhanced['total_score']}")
    print(f"   Accessibility Score: {result_enhanced['scores']['accessibility']}")
    if 'accessibility' in result_enhanced['details']:
        acc_details = result_enhanced['details']['accessibility']
        print(f"   URL Checking: {'Enabled' if acc_details.get('url_checking_enabled', False) else 'Disabled'}")
        if acc_details.get('url_accessibility'):
            url_summary = acc_details['url_accessibility']['summary']
            print(f"   URLs Found: {url_summary['total_urls']}")
            print(f"   Accessible: {url_summary['accessible_urls']}")
            print(f"   Homepage OK: {url_summary['homepage_accessible']}")
            print(f"   URL Bonus: {acc_details.get('url_bonus', 0):.2f} points")
    
    # Compare scores
    score_diff = result_enhanced['total_score'] - result_basic['total_score']
    print(f"\n3. Score Comparison:")
    print(f"   Difference: {score_diff:+.2f} points (with URL checking)")

def main():
    """Run all tests."""
    try:
        test_url_checker()
        test_enhanced_scorer()
        
        print("\n\n" + "=" * 60)
        print("✓ URL checking functionality test completed successfully!")
        print("=" * 60)
        print("\nTo use URL checking in evaluation, run:")
        print("python scripts/run_evaluation.py --topic Proteomics --limit 10 --check-urls")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
