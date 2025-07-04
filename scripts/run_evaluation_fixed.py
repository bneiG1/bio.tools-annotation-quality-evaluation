#!/usr/bin/env python3
"""
Main script for running bio.tools annotation quality evaluation.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
import yaml
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

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
        description='bio.tools Annotation Quality Evaluation'
    )
    
    parser.add_argument('--collection', type=str, 
                       help='Collection to analyze (e.g., proteomics)')
    parser.add_argument('--topic', type=str,
                       help='Topic to analyze (e.g., Proteomics)')
    parser.add_argument('--query', type=str,
                       help='Search query for tools')
    parser.add_argument('--limit', type=int, default=100,
                       help='Maximum number of tools to analyze')
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
    parser.add_argument('--load-from-file', type=str,
                       help='Load tools data from JSON file instead of API')
    parser.add_argument('--save-raw-data', action='store_true',
                       help='Save raw tool data to file')
    
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
        
        api_client = BioToolsAPIClient()
        data_parser = BioToolsDataParser()
        scorer = CompletenessScorer(args.config if Path(args.config).exists() else None)
        classifier = TierClassifier()
        statistics = QualityStatistics()
        
        if args.visualize:
            visualizer = QualityVisualizer()
        
        # Collect tool data
        logger.info("Collecting tool data...")
        
        if args.load_from_file:
            logger.info(f"Loading data from file: {args.load_from_file}")
            tools = api_client.load_tools_from_file(args.load_from_file)
        else:
            if args.collection:
                logger.info(f"Collecting tools from collection: {args.collection}")
                tools = api_client.get_tools_by_collection(args.collection, args.limit)
            elif args.topic:
                logger.info(f"Collecting tools by topic: {args.topic}")
                tools = api_client.get_tools_by_topic(args.topic, args.limit)
            elif args.query:
                logger.info(f"Searching tools with query: {args.query}")
                tools = api_client.search_tools(args.query, args.limit)
            else:
                logger.info(f"Collecting random tools (limit: {args.limit})")
                tools = api_client.get_all_tools(args.limit)
        
        if not tools:
            logger.error("No tools collected. Exiting.")
            return 1
        
        logger.info(f"Collected {len(tools)} tools")
        
        # Save raw data if requested
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
                'limit': args.limit
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
        if args.visualize:
            logger.info("Generating visualizations...")
            
            viz_dir = output_dir / 'visualizations'
            viz_dir.mkdir(exist_ok=True)
            
            # Tier distribution chart
            tier_chart = visualizer.create_tier_distribution_chart(
                scoring_results, str(viz_dir / 'tier_distribution.html')
            )
            
            # Score distribution histogram
            score_hist = visualizer.create_score_distribution_histogram(
                scoring_results, str(viz_dir / 'score_distribution.html')
            )
            
            # Component radar chart
            radar_chart = visualizer.create_component_radar_chart(
                scoring_results, by_tier=True, save_path=str(viz_dir / 'component_radar.html')
            )
            
            # Completeness heatmap
            heatmap = visualizer.create_completeness_heatmap(
                completeness_patterns, str(viz_dir / 'completeness_heatmap.html')
            )
            
            # Collection comparison
            if collection_analysis:
                collection_chart = visualizer.create_collection_comparison_chart(
                    collection_analysis, str(viz_dir / 'collection_comparison.html')
                )
            
            # Improvement opportunities
            improvement_chart = visualizer.create_improvement_opportunities_chart(
                quality_gaps, str(viz_dir / 'improvement_opportunities.html')
            )
            
            # Summary dashboard
            dashboard = visualizer.create_summary_dashboard(
                scoring_results, basic_stats, str(viz_dir / 'summary_dashboard.html')
            )
            
            logger.info(f"Visualizations saved to {viz_dir}")
        
        # Print summary to console
        print("\n" + "=" * 60)
        print("bio.tools ANNOTATION QUALITY EVALUATION COMPLETE")
        print("=" * 60)
        print(f"Tools analyzed: {len(tools)}")
        print(f"Average quality score: {basic_stats.get('score_statistics', {}).get('mean', 0):.2f}/100")
        print(f"Results saved to: {results_path}")
        if args.visualize:
            print(f"Visualizations saved to: {viz_dir}")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
