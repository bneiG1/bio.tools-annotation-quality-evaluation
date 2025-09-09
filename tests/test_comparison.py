#!/usr/bin/env python3
"""
Test different tools to see completeness scoring across the spectrum.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.analyzers.quality_analyzer import QualityAnalyzer


def test_multiple_tools():
    """Test multiple tools to show completeness scoring variation."""
    
    analyzer = QualityAnalyzer()
    cache_dir = Path("data/cache")
    sample_files = list(cache_dir.glob("*.json"))[:5]  # Test first 5 files
    
    print("="*100)
    print("TOOL COMPLETENESS COMPARISON")
    print("="*100)
    print(f"{'Tool ID':<20} {'Name':<30} {'Grade':<5} {'Overall':<8} {'Legacy':<8} {'Completeness':<12} {'Tier':<12}")
    print("-" * 100)
    
    results = []
    
    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tool_data = json.load(f)
            
            # Analyze tool
            report = analyzer.analyze_tool(tool_data)
            metrics = report.metrics
            
            tool_id = tool_data.get('biotoolsID', 'unknown')[:18]
            tool_name = tool_data.get('name', 'Unknown')[:28]
            
            print(f"{tool_id:<20} {tool_name:<30} {metrics.quality_grade:<5} "
                  f"{metrics.overall_score:<8.1f} {metrics.standards_score:<8.1f} "
                  f"{metrics.completeness_score:<12.1f} {metrics.completeness_tier:<12}")
            
            results.append({
                'tool_id': tool_id,
                'report': report
            })
            
        except Exception as e:
            print(f"Error with {file_path}: {e}")
    
    print("\n" + "="*50)
    print("DETAILED COMPLETENESS ANALYSIS")
    print("="*50)
    
    # Show detailed analysis for top and bottom performers
    if results:
        # Sort by completeness score
        sorted_results = sorted(results, key=lambda x: x['report'].metrics.completeness_score, reverse=True)
        
        print(f"\nBest performing tool:")
        print("-" * 30)
        best = sorted_results[0]['report']
        show_detailed_completeness(best)
        
        if len(sorted_results) > 1:
            print(f"\nWorst performing tool:")
            print("-" * 30)
            worst = sorted_results[-1]['report']
            show_detailed_completeness(worst)


def show_detailed_completeness(report):
    """Show detailed completeness analysis for a tool."""
    metrics = report.metrics
    completeness = report.completeness_analysis
    
    print(f"Tool: {report.tool_name} ({report.tool_id})")
    print(f"Completeness Tier: {metrics.completeness_tier} ({metrics.completeness_score:.1f}%)")
    print(f"Overall Grade: {metrics.quality_grade} ({metrics.overall_score:.1f}/100)")
    
    print("\nTier Status:")
    for tier, result in completeness['tier_results'].items():
        status = "✅ PASSED" if result['satisfied'] else "❌ FAILED"
        print(f"  {tier}: {status}")
        if not result['satisfied'] and result['missing_fields']:
            missing = result['missing_fields'][:3]  # Show first 3
            missing_str = ', '.join(missing)
            if len(result['missing_fields']) > 3:
                missing_str += f" (+{len(result['missing_fields'])-3} more)"
            print(f"    Missing: {missing_str}")
    
    if completeness.get('recommendations'):
        print(f"\nTop Recommendations:")
        for rec in completeness['recommendations'][:3]:
            print(f"  💡 {rec}")
    
    print()


if __name__ == "__main__":
    test_multiple_tools()
