#!/usr/bin/env python3
"""
Unified Bio.tools Quality Analysis CLI

Command-line interface for fetching bio.tools data and generating quality reports
with support for both sequential and parallel processing modes.
"""

import argparse
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import asyncio

import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.collectors.async_biotools_api import UnifiedBioToolsAPIClient, create_async_client
    from src.analyzers.quality_analyzer import QualityAnalyzer, QualityReport
    from src.reporters.quality_reporter import QualityReporter
    from src.utils.logger import Logger
    
    # Parallel processing imports (optional)
    try:
        from src.utils.parallel_config import ParallelProcessingConfig, create_optimal_config
        from src.utils.processing_pipeline import ProcessingPipeline, PipelineProgress
        from src.analyzers.parallel_processor import ParallelQualityProcessor
        PARALLEL_AVAILABLE = True
    except ImportError as e:
        logger = logging.getLogger(__name__)
        logger.info(f"Parallel processing not available: {e}")
        PARALLEL_AVAILABLE = False
        # Set defaults to avoid NameError
        ParallelProcessingConfig = None
        create_optimal_config = None
        ProcessingPipeline = None
        PipelineProgress = None
        ParallelQualityProcessor = None
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available in the src directory.")
    sys.exit(1)


class UnifiedBioToolsCLI:
    """Unified command-line interface supporting both sequential and parallel processing."""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.config: Optional[Any] = None  # Use Any to avoid type checking issues
        
    def setup_logging(self):
        """Configure logging for CLI usage."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('biotools_cli.log')
            ]
        )
    
    def create_output_dirs(self, base_dir: Path) -> Dict[str, Path]:
        """Create output directory structure."""
        dirs = {
            'raw': base_dir / 'raw',
            'processed': base_dir / 'processed', 
            'reports': base_dir / 'reports',
            'exports': base_dir / 'exports'
        }
        
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return dirs
    
    def setup_parallel_config(self, args) -> Optional[Any]:
        """Setup parallel processing configuration based on CLI arguments."""
        if not PARALLEL_AVAILABLE or not args.use_parallel:
            return None
            
        try:
            # Guard against missing modules
            if ParallelProcessingConfig is None or create_optimal_config is None:
                self.logger.warning("Parallel processing modules not available")
                return None
                
            if args.parallel_preset:
                if args.parallel_preset == "conservative":
                    config = ParallelProcessingConfig.create_conservative()
                elif args.parallel_preset == "aggressive":
                    config = ParallelProcessingConfig.create_aggressive()
                elif args.parallel_preset == "auto":
                    config = create_optimal_config("auto", "balanced")
                else:
                    config = ParallelProcessingConfig.create_default()
            else:
                config = ParallelProcessingConfig.create_default()
        except (NameError, AttributeError) as e:
            self.logger.warning(f"Parallel processing configuration failed: {e}")
            return None
        
        # Override with CLI arguments
        if args.max_concurrent_api:
            config.max_concurrent_api_requests = args.max_concurrent_api
        if args.max_concurrent_analysis:
            config.max_concurrent_analyses = args.max_concurrent_analysis
        if args.api_rate_limit:
            config.api_rate_limit_delay = args.api_rate_limit
        if args.batch_size:
            config.analysis_batch_size = args.batch_size
        if args.disable_pipeline:
            config.enable_pipeline_mode = False
        
        # Validate configuration
        if not config.validate():
            self.logger.error("Invalid parallel processing configuration")
            sys.exit(1)
        
        self.logger.info(f"Using parallel configuration: {config}")
        return config
    
    def progress_callback(self, progress: Any) -> None:
        """Handle pipeline progress updates."""
        if hasattr(progress, 'total') and progress.total > 0:
            fetch_pct = (progress.fetched / progress.total) * 100
            process_pct = (progress.processed / progress.total) * 100
            self.logger.info(f"Progress - Phase: {progress.phase}, "
                           f"Fetched: {progress.fetched}/{progress.total} ({fetch_pct:.1f}%), "
                           f"Processed: {progress.processed}/{progress.total} ({process_pct:.1f}%)")
    
    def error_callback(self, error_msg: str) -> None:
        """Handle pipeline errors."""
        self.logger.error(f"Pipeline error: {error_msg}")
    
    async def fetch_and_analyze_parallel(
        self,
        tool_ids: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        domain: Optional[str] = None,
        format_filter: Optional[str] = None,
        limit: Optional[int] = None,
        cache_dir: Optional[Path] = None
    ) -> List[QualityReport]:
        """Fetch and analyze tools using parallel processing."""
        
        if not PARALLEL_AVAILABLE or ProcessingPipeline is None:
            self.logger.error("Parallel processing not available")
            return []
        
        # Determine which tools to process
        if tool_ids:
            target_tools = tool_ids
        else:
            # Use async client to search for tools
            async with create_async_client(self.config, cache_dir) as client:
                tools_data = await client.search_tools(
                    query=search_query,
                    domain=domain,
                    format_filter=format_filter,
                    limit=limit
                )
                target_tools = [tool.get('biotoolsID') for tool in tools_data if tool.get('biotoolsID')]
        
        # Filter out None values and ensure all are strings
        target_tools = [tool_id for tool_id in target_tools if tool_id and isinstance(tool_id, str)]
        
        if not target_tools:
            self.logger.error("No tools found to process")
            return []
        
        # Create and run processing pipeline
        with ProcessingPipeline(
            config=self.config,
            cache_dir=cache_dir
        ) as pipeline:
            
            # Add callbacks for progress tracking
            pipeline.add_progress_callback(self.progress_callback)
            pipeline.add_error_callback(self.error_callback)
            
            # Process tools
            reports = await pipeline.process_tool_ids(target_tools)
            
            # Log final statistics
            stats = pipeline.get_stats()
            self.logger.info(f"Processing complete - Total: {stats.total_tools}, "
                           f"Successful: {stats.successful_analyses}, "
                           f"Time: {stats.total_time:.2f}s, "
                           f"Throughput: {stats.throughput:.1f} tools/sec")
            
            return reports
    
    
    def fetch_and_analyze_sequential(
        self,
        tool_ids: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        domain: Optional[str] = None,
        format_filter: Optional[str] = None,
        limit: Optional[int] = None,
        fetch_all: bool = False,
        batch_size_fetch: int = 1000,
        cache_dir: Optional[Path] = None
    ) -> List[QualityReport]:
        """Fetch and analyze tools using sequential processing (fallback)."""
        
        self.logger.info("Using sequential processing mode")
        
        # Use the unified sequential client
        with UnifiedBioToolsAPIClient(cache_dir=cache_dir) as client:
            tools_data = []
            
            try:
                if fetch_all:
                    self.logger.info("Fetching ALL bio.tools entries...")
                    tools_data = client.fetch_all_tools(batch_size=batch_size_fetch)
                    self.logger.info(f"Successfully fetched {len(tools_data)} total tools")
                
                elif tool_ids:
                    self.logger.info(f"Fetching {len(tool_ids)} specific tools...")
                    for tool_id in tool_ids:
                        self.logger.info(f"Fetching tool: {tool_id}")
                        tool_data = client.fetch_tool(tool_id)
                        if tool_data:
                            tools_data.append(tool_data)
                        else:
                            self.logger.warning(f"Tool not found: {tool_id}")
                
                elif search_query or domain or format_filter:
                    self.logger.info("Performing search query...")
                    
                    # Get search results using search_tools method
                    search_results = client.search_tools(
                        query=search_query,
                        domain=domain,
                        format_filter=format_filter,
                        limit=limit
                    )
                    total_found = len(search_results)
                    self.logger.info(f"Found {total_found} tools matching criteria")
                    
                    tools_data = search_results
                
                else:
                    self.logger.error("No search criteria provided")
                    return []
                
                # Save raw data
                if tools_data:
                    self.save_raw_data(tools_data, Path("./data/raw"))
                
                self.logger.info(f"Successfully fetched {len(tools_data)} tools")
                
                # Analyze tools sequentially
                analyzer = QualityAnalyzer()
                reports = []
                
                for i, tool_data in enumerate(tools_data, 1):
                    tool_id = tool_data.get('biotoolsID', f'unknown_{i}')
                    self.logger.info(f"Analyzing tool {i}/{len(tools_data)}: {tool_id}")
                    
                    try:
                        report = analyzer.analyze_tool(tool_data)
                        reports.append(report)
                    except Exception as e:
                        self.logger.error(f"Error analyzing tool {tool_id}: {e}")
                        continue
                
                self.logger.info(f"Analysis complete. Generated {len(reports)} reports")
                return reports
                
            except Exception as e:
                self.logger.error(f"Error in sequential processing: {e}")
                return []
    
    
    def save_raw_data(self, tools_data: List[Dict], output_dir: Path, filename_prefix: str = "biotools_raw") -> Path:
        """Save raw tool data to JSON file and individual tool files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save bulk data
        bulk_filename = f"{filename_prefix}_{timestamp}.json"
        bulk_filepath = output_dir / bulk_filename
        
        with open(bulk_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'fetched_at': datetime.now().isoformat(),
                    'total_tools': len(tools_data),
                    'source': 'bio.tools API'
                },
                'tools': tools_data
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Raw bulk data saved to: {bulk_filepath}")
        
        # Save individual tool files with tool names
        individual_dir = output_dir / "individual_tools"
        individual_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Saving individual tool files to: {individual_dir}")
        for i, tool_data in enumerate(tools_data, 1):
            tool_id = tool_data.get('biotoolsID', f'unknown_{i}')
            tool_name = tool_data.get('name', tool_id)
            
            # Create filename from tool name or tool_id
            display_name = tool_name if tool_name and tool_name != tool_id else tool_id
            
            # Clean name for filename - more aggressive cleaning for tool names
            safe_name = "".join(c for c in display_name if c.isalnum() or c in ('_', '-', '.', ' ')).strip()
            safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
            
            # Fallback to tool_id if name cleaning results in empty string
            if not safe_name:
                safe_name = "".join(c for c in tool_id if c.isalnum() or c in ('_', '-', '.')).rstrip()
                
            tool_filename = f"{safe_name}.json"
            tool_filepath = individual_dir / tool_filename
            
            with open(tool_filepath, 'w', encoding='utf-8') as f:
                json.dump(tool_data, f, indent=2, ensure_ascii=False)
            
            if i % 1000 == 0:
                self.logger.info(f"Saved {i}/{len(tools_data)} individual tool files")
        
        self.logger.info(f"All individual tool files saved to: {individual_dir}")
        return bulk_filepath
    
    def export_results(self, reports: List[QualityReport], dirs: Dict[str, Path], export_formats: List[str]) -> None:
        """Export results in specified formats."""
        if not reports:
            self.logger.warning("No reports to export")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for fmt in export_formats:
            if fmt == 'csv' or fmt == 'all':
                csv_path = dirs['exports'] / f"biotools_quality_{timestamp}.csv"
                self.export_to_csv(reports, csv_path)
            
            if fmt == 'excel' or fmt == 'all':
                excel_path = dirs['exports'] / f"biotools_quality_{timestamp}.xlsx"
                self.export_to_excel(reports, excel_path)
            
            if fmt == 'json' or fmt == 'all':
                json_path = dirs['exports'] / f"biotools_quality_{timestamp}.json"
                self.export_to_json(reports, json_path)
    
    def analyze_tools(self, tools_data: List[Dict]) -> List[QualityReport]:
        """Analyze tools and generate quality reports."""
        self.logger.info(f"Starting quality analysis of {len(tools_data)} tools...")
        
        analyzer = QualityAnalyzer()
        reports = []
        
        for i, tool_data in enumerate(tools_data, 1):
            tool_id = tool_data.get('biotoolsID', f'unknown_{i}')
            self.logger.info(f"Analyzing tool {i}/{len(tools_data)}: {tool_id}")
            
            try:
                report = analyzer.analyze_tool(tool_data)
                reports.append(report)
            except Exception as e:
                self.logger.error(f"Error analyzing tool {tool_id}: {e}")
                continue
        
        self.logger.info(f"Analysis complete. Generated {len(reports)} reports")
        return reports
    
    def export_to_csv(self, reports: List[QualityReport], output_path: Path) -> None:
        """Export quality reports to CSV format."""
        self.logger.info("Exporting to CSV...")
        
        # Flatten reports for CSV export
        rows = []
        for report in reports:
            row = {
                'tool_id': report.tool_id,
                'tool_name': report.tool_name,
                'overall_score': report.metrics.overall_score,
                'quality_grade': report.metrics.quality_grade,
                'standards_tier': report.metrics.standards_tier,
                'standards_score': report.metrics.standards_score,
                'completeness_tier': report.metrics.completeness_tier,
                'completeness_score': report.metrics.completeness_score,
                'schema_valid': report.metrics.schema_valid,
                'schema_errors': report.metrics.schema_errors,
                'schema_warnings': report.metrics.schema_warnings,
                'lint_issues': report.metrics.lint_issues,
                'critical_issues': report.metrics.critical_issues,
                'error_issues': report.metrics.error_issues,
                'warning_issues': report.metrics.warning_issues,
                'info_issues': report.metrics.info_issues,
                'field_completeness': report.metrics.field_completeness,
                'required_fields_complete': report.metrics.required_fields_complete,
                'recommended_fields_complete': report.metrics.recommended_fields_complete,
                'url_health': report.metrics.url_health,
                'edam_consistency': report.metrics.edam_consistency,
                'publication_quality': report.metrics.publication_quality,
                'has_functions': report.metrics.has_functions,
                'has_documentation': report.metrics.has_documentation,
                'has_publications': report.metrics.has_publications,
                'has_contacts': report.metrics.has_contacts,
                'analysis_date': report.metrics.analysis_date,
                'tool_last_update': report.metrics.tool_last_update,
                'summary': report.summary,
                'recommendations_count': len(report.recommendations),
                'priority_fixes_count': len(report.priority_fixes)
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        self.logger.info(f"CSV export saved to: {output_path}")
    
    def export_to_excel(self, reports: List[QualityReport], output_path: Path) -> None:
        """Export quality reports to Excel format with multiple sheets."""
        self.logger.info("Exporting to Excel...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_rows = []
            for report in reports:
                row = {
                    'Tool ID': report.tool_id,
                    'Tool Name': report.tool_name,
                    'Overall Score': report.metrics.overall_score,
                    'Quality Grade': report.metrics.quality_grade,
                    'Standards Tier': report.metrics.standards_tier,
                    'Completeness Tier': report.metrics.completeness_tier,
                    'Schema Valid': report.metrics.schema_valid,
                    'Total Issues': report.metrics.lint_issues,
                    'Critical Issues': report.metrics.critical_issues
                }
                summary_rows.append(row)
            
            summary_df = pd.DataFrame(summary_rows)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed metrics sheet
            detailed_rows = []
            for report in reports:
                row = {
                    'Tool ID': report.tool_id,
                    'Tool Name': report.tool_name,
                    'Overall Score': report.metrics.overall_score,
                    'Standards Score': report.metrics.standards_score,
                    'Completeness Score': report.metrics.completeness_score,
                    'Field Completeness': report.metrics.field_completeness,
                    'Required Fields Complete': report.metrics.required_fields_complete,
                    'Recommended Fields Complete': report.metrics.recommended_fields_complete,
                    'URL Health': report.metrics.url_health,
                    'EDAM Consistency': report.metrics.edam_consistency,
                    'Publication Quality': report.metrics.publication_quality,
                    'Has Functions': report.metrics.has_functions,
                    'Has Documentation': report.metrics.has_documentation,
                    'Has Publications': report.metrics.has_publications,
                    'Has Contacts': report.metrics.has_contacts,
                    'Analysis Date': report.metrics.analysis_date,
                    'Tool Last Update': report.metrics.tool_last_update
                }
                detailed_rows.append(row)
            
            detailed_df = pd.DataFrame(detailed_rows)
            detailed_df.to_excel(writer, sheet_name='Detailed Metrics', index=False)
            
            # Issues summary sheet
            issues_rows = []
            for report in reports:
                row = {
                    'Tool ID': report.tool_id,
                    'Tool Name': report.tool_name,
                    'Total Issues': report.metrics.lint_issues,
                    'Critical Issues': report.metrics.critical_issues,
                    'Error Issues': report.metrics.error_issues,
                    'Warning Issues': report.metrics.warning_issues,
                    'Info Issues': report.metrics.info_issues,
                    'Schema Errors': report.metrics.schema_errors,
                    'Schema Warnings': report.metrics.schema_warnings,
                    'Recommendations Count': len(report.recommendations),
                    'Priority Fixes Count': len(report.priority_fixes)
                }
                issues_rows.append(row)
            
            issues_df = pd.DataFrame(issues_rows)
            issues_df.to_excel(writer, sheet_name='Issues Summary', index=False)
        
        self.logger.info(f"Excel export saved to: {output_path}")
    
    def export_to_json(self, reports: List[QualityReport], output_path: Path) -> None:
        """Export quality reports to JSON format."""
        self.logger.info("Exporting to JSON...")
        
        # Convert reports to dict format
        reports_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_reports': len(reports),
                'generator': 'bio.tools-quality-cli'
            },
            'reports': [report.to_dict() for report in reports]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reports_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"JSON export saved to: {output_path}")
        
        # Also save individual processed analysis files with tool names
        self.save_individual_processed_reports(reports, output_path.parent)
    
    def save_individual_processed_reports(self, reports: List[QualityReport], output_dir: Path) -> None:
        """Save individual processed analysis reports with tool names."""
        individual_processed_dir = output_dir / "individual_analyses"
        individual_processed_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Saving individual processed analysis files to: {individual_processed_dir}")
        
        for i, report in enumerate(reports, 1):
            tool_id = report.tool_id
            tool_name = report.tool_name
            
            # Create filename from tool name or tool_id
            display_name = tool_name if tool_name and tool_name != tool_id else tool_id
            
            # Clean name for filename - more aggressive cleaning for tool names
            safe_name = "".join(c for c in display_name if c.isalnum() or c in ('_', '-', '.', ' ')).strip()
            safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
            
            # Fallback to tool_id if name cleaning results in empty string
            if not safe_name:
                safe_name = "".join(c for c in tool_id if c.isalnum() or c in ('_', '-', '.')).rstrip()
                
            analysis_filename = f"{safe_name}.json"
            analysis_filepath = individual_processed_dir / analysis_filename
            
            # Save the individual analysis report
            with open(analysis_filepath, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            
            if i % 1000 == 0:
                self.logger.info(f"Saved {i}/{len(reports)} individual analysis files")
        
        self.logger.info(f"All individual analysis files saved to: {individual_processed_dir}")
    
    async def run_async(self, args):
        """Main async CLI execution logic."""
        self.logger.info("Starting unified bio.tools quality analysis CLI")
        
        # Setup parallel processing configuration
        self.config = self.setup_parallel_config(args)
        
        # Create output directories
        output_base = Path(args.output_dir)
        dirs = self.create_output_dirs(output_base)
        
        # Setup cache directory
        cache_dir = dirs['raw'] / 'cache' if args.cache else None
        
        try:
            # Fetch and analyze data
            if args.use_parallel and PARALLEL_AVAILABLE:
                reports = await self.fetch_and_analyze_parallel(
                    tool_ids=args.tool_id,
                    search_query=args.search,
                    domain=args.domain,
                    format_filter=args.format,
                    limit=args.limit,
                    cache_dir=cache_dir
                )
            else:
                if args.use_parallel and not PARALLEL_AVAILABLE:
                    self.logger.warning("Parallel processing requested but not available, using sequential mode")
                reports = self.fetch_and_analyze_sequential(
                    tool_ids=args.tool_id,
                    search_query=args.search,
                    domain=args.domain,
                    format_filter=args.format,
                    limit=args.limit,
                    fetch_all=args.all,
                    batch_size_fetch=args.batch_size_fetch,
                    cache_dir=cache_dir
                )
            
            if not reports:
                self.logger.error("No analysis reports generated. Exiting.")
                return 1
            
            # Export results
            export_formats = []
            if args.export_csv:
                export_formats.append('csv')
            if args.export_excel:
                export_formats.append('excel')
            if args.export_json:
                export_formats.append('json')
            if args.export_all or not export_formats:
                export_formats = ['all']
            
            self.export_results(reports, dirs, export_formats)
            
            self.logger.info("Unified CLI execution completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"CLI execution failed: {e}")
            return 1
    
    def run(self, args):
        """Main CLI execution entry point."""
        # Check if parallel processing is requested and available
        if args.use_parallel and PARALLEL_AVAILABLE:
            return asyncio.run(self.run_async(args))
        else:
            # For sequential mode, we don't need async
            self.logger.info("Starting unified bio.tools quality analysis CLI (sequential mode)")
            
            # Create output directories
            output_base = Path(args.output_dir)
            dirs = self.create_output_dirs(output_base)
            
            # Setup cache directory
            cache_dir = dirs['raw'] / 'cache' if args.cache else None
            
            try:
                # Fetch and analyze data sequentially
                reports = self.fetch_and_analyze_sequential(
                    tool_ids=args.tool_id,
                    search_query=args.search,
                    domain=args.domain,
                    format_filter=args.format,
                    limit=args.limit,
                    fetch_all=args.all,
                    batch_size_fetch=args.batch_size_fetch,
                    cache_dir=cache_dir
                )
                
                if not reports:
                    self.logger.error("No analysis reports generated. Exiting.")
                    return 1
                
                # Export results
                export_formats = []
                if args.export_csv:
                    export_formats.append('csv')
                if args.export_excel:
                    export_formats.append('excel')
                if args.export_json:
                    export_formats.append('json')
                if args.export_all or not export_formats:
                    export_formats = ['all']
                
                self.export_results(reports, dirs, export_formats)
                
                self.logger.info("Unified CLI execution completed successfully")
                return 0
                
            except Exception as e:
                self.logger.error(f"CLI execution failed: {e}")
                return 1


def create_parser():
    """Create command-line argument parser with unified features."""
    parser = argparse.ArgumentParser(
        description="Unified Bio.tools Quality Analysis CLI with Sequential and Parallel Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch ALL biotools entries and export to all formats
  python -m src.cli --all --export-all
  
  # Sequential processing (default)
  python -m src.cli --tool-id blast --tool-id clustalw --export-all
  
  # Parallel processing for better performance
  python -m src.cli --search "alignment" --limit 50 --use-parallel --export-csv
  
  # Auto-tuned parallel configuration
  python -m src.cli --domain "Genomics" --limit 20 --use-parallel --parallel-preset auto
  
  # Conservative parallel settings for slower systems
  python -m src.cli --search "phylogeny" --use-parallel --parallel-preset conservative
  
  # Custom parallel configuration
  python -m src.cli --search "blast" --use-parallel --max-concurrent-api 3 --batch-size 5
        """
    )
    
    # Data fetching options
    fetch_group = parser.add_argument_group('Data Fetching')
    fetch_group.add_argument('--tool-id', action='append', 
                           help='Specific tool ID(s) to fetch (can be used multiple times)')
    fetch_group.add_argument('--search', 
                           help='Search query for tools')
    fetch_group.add_argument('--domain', 
                           help='Filter by scientific domain (e.g., "Genomics", "Proteomics")')
    fetch_group.add_argument('--format', 
                           help='Filter by data format')
    fetch_group.add_argument('--limit', type=int, 
                           help='Limit number of tools to fetch')
    fetch_group.add_argument('--all', action='store_true',
                           help='Fetch ALL biotools entries (overrides other search options)')
    fetch_group.add_argument('--batch-size-fetch', type=int, default=1000,
                           help='Batch size for fetching all tools (default: 1000)')
    
    # Parallel processing options (only shown if available)
    if PARALLEL_AVAILABLE:
        parallel_group = parser.add_argument_group('Parallel Processing (Enhanced Performance)')
        parallel_group.add_argument('--use-parallel', action='store_true',
                                  help='Use parallel processing for improved performance')
        parallel_group.add_argument('--parallel-preset', choices=['conservative', 'default', 'aggressive', 'auto'],
                                  help='Use predefined parallel processing settings')
        parallel_group.add_argument('--max-concurrent-api', type=int,
                                  help='Maximum concurrent API requests')
        parallel_group.add_argument('--max-concurrent-analysis', type=int,
                                  help='Maximum concurrent analyses')
        parallel_group.add_argument('--api-rate-limit', type=float,
                                  help='Rate limit delay between API requests (seconds)')
        parallel_group.add_argument('--batch-size', type=int,
                                  help='Batch size for processing')
        parallel_group.add_argument('--disable-pipeline', action='store_true',
                                  help='Disable pipeline mode (process all fetching before analysis)')
    
    # Processing options
    process_group = parser.add_argument_group('Processing')
    process_group.add_argument('--cache', action='store_true', default=True,
                             help='Use local caching for API requests (default: True)')
    process_group.add_argument('--no-cache', dest='cache', action='store_false',
                             help='Disable caching')
    
    # Export options
    export_group = parser.add_argument_group('Export Formats')
    export_group.add_argument('--export-csv', action='store_true',
                            help='Export analysis results to CSV')
    export_group.add_argument('--export-excel', action='store_true',
                            help='Export analysis results to Excel')
    export_group.add_argument('--export-json', action='store_true',
                            help='Export analysis results to JSON')
    export_group.add_argument('--export-all', action='store_true',
                            help='Export to all formats (CSV, Excel, JSON)')
    
    # Output options
    output_group = parser.add_argument_group('Output')
    output_group.add_argument('--output-dir', default='./data',
                            help='Base output directory (default: ./data)')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validation
    if not any([args.tool_id, args.search, args.domain, args.format, args.all]):
        parser.error("Must specify at least one of: --tool-id, --search, --domain, --format, or --all")
    
    # Set default for parallel processing if not available
    if not hasattr(args, 'use_parallel'):
        args.use_parallel = False
    
    # Check for parallel processing availability
    if hasattr(args, 'use_parallel') and args.use_parallel and not PARALLEL_AVAILABLE:
        print("Warning: Parallel processing requested but dependencies not available.")
        print("Please install: pip install aiohttp psutil")
        print("Falling back to sequential mode.")
        args.use_parallel = False
    
    if not any([args.export_csv, args.export_excel, args.export_json, args.export_all]):
        print("Warning: No export format specified. Results will not be saved.")
    
    # Run CLI
    cli = UnifiedBioToolsCLI()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())
