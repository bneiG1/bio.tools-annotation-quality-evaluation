#!/usr/bin/env python3
"""
Bio.tools Quality Dashboard Integration Script
Combines the existing analysis pipeline with the Streamlit web dashboard.
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def launch_dashboard_with_data(tools_data: List[Dict], statistics: Dict, config: Dict):
    """Launch Streamlit dashboard with provided data."""
    
    # Save data to temporary file for Streamlit app to load
    data_file = Path("data/temp_dashboard_data.json")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    dashboard_data = {
        "tools": tools_data,
        "statistics": statistics,
        "config": config,
        "timestamp": str(data_file.stat().st_mtime if data_file.exists() else 0)
    }
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    print(f"✅ Dashboard data saved to {data_file}")
    print(f"🔬 Launching Bio.tools Quality Dashboard...")
    print(f"📊 Dashboard will display {len(tools_data)} tools")
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start dashboard: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install with: pip install streamlit")
        sys.exit(1)

def load_data_from_file(file_path: str) -> tuple:
    """Load analysis results from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Try different data formats
        if 'tools' in data:
            return data['tools'], data.get('statistics', {}), data.get('config', {})
        elif isinstance(data, list):
            return data, {}, {}
        elif 'results' in data:
            return data['results'], data.get('statistics', {}), data.get('config', {})
        else:
            print(f"❌ Unrecognized data format in {file_path}")
            return [], {}, {}
            
    except Exception as e:
        print(f"❌ Error loading file {file_path}: {e}")
        return [], {}, {}

def generate_sample_data(count: int = 100) -> tuple:
    """Generate sample data for demonstration."""
    print(f"🔄 Generating {count} sample tools...")
    
    tools_data = []
    for i in range(count):
        tool = {
            'tool_id': f'sample_tool_{i:03d}',
            'tool_name': f'Sample Bioinformatics Tool {i}',
            'metrics': {
                'overall_score': 30 + (i % 70),
                'quality_grade': ['A', 'B', 'C', 'D', 'F'][i % 5],
                'standards_tier': f'Tier {(i % 5) + 1}',
                'completeness_tier': f'Tier {(i % 5) + 1}',
                'standards_score': 25 + (i % 75),
                'completeness_score': 35 + (i % 65),
                'schema_valid': i % 3 != 0,
                'schema_errors': (i % 4) if i % 3 == 0 else 0,
                'schema_warnings': (i % 3),
                'lint_issues': i % 6,
                'critical_issues': 1 if i % 15 == 0 else 0,
                'error_issues': (i % 4),
                'warning_issues': (i % 5),
                'info_issues': (i % 3),
                'field_completeness': 0.2 + (i % 80) / 100,
                'required_fields_complete': i % 2 == 0,
                'recommended_fields_complete': 0.1 + (i % 90) / 100,
                'url_health': 0.4 + (i % 60) / 100,
                'edam_consistency': 0.3 + (i % 70) / 100,
                'publication_quality': 0.2 + (i % 80) / 100,
                'has_functions': i % 4 != 0,
                'has_documentation': i % 3 != 0,
                'has_publications': i % 5 != 0,
                'has_contacts': i % 7 != 0,
                'analysis_date': '2024-09-09'
            },
            'summary': f'Sample bioinformatics tool #{i} for quality analysis demonstration',
            'recommendations': [
                'Improve metadata completeness',
                'Add more detailed documentation',
                'Include additional EDAM terms',
                'Update publication information',
                'Enhance URL accessibility'
            ][:((i % 5) + 1)]
        }
        tools_data.append(tool)
    
    # Calculate statistics
    total_tools = len(tools_data)
    grade_counts = {}
    tier_counts = {}
    
    for tool in tools_data:
        grade = tool['metrics']['quality_grade']
        tier = tool['metrics']['standards_tier']
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    statistics = {
        'total_tools': total_tools,
        'grade_distribution': grade_counts,
        'tier_distribution': tier_counts,
        'average_score': sum(t['metrics']['overall_score'] for t in tools_data) / total_tools,
        'validation_stats': {
            'valid': sum(1 for t in tools_data if t['metrics']['schema_valid']),
            'with_errors': sum(1 for t in tools_data if t['metrics']['schema_errors'] > 0),
            'with_warnings': sum(1 for t in tools_data if t['metrics']['schema_warnings'] > 0)
        },
        'content_stats': {
            'with_functions': sum(1 for t in tools_data if t['metrics']['has_functions']),
            'with_documentation': sum(1 for t in tools_data if t['metrics']['has_documentation']),
            'with_publications': sum(1 for t in tools_data if t['metrics']['has_publications']),
            'with_contacts': sum(1 for t in tools_data if t['metrics']['has_contacts'])
        }
    }
    
    config = {
        'data_source': 'sample_generation',
        'generated_count': count,
        'generation_date': '2024-09-09'
    }
    
    return tools_data, statistics, config

def main():
    """Main entry point for dashboard integration."""
    parser = argparse.ArgumentParser(
        description='Bio.tools Quality Dashboard Integration',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Launch dashboard with sample data
  python dashboard.py --sample --count 200

  # Load data from file and launch dashboard
  python dashboard.py --file data/analysis_results.json

  # Quick demo with default settings
  python dashboard.py --demo
        """
    )
    
    # Data source options
    data_group = parser.add_mutually_exclusive_group(required=True)
    data_group.add_argument('--sample', action='store_true',
                           help='Generate sample data for demonstration')
    data_group.add_argument('--file', type=str, metavar='PATH',
                           help='Load data from JSON file')
    data_group.add_argument('--demo', action='store_true',
                           help='Quick demo with 100 sample tools')
    
    # Options
    parser.add_argument('--count', type=int, default=100,
                       help='Number of sample tools to generate (default: 100)')
    parser.add_argument('--port', type=int, default=8501,
                       help='Port for Streamlit dashboard (default: 8501)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🔬 Bio.tools Quality Dashboard Integration")
    print("=" * 50)
    
    # Load or generate data
    if args.demo:
        tools_data, statistics, config = generate_sample_data(100)
    elif args.sample:
        tools_data, statistics, config = generate_sample_data(args.count)
    elif args.file:
        if not Path(args.file).exists():
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        tools_data, statistics, config = load_data_from_file(args.file)
        if not tools_data:
            print(f"❌ No valid data loaded from {args.file}")
            sys.exit(1)
    
    # Validate data
    if not tools_data:
        print("❌ No tools data available")
        sys.exit(1)
    
    print(f"✅ Loaded {len(tools_data)} tools")
    if statistics:
        avg_score = statistics.get('average_score', 0)
        print(f"📊 Average quality score: {avg_score:.1f}")
    
    # Launch dashboard
    try:
        launch_dashboard_with_data(tools_data, statistics, config)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
