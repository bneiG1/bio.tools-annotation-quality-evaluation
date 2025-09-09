#!/usr/bin/env python3
"""
Bio.tools CLI - Unified Data Fetcher and Quality Analyzer

Single comprehensive command-line interface for fetching bio.tools data and 
performing quality analysis. Includes both basic data export and full quality 
assessment capabilities.
"""

import sys
import os
import argparse
import json
import logging
import time
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin, urlencode
from collections import Counter

# Add project root to path to handle imports correctly
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Try to import quality analysis modules
try:
    from src.collectors.biotools_api import BioToolsAPIClient as FullBioToolsAPIClient
    from src.analyzers.quality_analyzer import QualityAnalyzer
    from src.utils.logger import Logger
    QUALITY_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Quality analysis modules not available: {e}")
    print("Will use basic data fetching only.")
    QUALITY_ANALYSIS_AVAILABLE = False
    FullBioToolsAPIClient = None
    QualityAnalyzer = None


class BioToolsAPIClient:
    """Bio.tools API client for data fetching."""
    
    BASE_URL = "https://bio.tools/api/"
    TOOLS_ENDPOINT = "tool/"
    
    def __init__(self, cache_dir: Optional[Path] = None, rate_limit_delay: float = 1.0):
        self.cache_dir = cache_dir
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cache_path(self, tool_id: str) -> Optional[Path]:
        """Get cache file path for a tool."""
        if self.cache_dir:
            return self.cache_dir / f"tool_{tool_id}.json"
        return None
    
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load data from cache file."""
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def _save_to_cache(self, cache_path: Path, data: Dict):
        """Save data to cache file."""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def get_tool(self, tool_id: str) -> Optional[Dict]:
        """Get a specific tool by ID."""
        # Check cache first
        if self.cache_dir:
            cache_path = self._get_cache_path(tool_id)
            if cache_path:
                cached_data = self._load_from_cache(cache_path)
                if cached_data:
                    return cached_data
        
        # Fetch from API
        self._rate_limit()
        url = urljoin(self.BASE_URL, f"{self.TOOLS_ENDPOINT}{tool_id}/")
        
        try:
            response = self.session.get(url, params={'format': 'json'})
            response.raise_for_status()
            data = response.json()
            
            # Save to cache
            if self.cache_dir:
                cache_path = self._get_cache_path(tool_id)
                if cache_path:
                    self._save_to_cache(cache_path, data)
            
            return data
        except Exception as e:
            print(f"Error fetching tool {tool_id}: {e}")
            return None
    
    def search_tools(self, query: Optional[str] = None, domain: Optional[str] = None, 
                    format_filter: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Search for tools with given criteria."""
        params = {"format": "json", "sort": "lastUpdate", "ord": "desc"}
        if query:
            params["q"] = query
        if domain:
            params["domain"] = domain
        if format_filter:
            params["format_filter"] = format_filter
        
        all_tools = []
        page = 1
        
        while True:
            params["page"] = str(page)
            self._rate_limit()
            
            try:
                url = urljoin(self.BASE_URL, self.TOOLS_ENDPOINT)
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                tools = data.get('list', [])
                if not tools:
                    break
                
                all_tools.extend(tools)
                
                # Check if we've reached the limit
                if limit and len(all_tools) >= limit:
                    all_tools = all_tools[:limit]
                    break
                
                # Check if there are more pages
                if not data.get('next'):
                    break
                
                page += 1
                
            except Exception as e:
                print(f"Error searching tools (page {page}): {e}")
                break
        
        return all_tools


class BioToolsCLI:
    """Unified CLI for bio.tools data fetching and quality analysis."""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
    def setup_logging(self):
        """Configure logging."""
        # Create logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(logs_dir / 'biotools_analysis.log')
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
    
    def fetch_tools_data(self, tool_ids: Optional[List[str]] = None,
                        search_query: Optional[str] = None,
                        domain: Optional[str] = None,
                        format_filter: Optional[str] = None,
                        limit: Optional[int] = None,
                        cache_dir: Optional[Path] = None) -> List[Dict]:
        """Fetch tools data from bio.tools API."""
        
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
                self.logger.info("Performing search...")
                tools_data = client.search_tools(
                    query=search_query,
                    domain=domain,
                    format_filter=format_filter,
                    limit=limit
                )
                self.logger.info(f"Found {len(tools_data)} tools")
            
        except Exception as e:
            self.logger.error(f"Error fetching tools data: {e}")
            return []
        
        return tools_data
    
    def save_raw_data(self, tools_data: List[Dict], output_dir: Path, filename_prefix: str = "biotools_raw") -> Path:
        """Save raw tool data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tools_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Raw data saved to: {filepath}")
        return filepath
    
    def analyze_tools(self, tools_data: List[Dict]) -> List:
        """Analyze tools and generate quality reports (if quality analysis is available)."""
        if not QUALITY_ANALYSIS_AVAILABLE:
            self.logger.warning("Quality analysis not available. Install required modules for full analysis.")
            return []
        
        self.logger.info(f"Starting quality analysis of {len(tools_data)} tools...")
        
        try:
            # Initialize quality analyzer
            if not QualityAnalyzer:
                self.logger.error("QualityAnalyzer not available")
                return []
                
            quality_analyzer = QualityAnalyzer()
            
            reports = []
            for i, tool_data in enumerate(tools_data, 1):
                tool_id = tool_data.get('biotoolsID', f'tool_{i}')
                self.logger.info(f"Analyzing tool {i}/{len(tools_data)}: {tool_id}")
                
                report = quality_analyzer.analyze_tool(tool_data)
                if report:
                    reports.append(report)
            
            self.logger.info(f"Analysis complete. Generated {len(reports)} reports")
            return reports
            
        except Exception as e:
            self.logger.error(f"Error during quality analysis: {e}")
            return []
    
    def export_results(self, tools_data: List[Dict], reports: List, dirs: Dict[str, Path], export_formats: List[str]):
        """Export results in specified formats."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Determine if we have quality analysis
        has_quality_analysis = QUALITY_ANALYSIS_AVAILABLE and reports
        
        if has_quality_analysis:
            self._export_comprehensive_results(reports, dirs, timestamp, export_formats)
        else:
            self._export_basic_results(tools_data, dirs, timestamp, export_formats)
    
    def _export_comprehensive_results(self, reports: List, dirs: Dict[str, Path], timestamp: str, export_formats: List[str]):
        """Export comprehensive quality analysis results."""
        
        if 'csv' in export_formats or 'all' in export_formats:
            csv_path = dirs['processed'] / f"biotools_detailed_{timestamp}.csv"
            self._export_comprehensive_csv(reports, csv_path)
        
        if 'json' in export_formats or 'all' in export_formats:
            json_path = dirs['processed'] / f"biotools_analysis_{timestamp}.json"
            self._export_comprehensive_json(reports, json_path)
        
        if 'excel' in export_formats or 'all' in export_formats:
            excel_path = dirs['processed'] / f"biotools_report_{timestamp}.xlsx"
            self._export_comprehensive_excel(reports, excel_path)
        
        # Always generate summary report
        summary_text = self._generate_summary_report(reports)
        summary_path = dirs['reports'] / f"summary_report_{timestamp}.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        self.logger.info(f"Summary report saved to: {summary_path}")
        
        # Export to exports directory for compatibility
        exports_csv_path = dirs['exports'] / f"quality_summary_{timestamp}.csv"
        self._export_quality_summary_csv(reports, exports_csv_path)
    
    def _export_basic_results(self, tools_data: List[Dict], dirs: Dict[str, Path], timestamp: str, export_formats: List[str]):
        """Export basic tool data without quality analysis."""
        
        if 'csv' in export_formats or 'all' in export_formats:
            csv_path = dirs['processed'] / f"biotools_basic_{timestamp}.csv"
            self._export_basic_csv(tools_data, csv_path)
        
        if 'json' in export_formats or 'all' in export_formats:
            json_path = dirs['processed'] / f"biotools_basic_{timestamp}.json"
            self._export_basic_json(tools_data, json_path)
        
        if 'excel' in export_formats or 'all' in export_formats:
            excel_path = dirs['processed'] / f"biotools_basic_{timestamp}.xlsx"
            self._export_basic_excel(tools_data, excel_path)
    
    def _export_comprehensive_csv(self, reports: List, output_path: Path):
        """Export comprehensive CSV with all quality metrics."""
        rows = []
        for report in reports:
            # Convert QualityReport to dict for CSV export
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
        self.logger.info(f"Comprehensive CSV saved to: {output_path}")
    
    def _export_comprehensive_json(self, reports: List, output_path: Path):
        """Export comprehensive JSON with all analysis results."""
        export_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_reports': len(reports),
                'analysis_type': 'comprehensive_quality_analysis',
                'generator': 'bio.tools-unified-cli'
            },
            'reports': []
        }
        
        for report in reports:
            report_dict = {
                'tool_id': report.tool_id,
                'tool_name': report.tool_name,
                'metrics': {
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
                    'tool_last_update': report.metrics.tool_last_update
                },
                'summary': report.summary,
                'recommendations': report.recommendations,
                'priority_fixes': report.priority_fixes,
                'standards_analysis': report.standards_analysis,
                'completeness_analysis': report.completeness_analysis,
                'schema_results': report.schema_results,
                'lint_issues_count': len(report.lint_issues) if hasattr(report, 'lint_issues') else 0
            }
            export_data['reports'].append(report_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Comprehensive JSON saved to: {output_path}")
    
    def _export_comprehensive_excel(self, reports: List, output_path: Path):
        """Export comprehensive Excel with multiple sheets."""
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
        
        self.logger.info(f"Comprehensive Excel saved to: {output_path}")
    
    def _export_quality_summary_csv(self, reports: List, output_path: Path):
        """Export quality summary CSV for exports directory."""
        rows = []
        for report in reports:
            row = {
                'tool_id': report.tool_id,
                'tool_name': report.tool_name,
                'overall_score': report.metrics.overall_score,
                'quality_grade': report.metrics.quality_grade,
                'standards_tier': report.metrics.standards_tier,
                'completeness_tier': report.metrics.completeness_tier,
                'total_issues': report.metrics.lint_issues,
                'critical_issues': report.metrics.critical_issues
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        self.logger.info(f"Quality summary CSV saved to: {output_path}")
    
    def _export_basic_csv(self, tools_data: List[Dict], output_path: Path):
        """Export basic tools data to CSV format."""
        rows = []
        for tool in tools_data:
            # Helper function to safely join lists
            def safe_join(data, key, separator=', '):
                value = data.get(key, [])
                if isinstance(value, list):
                    return separator.join(str(v) for v in value if v)
                return str(value) if value else ''
            
            def safe_join_nested(data, key, subkey, separator=', '):
                items = data.get(key, [])
                if isinstance(items, list):
                    values = [item.get(subkey, '') for item in items if isinstance(item, dict)]
                    return separator.join(str(v) for v in values if v)
                return ''
            
            row = {
                'biotoolsID': tool.get('biotoolsID', ''),
                'name': tool.get('name', ''),
                'description': tool.get('description', ''),
                'homepage': tool.get('homepage', ''),
                'version': safe_join(tool, 'version'),
                'topics': safe_join_nested(tool, 'topic', 'term'),
                'operations': safe_join_nested(tool, 'function', 'operation') if 'function' in tool else '',
                'toolType': safe_join(tool, 'toolType'),
                'license': tool.get('license', ''),
                'maturity': tool.get('maturity', ''),
                'cost': tool.get('cost', ''),
                'accessibility': safe_join(tool, 'accessibility'),
                'publication_count': len(tool.get('publication', [])),
                'link_count': len(tool.get('link', [])),
                'contact_count': len(tool.get('credit', [])),
                'last_update': tool.get('lastUpdate', ''),
                'additionDate': tool.get('additionDate', ''),
                'owner': tool.get('owner', '')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, encoding='utf-8')
        self.logger.info(f"Basic CSV export saved to: {output_path}")
    
    def _export_basic_json(self, tools_data: List[Dict], output_path: Path):
        """Export basic tools data to JSON format."""
        output_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'total_tools': len(tools_data),
                'source': 'bio.tools API',
                'processed_by': 'bio.tools-unified-cli'
            },
            'tools': tools_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Basic JSON export saved to: {output_path}")
    
    def _export_basic_excel(self, tools_data: List[Dict], output_path: Path):
        """Export basic tools data to Excel format."""
        # Reuse the CSV logic but save to Excel
        rows = []
        for tool in tools_data:
            def safe_join(data, key, separator=', '):
                value = data.get(key, [])
                if isinstance(value, list):
                    return separator.join(str(v) for v in value if v)
                return str(value) if value else ''
            
            def safe_join_nested(data, key, subkey, separator=', '):
                items = data.get(key, [])
                if isinstance(items, list):
                    values = [item.get(subkey, '') for item in items if isinstance(item, dict)]
                    return separator.join(str(v) for v in values if v)
                return ''
            
            row = {
                'biotoolsID': tool.get('biotoolsID', ''),
                'name': tool.get('name', ''),
                'description': tool.get('description', ''),
                'homepage': tool.get('homepage', ''),
                'version': safe_join(tool, 'version'),
                'topics': safe_join_nested(tool, 'topic', 'term'),
                'operations': safe_join_nested(tool, 'function', 'operation') if 'function' in tool else '',
                'toolType': safe_join(tool, 'toolType'),
                'license': tool.get('license', ''),
                'maturity': tool.get('maturity', ''),
                'cost': tool.get('cost', ''),
                'accessibility': safe_join(tool, 'accessibility'),
                'publication_count': len(tool.get('publication', [])),
                'link_count': len(tool.get('link', [])),
                'contact_count': len(tool.get('credit', [])),
                'last_update': tool.get('lastUpdate', ''),
                'additionDate': tool.get('additionDate', ''),
                'owner': tool.get('owner', '')
            }
            rows.append(row)
        
        df = pd.DataFrame(rows)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Tools Data', index=False)
        
        self.logger.info(f"Basic Excel export saved to: {output_path}")
    
    def _generate_summary_report(self, reports: List) -> str:
        """Generate a text summary report."""
        if not reports:
            return "No quality reports available."
        
        total_tools = len(reports)
        scores = [r.metrics.overall_score for r in reports]
        grades = [r.metrics.quality_grade for r in reports]
        
        # Calculate statistics
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        grade_counts = Counter(grades)
        
        report = f"""
BIO.TOOLS QUALITY ANALYSIS SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==========================================

OVERVIEW
--------
Total tools analyzed: {total_tools}
Average quality score: {avg_score:.1f}
Highest score: {max_score:.1f}
Lowest score: {min_score:.1f}

GRADE DISTRIBUTION
------------------
"""
        
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = grade_counts.get(grade, 0)
            percentage = (count / total_tools) * 100 if total_tools > 0 else 0
            report += f"Grade {grade}: {count} tools ({percentage:.1f}%)\n"
        
        # Top issues
        all_issues = []
        for rep in reports:
            if hasattr(rep, 'lint_issues'):
                all_issues.extend(rep.lint_issues)
        
        if all_issues:
            issue_codes = [issue.code for issue in all_issues if hasattr(issue, 'code')]
            top_issues = Counter(issue_codes).most_common(5)
            
            report += f"\nTOP ISSUES\n----------\n"
            for issue_code, count in top_issues:
                report += f"{issue_code}: {count} occurrences\n"
        
        report += f"\nDETAILS\n-------\n"
        for rep in reports:
            report += f"- {rep.tool_id}: Score {rep.metrics.overall_score:.1f} (Grade {rep.metrics.quality_grade})\n"
        
        return report
    
    def _print_summary(self, tools_data: List[Dict], reports: List):
        """Print execution summary."""
        has_quality_analysis = QUALITY_ANALYSIS_AVAILABLE and reports
        
        print("\n" + "="*60)
        print("BIO.TOOLS CLI - EXECUTION SUMMARY")
        print("="*60)
        print(f"Total tools fetched: {len(tools_data)}")
        print(f"Quality reports generated: {len(reports) if reports else 0}")
        print(f"Quality analysis available: {'Yes' if has_quality_analysis else 'No'}")
        
        if has_quality_analysis:
            scores = [r.metrics.overall_score for r in reports]
            grades = [r.metrics.quality_grade for r in reports]
            grade_counts = Counter(grades)
            
            print(f"\nQuality Score Statistics:")
            print(f"  Average score: {sum(scores)/len(scores):.1f}")
            print(f"  Highest score: {max(scores):.1f}")
            print(f"  Lowest score: {min(scores):.1f}")
            
            print(f"\nGrade Distribution:")
            for grade in ['A', 'B', 'C', 'D', 'F']:
                count = grade_counts.get(grade, 0)
                print(f"  Grade {grade}: {count} tools")
        
        output_dir = Path('./data').resolve()
        print(f"\nOutput files saved to: {output_dir}")
        print("="*60)
    
    def run(self, args):
        """Main CLI execution."""
        self.logger.info("Starting bio.tools CLI")
        
        try:
            # Create output directories
            base_dir = Path(args.output_dir)
            dirs = self.create_output_dirs(base_dir)
            
            # Setup cache directory
            cache_dir = dirs['raw'] / 'cache' if args.cache else None
            
            # Fetch tools data
            tools_data = self.fetch_tools_data(
                tool_ids=args.tool_id,
                search_query=args.search,
                domain=args.domain,
                format_filter=args.format,
                limit=args.limit,
                cache_dir=cache_dir
            )
            
            if not tools_data:
                self.logger.error("No tools data fetched. Exiting.")
                return 1
            
            # Save raw data
            if args.save_raw:
                self.save_raw_data(tools_data, dirs['raw'])
            
            # Perform quality analysis if requested
            reports = []
            if args.analyze:
                reports = self.analyze_tools(tools_data)
            
            # Export results
            export_formats = []
            if args.export_csv:
                export_formats.append('csv')
            if args.export_json:
                export_formats.append('json')
            if args.export_excel:
                export_formats.append('excel')
            if args.export_all or not export_formats:
                export_formats = ['all']
            
            self.export_results(tools_data, reports, dirs, export_formats)
            
            # Print summary
            self._print_summary(tools_data, reports)
            
            self.logger.info("CLI execution completed successfully")
            return 0
            
        except Exception as e:
            self.logger.error(f"CLI execution failed: {e}")
            return 1


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Bio.tools Unified CLI - Data Fetcher and Quality Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Individual tool with quality analysis
  python biotools_cli.py --tool-id blast --analyze
  
  # Bulk search with analysis
  python biotools_cli.py --search "alignment" --limit 10 --analyze
  
  # Basic data fetching only
  python biotools_cli.py --search "phylogeny" --limit 5 --no-analyze --export-csv
  
  # Domain-based analysis
  python biotools_cli.py --domain "Genomics" --limit 20 --analyze --export-all
        """
    )
    
    # Data fetching options
    fetch_group = parser.add_argument_group('Data Fetching')
    fetch_group.add_argument('--tool-id', action='append', 
                           help='Specific tool ID(s) to fetch (can be used multiple times)')
    fetch_group.add_argument('--search', 
                           help='Search query for tools')
    fetch_group.add_argument('--domain', 
                           help='Filter by scientific domain')
    fetch_group.add_argument('--format', 
                           help='Filter by data format')
    fetch_group.add_argument('--limit', type=int, 
                           help='Limit number of tools to fetch')
    
    # Analysis options
    analysis_group = parser.add_argument_group('Analysis')
    analysis_group.add_argument('--analyze', action='store_true', default=True,
                               help='Perform comprehensive quality analysis (default: True)')
    analysis_group.add_argument('--no-analyze', dest='analyze', action='store_false',
                               help='Skip quality analysis, only fetch and export basic data')
    
    # Processing options
    process_group = parser.add_argument_group('Processing')
    process_group.add_argument('--save-raw', action='store_true', default=True,
                             help='Save raw API data (default: True)')
    process_group.add_argument('--cache', action='store_true', default=True,
                             help='Use local caching for API requests (default: True)')
    
    # Export options
    export_group = parser.add_argument_group('Export Formats')
    export_group.add_argument('--export-csv', action='store_true',
                            help='Export data to CSV')
    export_group.add_argument('--export-json', action='store_true',
                            help='Export data to JSON')
    export_group.add_argument('--export-excel', action='store_true',
                            help='Export data to Excel')
    export_group.add_argument('--export-all', action='store_true',
                            help='Export to all formats (CSV, JSON, Excel)')
    
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
    
    # Run CLI
    cli = BioToolsCLI()
    return cli.run(args)


if __name__ == '__main__':
    sys.exit(main())
