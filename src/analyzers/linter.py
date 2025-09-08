"""
Linter integration module for bio.tools quality analysis.

This module integrates with existing bio.tools linters and implements
additional quality checks based on best practices and common issues.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IssueLevel(Enum):
    """Issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LintIssue:
    """Represents a linting issue found in tool metadata."""
    level: IssueLevel
    code: str
    message: str
    field_path: str
    suggestion: Optional[str] = None
    value: Optional[str] = None


class BiotoolsLinter:
    """
    Comprehensive linter for bio.tools entries.
    
    Performs various quality checks including:
    - URL validation
    - EDAM term validation
    - Metadata completeness
    - Consistency checks
    - Best practice compliance
    """
    
    def __init__(self):
        """Initialize the linter."""
        self.issues = []
        
        # Common patterns for validation
        self.doi_pattern = re.compile(r"^10\.\d{4,}/[^\s]+$")
        self.pmid_pattern = re.compile(r"^\d{1,8}$")
        self.pmcid_pattern = re.compile(r"^PMC\d+$")
        self.orcid_pattern = re.compile(r"^https?://orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")
        self.edam_topic_pattern = re.compile(r"^http://edamontology\.org/topic_\d{4}$")
        self.edam_operation_pattern = re.compile(r"^http://edamontology\.org/operation_\d{4}$")
        self.edam_data_pattern = re.compile(r"^http://edamontology\.org/data_\d{4}$")
        self.edam_format_pattern = re.compile(r"^http://edamontology\.org/format_\d{4}$")
    
    def lint_tool(self, tool_data: Dict) -> List[LintIssue]:
        """
        Lint a single tool entry.
        
        Args:
            tool_data: Tool metadata to analyze
            
        Returns:
            List of issues found
        """
        self.issues = []
        
        # Run all linting checks
        self._check_basic_fields(tool_data)
        self._check_urls(tool_data)
        self._check_edam_terms(tool_data)
        self._check_publications(tool_data)
        self._check_credits(tool_data)
        self._check_functions(tool_data)
        self._check_consistency(tool_data)
        self._check_best_practices(tool_data)
        
        return self.issues.copy()
    
    def _add_issue(
        self, 
        level: IssueLevel, 
        code: str, 
        message: str, 
        field_path: str,
        suggestion: Optional[str] = None,
        value: Optional[str] = None
    ) -> None:
        """Add an issue to the current issues list."""
        self.issues.append(LintIssue(
            level=level,
            code=code,
            message=message,
            field_path=field_path,
            suggestion=suggestion,
            value=value
        ))
    
    def _check_basic_fields(self, tool_data: Dict) -> None:
        """Check presence and quality of basic required fields."""
        # Check required fields
        required_fields = ["name", "description", "homepage", "biotoolsID"]
        
        for field in required_fields:
            if not tool_data.get(field):
                self._add_issue(
                    IssueLevel.ERROR,
                    "MISSING_REQUIRED_FIELD",
                    f"Required field '{field}' is missing or empty",
                    field,
                    f"Add a valid {field}"
                )
        
        # Check field quality
        description = tool_data.get("description", "")
        if description:
            if len(description) < 30:
                self._add_issue(
                    IssueLevel.WARNING,
                    "SHORT_DESCRIPTION",
                    "Description is quite short (less than 30 characters)",
                    "description",
                    "Provide a more detailed description",
                    str(len(description))
                )
            elif len(description) > 1000:
                self._add_issue(
                    IssueLevel.WARNING,
                    "LONG_DESCRIPTION",
                    "Description is very long (more than 1000 characters)",
                    "description",
                    "Consider shortening the description",
                    str(len(description))
                )
        
        # Check name length and format
        name = tool_data.get("name", "")
        if name:
            if len(name) > 100:
                self._add_issue(
                    IssueLevel.WARNING,
                    "LONG_NAME",
                    "Tool name is very long (more than 100 characters)",
                    "name",
                    "Consider using a shorter name",
                    str(len(name))
                )
    
    def _check_urls(self, tool_data: Dict) -> None:
        """Check URL validity and accessibility."""
        # Check homepage URL
        homepage = tool_data.get("homepage")
        if homepage:
            self._validate_url(homepage, "homepage", critical=True)
        
        # Check documentation URLs
        docs = tool_data.get("documentation", [])
        for i, doc in enumerate(docs):
            if isinstance(doc, dict):
                url = doc.get("url")
                if url:
                    self._validate_url(url, f"documentation[{i}].url")
        
        # Check download URLs
        downloads = tool_data.get("download", [])
        for i, download in enumerate(downloads):
            if isinstance(download, dict):
                url = download.get("url")
                if url:
                    self._validate_url(url, f"download[{i}].url")
        
        # Check link URLs
        links = tool_data.get("link", [])
        for i, link in enumerate(links):
            if isinstance(link, dict):
                url = link.get("url")
                if url:
                    self._validate_url(url, f"link[{i}].url")
    
    def _validate_url(self, url: str, field_path: str, critical: bool = False) -> None:
        """Validate a single URL."""
        if not url:
            return
        
        level = IssueLevel.ERROR if critical else IssueLevel.WARNING
        
        # Basic URL format check
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            self._add_issue(
                level,
                "INVALID_URL_FORMAT",
                f"Invalid URL format: {url}",
                field_path,
                "Provide a complete URL with protocol (http:// or https://)",
                url
            )
            return
        
        # Check for HTTPS (best practice)
        if parsed.scheme == "http":
            self._add_issue(
                IssueLevel.INFO,
                "HTTP_NOT_HTTPS",
                f"URL uses HTTP instead of HTTPS: {url}",
                field_path,
                "Consider using HTTPS for better security",
                url
            )
        
        # Check for common issues
        if " " in url:
            self._add_issue(
                IssueLevel.ERROR,
                "URL_WITH_SPACES",
                f"URL contains spaces: {url}",
                field_path,
                "Remove spaces from URL",
                url
            )
        
        # Check for suspicious domains
        suspicious_domains = ["localhost", "127.0.0.1", "example.com", "test.com"]
        if any(domain in parsed.netloc.lower() for domain in suspicious_domains):
            self._add_issue(
                IssueLevel.WARNING,
                "SUSPICIOUS_DOMAIN",
                f"URL uses suspicious/test domain: {url}",
                field_path,
                "Use a proper production domain",
                url
            )
    
    def _check_edam_terms(self, tool_data: Dict) -> None:
        """Check EDAM term format and validity."""
        # Check topics
        topics = tool_data.get("topic", [])
        for i, topic in enumerate(topics):
            if isinstance(topic, dict):
                self._validate_edam_concept(
                    topic, f"topic[{i}]", "topic", self.edam_topic_pattern
                )
        
        # Check function operations, inputs, outputs
        functions = tool_data.get("function", [])
        for i, func in enumerate(functions):
            # Check operations
            operations = func.get("operation", [])
            for j, operation in enumerate(operations):
                if isinstance(operation, dict):
                    self._validate_edam_concept(
                        operation, f"function[{i}].operation[{j}]", 
                        "operation", self.edam_operation_pattern
                    )
            
            # Check inputs
            inputs = func.get("input", [])
            for j, input_item in enumerate(inputs):
                if isinstance(input_item, dict):
                    data = input_item.get("data")
                    if isinstance(data, dict):
                        self._validate_edam_concept(
                            data, f"function[{i}].input[{j}].data",
                            "data", self.edam_data_pattern
                        )
                    
                    formats = input_item.get("format", [])
                    for k, format_item in enumerate(formats):
                        if isinstance(format_item, dict):
                            self._validate_edam_concept(
                                format_item, f"function[{i}].input[{j}].format[{k}]",
                                "format", self.edam_format_pattern
                            )
            
            # Check outputs (similar to inputs)
            outputs = func.get("output", [])
            for j, output_item in enumerate(outputs):
                if isinstance(output_item, dict):
                    data = output_item.get("data")
                    if isinstance(data, dict):
                        self._validate_edam_concept(
                            data, f"function[{i}].output[{j}].data",
                            "data", self.edam_data_pattern
                        )
                    
                    formats = output_item.get("format", [])
                    for k, format_item in enumerate(formats):
                        if isinstance(format_item, dict):
                            self._validate_edam_concept(
                                format_item, f"function[{i}].output[{j}].format[{k}]",
                                "format", self.edam_format_pattern
                            )
    
    def _validate_edam_concept(
        self, 
        concept: Dict, 
        field_path: str, 
        concept_type: str, 
        uri_pattern: re.Pattern
    ) -> None:
        """Validate an EDAM concept (topic, operation, data, format)."""
        term = concept.get("term")
        uri = concept.get("uri")
        
        # Check if both term and URI are present
        if not term and not uri:
            self._add_issue(
                IssueLevel.WARNING,
                "INCOMPLETE_EDAM_CONCEPT",
                f"EDAM {concept_type} missing both term and URI",
                field_path,
                f"Provide both term and URI for EDAM {concept_type}"
            )
        elif not term:
            self._add_issue(
                IssueLevel.INFO,
                "MISSING_EDAM_TERM",
                f"EDAM {concept_type} missing term",
                f"{field_path}.term",
                f"Add term for EDAM {concept_type}"
            )
        elif not uri:
            self._add_issue(
                IssueLevel.WARNING,
                "MISSING_EDAM_URI",
                f"EDAM {concept_type} missing URI",
                f"{field_path}.uri",
                f"Add URI for EDAM {concept_type}"
            )
        
        # Validate URI format
        if uri and not uri_pattern.match(uri):
            self._add_issue(
                IssueLevel.ERROR,
                "INVALID_EDAM_URI",
                f"Invalid EDAM {concept_type} URI format: {uri}",
                f"{field_path}.uri",
                f"Use correct EDAM {concept_type} URI format",
                uri
            )
    
    def _check_publications(self, tool_data: Dict) -> None:
        """Check publication identifiers and format."""
        pubs = tool_data.get("publication", [])
        
        for i, pub in enumerate(pubs):
            if not isinstance(pub, dict):
                continue
            
            doi = pub.get("doi")
            pmid = pub.get("pmid")
            pmcid = pub.get("pmcid")
            
            # At least one identifier should be present
            if not any([doi, pmid, pmcid]):
                self._add_issue(
                    IssueLevel.WARNING,
                    "INCOMPLETE_PUBLICATION",
                    "Publication missing identifiers (DOI, PMID, or PMCID)",
                    f"publication[{i}]",
                    "Add at least one publication identifier"
                )
                continue
            
            # Validate DOI format
            if doi and not self.doi_pattern.match(doi):
                self._add_issue(
                    IssueLevel.ERROR,
                    "INVALID_DOI_FORMAT",
                    f"Invalid DOI format: {doi}",
                    f"publication[{i}].doi",
                    "Use correct DOI format (e.g., 10.1234/example)",
                    doi
                )
            
            # Validate PMID format
            if pmid and not self.pmid_pattern.match(pmid):
                self._add_issue(
                    IssueLevel.ERROR,
                    "INVALID_PMID_FORMAT",
                    f"Invalid PMID format: {pmid}",
                    f"publication[{i}].pmid",
                    "PMID should be numeric (e.g., 12345678)",
                    pmid
                )
            
            # Validate PMCID format
            if pmcid and not self.pmcid_pattern.match(pmcid):
                self._add_issue(
                    IssueLevel.ERROR,
                    "INVALID_PMCID_FORMAT",
                    f"Invalid PMCID format: {pmcid}",
                    f"publication[{i}].pmcid",
                    "PMCID should start with 'PMC' followed by numbers",
                    pmcid
                )
    
    def _check_credits(self, tool_data: Dict) -> None:
        """Check credit information quality."""
        credits = tool_data.get("credit", [])
        
        if not credits:
            self._add_issue(
                IssueLevel.INFO,
                "NO_CREDITS",
                "No credit information provided",
                "credit",
                "Add contact or credit information"
            )
            return
        
        has_contact = False
        
        for i, credit in enumerate(credits):
            if not isinstance(credit, dict):
                continue
            
            name = credit.get("name")
            email = credit.get("email")
            orcidid = credit.get("orcidid")
            type_role = credit.get("typeRole", [])
            
            # Check if name is present
            if not name:
                self._add_issue(
                    IssueLevel.WARNING,
                    "CREDIT_MISSING_NAME",
                    "Credit entry missing name",
                    f"credit[{i}].name",
                    "Add name for credit entry"
                )
            
            # Check for contact information
            if "Primary contact" in type_role:
                has_contact = True
                if not email:
                    self._add_issue(
                        IssueLevel.WARNING,
                        "PRIMARY_CONTACT_NO_EMAIL",
                        "Primary contact missing email address",
                        f"credit[{i}].email",
                        "Add email for primary contact"
                    )
            
            # Validate ORCID format
            if orcidid and not self.orcid_pattern.match(orcidid):
                self._add_issue(
                    IssueLevel.ERROR,
                    "INVALID_ORCID_FORMAT",
                    f"Invalid ORCID format: {orcidid}",
                    f"credit[{i}].orcidid",
                    "Use correct ORCID format (https://orcid.org/0000-0000-0000-0000)",
                    orcidid
                )
        
        # Check if there's a primary contact
        if not has_contact:
            self._add_issue(
                IssueLevel.INFO,
                "NO_PRIMARY_CONTACT",
                "No primary contact specified",
                "credit",
                "Add a primary contact with email"
            )
    
    def _check_functions(self, tool_data: Dict) -> None:
        """Check function definitions quality."""
        functions = tool_data.get("function", [])
        
        if not functions:
            self._add_issue(
                IssueLevel.WARNING,
                "NO_FUNCTIONS",
                "No function information provided",
                "function",
                "Add function descriptions with operations and data types"
            )
            return
        
        for i, func in enumerate(functions):
            if not isinstance(func, dict):
                continue
            
            operations = func.get("operation", [])
            inputs = func.get("input", [])
            outputs = func.get("output", [])
            
            # Check if operations are defined
            if not operations:
                self._add_issue(
                    IssueLevel.WARNING,
                    "FUNCTION_NO_OPERATIONS",
                    "Function missing operation definitions",
                    f"function[{i}].operation",
                    "Add EDAM operations for this function"
                )
            
            # Check if function has input or output
            if not inputs and not outputs:
                self._add_issue(
                    IssueLevel.INFO,
                    "FUNCTION_NO_DATA",
                    "Function missing input and output data types",
                    f"function[{i}]",
                    "Add input and/or output data types"
                )
    
    def _check_consistency(self, tool_data: Dict) -> None:
        """Check internal consistency of the tool metadata."""
        # Check version consistency across different fields
        main_version = tool_data.get("version", [])
        
        # Check download versions
        downloads = tool_data.get("download", [])
        download_versions = set()
        for download in downloads:
            if isinstance(download, dict) and download.get("version"):
                download_versions.add(download["version"])
        
        # Check publication versions
        pubs = tool_data.get("publication", [])
        pub_versions = set()
        for pub in pubs:
            if isinstance(pub, dict) and pub.get("version"):
                pub_versions.add(pub["version"])
        
        # Warn about version inconsistencies
        all_versions = set(main_version) | download_versions | pub_versions
        if len(all_versions) > 3:  # Allow some reasonable variation
            self._add_issue(
                IssueLevel.INFO,
                "MANY_VERSIONS",
                f"Tool has many different versions mentioned ({len(all_versions)})",
                "version",
                "Consider consolidating or clarifying version information"
            )
    
    def _check_best_practices(self, tool_data: Dict) -> None:
        """Check compliance with bio.tools best practices."""
        # Check for comprehensive metadata
        optional_but_recommended = [
            "topic", "toolType", "operatingSystem", "language",
            "license", "maturity", "cost"
        ]
        
        missing_recommended = []
        for field in optional_but_recommended:
            if not tool_data.get(field):
                missing_recommended.append(field)
        
        if len(missing_recommended) > 3:
            self._add_issue(
                IssueLevel.INFO,
                "MISSING_RECOMMENDED_FIELDS",
                f"Several recommended fields missing: {', '.join(missing_recommended[:3])}...",
                "metadata",
                "Add recommended fields for better discoverability"
            )
        
        # Check for rich function descriptions
        functions = tool_data.get("function", [])
        if functions:
            functions_with_note = sum(1 for f in functions if f.get("note"))
            if functions_with_note < len(functions):
                self._add_issue(
                    IssueLevel.INFO,
                    "FUNCTIONS_MISSING_NOTES",
                    "Some functions missing descriptive notes",
                    "function",
                    "Add descriptive notes to explain function purposes"
                )


def format_lint_report(issues: List[LintIssue], tool_id: str = "Unknown") -> str:
    """
    Format linting issues into a human-readable report.
    
    Args:
        issues: List of linting issues
        tool_id: Tool identifier for the report
        
    Returns:
        Formatted report string
    """
    if not issues:
        return f"✅ {tool_id}: No issues found"
    
    # Group issues by level
    by_level = {level: [] for level in IssueLevel}
    for issue in issues:
        by_level[issue.level].append(issue)
    
    report_lines = [f"📋 Lint Report for {tool_id}"]
    report_lines.append("=" * (20 + len(tool_id)))
    
    # Summary
    total = len(issues)
    critical = len(by_level[IssueLevel.CRITICAL])
    errors = len(by_level[IssueLevel.ERROR])
    warnings = len(by_level[IssueLevel.WARNING])
    info = len(by_level[IssueLevel.INFO])
    
    report_lines.append(f"Total issues: {total}")
    if critical > 0:
        report_lines.append(f"🔴 Critical: {critical}")
    if errors > 0:
        report_lines.append(f"❌ Errors: {errors}")
    if warnings > 0:
        report_lines.append(f"⚠️  Warnings: {warnings}")
    if info > 0:
        report_lines.append(f"ℹ️  Info: {info}")
    
    report_lines.append("")
    
    # Detail each issue type
    for level in [IssueLevel.CRITICAL, IssueLevel.ERROR, IssueLevel.WARNING, IssueLevel.INFO]:
        level_issues = by_level[level]
        if not level_issues:
            continue
        
        level_symbol = {
            IssueLevel.CRITICAL: "🔴",
            IssueLevel.ERROR: "❌",
            IssueLevel.WARNING: "⚠️",
            IssueLevel.INFO: "ℹ️"
        }[level]
        
        report_lines.append(f"{level_symbol} {level.value.upper()}")
        report_lines.append("-" * 20)
        
        for issue in level_issues:
            report_lines.append(f"  {issue.code}: {issue.message}")
            report_lines.append(f"    Field: {issue.field_path}")
            if issue.value:
                report_lines.append(f"    Value: {issue.value}")
            if issue.suggestion:
                report_lines.append(f"    💡 Suggestion: {issue.suggestion}")
            report_lines.append("")
    
    return "\n".join(report_lines)
