"""
Visualization and reporting module for bio.tools quality analysis.

This module provides various visualization and reporting capabilities
for quality analysis results.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import pandas as pd

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTTING_AVAILABLE = True
except ImportError:
    plt = None
    sns = None
    go = None
    px = None
    make_subplots = None
    PLOTTING_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from ..analyzers.quality_analyzer import QualityReport, QualityMetrics

logger = logging.getLogger(__name__)


class QualityReporter:
    """
    Generates various reports and visualizations for bio.tools quality analysis.
    """
    
    def __init__(self, output_dir: Union[str, Path] = "reports"):
        """
        Initialize the reporter.
        
        Args:
            output_dir: Directory to save reports and visualizations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up matplotlib style if available
        if PLOTTING_AVAILABLE and plt is not None and sns is not None:
            try:
                plt.style.use('seaborn-v0_8')
                sns.set_palette("husl")
            except Exception:
                pass  # Fall back to default styles
    
    def export_detailed_data(
        self, 
        reports: List[QualityReport], 
        format: str = "csv",
        filename: Optional[str] = None
    ) -> str:
        """
        Export detailed analysis data in various formats.
        
        Args:
            reports: List of quality reports
            format: Export format ("csv", "json", "excel")
            filename: Output filename (optional)
            
        Returns:
            Path to exported file
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "csv":
            df = self._reports_to_dataframe(reports)
            filename = filename or f"biotools_quality_analysis_{timestamp}.csv"
            output_path = self.output_dir / filename
            df.to_csv(output_path, index=False)
        
        elif format == "json":
            filename = filename or f"biotools_quality_analysis_{timestamp}.json"
            output_path = self.output_dir / filename
            export_data = [report.to_dict() for report in reports]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        elif format == "excel":
            if not EXCEL_AVAILABLE:
                raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
                
            df = self._reports_to_dataframe(reports)
            filename = filename or f"biotools_quality_analysis_{timestamp}.xlsx"
            output_path = self.output_dir / filename
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Main metrics
                df.to_excel(writer, sheet_name='Quality_Metrics', index=False)
                
                # Summary statistics
                stats_df = pd.DataFrame([self._calculate_summary_stats(reports)])
                stats_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
                
                # Top issues
                issues_df = pd.DataFrame(
                    self._get_top_issues(reports), 
                    columns=['Issue', 'Count']
                )
                issues_df.to_excel(writer, sheet_name='Top_Issues', index=False)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Data exported to: {output_path}")
        return str(output_path)
    
    def export_to_bytes(
        self, 
        reports: List[QualityReport], 
        format: str = "csv"
    ) -> bytes:
        """
        Export data to bytes for direct download (useful for Streamlit).
        
        Args:
            reports: List of quality reports
            format: Export format ("csv", "json", "excel")
            
        Returns:
            Data as bytes
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        if format == "csv":
            df = self._reports_to_dataframe(reports)
            return df.to_csv(index=False).encode('utf-8')
        
        elif format == "json":
            export_data = [report.to_dict() for report in reports]
            return json.dumps(export_data, indent=2, ensure_ascii=False).encode('utf-8')
        
        elif format == "excel":
            if not EXCEL_AVAILABLE:
                raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
                
            df = self._reports_to_dataframe(reports)
            # For Excel, we need to use BytesIO
            from io import BytesIO
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Main metrics
                df.to_excel(writer, sheet_name='Quality_Metrics', index=False)
                
                # Summary statistics
                stats_df = pd.DataFrame([self._calculate_summary_stats(reports)])
                stats_df.to_excel(writer, sheet_name='Summary_Stats', index=False)
                
                # Top issues
                issues_df = pd.DataFrame(
                    self._get_top_issues(reports), 
                    columns=['Issue', 'Count']
                )
                issues_df.to_excel(writer, sheet_name='Top_Issues', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def export_single_tool_data(
        self, 
        report: QualityReport, 
        format: str = "json"
    ) -> bytes:
        """
        Export single tool data to bytes for direct download.
        
        Args:
            report: Single quality report
            format: Export format ("csv", "json", "excel")
            
        Returns:
            Data as bytes
        """
        if format == "json":
            return json.dumps(report.to_dict(), indent=2, ensure_ascii=False).encode('utf-8')
        
        elif format == "csv":
            # Convert single report to DataFrame
            df = self._single_report_to_dataframe(report)
            return df.to_csv(index=False).encode('utf-8')
        
        elif format == "excel":
            if not EXCEL_AVAILABLE:
                raise ImportError("openpyxl is required for Excel export. Install with: pip install openpyxl")
                
            from io import BytesIO
            buffer = BytesIO()
            
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # Tool details
                details_df = self._create_tool_details_dataframe(report)
                details_df.to_excel(writer, sheet_name='Tool_Details', index=False)
                
                # Lint issues
                issues_df = self._create_lint_issues_dataframe(report.lint_issues)
                issues_df.to_excel(writer, sheet_name='Lint_Issues', index=False)
                
                # Recommendations
                rec_df = self._create_recommendations_dataframe(report)
                rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
                
                # Standards analysis
                standards_df = self._create_standards_dataframe(report)
                standards_df.to_excel(writer, sheet_name='Standards_Analysis', index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def generate_summary_report(
        self, 
        reports: List[QualityReport], 
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a comprehensive summary report.
        
        Args:
            reports: List of quality reports
            output_file: Output file path (optional)
            
        Returns:
            Report content as string
        """
        if not reports:
            return "No reports to analyze."
        
        # Calculate summary statistics
        stats = self._calculate_summary_stats(reports)
        
        # Generate report content
        report_lines = [
            "# Bio.tools Quality Analysis Summary Report",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total tools analyzed: {len(reports)}",
            "",
            "## Overall Quality Distribution",
            f"- Excellent (A): {stats['grade_counts'].get('A', 0)} tools ({stats['grade_percentages'].get('A', 0):.1f}%)",
            f"- Good (B): {stats['grade_counts'].get('B', 0)} tools ({stats['grade_percentages'].get('B', 0):.1f}%)",
            f"- Fair (C): {stats['grade_counts'].get('C', 0)} tools ({stats['grade_percentages'].get('C', 0):.1f}%)",
            f"- Poor (D): {stats['grade_counts'].get('D', 0)} tools ({stats['grade_percentages'].get('D', 0):.1f}%)",
            f"- Needs Improvement (F): {stats['grade_counts'].get('F', 0)} tools ({stats['grade_percentages'].get('F', 0):.1f}%)",
            "",
            "## Quality Metrics",
            f"- Average overall score: {stats['avg_score']:.1f}/100",
            f"- Average standards score: {stats['avg_standards_score']:.1f}/100",
            f"- Schema validation success rate: {stats['schema_success_rate']:.1f}%",
            f"- Average field completeness: {stats['avg_completeness']:.1%}",
            "",
            "## Standards Tier Distribution",
        ]
        
        for tier, count in stats['tier_counts'].items():
            percentage = count / len(reports) * 100
            report_lines.append(f"- {tier}: {count} tools ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "## Common Issues",
            f"- Tools with critical issues: {stats['tools_with_critical']}/{len(reports)} ({stats['tools_with_critical']/len(reports)*100:.1f}%)",
            f"- Tools with schema errors: {stats['tools_with_schema_errors']}/{len(reports)} ({stats['tools_with_schema_errors']/len(reports)*100:.1f}%)",
            f"- Average lint issues per tool: {stats['avg_lint_issues']:.1f}",
            "",
            "## Content Quality",
            f"- Tools with functions: {stats['tools_with_functions']}/{len(reports)} ({stats['tools_with_functions']/len(reports)*100:.1f}%)",
            f"- Tools with documentation: {stats['tools_with_docs']}/{len(reports)} ({stats['tools_with_docs']/len(reports)*100:.1f}%)",
            f"- Tools with publications: {stats['tools_with_pubs']}/{len(reports)} ({stats['tools_with_pubs']/len(reports)*100:.1f}%)",
            f"- Tools with contacts: {stats['tools_with_contacts']}/{len(reports)} ({stats['tools_with_contacts']/len(reports)*100:.1f}%)",
            "",
            "## Top Issues to Address",
        ])
        
        # Add top priority issues
        top_issues = self._get_top_issues(reports)
        for i, (issue, count) in enumerate(top_issues[:10], 1):
            report_lines.append(f"{i}. {issue} ({count} tools affected)")
        
        report_content = "\n".join(report_lines)
        
        # Save to file if specified
        if output_file:
            output_path = self.output_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Summary report saved to: {output_path}")
        
        return report_content
    
    def _reports_to_dataframe(self, reports: List[QualityReport]) -> pd.DataFrame:
        """Convert quality reports to pandas DataFrame."""
        data = []
        
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
                'tool_last_update': report.metrics.tool_last_update
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _single_report_to_dataframe(self, report: QualityReport) -> pd.DataFrame:
        """Convert single quality report to pandas DataFrame with detailed breakdown."""
        # Create a detailed breakdown of the single tool
        details = {
            'Metric': [],
            'Value': [],
            'Category': []
        }
        
        # Basic information
        details['Metric'].extend(['Tool ID', 'Tool Name', 'Analysis Date'])
        details['Value'].extend([report.tool_id, report.tool_name, report.metrics.analysis_date])
        details['Category'].extend(['Basic Info'] * 3)
        
        # Quality scores
        details['Metric'].extend([
            'Overall Score', 'Quality Grade', 'Standards Tier', 'Standards Score',
            'Completeness Tier', 'Completeness Score'
        ])
        details['Value'].extend([
            f"{report.metrics.overall_score}/100",
            report.metrics.quality_grade,
            report.metrics.standards_tier,
            f"{report.metrics.standards_score}/100",
            report.metrics.completeness_tier,
            f"{report.metrics.completeness_score}/100"
        ])
        details['Category'].extend(['Quality Metrics'] * 6)
        
        # Schema validation
        details['Metric'].extend(['Schema Valid', 'Schema Errors', 'Schema Warnings'])
        details['Value'].extend([
            'Yes' if report.metrics.schema_valid else 'No',
            report.metrics.schema_errors,
            report.metrics.schema_warnings
        ])
        details['Category'].extend(['Schema Validation'] * 3)
        
        # Lint issues
        details['Metric'].extend([
            'Total Lint Issues', 'Critical Issues', 'Error Issues', 
            'Warning Issues', 'Info Issues'
        ])
        details['Value'].extend([
            report.metrics.lint_issues,
            report.metrics.critical_issues,
            report.metrics.error_issues,
            report.metrics.warning_issues,
            report.metrics.info_issues
        ])
        details['Category'].extend(['Lint Issues'] * 5)
        
        # Completeness
        details['Metric'].extend([
            'Field Completeness', 'Required Fields Complete', 'Recommended Fields Complete'
        ])
        details['Value'].extend([
            f"{report.metrics.field_completeness:.1%}",
            'Yes' if report.metrics.required_fields_complete else 'No',
            f"{report.metrics.recommended_fields_complete:.1%}"
        ])
        details['Category'].extend(['Completeness'] * 3)
        
        # Content quality
        details['Metric'].extend([
            'Has Functions', 'Has Documentation', 'Has Publications', 'Has Contacts',
            'URL Health', 'EDAM Consistency', 'Publication Quality'
        ])
        details['Value'].extend([
            'Yes' if report.metrics.has_functions else 'No',
            'Yes' if report.metrics.has_documentation else 'No',
            'Yes' if report.metrics.has_publications else 'No',
            'Yes' if report.metrics.has_contacts else 'No',
            f"{report.metrics.url_health:.1%}",
            f"{report.metrics.edam_consistency:.1%}",
            f"{report.metrics.publication_quality:.1%}"
        ])
        details['Category'].extend(['Content Quality'] * 7)
        
        return pd.DataFrame(details)
    
    def _create_tool_details_dataframe(self, report: QualityReport) -> pd.DataFrame:
        """Create a DataFrame with detailed tool information."""
        details = {
            'Field': [],
            'Value': [],
            'Notes': []
        }
        
        # Basic tool information
        details['Field'].extend(['Tool ID', 'Tool Name', 'Analysis Date', 'Last Update'])
        details['Value'].extend([
            report.tool_id,
            report.tool_name,
            report.metrics.analysis_date,
            report.metrics.tool_last_update or 'N/A'
        ])
        details['Notes'].extend(['', '', '', ''])
        
        # Quality metrics
        details['Field'].extend([
            'Overall Score', 'Quality Grade', 'Standards Tier', 'Completeness Score',
            'Schema Valid', 'Field Completeness', 'Has Functions', 'Has Documentation',
            'Has Publications', 'Has Contacts'
        ])
        details['Value'].extend([
            f"{report.metrics.overall_score}/100",
            report.metrics.quality_grade,
            report.metrics.standards_tier,
            f"{report.metrics.completeness_score}/100",
            'Yes' if report.metrics.schema_valid else 'No',
            f"{report.metrics.field_completeness:.1%}",
            'Yes' if report.metrics.has_functions else 'No',
            'Yes' if report.metrics.has_documentation else 'No',
            'Yes' if report.metrics.has_publications else 'No',
            'Yes' if report.metrics.has_contacts else 'No'
        ])
        details['Notes'].extend([''] * 10)
        
        return pd.DataFrame(details)
    
    def _create_lint_issues_dataframe(self, lint_issues: List) -> pd.DataFrame:
        """Create a DataFrame with lint issues."""
        if not lint_issues:
            return pd.DataFrame({'Message': ['No lint issues found']})
        
        issues_data = {
            'Level': [],
            'Code': [],
            'Message': [],
            'Suggestion': [],
            'Location': []
        }
        
        for issue in lint_issues:
            issues_data['Level'].append(issue.level.value if hasattr(issue.level, 'value') else str(issue.level))
            issues_data['Code'].append(getattr(issue, 'code', 'Unknown'))
            issues_data['Message'].append(getattr(issue, 'message', str(issue)))
            issues_data['Suggestion'].append(getattr(issue, 'suggestion', 'N/A') or 'N/A')
            issues_data['Location'].append(getattr(issue, 'location', 'N/A') or 'N/A')
        
        return pd.DataFrame(issues_data)
    
    def _create_recommendations_dataframe(self, report: QualityReport) -> pd.DataFrame:
        """Create a DataFrame with recommendations and priority fixes."""
        rec_data = {
            'Type': [],
            'Recommendation': [],
            'Priority': []
        }
        
        # Add priority fixes
        for fix in report.priority_fixes:
            rec_data['Type'].append('Priority Fix')
            rec_data['Recommendation'].append(fix)
            rec_data['Priority'].append('High')
        
        # Add general recommendations
        for rec in report.recommendations:
            rec_data['Type'].append('Recommendation')
            rec_data['Recommendation'].append(rec)
            rec_data['Priority'].append('Medium')
        
        if not rec_data['Type']:
            rec_data = {'Message': ['No specific recommendations available']}
        
        return pd.DataFrame(rec_data)
    
    def _create_standards_dataframe(self, report: QualityReport) -> pd.DataFrame:
        """Create a DataFrame with standards analysis details."""
        standards_data = {
            'Field': [],
            'Present': [],
            'Completeness': [],
            'Issues': []
        }
        
        # Extract field analysis from standards analysis
        field_analysis = report.standards_analysis.get('field_analysis', {}).get('field_quality', {})
        
        for field_name, field_info in field_analysis.items():
            if isinstance(field_info, dict):
                standards_data['Field'].append(field_name)
                standards_data['Present'].append('Yes' if field_info.get('present', False) else 'No')
                standards_data['Completeness'].append(f"{field_info.get('completeness', 0):.1%}")
                issues = field_info.get('issues', [])
                standards_data['Issues'].append('; '.join(issues) if issues else 'None')
        
        if not standards_data['Field']:
            standards_data = {'Message': ['No field analysis data available']}
        
        return pd.DataFrame(standards_data)
    
    def _calculate_summary_stats(self, reports: List[QualityReport]) -> Dict[str, Any]:
        """Calculate summary statistics from reports."""
        if not reports:
            return {}
        
        # Grade distribution
        grade_counts = {}
        tier_counts = {}
        total_score = 0
        total_standards_score = 0
        total_completeness = 0
        schema_valid_count = 0
        tools_with_critical = 0
        tools_with_schema_errors = 0
        total_lint_issues = 0
        
        content_counters = {
            'functions': 0, 'docs': 0, 'pubs': 0, 'contacts': 0
        }
        
        for report in reports:
            metrics = report.metrics
            
            # Count grades
            grade = metrics.quality_grade
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
            # Count tiers
            tier = metrics.standards_tier
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            # Accumulate scores
            total_score += metrics.overall_score
            total_standards_score += metrics.standards_score
            total_completeness += metrics.field_completeness
            
            # Count validation results
            if metrics.schema_valid:
                schema_valid_count += 1
            
            if metrics.critical_issues > 0:
                tools_with_critical += 1
            
            if metrics.schema_errors > 0:
                tools_with_schema_errors += 1
            
            total_lint_issues += metrics.lint_issues
            
            # Count content features
            if metrics.has_functions:
                content_counters['functions'] += 1
            if metrics.has_documentation:
                content_counters['docs'] += 1
            if metrics.has_publications:
                content_counters['pubs'] += 1
            if metrics.has_contacts:
                content_counters['contacts'] += 1
        
        total_tools = len(reports)
        
        # Calculate percentages
        grade_percentages = {
            grade: (count / total_tools * 100) for grade, count in grade_counts.items()
        }
        
        return {
            'total_tools': total_tools,
            'grade_counts': grade_counts,
            'grade_percentages': grade_percentages,
            'tier_counts': tier_counts,
            'avg_score': total_score / total_tools,
            'avg_standards_score': total_standards_score / total_tools,
            'avg_completeness': total_completeness / total_tools,
            'schema_success_rate': schema_valid_count / total_tools * 100,
            'tools_with_critical': tools_with_critical,
            'tools_with_schema_errors': tools_with_schema_errors,
            'avg_lint_issues': total_lint_issues / total_tools,
            'tools_with_functions': content_counters['functions'],
            'tools_with_docs': content_counters['docs'],
            'tools_with_pubs': content_counters['pubs'],
            'tools_with_contacts': content_counters['contacts']
        }
    
    def _get_top_issues(self, reports: List[QualityReport]) -> List[tuple[str, int]]:
        """Get most common issues across all reports."""
        issue_counts = {}
        
        for report in reports:
            # Count issues from priority fixes and recommendations
            for fix in report.priority_fixes:
                issue_key = fix.split(':')[0] if ':' in fix else fix[:50]
                issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1
            
            # Count lint issue types
            for issue in report.lint_issues:
                issue_code = getattr(issue, 'code', 'Unknown')
                issue_counts[issue_code] = issue_counts.get(issue_code, 0) + 1
        
        # Sort by frequency
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_issues
