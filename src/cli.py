#!/usr/bin/env python3
"""
Bio.tools Quality Analysis CLI

Command-line interface for fetching bio.tools data and generating quality reports
in multiple formats (JSON, CSV, Excel).
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

import pandas as pd

# Add src to path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

try:
    from collectors.biotools_api import BioToolsAPIClient
    from analyzers.quality_analyzer import QualityAnalyzer, QualityReport
    from reporters.quality_reporter import QualityReporter
    from utils.logger import Logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available in the src directory.")
    sys.exit(1)


class BioToolsCLI:
    """Command-line interface for bio.tools quality analysis."""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
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
    
    def fetch_tool_data(self, 
                       tool_ids: Optional[List[str]] = None,
                       search_query: Optional[str] = None,
                       domain: Optional[str] = None,
                       format_filter: Optional[str] = None,
                       limit: Optional[int] = None,
                       cache_dir: Optional[Path] = None) -> List[Dict]:
        """Fetch tool data from bio.tools API."""
        
        self.logger.info("Initializing bio.tools API client...")
        client = BioToolsAPIClient(cache_dir=cache_dir)
        
        tools_data = []
        
        try:
            if tool_ids:
                self.logger.info(f"Fetching {len(tool_ids)} specific tools...")
                for tool_id in tool_ids:
                    self.logger.info(f"Fetching tool: {tool_id}")
                    tool_data = client.get_tool(tool_id)
                    if tool_data:
                        tools_data.append(tool_data)
                    else:
                        self.logger.warning(f"Tool not found: {tool_id}")
            
            elif search_query or domain or format_filter:
                self.logger.info("Performing search query...")
                search_params = {}
                if search_query:
                    search_params['query'] = search_query
                if domain:
                    search_params['domain'] = domain
                if format_filter:
                    search_params['format'] = format_filter
                
                # Get search results using list_tools method
                search_response = client.list_tools(**search_params)
                search_results = search_response.get('list', [])
                total_found = len(search_results)
                self.logger.info(f"Found {total_found} tools matching criteria")
                
                # Apply limit if specified
                if limit and limit < total_found:
                    search_results = search_results[:limit]
                    self.logger.info(f"Limited to first {limit} tools")
                
                tools_data = search_results
            
            else:
                self.logger.error("No search criteria provided. Use --tool-id, --search, --domain, or --format")
                return []
            
            self.logger.info(f"Successfully fetched {len(tools_data)} tools")
            return tools_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return []
    
    def save_raw_data(self, tools_data: List[Dict], output_dir: Path, filename_prefix: str = "biotools_raw") -> Path:
        """Save raw tool data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'fetched_at': datetime.now().isoformat(),
                    'total_tools': len(tools_data),
                    'source': 'bio.tools API'
                },
                'tools': tools_data
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Raw data saved to: {filepath}")
        return filepath
    
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
    
    def run(self, args):
        """Main CLI execution logic."""
        self.logger.info("Starting bio.tools quality analysis CLI")
        
        # Create output directories
        output_base = Path(args.output_dir)
        dirs = self.create_output_dirs(output_base)
        
        # Fetch data
        cache_dir = dirs['raw'] / 'cache' if args.cache else None
        tools_data = self.fetch_tool_data(
            tool_ids=args.tool_id,
            search_query=args.search,
            domain=args.domain, 
            format_filter=args.format,
            limit=args.limit,
            cache_dir=cache_dir
        )
        
        if not tools_data:
            self.logger.error("No tools found or fetched. Exiting.")
            return 1
        
        # Save raw data
        if args.save_raw:
            raw_file = self.save_raw_data(tools_data, dirs['raw'])
        
        # Analyze tools
        if args.analyze:
            reports = self.analyze_tools(tools_data)
            
            if not reports:
                self.logger.error("No analysis reports generated. Exiting.")
                return 1
            
            # Generate timestamp for export files
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export to different formats
            if args.export_csv or args.export_all:
                csv_path = dirs['exports'] / f"biotools_quality_{timestamp}.csv"
                self.export_to_csv(reports, csv_path)
            
            if args.export_excel or args.export_all:
                excel_path = dirs['exports'] / f"biotools_quality_{timestamp}.xlsx"
                self.export_to_excel(reports, excel_path)
            
            if args.export_json or args.export_all:
                json_path = dirs['exports'] / f"biotools_quality_{timestamp}.json"
                self.export_to_json(reports, json_path)
        
        self.logger.info("CLI execution completed successfully")
        return 0


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Bio.tools Quality Analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch specific tools
  python -m src.cli --tool-id blast --tool-id clustalw --analyze --export-all
  
  # Search and analyze tools
  python -m src.cli --search "alignment" --limit 10 --analyze --export-csv
  
  # Fetch by domain
  python -m src.cli --domain "Genomics" --limit 50 --analyze --export-excel
  
  # Just fetch raw data without analysis
  python -m src.cli --search "phylogeny" --save-raw --no-analyze
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
    
    # Processing options
    process_group = parser.add_argument_group('Processing')
    process_group.add_argument('--analyze', action='store_true', default=True,
                             help='Perform quality analysis (default: True)')
    process_group.add_argument('--no-analyze', dest='analyze', action='store_false',
                             help='Skip quality analysis, only fetch raw data')
    process_group.add_argument('--save-raw', action='store_true', default=True,
                             help='Save raw API data (default: True)')
    process_group.add_argument('--cache', action='store_true', default=True,
                             help='Use local caching for API requests (default: True)')
    
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
    if not any([args.tool_id, args.search, args.domain, args.format]):
        parser.error("Must specify at least one of: --tool-id, --search, --domain, or --format")
    
    if args.analyze and not any([args.export_csv, args.export_excel, args.export_json, args.export_all]):
        print("Warning: Analysis enabled but no export format specified. Results will not be saved.")
    
    # Run CLI
    cli = BioToolsCLI()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())
