import argparse
import sys
from pathlib import Path
from utils import fetch_all_biotools
from logger import get_logger


def parse_arguments():
    """
    Parse command line arguments for bio.tools data collection.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Bio.tools Annotation Quality Evaluation - Data Collection Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect first 100 tools for testing
  python main.py --max-tools 100 --page-size 25
  
  # Collect all tools with maximum efficiency
  python main.py --page-size 100
  
  # Collect tools starting from page 5, save to specific file
  python main.py --start-page 5 --output data/custom_collection.json
  
  # Collect with custom API delay and debug logging
  python main.py --delay 1.0 --log-level DEBUG --max-tools 500
        """
    )
    
    # Data collection parameters
    parser.add_argument(
        "--max-tools", 
        type=int, 
        default=None,
        help="Maximum number of tools to collect (default: all tools ~27,000)"
    )
    
    parser.add_argument(
        "--page-size", 
        type=int, 
        default=100, 
        choices=range(1, 101),
        metavar="[1-100]",
        help="Number of tools per API page (default: 100, max: 100)"
    )
    
    parser.add_argument(
        "--start-page", 
        type=int, 
        default=1,
        help="Page number to start collection from (default: 1)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file path for collected data (default: auto-generated timestamped file)"
    )
    
    parser.add_argument(
        "--base-url",
        type=str,
        default="https://bio.tools/api/tool/",
        help="Base URL for bio.tools API (default: https://bio.tools/api/tool/)"
    )
    
    # API behavior parameters
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between API requests in seconds (default: 0.5)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed requests (default: 3)"
    )
    
    # Logging and output parameters
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Custom log file path (default: auto-generated in logs/ directory)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress console output (logs only to file)"
    )
    
    # Advanced options
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Resume collection from a partial data file"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be collected without making API calls"
    )
    
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only collect and display API statistics, don't save data"
    )
    
    parser.add_argument(
        "--save-mode",
        choices=["single", "individual", "batch"],
        default="single",
        help="How to save tools: 'single' (one file), 'individual' (one JSON file per tool), 'batch' (multiple JSON files)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Number of tools per batch file when using --save-mode batch (default: 1000)"
    )
    
    return parser.parse_args()


def main():
    """
    Main function with command line argument support.
    """
    args = parse_arguments()
    
    # Set up logger with parsed arguments
    logger = get_logger("main")
    logger.setLevel(getattr(__import__('logging'), args.log_level))
    
    logger.info("=" * 60)
    logger.info("Bio.tools Annotation Quality Evaluation - Data Collector")
    logger.info("=" * 60)
    
    # Log configuration
    logger.info("Configuration:")
    logger.info(f"  Max tools: {args.max_tools or 'ALL (~27,000)'}")
    logger.info(f"  Page size: {args.page_size}")
    logger.info(f"  Start page: {args.start_page}")
    logger.info(f"  API delay: {args.delay}s")
    logger.info(f"  Log level: {args.log_level}")
    logger.info(f"  Output file: {args.output or 'auto-generated'}")
    logger.info(f"  Save mode: {args.save_mode}")
    if args.save_mode == "batch":
        logger.info(f"  Batch size: {args.batch_size}")
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No actual API calls will be made")
        estimated_pages = (args.max_tools or 27000) // args.page_size + 1
        logger.info(f"Would collect approximately {estimated_pages} pages")
        return
    
    if args.stats_only:
        logger.info("STATS ONLY MODE - Will collect basic statistics")
    
    try:
        logger.info("Starting bio.tools data collection...")
        
        # Call the collection function with parsed arguments
        all_tools = fetch_all_biotools(
            base_url=args.base_url,
            output_file=args.output,
            page_size=args.page_size,
            max_tools=args.max_tools,
            start_page=args.start_page,
            delay=args.delay,
            stats_only=args.stats_only,
            save_mode=args.save_mode,
            batch_size=args.batch_size
        )
        
        logger.info(f"Successfully collected {len(all_tools):,} tools")
        
        # Show sample data unless in stats-only mode
        if all_tools and not args.stats_only:
            logger.info("Sample tool entries:")
            for i, tool in enumerate(all_tools[:5]):
                name = tool.get('name', 'Unknown')
                biotoolsID = tool.get('biotoolsID', 'Unknown')
                version = tool.get('version', ['Unknown'])[0] if tool.get('version') else 'Unknown'
                logger.info(f"  {i+1}. {name} (ID: {biotoolsID}, v{version})")
        
        logger.info("=" * 60)
        logger.info("Bio.tools data collection completed successfully!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.warning("Collection interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to collect bio.tools data: {e}")
        logger.debug("Check network connectivity and API availability")
        sys.exit(1)


if __name__ == "__main__":
    main()