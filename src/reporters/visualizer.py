"""
Visualization and reporting module for bio.tools quality analysis.

This module provides various visualization and reporting capabilities
for quality analysis results.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json
import re
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

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
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
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
    
    def create_quality_dashboard(
        self, 
        reports: List[QualityReport], 
        output_file: str = "quality_dashboard.html"
    ) -> str:
        """
        Create an interactive HTML dashboard with multiple visualizations.
        
        Args:
            reports: List of quality reports
            output_file: Output HTML file name
            
        Returns:
            Path to generated dashboard
        """
        if not reports:
            raise ValueError("No reports provided for dashboard creation")
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "Quality Grade Distribution",
                "Standards Tier Distribution", 
                "Score Distribution",
                "Field Completeness vs Score",
                "Issues by Category",
                "Content Quality Metrics"
            ),
            specs=[
                [{"type": "domain"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "xy"}],
                [{"type": "xy"}, {"type": "xy"}]
            ]
        )
        
        # Extract data for visualizations
        df = self._reports_to_dataframe(reports)
        
        # 1. Quality grade distribution (pie chart)
        grade_counts = df['quality_grade'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=grade_counts.index,
                values=grade_counts.values,
                name="Grades"
            ),
            row=1, col=1
        )
        
        # 2. Standards tier distribution (bar chart)
        tier_counts = df['standards_tier'].value_counts()
        fig.add_trace(
            go.Bar(
                x=tier_counts.index,
                y=tier_counts.values,
                name="Tiers"
            ),
            row=1, col=2
        )
        
        # 3. Score distribution (histogram)
        fig.add_trace(
            go.Histogram(
                x=df['overall_score'],
                nbinsx=20,
                name="Scores"
            ),
            row=2, col=1
        )
        
        # 4. Field completeness vs score (scatter)
        fig.add_trace(
            go.Scatter(
                x=df['field_completeness'],
                y=df['overall_score'],
                mode='markers',
                name="Completeness vs Score",
                text=df['tool_id'],
                hovertemplate="<b>%{text}</b><br>Completeness: %{x:.2f}<br>Score: %{y:.1f}<extra></extra>"
            ),
            row=2, col=2
        )
        
        # 5. Issues by category (bar chart)
        issue_cols = ['critical_issues', 'error_issues', 'warning_issues', 'info_issues']
        issue_totals = df[issue_cols].sum()
        fig.add_trace(
            go.Bar(
                x=issue_cols,
                y=issue_totals.values,
                name="Issues"
            ),
            row=3, col=1
        )
        
        # 6. Content quality metrics (bar chart)
        content_metrics = [
            ('Has Functions', df['has_functions'].sum()),
            ('Has Documentation', df['has_documentation'].sum()),
            ('Has Publications', df['has_publications'].sum()),
            ('Has Contacts', df['has_contacts'].sum())
        ]
        
        fig.add_trace(
            go.Bar(
                x=[m[0] for m in content_metrics],
                y=[m[1] for m in content_metrics],
                name="Content"
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title="Bio.tools Quality Analysis Dashboard",
            height=1200,
            showlegend=False
        )
        
        # Save dashboard
        output_path = self.output_dir / output_file
        fig.write_html(str(output_path))
        logger.info(f"Dashboard saved to: {output_path}")
        
        return str(output_path)
    
    def create_detailed_charts(
        self, 
        reports: List[QualityReport], 
        chart_type: str = "all"
    ) -> List[str]:
        """
        Create detailed charts for specific aspects of quality analysis.
        
        Args:
            reports: List of quality reports
            chart_type: Type of charts to create ("all", "scores", "issues", "content")
            
        Returns:
            List of paths to generated chart files
        """
        if not reports:
            raise ValueError("No reports provided for chart creation")
        
        df = self._reports_to_dataframe(reports)
        chart_paths = []
        
        if chart_type in ["all", "scores"]:
            # Score distribution and correlations
            chart_paths.append(self._create_score_analysis_chart(df))
        
        if chart_type in ["all", "issues"]:
            # Issue analysis charts
            chart_paths.append(self._create_issues_analysis_chart(df))
        
        if chart_type in ["all", "content"]:
            # Content quality analysis
            chart_paths.append(self._create_content_analysis_chart(df))
        
        if chart_type in ["all", "standards"]:
            # Standards tier analysis
            chart_paths.append(self._create_standards_analysis_chart(df))
        
        return chart_paths
    
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
    
    def export_per_tool_json(
        self, 
        reports: List[QualityReport], 
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export individual JSON files for each tool.
        
        Args:
            reports: List of quality reports
            output_dir: Custom output directory (optional, uses self.output_dir if not provided)
            
        Returns:
            List of paths to exported files
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        # Use custom output directory or default
        export_dir = Path(output_dir) if output_dir else self.output_dir
        
        # Create per-tool subdirectory
        per_tool_dir = export_dir / "per_tool_analysis"
        per_tool_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Exporting {len(reports)} individual tool reports...")
        
        for report in reports:
            try:
                # Create safe filename from tool ID
                safe_tool_id = self._sanitize_filename(report.tool_id)
                filename = f"{safe_tool_id}_{timestamp}.json"
                output_path = per_tool_dir / filename
                
                # Export individual report
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
                
                exported_files.append(str(output_path))
                logger.debug(f"Exported: {report.tool_id} -> {filename}")
                
            except Exception as e:
                logger.error(f"Failed to export report for tool {report.tool_id}: {e}")
                continue
        
        logger.info(f"Successfully exported {len(exported_files)} individual tool reports to: {per_tool_dir}")
        return exported_files
    
    def _sanitize_filename(self, tool_id: str) -> str:
        """
        Create a safe filename from a tool ID.
        
        Args:
            tool_id: Bio.tools ID
            
        Returns:
            Sanitized filename
        """
        import re
        # Replace invalid filename characters with underscores
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', tool_id)
        # Remove leading/trailing dots and spaces
        safe_name = safe_name.strip('. ')
        # Limit length
        if len(safe_name) > 200:
            safe_name = safe_name[:200]
        return safe_name or "unknown_tool"
    
    def export_per_tool_csv(
        self, 
        reports: List[QualityReport], 
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export individual CSV files for each tool.
        
        Args:
            reports: List of quality reports
            output_dir: Custom output directory (optional, uses self.output_dir if not provided)
            
        Returns:
            List of paths to exported files
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        # Use custom output directory or default
        export_dir = Path(output_dir) if output_dir else self.output_dir
        
        # Create per-tool subdirectory
        per_tool_dir = export_dir / "per_tool_analysis"
        per_tool_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Exporting {len(reports)} individual tool CSV reports...")
        
        for report in reports:
            try:
                # Create safe filename from tool ID
                safe_tool_id = self._sanitize_filename(report.tool_id)
                filename = f"{safe_tool_id}_{timestamp}.csv"
                output_path = per_tool_dir / filename
                
                # Convert single report to DataFrame
                df = self._reports_to_dataframe([report])
                df.to_csv(output_path, index=False)
                
                exported_files.append(str(output_path))
                logger.debug(f"Exported: {report.tool_id} -> {filename}")
                
            except Exception as e:
                logger.error(f"Failed to export CSV report for tool {report.tool_id}: {e}")
                continue
        
        logger.info(f"Successfully exported {len(exported_files)} individual tool CSV reports to: {per_tool_dir}")
        return exported_files
    
    def export_per_tool_excel(
        self, 
        reports: List[QualityReport], 
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export individual Excel files for each tool with multiple sheets.
        
        Args:
            reports: List of quality reports
            output_dir: Custom output directory (optional, uses self.output_dir if not provided)
            
        Returns:
            List of paths to exported files
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        # Use custom output directory or default
        export_dir = Path(output_dir) if output_dir else self.output_dir
        
        # Create per-tool subdirectory
        per_tool_dir = export_dir / "per_tool_analysis"
        per_tool_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Exporting {len(reports)} individual tool Excel reports...")
        
        for report in reports:
            try:
                # Create safe filename from tool ID
                safe_tool_id = self._sanitize_filename(report.tool_id)
                filename = f"{safe_tool_id}_{timestamp}.xlsx"
                output_path = per_tool_dir / filename
                
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    # Main metrics sheet
                    df = self._reports_to_dataframe([report])
                    df.to_excel(writer, sheet_name='Quality_Metrics', index=False)
                    
                    # Tool details sheet
                    tool_details = self._create_tool_details_dataframe(report)
                    tool_details.to_excel(writer, sheet_name='Tool_Details', index=False)
                    
                    # Lint issues sheet
                    if report.lint_issues:
                        lint_df = self._create_lint_issues_dataframe(report.lint_issues)
                        lint_df.to_excel(writer, sheet_name='Lint_Issues', index=False)
                    
                    # Recommendations sheet
                    rec_df = self._create_recommendations_dataframe(report)
                    rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
                    
                    # Standards analysis sheet
                    standards_df = self._create_standards_dataframe(report)
                    standards_df.to_excel(writer, sheet_name='Standards_Analysis', index=False)
                
                exported_files.append(str(output_path))
                logger.debug(f"Exported: {report.tool_id} -> {filename}")
                
            except Exception as e:
                logger.error(f"Failed to export Excel report for tool {report.tool_id}: {e}")
                continue
        
        logger.info(f"Successfully exported {len(exported_files)} individual tool Excel reports to: {per_tool_dir}")
        return exported_files
    
    def export_per_tool_html(
        self, 
        reports: List[QualityReport], 
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export individual HTML reports for each tool.
        
        Args:
            reports: List of quality reports
            output_dir: Custom output directory (optional, uses self.output_dir if not provided)
            
        Returns:
            List of paths to exported files
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        # Use custom output directory or default
        export_dir = Path(output_dir) if output_dir else self.output_dir
        
        # Create per-tool subdirectory
        per_tool_dir = export_dir / "per_tool_analysis"
        per_tool_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Exporting {len(reports)} individual tool HTML reports...")
        
        for report in reports:
            try:
                # Create safe filename from tool ID
                safe_tool_id = self._sanitize_filename(report.tool_id)
                filename = f"{safe_tool_id}_{timestamp}.html"
                output_path = per_tool_dir / filename
                
                # Generate HTML content
                html_content = self._generate_tool_html_report(report)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                exported_files.append(str(output_path))
                logger.debug(f"Exported: {report.tool_id} -> {filename}")
                
            except Exception as e:
                logger.error(f"Failed to export HTML report for tool {report.tool_id}: {e}")
                continue
        
        logger.info(f"Successfully exported {len(exported_files)} individual tool HTML reports to: {per_tool_dir}")
        return exported_files
    
    def export_per_tool_all_formats(
        self, 
        reports: List[QualityReport], 
        output_dir: Optional[str] = None,
        formats: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Export individual files for each tool in multiple formats.
        
        Args:
            reports: List of quality reports
            output_dir: Custom output directory (optional, uses self.output_dir if not provided)
            formats: List of formats to export (default: all supported formats)
            
        Returns:
            Dictionary mapping format names to lists of exported file paths
        """
        if not reports:
            raise ValueError("No reports provided for export")
        
        if formats is None:
            formats = ['json', 'csv', 'excel', 'html']
        
        exported_files = {}
        
        logger.info(f"Exporting {len(reports)} individual tool reports in {len(formats)} formats...")
        
        if 'json' in formats:
            exported_files['json'] = self.export_per_tool_json(reports, output_dir)
        
        if 'csv' in formats:
            exported_files['csv'] = self.export_per_tool_csv(reports, output_dir)
        
        if 'excel' in formats:
            exported_files['excel'] = self.export_per_tool_excel(reports, output_dir)
        
        if 'html' in formats:
            exported_files['html'] = self.export_per_tool_html(reports, output_dir)
        
        total_files = sum(len(files) for files in exported_files.values())
        logger.info(f"Successfully exported {total_files} individual tool files across {len(formats)} formats")
        
        return exported_files
    
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
            issues_data['Code'].append(issue.code)
            issues_data['Message'].append(issue.message)
            issues_data['Suggestion'].append(issue.suggestion or 'N/A')
            issues_data['Location'].append(issue.location or 'N/A')
        
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
    
    def _generate_tool_html_report(self, report: QualityReport) -> str:
        """Generate an HTML report for a single tool using template."""
        
        # Load the HTML template
        template_path = Path(__file__).parent / "templates" / "tool_report_template.html"
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            logger.error(f"HTML template not found at: {template_path}")
            return self._generate_fallback_html_report(report)
        
        # Quality grade color mapping
        grade_colors = {
            'A': '#28a745',  # Green
            'B': '#6f42c1',  # Purple  
            'C': '#fd7e14',  # Orange
            'D': '#dc3545',  # Red
            'F': '#6c757d'   # Gray
        }
        
        grade_color = grade_colors.get(report.metrics.quality_grade, '#6c757d')
        
        # Prepare template variables
        template_vars = {
            'tool_name': report.tool_name,
            'tool_id': report.tool_id,
            'grade_color': grade_color,
            'quality_grade': report.metrics.quality_grade,
            'overall_score': report.metrics.overall_score,
            'standards_tier': report.metrics.standards_tier,
            'completeness_score': f"{report.metrics.completeness_score:.1f}",
            
            # Field completeness
            'field_completeness_percent': f"{report.metrics.field_completeness:.1%}",
            'field_completeness_width': report.metrics.field_completeness * 100,
            'recommended_fields_percent': f"{report.metrics.recommended_fields_complete:.1%}",
            'recommended_fields_width': report.metrics.recommended_fields_complete * 100,
            
            # Content quality status
            'functions_status': '✅ Present' if report.metrics.has_functions else '❌ Missing',
            'functions_status_class': 'status-yes' if report.metrics.has_functions else 'status-no',
            'documentation_status': '✅ Present' if report.metrics.has_documentation else '❌ Missing',
            'documentation_status_class': 'status-yes' if report.metrics.has_documentation else 'status-no',
            'publications_status': '✅ Present' if report.metrics.has_publications else '❌ Missing',
            'publications_status_class': 'status-yes' if report.metrics.has_publications else 'status-no',
            'contacts_status': '✅ Present' if report.metrics.has_contacts else '❌ Missing',
            'contacts_status_class': 'status-yes' if report.metrics.has_contacts else 'status-no',
            
            # Quality scores
            'publication_quality': f"{report.metrics.publication_quality:.1%}",
            'url_health': f"{report.metrics.url_health:.1%}",
            'edam_consistency': f"{report.metrics.edam_consistency:.1%}",
            
            # Schema validation
            'schema_status': '✅ Valid' if report.metrics.schema_valid else '❌ Invalid',
            'schema_status_class': 'status-yes' if report.metrics.schema_valid else 'status-no',
            'schema_errors': report.metrics.schema_errors,
            'schema_warnings': report.metrics.schema_warnings,
            
            # Lint issues
            'lint_issues_count': report.metrics.lint_issues,
            'lint_issues_content': self._generate_lint_issues_html(report.lint_issues),
            
            # Schema validation details
            'schema_details_content': self._generate_schema_details_html(report.schema_results),
            
            # Tier requirements
            'current_tier': report.metrics.completeness_tier,
            'current_tier_lower': report.metrics.completeness_tier.lower(),
            'tier_requirements_content': self._generate_tier_requirements_html(report.completeness_analysis),
            
            # Recommendations
            'recommendations_content': self._generate_recommendations_html(report),
            
            # Summary and metadata
            'summary': report.summary,
            'analysis_date': report.metrics.analysis_date
        }
        
        # Replace template variables
        html_content = template_content.format(**template_vars)
        
        return html_content
    
    def _generate_lint_issues_html(self, lint_issues: List) -> str:
        """Generate HTML content for lint issues."""
        if not lint_issues:
            return '''
                    <li class="issue-item issue-info">
                        <strong>No issues found!</strong> This tool has excellent quality.
                    </li>'''
        
        html_parts = []
        
        # Show first 10 issues
        for issue in lint_issues[:10]:
            issue_level = issue.level.value.lower() if hasattr(issue.level, 'value') else str(issue.level).lower()
            issue_class = f"issue-{issue_level}"
            
            suggestion_html = ""
            if issue.suggestion:
                suggestion_html = f'<br><em>Suggestion: {issue.suggestion}</em>'
            
            html_parts.append(f'''
                    <li class="issue-item {issue_class}">
                        <strong>{issue.code}:</strong> {issue.message}
                        {suggestion_html}
                    </li>''')
        
        # Add note about additional issues if there are more than 10
        if len(lint_issues) > 10:
            html_parts.append(f'''
                    <li class="issue-item">
                        <em>... and {len(lint_issues) - 10} more issues</em>
                    </li>''')
        
        return ''.join(html_parts)
    
    def _generate_recommendations_html(self, report: QualityReport) -> str:
        """Generate HTML content for recommendations."""
        html_parts = []
        
        # Add priority fixes
        if report.priority_fixes:
            html_parts.append("<h3>Priority Fixes</h3><ul>")
            for fix in report.priority_fixes:
                html_parts.append(f"<li><strong>{fix}</strong></li>")
            html_parts.append("</ul>")
        
        # Add general recommendations
        if report.recommendations:
            html_parts.append("<h3>Improvement Suggestions</h3><ul>")
            for rec in report.recommendations:
                html_parts.append(f"<li>{rec}</li>")
            html_parts.append("</ul>")
        
        # Default message if no recommendations
        if not report.priority_fixes and not report.recommendations:
            html_parts.append("<p>No specific recommendations available. This tool has good quality overall.</p>")
        
        return ''.join(html_parts)
    
    def _generate_schema_details_html(self, schema_results: Dict) -> str:
        """Generate HTML content for detailed schema validation results."""
        if not schema_results:
            return ""
        
        html_parts = []
        
        # Add detailed errors
        errors = schema_results.get('errors', [])
        if errors:
            html_parts.append('<div class="schema-details">')
            html_parts.append('<h3>Schema Errors</h3>')
            
            for error in errors[:10]:  # Limit to first 10 errors
                path = error.get('path', 'unknown')
                message = error.get('message', 'Unknown error')
                validator = error.get('validator', '')
                
                html_parts.append(f'''
                <div class="schema-item schema-error">
                    <strong>{validator.upper() if validator else 'ERROR'}:</strong> {message}
                    <br><span class="schema-path">Path: {path}</span>
                </div>''')
            
            if len(errors) > 10:
                html_parts.append(f'<p><em>... and {len(errors) - 10} more errors</em></p>')
            
            html_parts.append('</div>')
        
        # Add detailed warnings
        warnings = schema_results.get('warnings', [])
        if warnings:
            html_parts.append('<div class="schema-details">')
            html_parts.append('<h3>Schema Warnings</h3>')
            
            for warning in warnings[:10]:  # Limit to first 10 warnings
                path = warning.get('path', 'unknown')
                message = warning.get('message', 'Unknown warning')
                validator = warning.get('validator', '')
                
                html_parts.append(f'''
                <div class="schema-item schema-warning">
                    <strong>{validator.upper() if validator else 'WARNING'}:</strong> {message}
                    <br><span class="schema-path">Path: {path}</span>
                </div>''')
            
            if len(warnings) > 10:
                html_parts.append(f'<p><em>... and {len(warnings) - 10} more warnings</em></p>')
            
            html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _generate_tier_requirements_html(self, completeness_analysis: Dict) -> str:
        """Generate HTML content for tier requirements and progress."""
        if not completeness_analysis:
            return "<p>No tier analysis available.</p>"
        
        html_parts = []
        
        # Get tier information
        tier_scores = completeness_analysis.get('tier_scores', {})
        field_analysis = completeness_analysis.get('field_analysis', {})
        achieved_tier = completeness_analysis.get('achieved_tier_name', 'SPARSE')
        
        # Define tier information
        tier_info = {
            'SPARSE': {
                'name': 'Sparse',
                'color': 'sparse',
                'description': 'Basic tool information',
                'fields': ['name', 'description', 'homepage', 'biotoolsID']
            },
            'MINIMAL': {
                'name': 'Minimal', 
                'color': 'minimal',
                'description': 'Essential scientific information',
                'fields': ['toolType', 'topic', 'publication', 'support']
            },
            'DETAILED': {
                'name': 'Detailed',
                'color': 'detailed', 
                'description': 'Comprehensive tool details',
                'fields': ['function', 'documentation', 'operatingSystem', 'language', 'license', 'input_output']
            },
            'COMPLETE': {
                'name': 'Complete',
                'color': 'complete',
                'description': 'Full accessibility and availability',
                'fields': ['accessibility', 'code_availability', 'downloads', 'supported_data_formats']
            },
            'COMPREHENSIVE': {
                'name': 'Comprehensive',
                'color': 'comprehensive', 
                'description': 'Scientific validation and monitoring',
                'fields': ['scientific_benchmark', 'technical_monitoring']
            }
        }
        
        # Generate tier sections
        for tier_name, info in tier_info.items():
            tier_achieved = tier_scores.get(tier_name, False)
            is_current = (tier_name == achieved_tier)
            
            # Determine section class
            section_class = "tier-section"
            if tier_achieved:
                section_class += " achieved"
            elif is_current:
                section_class += " current"
            
            html_parts.append(f'''
            <div class="{section_class}">
                <h4>
                    <span class="tier-badge tier-{info['color']}">{info['name']}</span>
                    {info['description']}
                    {'✅' if tier_achieved else '❌'}
                </h4>
                <div class="field-list">''')
            
            # Show field requirements for this tier
            for field in info['fields']:
                field_present = self._check_field_present(field, field_analysis)
                field_class = "field-present" if field_present else "field-missing"
                field_icon = "✅" if field_present else "❌"
                
                html_parts.append(f'''
                    <div class="{field_class}">
                        {field_icon} {field.replace('_', ' ').title()}
                    </div>''')
            
            html_parts.append('</div></div>')
        
        # Add next tier recommendations
        next_tier_info = self._get_next_tier_info(achieved_tier, tier_info)
        if next_tier_info:
            html_parts.append(f'''
            <div class="tier-section">
                <h4>🎯 Next Tier: {next_tier_info['name']}</h4>
                <p>To achieve <strong>{next_tier_info['name']}</strong> tier, add the following:</p>
                <div class="field-list">''')
            
            for field in next_tier_info['fields']:
                field_present = self._check_field_present(field, field_analysis)
                if not field_present:
                    html_parts.append(f'''
                        <div class="field-missing">
                            ❌ {field.replace('_', ' ').title()}
                        </div>''')
            
            html_parts.append('</div></div>')
        
        return ''.join(html_parts)
    
    def _check_field_present(self, field_name: str, field_analysis: Dict) -> bool:
        """Check if a field is present in the field analysis."""
        # Handle different field analysis structures
        if isinstance(field_analysis, dict):
            # Look for the field directly
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                if isinstance(field_info, dict):
                    return field_info.get('present', False)
                return bool(field_info)
            
            # Look in nested structures
            for key, value in field_analysis.items():
                if isinstance(value, dict) and field_name in value:
                    field_info = value[field_name]
                    if isinstance(field_info, dict):
                        return field_info.get('present', False)
                    return bool(field_info)
        
        return False
    
    def _get_next_tier_info(self, current_tier: str, tier_info: Dict) -> Optional[Dict]:
        """Get information about the next tier to achieve."""
        tier_order = ['SPARSE', 'MINIMAL', 'DETAILED', 'COMPLETE', 'COMPREHENSIVE']
        
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                next_tier = tier_order[current_index + 1]
                return tier_info.get(next_tier)
        except ValueError:
            pass
        
        return None
    
    def _generate_fallback_html_report(self, report: QualityReport) -> str:
        """Generate a simple fallback HTML report if template is not available."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Report: {report.tool_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .metric {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report.tool_name}</h1>
        <p>Quality Analysis Report • {report.tool_id}</p>
    </div>
    <div class="content">
        <div class="metric"><strong>Overall Score:</strong> {report.metrics.overall_score}/100</div>
        <div class="metric"><strong>Quality Grade:</strong> {report.metrics.quality_grade}</div>
        <div class="metric"><strong>Standards Tier:</strong> {report.metrics.standards_tier}</div>
        <div class="metric"><strong>Summary:</strong> {report.summary}</div>
        <p><em>Report generated on {report.metrics.analysis_date}</em></p>
    </div>
</body>
</html>"""
    
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
                issue_counts[fix] = issue_counts.get(fix, 0) + 1
            
            # Count lint issue types
            for issue in report.lint_issues:
                issue_type = f"{issue.code}: {issue.message}"
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Sort by frequency
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_issues
    
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
                'analysis_date': report.metrics.analysis_date
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _create_score_analysis_chart(self, df: pd.DataFrame) -> str:
        """Create score analysis charts."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Score Analysis', fontsize=16)
        
        # Overall score distribution
        axes[0, 0].hist(df['overall_score'], bins=20, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Overall Score Distribution')
        axes[0, 0].set_xlabel('Score')
        axes[0, 0].set_ylabel('Frequency')
        
        # Standards score vs overall score
        axes[0, 1].scatter(df['standards_score'], df['overall_score'], alpha=0.6)
        axes[0, 1].set_title('Standards Score vs Overall Score')
        axes[0, 1].set_xlabel('Standards Score')
        axes[0, 1].set_ylabel('Overall Score')
        
        # Field completeness vs score
        axes[1, 0].scatter(df['field_completeness'], df['overall_score'], alpha=0.6)
        axes[1, 0].set_title('Field Completeness vs Overall Score')
        axes[1, 0].set_xlabel('Field Completeness')
        axes[1, 0].set_ylabel('Overall Score')
        
        # Quality grade distribution
        grade_counts = df['quality_grade'].value_counts()
        axes[1, 1].bar(grade_counts.index, grade_counts.values)
        axes[1, 1].set_title('Quality Grade Distribution')
        axes[1, 1].set_xlabel('Grade')
        axes[1, 1].set_ylabel('Count')
        
        plt.tight_layout()
        
        output_path = self.output_dir / "score_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Score analysis chart saved to: {output_path}")
        return str(output_path)
    
    def _create_issues_analysis_chart(self, df: pd.DataFrame) -> str:
        """Create issues analysis charts."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Issues Analysis', fontsize=16)
        
        # Issue counts by category
        issue_columns = ['critical_issues', 'error_issues', 'warning_issues', 'info_issues']
        issue_totals = df[issue_columns].sum()
        
        axes[0, 0].bar(issue_columns, issue_totals.values)
        axes[0, 0].set_title('Total Issues by Category')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Tools with issues distribution
        tools_with_issues = (df['lint_issues'] > 0).sum()
        tools_without_issues = len(df) - tools_with_issues
        
        axes[0, 1].pie([tools_with_issues, tools_without_issues], 
                       labels=['With Issues', 'No Issues'], autopct='%1.1f%%')
        axes[0, 1].set_title('Tools with/without Issues')
        
        # Schema validation results
        schema_valid = df['schema_valid'].sum()
        schema_invalid = len(df) - schema_valid
        
        axes[1, 0].pie([schema_valid, schema_invalid],
                       labels=['Valid', 'Invalid'], autopct='%1.1f%%')
        axes[1, 0].set_title('Schema Validation Results')
        
        # Issues vs score relationship
        axes[1, 1].scatter(df['lint_issues'], df['overall_score'], alpha=0.6)
        axes[1, 1].set_title('Issues Count vs Overall Score')
        axes[1, 1].set_xlabel('Number of Issues')
        axes[1, 1].set_ylabel('Overall Score')
        
        plt.tight_layout()
        
        output_path = self.output_dir / "issues_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Issues analysis chart saved to: {output_path}")
        return str(output_path)
    
    def _create_content_analysis_chart(self, df: pd.DataFrame) -> str:
        """Create content quality analysis charts."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Content Quality Analysis', fontsize=16)
        
        # Content features availability
        content_features = ['has_functions', 'has_documentation', 'has_publications', 'has_contacts']
        feature_counts = df[content_features].sum()
        
        axes[0, 0].bar(content_features, feature_counts.values)
        axes[0, 0].set_title('Content Features Availability')
        axes[0, 0].set_ylabel('Number of Tools')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # URL health distribution
        axes[0, 1].hist(df['url_health'], bins=20, alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('URL Health Score Distribution')
        axes[0, 1].set_xlabel('URL Health Score')
        axes[0, 1].set_ylabel('Frequency')
        
        # EDAM consistency distribution
        axes[1, 0].hist(df['edam_consistency'], bins=20, alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('EDAM Consistency Score Distribution')
        axes[1, 0].set_xlabel('EDAM Consistency Score')
        axes[1, 0].set_ylabel('Frequency')
        
        # Publication quality distribution
        axes[1, 1].hist(df['publication_quality'], bins=20, alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('Publication Quality Score Distribution')
        axes[1, 1].set_xlabel('Publication Quality Score')
        axes[1, 1].set_ylabel('Frequency')
        
        plt.tight_layout()
        
        output_path = self.output_dir / "content_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Content analysis chart saved to: {output_path}")
        return str(output_path)
    
    def _create_standards_analysis_chart(self, df: pd.DataFrame) -> str:
        """Create standards tier analysis charts."""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Tool Information Standards Analysis', fontsize=16)
        
        # Tier distribution
        tier_counts = df['standards_tier'].value_counts()
        axes[0].bar(tier_counts.index, tier_counts.values)
        axes[0].set_title('Standards Tier Distribution')
        axes[0].set_xlabel('Tier')
        axes[0].set_ylabel('Number of Tools')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Standards score vs overall score
        axes[1].scatter(df['standards_score'], df['overall_score'], alpha=0.6)
        axes[1].set_title('Standards Score vs Overall Score')
        axes[1].set_xlabel('Standards Score')
        axes[1].set_ylabel('Overall Score')
        
        # Add trend line
        z = np.polyfit(df['standards_score'], df['overall_score'], 1)
        p = np.poly1d(z)
        axes[1].plot(df['standards_score'], p(df['standards_score']), "r--", alpha=0.8)
        
        plt.tight_layout()
        
        output_path = self.output_dir / "standards_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Standards analysis chart saved to: {output_path}")
        return str(output_path)
