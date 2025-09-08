"""
Visualization and reporting module for bio.tools quality analysis.

This module provides various visualization and reporting capabilities
for quality analysis results.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import json
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
                [{"type": "xy"}, {"type": "xy"}],
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
