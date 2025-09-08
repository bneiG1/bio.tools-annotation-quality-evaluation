"""
Comprehensive quality analysis module.

This module combines schema validation, standards scoring, linting,
and other quality metrics to provide a complete analysis of bio.tools entries.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from ..validators.schema_validator import ExtendedSchemaValidator
from ..validators.standards_scorer import ToolInformationStandardsScorer, Tier
from ..analyzers.linter import BiotoolsLinter, LintIssue, IssueLevel

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for a bio.tools entry."""
    
    # Overall scores
    overall_score: float  # 0-100
    quality_grade: str   # A, B, C, D, F
    
    # Standards compliance
    standards_tier: str
    standards_score: float
    
    # Schema validation
    schema_valid: bool
    schema_errors: int
    schema_warnings: int
    
    # Linting results
    lint_issues: int
    critical_issues: int
    error_issues: int
    warning_issues: int
    info_issues: int
    
    # Completeness metrics
    field_completeness: float  # 0-1
    required_fields_complete: bool
    recommended_fields_complete: float  # 0-1
    
    # Content quality
    url_health: float  # 0-1 (fraction of valid URLs)
    edam_consistency: float  # 0-1
    publication_quality: float  # 0-1
    
    # Metadata richness
    has_functions: bool
    has_documentation: bool
    has_publications: bool
    has_contacts: bool
    
    # Time-based metrics
    analysis_date: str
    tool_last_update: Optional[str] = None


@dataclass
class QualityReport:
    """Complete quality assessment report for a bio.tools entry."""
    
    tool_id: str
    tool_name: str
    metrics: QualityMetrics
    
    # Detailed results
    standards_analysis: Dict
    schema_results: Dict
    lint_issues: List[LintIssue]
    
    # Recommendations
    recommendations: List[str]
    priority_fixes: List[str]
    
    # Summary
    summary: str
    
    def to_dict(self) -> Dict:
        """Convert report to dictionary for serialization."""
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "metrics": asdict(self.metrics),
            "standards_analysis": self.standards_analysis,
            "schema_results": self.schema_results,
            "lint_issues": [asdict(issue) for issue in self.lint_issues],
            "recommendations": self.recommendations,
            "priority_fixes": self.priority_fixes,
            "summary": self.summary
        }


class QualityAnalyzer:
    """
    Comprehensive quality analyzer for bio.tools entries.
    
    Combines multiple analysis techniques to provide detailed
    quality assessments and actionable recommendations.
    """
    
    def __init__(
        self,
        schema_path: Optional[str] = None,
        enable_extended_validation: bool = True
    ):
        """
        Initialize the quality analyzer.
        
        Args:
            schema_path: Path to biotoolsSchema file
            enable_extended_validation: Enable extended validation checks
        """
        self.schema_validator = ExtendedSchemaValidator(schema_path)
        self.standards_scorer = ToolInformationStandardsScorer()
        self.linter = BiotoolsLinter()
        self.enable_extended_validation = enable_extended_validation
    
    def analyze_tool(self, tool_data: Dict) -> QualityReport:
        """
        Perform comprehensive quality analysis on a tool.
        
        Args:
            tool_data: Tool metadata from bio.tools API
            
        Returns:
            Complete quality report
        """
        tool_id = tool_data.get("biotoolsID", "unknown")
        tool_name = tool_data.get("name", "Unknown Tool")
        
        logger.info(f"Analyzing tool: {tool_id}")
        
        # Perform all analyses
        standards_analysis = self.standards_scorer.score_tool(tool_data)
        schema_results = self.schema_validator.validate_tool(tool_data)
        lint_issues = self.linter.lint_tool(tool_data)
        
        # Calculate comprehensive metrics
        metrics = self._calculate_metrics(
            tool_data, standards_analysis, schema_results, lint_issues
        )
        
        # Generate recommendations
        recommendations, priority_fixes = self._generate_recommendations(
            standards_analysis, schema_results, lint_issues
        )
        
        # Create summary
        summary = self._generate_summary(metrics, tool_id)
        
        return QualityReport(
            tool_id=tool_id,
            tool_name=tool_name,
            metrics=metrics,
            standards_analysis=standards_analysis,
            schema_results=schema_results,
            lint_issues=lint_issues,
            recommendations=recommendations,
            priority_fixes=priority_fixes,
            summary=summary
        )
    
    def analyze_tools_batch(self, tools_data: List[Dict]) -> List[QualityReport]:
        """
        Analyze multiple tools in batch.
        
        Args:
            tools_data: List of tool metadata
            
        Returns:
            List of quality reports
        """
        reports = []
        total_tools = len(tools_data)
        
        for i, tool_data in enumerate(tools_data):
            try:
                logger.info(f"Analyzing tool {i+1}/{total_tools}")
                report = self.analyze_tool(tool_data)
                reports.append(report)
            except Exception as e:
                tool_id = tool_data.get("biotoolsID", f"tool_{i}")
                logger.error(f"Failed to analyze tool {tool_id}: {e}")
                # Create a minimal error report
                error_report = self._create_error_report(tool_data, str(e))
                reports.append(error_report)
        
        return reports
    
    def _calculate_metrics(
        self,
        tool_data: Dict,
        standards_analysis: Dict,
        schema_results: Dict,
        lint_issues: List[LintIssue]
    ) -> QualityMetrics:
        """Calculate comprehensive quality metrics."""
        
        # Count lint issues by level
        issue_counts = {level: 0 for level in IssueLevel}
        for issue in lint_issues:
            issue_counts[issue.level] += 1
        
        # Calculate field completeness
        field_completeness = self._calculate_field_completeness(tool_data)
        required_complete = self._check_required_fields_complete(tool_data)
        recommended_complete = self._calculate_recommended_fields_complete(tool_data)
        
        # Calculate content quality scores
        url_health = self._calculate_url_health(lint_issues)
        edam_consistency = self._calculate_edam_consistency(lint_issues)
        publication_quality = self._calculate_publication_quality(tool_data, lint_issues)
        
        # Check metadata richness
        has_functions = bool(tool_data.get("function"))
        has_docs = bool(tool_data.get("documentation"))
        has_pubs = bool(tool_data.get("publication"))
        has_contacts = bool(tool_data.get("credit"))
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            standards_analysis["score"],
            schema_results["error_count"],
            issue_counts,
            field_completeness,
            url_health,
            edam_consistency
        )
        
        # Determine quality grade
        quality_grade = self._determine_quality_grade(overall_score)
        
        return QualityMetrics(
            overall_score=overall_score,
            quality_grade=quality_grade,
            standards_tier=standards_analysis["tier_name"],
            standards_score=standards_analysis["score"],
            schema_valid=schema_results["valid"],
            schema_errors=schema_results["error_count"],
            schema_warnings=schema_results["warning_count"],
            lint_issues=len(lint_issues),
            critical_issues=issue_counts[IssueLevel.CRITICAL],
            error_issues=issue_counts[IssueLevel.ERROR],
            warning_issues=issue_counts[IssueLevel.WARNING],
            info_issues=issue_counts[IssueLevel.INFO],
            field_completeness=field_completeness,
            required_fields_complete=required_complete,
            recommended_fields_complete=recommended_complete,
            url_health=url_health,
            edam_consistency=edam_consistency,
            publication_quality=publication_quality,
            has_functions=has_functions,
            has_documentation=has_docs,
            has_publications=has_pubs,
            has_contacts=has_contacts,
            analysis_date=datetime.now().isoformat(),
            tool_last_update=tool_data.get("lastUpdate")
        )
    
    def _calculate_field_completeness(self, tool_data: Dict) -> float:
        """Calculate overall field completeness (0-1)."""
        all_possible_fields = [
            "name", "description", "homepage", "biotoolsID", "version",
            "topic", "toolType", "operatingSystem", "language", "license",
            "maturity", "cost", "accessibility", "function", "documentation",
            "download", "link", "publication", "credit", "relation"
        ]
        
        present_count = sum(1 for field in all_possible_fields if tool_data.get(field))
        return present_count / len(all_possible_fields)
    
    def _check_required_fields_complete(self, tool_data: Dict) -> bool:
        """Check if all required fields are present."""
        required_fields = ["name", "description", "homepage", "biotoolsID"]
        return all(tool_data.get(field) for field in required_fields)
    
    def _calculate_recommended_fields_complete(self, tool_data: Dict) -> float:
        """Calculate recommended fields completeness (0-1)."""
        recommended_fields = [
            "topic", "toolType", "operatingSystem", "language",
            "license", "maturity", "cost", "function"
        ]
        
        present_count = sum(1 for field in recommended_fields if tool_data.get(field))
        return present_count / len(recommended_fields)
    
    def _calculate_url_health(self, lint_issues: List[LintIssue]) -> float:
        """Calculate URL health score based on linting results."""
        url_issues = [
            issue for issue in lint_issues
            if issue.code in ["INVALID_URL_FORMAT", "URL_WITH_SPACES", "SUSPICIOUS_DOMAIN"]
        ]
        
        # If no URL-related lint issues, assume good health
        # This is a simplified calculation - real implementation would check URLs
        if not url_issues:
            return 1.0
        
        # Penalty based on number of URL issues
        penalty = min(0.8, len(url_issues) * 0.1)
        return max(0.2, 1.0 - penalty)
    
    def _calculate_edam_consistency(self, lint_issues: List[LintIssue]) -> float:
        """Calculate EDAM term consistency score."""
        edam_issues = [
            issue for issue in lint_issues
            if "EDAM" in issue.code
        ]
        
        if not edam_issues:
            return 1.0
        
        # Penalty based on EDAM issues
        penalty = min(0.6, len(edam_issues) * 0.05)
        return max(0.4, 1.0 - penalty)
    
    def _calculate_publication_quality(self, tool_data: Dict, lint_issues: List[LintIssue]) -> float:
        """Calculate publication information quality."""
        pubs = tool_data.get("publication", [])
        
        if not pubs:
            return 0.5  # Neutral score for no publications
        
        pub_issues = [
            issue for issue in lint_issues
            if "PUBLICATION" in issue.code or any(x in issue.code for x in ["DOI", "PMID", "PMCID"])
        ]
        
        # Base score from having publications
        base_score = min(1.0, len(pubs) * 0.3 + 0.4)
        
        # Penalty for publication-related issues
        if pub_issues:
            penalty = min(0.4, len(pub_issues) * 0.1)
            base_score -= penalty
        
        return max(0.0, base_score)
    
    def _calculate_overall_score(
        self,
        standards_score: float,
        schema_errors: int,
        issue_counts: Dict[IssueLevel, int],
        field_completeness: float,
        url_health: float,
        edam_consistency: float
    ) -> float:
        """Calculate overall quality score (0-100)."""
        
        # Weighted combination of different factors
        weights = {
            "standards": 0.3,
            "schema": 0.2,
            "linting": 0.2,
            "completeness": 0.15,
            "content_quality": 0.15
        }
        
        # Standards score (0-100)
        standards_component = standards_score * weights["standards"]
        
        # Schema validation score
        schema_score = 100 if schema_errors == 0 else max(0, 100 - schema_errors * 20)
        schema_component = schema_score * weights["schema"]
        
        # Linting score (penalties for issues)
        lint_penalties = (
            issue_counts[IssueLevel.CRITICAL] * 25 +
            issue_counts[IssueLevel.ERROR] * 10 +
            issue_counts[IssueLevel.WARNING] * 3 +
            issue_counts[IssueLevel.INFO] * 1
        )
        lint_score = max(0, 100 - lint_penalties)
        lint_component = lint_score * weights["linting"]
        
        # Field completeness score
        completeness_score = field_completeness * 100
        completeness_component = completeness_score * weights["completeness"]
        
        # Content quality score
        content_score = (url_health + edam_consistency) / 2 * 100
        content_component = content_score * weights["content_quality"]
        
        # Final score
        final_score = (
            standards_component + schema_component + lint_component +
            completeness_component + content_component
        )
        
        return round(final_score, 1)
    
    def _determine_quality_grade(self, score: float) -> str:
        """Determine quality grade based on overall score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(
        self,
        standards_analysis: Dict,
        schema_results: Dict,
        lint_issues: List[LintIssue]
    ) -> tuple[List[str], List[str]]:
        """Generate recommendations and priority fixes."""
        recommendations = []
        priority_fixes = []
        
        # Add standards recommendations
        if standards_analysis.get("recommendations"):
            recommendations.extend(standards_analysis["recommendations"])
        
        # Add schema error fixes as priority
        for error in schema_results.get("errors", []):
            priority_fixes.append(f"Schema error: {error['message']} at {error['path']}")
        
        # Add critical lint issues as priority
        critical_issues = [issue for issue in lint_issues if issue.level == IssueLevel.CRITICAL]
        for issue in critical_issues:
            priority_fixes.append(f"Critical: {issue.message}")
        
        # Add error lint issues as recommendations
        error_issues = [issue for issue in lint_issues if issue.level == IssueLevel.ERROR]
        for issue in error_issues[:5]:  # Limit to top 5
            recommendations.append(f"Fix: {issue.message}")
            if issue.suggestion:
                recommendations.append(f"  → {issue.suggestion}")
        
        # Add general improvement suggestions
        warning_issues = [issue for issue in lint_issues if issue.level == IssueLevel.WARNING]
        if len(warning_issues) > 3:
            recommendations.append(f"Address {len(warning_issues)} warning issues to improve quality")
        
        return recommendations, priority_fixes
    
    def _generate_summary(self, metrics: QualityMetrics, tool_id: str) -> str:
        """Generate a human-readable summary."""
        grade_descriptions = {
            "A": "Excellent",
            "B": "Good", 
            "C": "Fair",
            "D": "Poor",
            "F": "Needs Improvement"
        }
        
        grade_desc = grade_descriptions.get(metrics.quality_grade, "Unknown")
        
        summary_parts = [
            f"Tool {tool_id} has {grade_desc.lower()} quality (Grade {metrics.quality_grade}, Score: {metrics.overall_score}/100)",
            f"Achieves {metrics.standards_tier} standards tier",
        ]
        
        if not metrics.schema_valid:
            summary_parts.append(f"Has {metrics.schema_errors} schema errors")
        
        if metrics.critical_issues > 0:
            summary_parts.append(f"Has {metrics.critical_issues} critical issues")
        
        if metrics.field_completeness < 0.5:
            summary_parts.append("Metadata is incomplete")
        
        return ". ".join(summary_parts) + "."
    
    def _create_error_report(self, tool_data: Dict, error_message: str) -> QualityReport:
        """Create a minimal error report for failed analysis."""
        tool_id = tool_data.get("biotoolsID", "unknown")
        tool_name = tool_data.get("name", "Unknown Tool")
        
        # Create minimal metrics indicating failure
        metrics = QualityMetrics(
            overall_score=0.0,
            quality_grade="F",
            standards_tier="UNKNOWN",
            standards_score=0.0,
            schema_valid=False,
            schema_errors=1,
            schema_warnings=0,
            lint_issues=1,
            critical_issues=1,
            error_issues=0,
            warning_issues=0,
            info_issues=0,
            field_completeness=0.0,
            required_fields_complete=False,
            recommended_fields_complete=0.0,
            url_health=0.0,
            edam_consistency=0.0,
            publication_quality=0.0,
            has_functions=False,
            has_documentation=False,
            has_publications=False,
            has_contacts=False,
            analysis_date=datetime.now().isoformat()
        )
        
        return QualityReport(
            tool_id=tool_id,
            tool_name=tool_name,
            metrics=metrics,
            standards_analysis={},
            schema_results={"valid": False, "errors": [{"message": error_message}]},
            lint_issues=[],
            recommendations=[],
            priority_fixes=[f"Fix analysis error: {error_message}"],
            summary=f"Analysis failed for tool {tool_id}: {error_message}"
        )
