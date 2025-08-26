#!/usr/bin/env python3
"""
Bio.tools annotation quality evaluation with local storage support.
Comprehensive script for evaluating metadata quality in the ELIXIR bio.tools registry.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
import yaml
from datetime import datetime

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
            logging.FileHandler('evaluation.log'),
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

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='bio.tools Annotation Quality Evaluation with Local Storage Support',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Run evaluation on local data (recommended for speed)
  python scripts/run_evaluation.py --use-local --limit 1000 --visualize

  # Run evaluation on ALL local tools (full evaluation)
  python scripts/run_evaluation.py --use-local --all --visualize

  # Check what data is available locally
  python scripts/run_evaluation.py --storage-info

  # Run evaluation with URL checking (slower but more detailed)
  python scripts/run_evaluation.py --use-local --limit 500 --check-urls --visualize

  # Run evaluation by topic using local data
  python scripts/run_evaluation.py --use-local --topic Proteomics --visualize

  # Traditional API-based evaluation (slower)
  python scripts/run_evaluation.py --topic Proteomics --limit 100 --visualize
        """
    )
    
    # Data source options
    parser.add_argument('--collection', type=str, 
                       help='Collection to analyze (e.g., proteomics)')
    parser.add_argument('--topic', type=str,
                       help='Topic to analyze (e.g., Proteomics)')
    parser.add_argument('--query', type=str,
                       help='Search query for tools')
    parser.add_argument('--limit', type=int, default=1000,
                       help='Maximum number of tools to analyze (default: 1000)')
    parser.add_argument('--all', action='store_true',
                       help='Run evaluation on all locally stored tools (sets limit to 50000)')
    
    # Local storage options (recommended)
    parser.add_argument('--use-local', action='store_true',
                       help='Use locally stored data instead of API (RECOMMENDED for speed)')
    parser.add_argument('--save-locally', action='store_true', default=True,
                       help='Save API data locally (enabled by default)')
    parser.add_argument('--local-data-dir', type=str, default='data/biotools',
                       help='Directory for local biotool storage')
    parser.add_argument('--disable-local-storage', action='store_true',
                       help='Disable local storage completely')
    
    # Legacy file loading support
    parser.add_argument('--load-from-file', type=str,
                       help='Load tools data from JSON file instead of API')
    
    # Configuration and output
    parser.add_argument('--config', type=str, 
                       default='config/scoring_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--output-dir', type=str, default='data/processed',
                       help='Output directory for results')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualizations')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    # Additional options
    parser.add_argument('--save-raw-data', action='store_true',
                       help='Save raw tool data to file (legacy batch format)')
    parser.add_argument('--real-linter', action='store_true',
                       help='Use real bio.tools linter for validation')
    parser.add_argument('--check-urls', action='store_true',
                       help='Check URL accessibility (homepage and other links)')
    
    # Local data management commands
    parser.add_argument('--list-local-tools', action='store_true',
                       help='List locally stored tools and exit')
    parser.add_argument('--storage-info', action='store_true',
                       help='Show local storage information and exit')
    parser.add_argument('--clear-local-data', type=str, choices=['all', 'collections', 'topics', 'queries'],
                       help='Clear local data from specified subdirectory')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        config = load_config(args.config) if Path(args.config).exists() else {}
        
        # Initialize API client with local storage support
        enable_local_storage = not args.disable_local_storage
        api_client = BioToolsAPIClient(
            enable_local_storage=enable_local_storage,
            local_data_dir=args.local_data_dir
        )
        
        # Handle local storage management commands
        if args.storage_info:
            info = api_client.get_local_storage_info()
            print("\nLocal Storage Information:")
            print("=" * 40)
            print(f"Data Directory: {info['data_directory']}")
            print("\nSubdirectories:")
            for subdir, details in info['subdirectories'].items():
                print(f"  {subdir}: {details['tool_count']} tools ({'exists' if details['exists'] else 'missing'})")
            return 0
        
        if args.list_local_tools:
            print("\nLocally Stored Tools:")
            print("=" * 30)
            for subdir in ['all', 'collections', 'topics', 'queries']:
                tools = api_client.list_local_tools(subdir)
                print(f"\n{subdir.title()}: {len(tools)} tools")
                if tools and len(tools) <= 10:  # Show first 10 for smaller lists
                    for tool_id in tools[:10]:
                        print(f"  - {tool_id}")
                elif tools:
                    print(f"  - {tools[0]}")
                    print(f"  - ... ({len(tools) - 1} more)")
            return 0
        
        if args.clear_local_data:
            deleted_count = api_client.clear_local_data(args.clear_local_data)
            print(f"Deleted {deleted_count} tools from '{args.clear_local_data}' subdirectory")
            return 0
        
        # Initialize other components
        data_parser = BioToolsDataParser()
        scorer = CompletenessScorer(
            config_path=args.config if Path(args.config).exists() else None,
            enable_url_checking=args.check_urls
        )
        classifier = TierClassifier()
        statistics = QualityStatistics()
        
        if args.check_urls:
            logger.info("URL accessibility checking enabled")
        
        if args.visualize:
            visualizer = QualityVisualizer()
        else:
            visualizer = None
        
        # Collect tool data
        logger.info("Collecting tool data...")
        
        # Determine data collection parameters
        use_local = args.use_local
        save_locally = args.save_locally and enable_local_storage
        
        # Handle --all flag for local data
        limit = args.limit
        if args.all:
            if use_local:
                limit = 50000  # Very high limit to get all local tools
                logger.info("--all flag detected: setting limit to 50000 for local evaluation")
            else:
                logger.warning("--all flag is intended for local data. Consider adding --use-local flag.")
                limit = args.limit
        
        if args.load_from_file:
            logger.info(f"Loading data from file: {args.load_from_file}")
            tools = api_client.load_tools_from_file(args.load_from_file)
        else:
            if args.collection:
                logger.info(f"Collecting tools from collection: {args.collection}")
                if use_local:
                    logger.info("Using local storage (if available)")
                tools = api_client.get_tools_by_collection(
                    args.collection, 
                    limit, 
                    use_local=use_local, 
                    save_locally=save_locally
                )
            elif args.topic:
                logger.info(f"Collecting tools by topic: {args.topic}")
                if use_local:
                    logger.info("Using local storage (if available)")
                tools = api_client.get_tools_by_topic(
                    args.topic, 
                    limit, 
                    use_local=use_local, 
                    save_locally=save_locally
                )
            elif args.query:
                logger.info(f"Searching tools with query: {args.query}")
                if use_local:
                    logger.info("Using local storage (if available)")
                tools = api_client.search_tools(
                    args.query, 
                    limit, 
                    use_local=use_local, 
                    save_locally=save_locally
                )
            else:
                logger.info(f"Collecting random tools (limit: {limit})")
                if use_local:
                    logger.info("Using local storage (if available)")
                tools = api_client.get_all_tools(
                    limit, 
                    use_local=use_local, 
                    save_locally=save_locally
                )
        
        if not tools:
            logger.error("No tools collected. Exiting.")
            return 1
        
        logger.info(f"Collected {len(tools)} tools")
        
        # Show local storage status
        if enable_local_storage:
            storage_info = api_client.get_local_storage_info()
            total_local_tools = sum(
                details['tool_count'] for details in storage_info['subdirectories'].values()
            )
            logger.info(f"Local storage contains {total_local_tools} total tools")
        
        # Save raw data if requested (legacy support)
        if args.save_raw_data:
            raw_data_path = output_dir / 'raw_tools_data.json'
            api_client.save_tools_to_file(tools, str(raw_data_path))
            logger.info(f"Saved raw data to {raw_data_path}")
        
        # Parse tool data
        logger.info("Parsing tool data...")
        parsed_tools = data_parser.batch_parse_tools(tools)
        
        # Score tools
        logger.info("Scoring tools...")
        scoring_results = scorer.score_tools(tools)
        
        # Classify tools
        logger.info("Classifying tools into tiers...")
        classifications = classifier.classify_tools(scoring_results)
        
        # Generate statistics
        logger.info("Generating statistics...")
        basic_stats = statistics.generate_basic_statistics(scoring_results)
        component_analysis = statistics.analyze_score_components(scoring_results)
        completeness_patterns = statistics.analyze_completeness_patterns(scoring_results)
        collection_analysis = statistics.analyze_by_collection(scoring_results, tools)
        quality_gaps = statistics.identify_quality_gaps(scoring_results)
        
        # Prepare comprehensive results
        results = {
            'metadata': {
                'total_tools': len(tools),
                'analysis_date': datetime.now().isoformat(),
                'collection': args.collection,
                'topic': args.topic,
                'query': args.query,
                'limit': limit,  # Use the actual limit that was applied
                'all_tools_requested': args.all,
                'data_source': 'local' if use_local else 'api',
                'local_storage_enabled': enable_local_storage,
                'local_tools_saved': save_locally,
                'url_checking_enabled': args.check_urls
            },
            'basic_statistics': basic_stats,
            'component_analysis': component_analysis,
            'completeness_patterns': completeness_patterns,
            'collection_analysis': collection_analysis,
            'quality_gaps': quality_gaps,
            'scoring_results': scoring_results,
            'classifications': classifications
        }
        
        # Save results
        results_path = output_dir / 'evaluation_results.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results saved to {results_path}")
        
        # Generate summary report
        summary_path = output_dir / 'summary_report.txt'
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("bio.tools Annotation Quality Evaluation Summary\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Analysis Date: {results['metadata']['analysis_date']}\n")
            f.write(f"Total Tools Analyzed: {results['metadata']['total_tools']}\n")
            f.write(f"Data Source: {results['metadata']['data_source']}\n")
            f.write(f"Local Storage Enabled: {results['metadata']['local_storage_enabled']}\n")
            f.write(f"URL Accessibility Checking: {'Enabled' if results['metadata']['url_checking_enabled'] else 'Disabled'}\n")
            if args.collection:
                f.write(f"Collection: {args.collection}\n")
            if args.topic:
                f.write(f"Topic: {args.topic}\n")
            if args.query:
                f.write(f"Query: {args.query}\n")
            f.write("\n")
            
            # Basic statistics
            f.write("BASIC STATISTICS\n")
            f.write("-" * 20 + "\n")
            score_stats = basic_stats.get('score_statistics', {})
            f.write(f"Average Score: {score_stats.get('mean', 0):.2f}\n")
            f.write(f"Median Score: {score_stats.get('median', 0):.2f}\n")
            f.write(f"Standard Deviation: {score_stats.get('std', 0):.2f}\n")
            f.write(f"Score Range: {score_stats.get('min', 0):.2f} - {score_stats.get('max', 0):.2f}\n")
            f.write("\n")
            
            # Tier distribution
            f.write("TIER DISTRIBUTION\n")
            f.write("-" * 20 + "\n")
            tier_dist = basic_stats.get('tier_distribution', {})
            tier_pct = basic_stats.get('tier_percentages', {})
            for tier in sorted(tier_dist.keys()):
                f.write(f"Tier {tier}: {tier_dist[tier]} tools ({tier_pct.get(tier, 0):.1f}%)\n")
            f.write("\n")
            
            # Top missing fields
            f.write("MOST COMMONLY MISSING FIELDS\n")
            f.write("-" * 30 + "\n")
            missing_fields = quality_gaps.get('most_common_missing_fields', [])[:10]
            for field, count in missing_fields:
                f.write(f"{field}: {count} tools\n")
            f.write("\n")
            
            # Improvement opportunities
            f.write("TIER UPGRADE OPPORTUNITIES\n")
            f.write("-" * 30 + "\n")
            tier_opps = quality_gaps.get('tier_upgrade_opportunities', {})
            for transition, tools_list in tier_opps.items():
                f.write(f"{transition}: {len(tools_list)} tools\n")
        
        logger.info(f"Summary report saved to {summary_path}")
        
        # Generate visualizations if requested
        if args.visualize and visualizer:
            logger.info("Generating comprehensive tier dashboard...")
            
            viz_dir = output_dir / 'visualizations'
            viz_dir.mkdir(exist_ok=True)
            
            # For now, we'll skip linter integration and use the built-in dashboard functionality
            logger.info("Preparing dashboard generation...")
            linter_results = []
            
            # Create complete dashboard with all pages
            logger.info("Creating complete dashboard...")
            
            # Safely calculate average score using the correct field name 'total_score'
            scores = []
            for r in scoring_results:
                if isinstance(r, dict) and 'total_score' in r:
                    scores.append(r['total_score'])
                    # Also add 'score' field for dashboard compatibility
                    r['score'] = r['total_score']
                else:
                    logger.warning(f"Result missing total_score field: {r}")
            
            avg_score = sum(scores) / len(scores) if scores else 0
            
            visualizer.generate_complete_dashboard(
                scoring_results, 
                results,  # Pass the complete results object which contains basic_statistics
                config,  # Pass the loaded config
                str(viz_dir)
            )
            logger.info("Created complete dashboard with all pages")
            
            logger.info("Main visualizations completed!")
            print(f"\nDashboard Created:")
            print(f"• Main Dashboard: {viz_dir / 'index.html'}")
            print(f"• Tools Overview: {viz_dir / 'tools-overview.html'}")
            print(f"• Field Analysis: {viz_dir / 'field-analysis.html'}")
            print(f"• Statistics: {viz_dir / 'statistics.html'}")
            print(f"• Linter Reports: {viz_dir / 'linter-reports.html'}")
            logger.info(f"Visualizations saved to {viz_dir}")
        
        # Print summary to console
        print("\n" + "=" * 60)
        print("bio.tools ANNOTATION QUALITY EVALUATION COMPLETE")
        print("=" * 60)
        print(f"Tools analyzed: {len(tools)}")
        print(f"Data source: {results['metadata']['data_source']}")
        print(f"Average quality score: {basic_stats.get('score_statistics', {}).get('mean', 0):.2f}/100")
        print(f"Results saved to: {results_path}")
        
        if enable_local_storage:
            storage_info = api_client.get_local_storage_info()
            total_local_tools = sum(
                details['tool_count'] for details in storage_info['subdirectories'].values()
            )
            print(f"Local storage: {total_local_tools} tools stored")
        
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
