#!/usr/bin/env python3
"""
Bio.tools Quality Dashboard Runner
Launch dashboards using Streamlit or simple HTML.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
import yaml

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_collection.api_client import BioToolsAPIClient
from data_collection.data_parser import BioToolsDataParser
from scoring.completeness_scorer import CompletenessScorer
from scoring.tier_classifier import TierClassifier
from analysis.statistics import QualityStatistics
from visualization.charts import QualityVisualizer

def setup_logging(level: str = 'INFO'):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dashboard.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return {}

def load_existing_results(results_file: str) -> tuple:
    """Load existing evaluation results from file."""
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both old and new file formats
        if 'results' in data:
            results = data.get('results', [])
        else:
            # New format - combine scoring_results and classifications
            scoring_results = data.get('scoring_results', [])
            classifications = data.get('classifications', [])
            
            results = []
            for score_data, class_data in zip(scoring_results, classifications):
                result = {
                    'biotoolsID': score_data.get('biotoolsID', 'unknown'),
                    'score': score_data.get('total_score', 0),
                    'total_score': score_data.get('total_score', 0),
                    'tier': class_data.get('tier', 1),
                    'details': score_data
                }
                results.append(result)
        
        statistics = data.get('statistics', data.get('basic_statistics', {}))
        scoring_config = data.get('scoring_config', {})
        
        logging.info(f"Loaded {len(results)} results from {results_file}")
        return results, statistics, scoring_config
    
    except Exception as e:
        logging.error(f"Failed to load results from {results_file}: {e}")
        return [], {}, {}

def run_quick_evaluation(limit: int = 100) -> tuple:
    """Run a quick evaluation to generate sample data."""
    logging.info("Running quick evaluation to generate dashboard data...")
    
    # Load configuration
    config = load_config('config/scoring_config.yaml')
    
    # Initialize components
    api_client = BioToolsAPIClient()
    data_parser = BioToolsDataParser()
    scorer = CompletenessScorer('config/scoring_config.yaml')
    classifier = TierClassifier()
    stats_analyzer = QualityStatistics()
    
    # Get data
    tools_data = api_client.get_all_tools(limit=limit)
    if not tools_data:
        logging.error("No data retrieved from API")
        return [], {}, {}
    
    # Process and score
    results = []
    for tool in tools_data:
        try:
            # Use the tool data directly (already parsed from API)
            score_result = scorer.score_tool(tool)
            tier = classifier.classify_tool(score_result['total_score'])
            
            result = {
                'biotoolsID': tool.get('biotoolsID', 'unknown'),
                'score': score_result['total_score'],
                'tier': tier,
                'details': score_result
            }
            results.append(result)
            
        except Exception as e:
            logging.warning(f"Failed to process tool: {e}")
    
    # Calculate statistics
    statistics = stats_analyzer.generate_basic_statistics(results)
    
    return results, statistics, config

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Bio.tools Quality Dashboard Runner',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Generate simple HTML dashboard
  python scripts/run_dashboard.py --html

  # Launch Streamlit dashboard
  python scripts/run_dashboard.py --streamlit

  # Use existing results file
  python scripts/run_dashboard.py --html --results-file data/processed/evaluation_results.json

  # Quick evaluation and dashboard
  python scripts/run_dashboard.py --streamlit --quick --limit 50
        """
    )
    
    # Dashboard type selection
    dashboard_group = parser.add_mutually_exclusive_group(required=True)
    dashboard_group.add_argument('--html', action='store_true',
                               help='Generate simple HTML dashboard')
    dashboard_group.add_argument('--streamlit', action='store_true',
                               help='Launch Streamlit dashboard')
    
    # Data source options
    parser.add_argument('--results-file', type=str,
                       help='Load results from existing JSON file')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick evaluation to generate sample data')
    parser.add_argument('--limit', type=int, default=100,
                       help='Limit for quick evaluation (default: 100)')
    
    # Dashboard configuration
    parser.add_argument('--output-dir', type=str, default='dashboard',
                       help='Output directory for HTML dashboard')
    parser.add_argument('--port', type=int, default=8051,
                       help='Port for Streamlit dashboard (default: 8051)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode for web dashboards')
    
    # Configuration
    parser.add_argument('--config', type=str, 
                       default='config/scoring_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup
    setup_logging(args.log_level)
    logging.info("Starting Bio.tools Quality Dashboard Runner")
    
    # Load data
    if args.results_file:
        results, statistics, scoring_config = load_existing_results(args.results_file)
        if not results:
            logging.error("No valid results loaded from file")
            sys.exit(1)
    elif args.quick:
        results, statistics, scoring_config = run_quick_evaluation(args.limit)
        if not results:
            logging.error("Quick evaluation failed")
            sys.exit(1)
    else:
        logging.error("Either --results-file or --quick must be specified")
        sys.exit(1)
    
    logging.info(f"Dashboard will display {len(results)} tools")
    
    # Initialize visualizer
    visualizer = QualityVisualizer()
    
    # Launch appropriate dashboard
    if args.html:
        logging.info(f"Generating simple HTML dashboard in {args.output_dir}")
        visualizer.generate_complete_dashboard(
            results, statistics, scoring_config, args.output_dir
        )
        
        # Open in browser
        import webbrowser
        import os
        index_file = os.path.join(args.output_dir, 'index.html')
        if os.path.exists(index_file):
            webbrowser.open(f'file://{os.path.abspath(index_file)}')
            logging.info(f"Dashboard opened in browser: {index_file}")
        
    elif args.streamlit:
        try:
            logging.info("Launching Streamlit dashboard")
            # Import here to avoid dependency issues if not available
            from visualization.streamlit_dashboard import run_streamlit_dashboard
            
            run_streamlit_dashboard(results, statistics, scoring_config)
            
        except ImportError:
            logging.error("Streamlit is not available. Install with: pip install streamlit streamlit-aggrid")
            sys.exit(1)

if __name__ == "__main__":
    main()
