"""
Command-line interface for bio.tools annotation quality evaluation.

This module provides a CLI for running quality analysis on bio.tools entries
with various options for data collection, analysis, and reporting.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List
import json

import click

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.collectors.biotools_api import BioToolsAPIClient
from src.analyzers.quality_analyzer import QualityAnalyzer
from src.reporters.visualizer import QualityReporter
from src.utils.logger import Logger
from src.utils.config import get_config_manager


# Configure logging with new centralized system
def setup_logging(verbose: bool = False, config_path: Optional[str] = None) -> None:
    """Set up logging configuration using centralized logger."""
    if config_path and Path(config_path).exists():
        Logger.setup_from_config_file(config_path)
    else:
        level = 'DEBUG' if verbose else 'INFO'
        Logger.setup_logging(level=level)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def cli(ctx, verbose, config):
    """Bio.tools annotation quality evaluation tool."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config'] = config
    setup_logging(verbose, config)


@cli.command()
@click.option('--tool-id', '-t', help='Specific bio.tools ID to analyze')
@click.option('--collection', '-c', help='Collection ID to analyze')
@click.option('--query', '-q', help='Search query for tools')
@click.option('--max-tools', '-m', type=int, help='Maximum number of tools to analyze')
@click.option('--output-dir', '-o', default='data/reports', 
              help='Output directory for reports')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'excel', 'html']), 
              default='json', help='Output format')
@click.option('--cache-dir', default='data/cache', 
              help='Directory for caching API responses')
@click.option('--generate-charts', is_flag=True, 
              help='Generate visualization charts')
@click.option('--create-dashboard', is_flag=True,
              help='Create interactive HTML dashboard')
@click.option('--per-tool-json', is_flag=True,
              help='Create individual JSON files per tool (in addition to combined output)')
@click.option('--per-tool-formats', multiple=True,
              type=click.Choice(['json', 'csv', 'excel', 'html']),
              help='Create individual files per tool in specified formats (can specify multiple)')
@click.option('--no-clean', is_flag=True,
              help='Disable data cleaning before analysis')
@click.option('--aggressive-clean', is_flag=True,
              help='Use aggressive data cleaning (removes more empty values)')
@click.pass_context
def analyze(ctx, tool_id, collection, query, max_tools, output_dir, format, 
           cache_dir, generate_charts, create_dashboard, per_tool_json, per_tool_formats, no_clean, aggressive_clean):
    """Analyze bio.tools entries for quality metrics."""
    
    logger = Logger.get_logger(__name__)
    config_path = ctx.obj.get('config')
    
    # Load configuration if provided
    if config_path:
        config_manager = get_config_manager(config_path)
        logger.info(f"Loaded configuration from: {config_path}")
    else:
        config_manager = get_config_manager()
        logger.info("Using default configuration")
    
    try:
        # Initialize components
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        analyzer = QualityAnalyzer(
            clean_data=not no_clean,
            aggressive_cleaning=aggressive_clean
        )
        reporter = QualityReporter(output_dir=output_dir)
        
        # Collect tools data
        tools_data = []
        
        if tool_id:
            logger.info(f"Fetching tool: {tool_id}")
            tool_data = api_client.get_tool(tool_id)
            tools_data = [tool_data]
        
        elif collection:
            logger.info(f"Fetching tools from collection: {collection}")
            tools_data = api_client.get_tools_by_collection(collection)
        
        elif query:
            logger.info(f"Searching tools with query: {query}")
            tools_data = api_client.search_tools(query, max_results=max_tools)
        
        else:
            logger.info("Fetching all tools (limited by max_tools)")
            tools_data = list(api_client.get_all_tools(max_tools=max_tools or 100))
        
        if not tools_data:
            click.echo("No tools found to analyze.")
            return
        
        click.echo(f"Analyzing {len(tools_data)} tools...")
        
        # Analyze tools
        reports = analyzer.analyze_tools_batch(tools_data)
        
        if not reports:
            click.echo("No analysis reports generated.")
            return
        
        # Generate outputs
        click.echo(f"Generating reports in {format} format...")
        
        if format == 'json':
            output_file = reporter.export_detailed_data(reports, format='json')
            click.echo(f"Detailed data exported to: {output_file}")
        
        elif format == 'csv':
            output_file = reporter.export_detailed_data(reports, format='csv')
            click.echo(f"CSV data exported to: {output_file}")
        
        elif format == 'excel':
            output_file = reporter.export_detailed_data(reports, format='excel')
            click.echo(f"Excel report exported to: {output_file}")
        
        elif format == 'html':
            summary_report = reporter.generate_summary_report(reports, "summary_report.md")
            click.echo("Summary report generated")
        
        # Generate summary report
        summary = reporter.generate_summary_report(reports, "summary_report.md")
        click.echo("\n" + "="*50)
        click.echo("SUMMARY")
        click.echo("="*50)
        click.echo(summary)
        
        # Generate charts if requested
        if generate_charts:
            click.echo("Generating visualization charts...")
            chart_paths = reporter.create_detailed_charts(reports)
            for path in chart_paths:
                click.echo(f"Chart saved: {path}")
        
        # Create dashboard if requested
        if create_dashboard:
            click.echo("Creating interactive dashboard...")
            dashboard_path = reporter.create_quality_dashboard(reports)
            click.echo(f"Dashboard created: {dashboard_path}")
        
        # Create per-tool JSON files if requested
        if per_tool_json:
            click.echo("Creating individual JSON files per tool...")
            per_tool_files = reporter.export_per_tool_json(reports, output_dir)
            click.echo(f"Created {len(per_tool_files)} individual JSON files")
            click.echo(f"Per-tool files saved to: {Path(output_dir) / 'per_tool_analysis'}")
        
        # Create per-tool files in specified formats
        if per_tool_formats:
            click.echo(f"Creating individual files per tool in {len(per_tool_formats)} format(s)...")
            exported_files_dict = reporter.export_per_tool_all_formats(reports, output_dir, list(per_tool_formats))
            total_files = sum(len(files) for files in exported_files_dict.values())
            click.echo(f"Created {total_files} individual files across {len(per_tool_formats)} format(s)")
            
            # Show breakdown by format
            for fmt, files in exported_files_dict.items():
                click.echo(f"  {fmt.upper()}: {len(files)} files")
            click.echo(f"Per-tool files saved to: {Path(output_dir) / 'per_tool_analysis'}")
        
        click.echo(f"\nAnalysis complete! Results saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--tool-id', '-t', required=True, help='bio.tools ID to validate')
@click.option('--cache-dir', default='data/cache', 
              help='Directory for caching API responses')
@click.option('--show-details', is_flag=True, 
              help='Show detailed validation results')
@click.option('--no-clean', is_flag=True,
              help='Disable data cleaning before validation')
@click.option('--aggressive-clean', is_flag=True,
              help='Use aggressive data cleaning')
@click.pass_context
def validate(ctx, tool_id, cache_dir, show_details, no_clean, aggressive_clean):
    """Validate a single tool against bio.tools schema and standards."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        # Initialize components
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        analyzer = QualityAnalyzer(
            clean_data=not no_clean,
            aggressive_cleaning=aggressive_clean
        )
        
        # Fetch tool data
        click.echo(f"Fetching tool: {tool_id}")
        tool_data = api_client.get_tool(tool_id)
        
        # Analyze tool
        click.echo("Performing quality analysis...")
        report = analyzer.analyze_tool(tool_data)
        
        # Display results
        click.echo(f"\n{'='*50}")
        click.echo(f"QUALITY REPORT FOR {tool_id.upper()}")
        click.echo(f"{'='*50}")
        
        metrics = report.metrics
        
        # Overall quality
        click.echo(f"Overall Quality: Grade {metrics.quality_grade} ({metrics.overall_score}/100)")
        click.echo(f"Standards Tier: {metrics.standards_tier} ({metrics.standards_score}/100)")
        click.echo(f"Schema Valid: {'✅ Yes' if metrics.schema_valid else '❌ No'}")
        
        # Issues summary
        if metrics.critical_issues > 0:
            click.echo(f"🔴 Critical Issues: {metrics.critical_issues}")
        if metrics.error_issues > 0:
            click.echo(f"❌ Error Issues: {metrics.error_issues}")
        if metrics.warning_issues > 0:
            click.echo(f"⚠️  Warning Issues: {metrics.warning_issues}")
        if metrics.info_issues > 0:
            click.echo(f"ℹ️  Info Issues: {metrics.info_issues}")
        
        # Completeness
        click.echo(f"Field Completeness: {metrics.field_completeness:.1%}")
        click.echo(f"Required Fields: {'✅' if metrics.required_fields_complete else '❌'}")
        
        # Content features
        features = []
        if metrics.has_functions:
            features.append("Functions")
        if metrics.has_documentation:
            features.append("Documentation")
        if metrics.has_publications:
            features.append("Publications")
        if metrics.has_contacts:
            features.append("Contacts")
        
        if features:
            click.echo(f"Content Features: {', '.join(features)}")
        else:
            click.echo("Content Features: None")
        
        # Priority fixes
        if report.priority_fixes:
            click.echo(f"\n🔧 PRIORITY FIXES:")
            for fix in report.priority_fixes[:5]:
                click.echo(f"  • {fix}")
        
        # Recommendations
        if report.recommendations:
            click.echo(f"\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations[:5]:
                click.echo(f"  • {rec}")
        
        # Detailed results if requested
        if show_details:
            click.echo(f"\n📋 DETAILED VALIDATION RESULTS:")
            
            # Schema errors
            if report.schema_results.get('errors'):
                click.echo("\nSchema Errors:")
                for error in report.schema_results['errors'][:10]:
                    click.echo(f"  • {error.get('path', 'unknown')}: {error.get('message', 'unknown error')}")
            
            # Lint issues
            if report.lint_issues:
                click.echo(f"\nLint Issues (showing first 10):")
                for issue in report.lint_issues[:10]:
                    level_symbol = {
                        'critical': '🔴',
                        'error': '❌',
                        'warning': '⚠️',
                        'info': 'ℹ️'
                    }.get(issue.level.value, '?')
                    click.echo(f"  {level_symbol} {issue.code}: {issue.message}")
                    if issue.suggestion:
                        click.echo(f"    💡 {issue.suggestion}")
        
        click.echo(f"\n{report.summary}")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command('per-tool-analysis')
@click.option('--tool-id', '-t', multiple=True, help='Specific bio.tools ID(s) to analyze')
@click.option('--collection', '-c', help='Collection ID to analyze')
@click.option('--query', '-q', help='Search query for tools')
@click.option('--max-tools', '-m', type=int, help='Maximum number of tools to analyze')
@click.option('--output-dir', '-o', default='data/reports', 
              help='Output directory for individual reports')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'excel', 'html', 'all']), 
              default='json', help='Output format for individual files (all creates files in all formats)')
@click.option('--cache-dir', default='data/cache', 
              help='Directory for caching API responses')
@click.option('--no-clean', is_flag=True,
              help='Disable data cleaning before analysis')
@click.option('--aggressive-clean', is_flag=True,
              help='Use aggressive data cleaning (removes more empty values)')
@click.pass_context
def per_tool_analysis(ctx, tool_id, collection, query, max_tools, output_dir, format, 
                     cache_dir, no_clean, aggressive_clean):
    """Analyze bio.tools entries and create individual JSON files per tool."""
    
    logger = Logger.get_logger(__name__)
    config_path = ctx.obj.get('config')
    
    # Load configuration if provided
    if config_path:
        config_manager = get_config_manager(config_path)
        logger.info(f"Loaded configuration from: {config_path}")
    else:
        config_manager = get_config_manager()
        logger.info("Using default configuration")
    
    try:
        # Initialize components
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        analyzer = QualityAnalyzer(
            clean_data=not no_clean,
            aggressive_cleaning=aggressive_clean
        )
        reporter = QualityReporter(output_dir=output_dir)
        
        # Collect tools data
        tools_data = []
        
        if tool_id:
            logger.info(f"Fetching {len(tool_id)} specific tool(s): {', '.join(tool_id)}")
            for tid in tool_id:
                try:
                    tool_data = api_client.get_tool(tid)
                    tools_data.append(tool_data)
                except Exception as e:
                    logger.warning(f"Failed to fetch tool {tid}: {e}")
                    continue
        
        elif collection:
            logger.info(f"Fetching tools from collection: {collection}")
            tools_data = api_client.get_tools_by_collection(collection)
        
        elif query:
            logger.info(f"Searching tools with query: {query}")
            tools_data = api_client.search_tools(query, max_results=max_tools)
        
        else:
            logger.info("Fetching all tools (limited by max_tools)")
            tools_data = list(api_client.get_all_tools(max_tools=max_tools or 100))
        
        if not tools_data:
            click.echo("No tools found to analyze.")
            return
        
        # Limit tools if max_tools is specified
        if max_tools and len(tools_data) > max_tools:
            tools_data = tools_data[:max_tools]
        
        click.echo(f"Analyzing {len(tools_data)} tools for per-tool analysis...")
        
        # Analyze tools
        reports = analyzer.analyze_tools_batch(tools_data)
        
        if not reports:
            click.echo("No analysis reports generated.")
            return
        
        # Generate individual files based on format
        click.echo(f"Creating individual {format} files per tool...")
        
        exported_files = []
        exported_files_dict = {}
        
        if format == 'all':
            # Export all formats
            exported_files_dict = reporter.export_per_tool_all_formats(reports, output_dir)
            total_files = sum(len(files) for files in exported_files_dict.values())
            click.echo(f"Successfully created {total_files} individual files in all formats")
            
            # Show breakdown by format
            for fmt, files in exported_files_dict.items():
                click.echo(f"  {fmt.upper()}: {len(files)} files")
        
        elif format == 'json':
            exported_files = reporter.export_per_tool_json(reports, output_dir)
            click.echo(f"Successfully created {len(exported_files)} individual JSON files")
        
        elif format == 'csv':
            exported_files = reporter.export_per_tool_csv(reports, output_dir)
            click.echo(f"Successfully created {len(exported_files)} individual CSV files")
        
        elif format == 'excel':
            exported_files = reporter.export_per_tool_excel(reports, output_dir)
            click.echo(f"Successfully created {len(exported_files)} individual Excel files")
        
        elif format == 'html':
            exported_files = reporter.export_per_tool_html(reports, output_dir)
            click.echo(f"Successfully created {len(exported_files)} individual HTML files")
        
        click.echo(f"Files saved to: {Path(output_dir) / 'per_tool_analysis'}")
        
        # Show some sample filenames
        if format != 'all' and exported_files:
            click.echo(f"\nSample files created:")
            for file_path in exported_files[:3]:  # Show first 3
                filename = Path(file_path).name
                click.echo(f"  - {filename}")
            if len(exported_files) > 3:
                click.echo(f"  ... and {len(exported_files) - 3} more files")
        elif format == 'all' and exported_files_dict:
            click.echo(f"\nSample files created:")
            sample_count = 0
            for fmt, files in exported_files_dict.items():
                if files and sample_count < 2:  # Show 2 examples max
                    filename = Path(files[0]).name
                    click.echo(f"  - {filename} ({fmt.upper()})")
                    sample_count += 1
        
        # Generate quick summary
        if reports:
            avg_score = sum(r.metrics.overall_score for r in reports) / len(reports)
            grade_counts = {}
            for report in reports:
                grade = report.metrics.quality_grade
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            click.echo(f"\n📊 ANALYSIS SUMMARY:")
            click.echo(f"Average quality score: {avg_score:.1f}/100")
            click.echo(f"Grade distribution: {dict(sorted(grade_counts.items()))}")
        
        click.echo(f"\nPer-tool analysis complete! Individual files saved to: {Path(output_dir) / 'per_tool_analysis'}")
        
    except Exception as e:
        logger.error(f"Per-tool analysis failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--collection', '-c', help='Collection ID to analyze')
@click.option('--query', '-q', help='Search query for tools')
@click.option('--max-tools', '-m', type=int, default=50,
              help='Maximum number of tools to compare')
@click.option('--output-dir', '-o', default='data/reports',
              help='Output directory for comparison report')
@click.option('--cache-dir', default='data/cache',
              help='Directory for caching API responses')
@click.pass_context
def compare(ctx, collection, query, max_tools, output_dir, cache_dir):
    """Compare quality metrics across multiple tools."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        # Initialize components
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        analyzer = QualityAnalyzer()
        reporter = QualityReporter(output_dir=output_dir)
        
        # Collect tools data
        if collection:
            click.echo(f"Fetching tools from collection: {collection}")
            tools_data = api_client.get_tools_by_collection(collection)
        elif query:
            click.echo(f"Searching tools with query: {query}")
            tools_data = api_client.search_tools(query, max_results=max_tools)
        else:
            click.echo("Either --collection or --query must be specified")
            return
        
        if len(tools_data) < 2:
            click.echo("Need at least 2 tools for comparison")
            return
        
        # Limit to max_tools
        if len(tools_data) > max_tools:
            tools_data = tools_data[:max_tools]
        
        click.echo(f"Comparing {len(tools_data)} tools...")
        
        # Analyze tools
        reports = analyzer.analyze_tools_batch(tools_data)
        
        if not reports:
            click.echo("No analysis reports generated.")
            return
        
        # Generate comparison report
        click.echo("Generating comparison visualizations...")
        
        # Create dashboard
        dashboard_path = reporter.create_quality_dashboard(reports, "comparison_dashboard.html")
        
        # Create detailed charts
        chart_paths = reporter.create_detailed_charts(reports, "all")
        
        # Generate summary
        summary = reporter.generate_summary_report(reports, "comparison_summary.md")
        
        # Show quick comparison
        click.echo(f"\n{'='*60}")
        click.echo("QUALITY COMPARISON SUMMARY")
        click.echo(f"{'='*60}")
        
        # Sort by overall score
        sorted_reports = sorted(reports, key=lambda r: r.metrics.overall_score, reverse=True)
        
        click.echo(f"{'Rank':<4} {'Tool ID':<20} {'Grade':<6} {'Score':<6} {'Tier':<12}")
        click.echo("-" * 60)
        
        for i, report in enumerate(sorted_reports[:10], 1):
            metrics = report.metrics
            click.echo(f"{i:<4} {report.tool_id:<20} {metrics.quality_grade:<6} "
                      f"{metrics.overall_score:<6.1f} {metrics.standards_tier:<12}")
        
        if len(sorted_reports) > 10:
            click.echo(f"... and {len(sorted_reports) - 10} more tools")
        
        click.echo(f"\nDashboard created: {dashboard_path}")
        click.echo(f"Charts saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--input-file', '-i', required=True, type=click.Path(exists=True),
              help='Input file with tool data (JSON)')
@click.option('--output-dir', '-o', default='data/reports',
              help='Output directory for reports')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'excel', 'html']), 
              default='json', help='Output format')
@click.pass_context
def batch(ctx, input_file, output_dir, format):
    """Analyze tools from a local JSON file."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        # Load tools data from file
        click.echo(f"Loading tools data from: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            tools_data = json.load(f)
        
        if not isinstance(tools_data, list):
            tools_data = [tools_data]
        
        click.echo(f"Loaded {len(tools_data)} tools")
        
        # Initialize components
        analyzer = QualityAnalyzer()
        reporter = QualityReporter(output_dir=output_dir)
        
        # Analyze tools
        click.echo("Analyzing tools...")
        reports = analyzer.analyze_tools_batch(tools_data)
        
        if not reports:
            click.echo("No analysis reports generated.")
            return
        
        # Generate outputs
        click.echo(f"Generating reports in {format} format...")
        
        output_file = None
        if format == 'json':
            output_file = reporter.export_detailed_data(reports, format='json')
        elif format == 'csv':
            output_file = reporter.export_detailed_data(reports, format='csv')
        elif format == 'excel':
            output_file = reporter.export_detailed_data(reports, format='excel')
        elif format == 'html':
            summary_report = reporter.generate_summary_report(reports, "batch_summary.md")
            output_file = "batch_summary.md"
        
        # Generate summary
        summary = reporter.generate_summary_report(reports)
        click.echo("\n" + summary)
        
        if output_file:
            click.echo(f"\nBatch analysis complete! Results saved to: {output_file}")
        else:
            click.echo(f"\nBatch analysis complete! Results saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--cache-dir', default='data/cache', 
              help='Directory for caching API responses')
@click.option('--max-tools', '-m', type=int, 
              help='Maximum number of tools to cache (default: all)')
@click.option('--batch-size', '-b', type=int, default=25,
              help='Number of tools to fetch per API request')
@click.option('--resume', is_flag=True,
              help='Resume caching from where it left off')
@click.option('--force', is_flag=True,
              help='Force re-caching of existing entries')
@click.pass_context
def cache(ctx, cache_dir, max_tools, batch_size, resume, force):
    """Cache all bio.tools entries locally for offline processing."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        # Initialize API client
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        
        # Get registry statistics first
        click.echo("Fetching bio.tools registry statistics...")
        stats_data = api_client.get_stats()
        total_tools = stats_data.get('totalentries', 0)
        
        click.echo(f"Total tools in registry: {total_tools:,}")
        
        if max_tools:
            tools_to_cache = min(max_tools, total_tools)
            click.echo(f"Caching first {tools_to_cache:,} tools")
        else:
            tools_to_cache = total_tools
            click.echo(f"Caching all {tools_to_cache:,} tools")
        
        # Check existing cache if resuming
        cache_path = Path(cache_dir)
        cached_files = 0
        if cache_path.exists():
            cached_files = len(list(cache_path.glob("tool__*.json")))
            click.echo(f"Found {cached_files:,} already cached tools")
            
            if resume and not force:
                click.echo("Resume mode: will skip already cached tools")
            elif force:
                click.echo("Force mode: will re-cache all tools")
            else:
                click.echo("Normal mode: will cache new tools only")
        
        # Start caching process
        click.echo(f"\nStarting caching process...")
        click.echo(f"Batch size: {batch_size}")
        click.echo("-" * 50)
        
        cached_count = 0
        skipped_count = 0
        failed_count = 0
        
        with click.progressbar(
            length=tools_to_cache, 
            label='Caching tools',
            show_eta=True,
            show_percent=True
        ) as bar:
            
            for tool_data in api_client.get_all_tools(
                batch_size=batch_size, 
                max_tools=max_tools
            ):
                try:
                    tool_id = tool_data.get('biotoolsID', 'unknown')
                    
                    # Check if already cached (unless force mode)
                    if not force and resume:
                        # Check if this specific tool is already cached
                        tool_cache_path = cache_path / f"tool__{hash(tool_id)}.json"
                        if tool_cache_path.exists():
                            skipped_count += 1
                            bar.update(1)
                            continue
                    
                    # Fetch full tool details (this will cache automatically)
                    full_tool_data = api_client.get_tool(tool_id)
                    cached_count += 1
                    
                    # Update progress every 10 tools
                    if cached_count % 10 == 0:
                        bar.label = f'Cached: {cached_count:,}, Skipped: {skipped_count:,}, Failed: {failed_count:,}'
                    
                except Exception as e:
                    tool_id = tool_data.get('biotoolsID', 'unknown') if 'tool_data' in locals() else 'unknown'
                    logger.warning(f"Failed to cache tool {tool_id}: {e}")
                    failed_count += 1
                
                bar.update(1)
                
                # Check if we've reached the limit
                if max_tools and (cached_count + skipped_count + failed_count) >= max_tools:
                    break
        
        # Final summary
        click.echo(f"\n{'='*50}")
        click.echo("CACHING SUMMARY")
        click.echo(f"{'='*50}")
        click.echo(f"Total processed: {cached_count + skipped_count + failed_count:,}")
        click.echo(f"Successfully cached: {cached_count:,}")
        click.echo(f"Skipped (already cached): {skipped_count:,}")
        click.echo(f"Failed: {failed_count:,}")
        
        # Show cache directory info
        if cache_path.exists():
            final_cached_files = len(list(cache_path.glob("tool__*.json")))
            cache_size = sum(f.stat().st_size for f in cache_path.glob("*.json")) / (1024 * 1024)
            click.echo(f"\nCache directory: {cache_path}")
            click.echo(f"Total cached files: {final_cached_files:,}")
            click.echo(f"Cache size: {cache_size:.1f} MB")
        
        click.echo(f"\nCaching complete! Use 'process-cache' command to analyze cached data.")
        
    except Exception as e:
        logger.error(f"Caching failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--cache-dir', default='data/cache', 
              help='Directory containing cached tool data')
@click.option('--output-dir', '-o', default='data/reports', 
              help='Output directory for reports')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'csv', 'excel', 'html']), 
              default='json', help='Output format')
@click.option('--max-tools', '-m', type=int, 
              help='Maximum number of cached tools to process')
@click.option('--generate-charts', is_flag=True, 
              help='Generate visualization charts')
@click.option('--create-dashboard', is_flag=True,
              help='Create interactive HTML dashboard')
@click.option('--per-tool-json', is_flag=True,
              help='Create individual JSON files per tool (in addition to combined output)')
@click.option('--per-tool-formats', multiple=True,
              type=click.Choice(['json', 'csv', 'excel', 'html']),
              help='Create individual files per tool in specified formats (can specify multiple)')
@click.option('--no-clean', is_flag=True,
              help='Disable data cleaning before analysis')
@click.option('--aggressive-clean', is_flag=True,
              help='Use aggressive data cleaning')
@click.option('--chunk-size', type=int, default=1000,
              help='Process tools in chunks of this size')
@click.pass_context
def process_cache(ctx, cache_dir, output_dir, format, max_tools, generate_charts, 
                 create_dashboard, per_tool_json, per_tool_formats, no_clean, aggressive_clean, chunk_size):
    """Process cached bio.tools data to generate quality reports."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            click.echo(f"Cache directory not found: {cache_dir}")
            click.echo("Run 'cache' command first to download tools data.")
            return
        
        # Find all cached tool files
        cached_files = list(cache_path.glob("tool_*.json"))
        if not cached_files:
            click.echo(f"No cached tool files found in {cache_dir}")
            return
        
        total_tools = len(cached_files)
        tools_to_process = min(max_tools, total_tools) if max_tools else total_tools
        
        click.echo(f"Found {total_tools:,} cached tools")
        click.echo(f"Processing {tools_to_process:,} tools")
        
        # Initialize analyzer and reporter
        analyzer = QualityAnalyzer(
            clean_data=not no_clean,
            aggressive_cleaning=aggressive_clean
        )
        reporter = QualityReporter(output_dir=output_dir)
        
        # Process tools in chunks
        all_reports = []
        processed_count = 0
        failed_count = 0
        
        click.echo(f"\nProcessing tools in chunks of {chunk_size:,}")
        click.echo("-" * 50)
        
        with click.progressbar(
            length=tools_to_process, 
            label='Processing tools',
            show_eta=True,
            show_percent=True
        ) as bar:
            
            for i in range(0, tools_to_process, chunk_size):
                chunk_files = cached_files[i:i + chunk_size]
                chunk_tools = []
                
                # Load tools data from cache files
                for cache_file in chunk_files:
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # Check if this is a single tool or a list response
                            if isinstance(data, dict):
                                if 'biotoolsID' in data:
                                    # Single tool data
                                    chunk_tools.append(data)
                                elif 'list' in data:
                                    # API response with list of tools
                                    tools_in_file = data.get('list', [])
                                    chunk_tools.extend(tools_in_file)
                                    
                                    # If we have a max limit, truncate
                                    if max_tools and len(chunk_tools) > max_tools:
                                        chunk_tools = chunk_tools[:max_tools]
                                        break
                            elif isinstance(data, list):
                                # Direct list of tools
                                chunk_tools.extend(data)
                                
                                # If we have a max limit, truncate
                                if max_tools and len(chunk_tools) > max_tools:
                                    chunk_tools = chunk_tools[:max_tools]
                                    break
                                    
                    except Exception as e:
                        logger.warning(f"Failed to load cached file {cache_file}: {e}")
                        failed_count += 1
                
                # Process chunk
                if chunk_tools:
                    try:
                        chunk_reports = analyzer.analyze_tools_batch(chunk_tools)
                        all_reports.extend(chunk_reports)
                        processed_count += len(chunk_reports)
                        
                        bar.label = f'Processed: {processed_count:,}, Failed: {failed_count:,}'
                    except Exception as e:
                        logger.error(f"Failed to process chunk: {e}")
                        failed_count += len(chunk_tools)
                
                bar.update(len(chunk_files))
                
                # Stop if we've reached the limit
                if max_tools and processed_count >= max_tools:
                    break
        
        if not all_reports:
            click.echo("No reports generated.")
            return
        
        click.echo(f"\n{'='*50}")
        click.echo("PROCESSING SUMMARY")
        click.echo(f"{'='*50}")
        click.echo(f"Successfully processed: {processed_count:,}")
        click.echo(f"Failed: {failed_count:,}")
        
        # Generate outputs
        click.echo(f"\nGenerating reports in {format} format...")
        
        output_files = []
        
        if format == 'json':
            output_file = reporter.export_detailed_data(all_reports, format='json')
            output_files.append(output_file)
            click.echo(f"JSON data exported to: {output_file}")
        
        elif format == 'csv':
            output_file = reporter.export_detailed_data(all_reports, format='csv')
            output_files.append(output_file)
            click.echo(f"CSV data exported to: {output_file}")
        
        elif format == 'excel':
            output_file = reporter.export_detailed_data(all_reports, format='excel')
            output_files.append(output_file)
            click.echo(f"Excel report exported to: {output_file}")
        
        elif format == 'html':
            summary_report = reporter.generate_summary_report(all_reports, "cache_processing_summary.md")
            output_files.append("cache_processing_summary.md")
            click.echo("Summary report generated")
        
        # Generate summary report
        summary = reporter.generate_summary_report(all_reports, "cache_processing_summary.md")
        click.echo("\n" + "="*50)
        click.echo("ANALYSIS SUMMARY")
        click.echo("="*50)
        click.echo(summary)
        
        # Generate charts if requested
        if generate_charts:
            click.echo("\nGenerating visualization charts...")
            chart_paths = reporter.create_detailed_charts(all_reports)
            output_files.extend(chart_paths)
            for path in chart_paths:
                click.echo(f"Chart saved: {path}")
        
        # Create dashboard if requested
        if create_dashboard:
            click.echo("\nCreating interactive dashboard...")
            dashboard_path = reporter.create_quality_dashboard(all_reports, "cache_analysis_dashboard.html")
            output_files.append(dashboard_path)
            click.echo(f"Dashboard created: {dashboard_path}")
        
        # Create per-tool JSON files if requested
        if per_tool_json:
            click.echo("\nCreating individual JSON files per tool...")
            per_tool_files = reporter.export_per_tool_json(all_reports, output_dir)
            output_files.extend(per_tool_files)
            click.echo(f"Created {len(per_tool_files)} individual JSON files")
            click.echo(f"Per-tool files saved to: {Path(output_dir) / 'per_tool_analysis'}")
        
        # Create per-tool files in specified formats
        if per_tool_formats:
            click.echo(f"\nCreating individual files per tool in {len(per_tool_formats)} format(s)...")
            exported_files_dict = reporter.export_per_tool_all_formats(all_reports, output_dir, list(per_tool_formats))
            total_files = sum(len(files) for files in exported_files_dict.values())
            for files in exported_files_dict.values():
                output_files.extend(files)
            click.echo(f"Created {total_files} individual files across {len(per_tool_formats)} format(s)")
            
            # Show breakdown by format
            for fmt, files in exported_files_dict.items():
                click.echo(f"  {fmt.upper()}: {len(files)} files")
            click.echo(f"Per-tool files saved to: {Path(output_dir) / 'per_tool_analysis'}")
        
        click.echo(f"\nProcessing complete! Results saved to: {output_dir}")
        
        # Show final statistics
        if all_reports:
            sorted_reports = sorted(all_reports, key=lambda r: r.metrics.overall_score, reverse=True)
            avg_score = sum(r.metrics.overall_score for r in all_reports) / len(all_reports)
            
            click.echo(f"\n📊 QUALITY STATISTICS:")
            click.echo(f"Average quality score: {avg_score:.1f}/100")
            click.echo(f"Best tool: {sorted_reports[0].tool_id} ({sorted_reports[0].metrics.overall_score:.1f}/100)")
            click.echo(f"Worst tool: {sorted_reports[-1].tool_id} ({sorted_reports[-1].metrics.overall_score:.1f}/100)")
            
            # Grade distribution
            grade_counts = {}
            for report in all_reports:
                grade = report.metrics.quality_grade
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            click.echo(f"\n📈 GRADE DISTRIBUTION:")
            for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']:
                count = grade_counts.get(grade, 0)
                percentage = (count / len(all_reports)) * 100 if all_reports else 0
                click.echo(f"  {grade}: {count:,} tools ({percentage:.1f}%)")
        
    except Exception as e:
        logger.error(f"Cache processing failed: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--cache-dir', default='data/cache', 
              help='Directory containing cached data')
@click.option('--clear', is_flag=True,
              help='Clear all cached data')
@click.pass_context
def cache_info(ctx, cache_dir, clear):
    """Show information about cached data or clear cache."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        # Initialize API client to get cache info
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        
        if clear:
            click.echo("Clearing cache...")
            deleted_count = api_client.clear_cache()
            click.echo(f"Deleted {deleted_count} cached files.")
            return
        
        # Get cache information
        cache_info = api_client.get_cache_info()
        
        click.echo(f"\n{'='*40}")
        click.echo("CACHE INFORMATION")
        click.echo(f"{'='*40}")
        
        if cache_info['exists']:
            click.echo(f"Cache directory: {cache_info['path']}")
            click.echo(f"Total files: {cache_info['file_count']:,}")
            click.echo(f"Tool files: {cache_info['tool_files']:,}")
            click.echo(f"Cache size: {cache_info['total_size_mb']:.1f} MB")
            
            if cache_info['tool_files'] > 0:
                click.echo(f"\nTo process cached data, run:")
                click.echo(f"  python main.py process-cache --cache-dir {cache_dir}")
                click.echo(f"\nTo clear cache, run:")
                click.echo(f"  python main.py cache-info --cache-dir {cache_dir} --clear")
        else:
            click.echo("No cache directory found.")
            click.echo(f"\nTo start caching tools, run:")
            click.echo(f"  python main.py cache --cache-dir {cache_dir}")
        
    except Exception as e:
        logger.error(f"Failed to get cache info: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx):
    """Show bio.tools registry statistics."""
    
    logger = Logger.get_logger(__name__)
    
    try:
        # Initialize API client
        api_client = BioToolsAPIClient()
        
        # Get registry statistics
        click.echo("Fetching bio.tools registry statistics...")
        stats_data = api_client.get_stats()
        
        click.echo(f"\n{'='*40}")
        click.echo("BIO.TOOLS REGISTRY STATISTICS")
        click.echo(f"{'='*40}")
        
        # Display key statistics
        for key, value in stats_data.items():
            if isinstance(value, (int, float)):
                click.echo(f"{key.replace('_', ' ').title()}: {value:,}")
            elif isinstance(value, dict):
                click.echo(f"\n{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)):
                        click.echo(f"  {sub_key.replace('_', ' ').title()}: {sub_value:,}")
        
    except Exception as e:
        logger.error(f"Failed to fetch statistics: {e}")
        verbose = ctx.obj.get('verbose', False)
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
