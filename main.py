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
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.biotools_api import BioToolsAPIClient
from src.analyzers.quality_analyzer import QualityAnalyzer
from src.reporters.visualizer import QualityReporter


# Configure logging
def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('biotools_quality_analysis.log')
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """Bio.tools annotation quality evaluation tool."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


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
@click.pass_context
def analyze(ctx, tool_id, collection, query, max_tools, output_dir, format, 
           cache_dir, generate_charts, create_dashboard):
    """Analyze bio.tools entries for quality metrics."""
    
    logger = logging.getLogger(__name__)
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Initialize components
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        analyzer = QualityAnalyzer()
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
        
        click.echo(f"\nAnalysis complete! Results saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
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
@click.pass_context
def validate(ctx, tool_id, cache_dir, show_details):
    """Validate a single tool against bio.tools schema and standards."""
    
    logger = logging.getLogger(__name__)
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Initialize components
        api_client = BioToolsAPIClient(cache_dir=cache_dir)
        analyzer = QualityAnalyzer()
        
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
    
    logger = logging.getLogger(__name__)
    verbose = ctx.obj.get('verbose', False)
    
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
    
    logger = logging.getLogger(__name__)
    verbose = ctx.obj.get('verbose', False)
    
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
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx):
    """Show bio.tools registry statistics."""
    
    logger = logging.getLogger(__name__)
    verbose = ctx.obj.get('verbose', False)
    
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
        if verbose:
            raise
        click.echo(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli()
