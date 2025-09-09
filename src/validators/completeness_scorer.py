"""
Completeness scoring module based on Tool Information Standards.

This module implements the exact field checking shown in the Tool Information
Standards diagram, mapping each field to specific tiers and scoring completeness
based on presence and quality of the required attributes.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import logging
from ..utils.logger import Logger

logger = Logger.get_logger(__name__)


class CompletnessTier(Enum):
    """Tool Information Standards tiers based on the official diagram."""
    SPARSE = 1
    MINIMAL = 2
    DETAILED = 3
    COMPLETE = 4
    COMPREHENSIVE = 5


class ToolCompletenessScorer:
    """
    Scores bio.tools entries based on the exact Tool Information Standards diagram.
    
    Implements field checking for each tier as shown in the official standards,
    providing detailed analysis of what fields are present/missing.
    """
    
    # Field requirements based on the Tool Information Standards diagram
    TIER_FIELDS = {
        CompletnessTier.SPARSE: {
            # Basic details
            "name": True,
            "description": True, 
            "homepage": True,
            "biotoolsID": True,  # Unique ID
        },
        
        CompletnessTier.MINIMAL: {
            # Inherits SPARSE fields plus:
            "toolType": True,
            "topic": True,  # Scientific topic(s)
            "publication": True,  # Publication (1)
            "support": "at_least_one",  # Support -> (2) - at least one support type
        },
        
        CompletnessTier.DETAILED: {
            # Inherits MINIMAL fields plus:
            "function": True,  # Scientific operation(s)
            "documentation": "at_least_one",  # Documentation (3) -> at least one type
            "operatingSystem": True,
            "language": True,
            "license": True,  # License (4)
            "input_output": True,  # Type of input & output data (5)
        },
        
        CompletnessTier.COMPLETE: {
            # Inherits DETAILED fields plus:
            "accessibility": "at_least_one",  # Accessibility -> at least one type
            "code_availability": "at_least_one",  # Code availability (3) -> at least one type
            "downloads": "at_least_one",  # Downloads (3) -> at least one type
            "supported_data_formats": True,  # Supported data format(s) (6)
        },
        
        CompletnessTier.COMPREHENSIVE: {
            # Inherits COMPLETE fields plus:
            "scientific_benchmark": True,  # Scientific benchmark (3)
            "technical_monitoring": True,  # Technical monitoring (3)
        }
    }

    def __init__(self):
        """Initialize the completeness scorer."""
        pass

    def score_tool(self, tool_data: Dict) -> Dict:
        """
        Score a tool based on Tool Information Standards completeness.
        
        Args:
            tool_data: Tool metadata from bio.tools API
            
        Returns:
            Dictionary with completeness analysis including:
            - achieved_tier: Highest tier achieved
            - tier_scores: Score for each tier (boolean)
            - field_analysis: Detailed field-by-field analysis
            - missing_fields: What's needed for next tier
            - completeness_percentage: Overall completeness score
        """
        # Analyze all fields
        field_analysis = self._analyze_all_fields(tool_data)
        
        # Determine achieved tiers
        tier_results = self._evaluate_all_tiers(field_analysis)
        
        # Calculate overall score
        completeness_score = self._calculate_completeness_score(tier_results)
        
        # Get highest achieved tier
        achieved_tier = self._get_highest_tier(tier_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(tier_results, field_analysis)
        
        return {
            "achieved_tier": achieved_tier,
            "achieved_tier_name": achieved_tier.name if achieved_tier else "NONE",
            "tier_results": {tier.name: result for tier, result in tier_results.items()},
            "field_analysis": field_analysis,
            "completeness_score": completeness_score,
            "recommendations": recommendations,
            "summary": self._generate_summary(achieved_tier, completeness_score, tier_results)
        }

    def _analyze_all_fields(self, tool_data: Dict) -> Dict:
        """Analyze all fields relevant to the Tool Information Standards."""
        analysis = {}
        
        # Basic fields (SPARSE tier)
        analysis["name"] = self._check_name(tool_data)
        analysis["description"] = self._check_description(tool_data)
        analysis["homepage"] = self._check_homepage(tool_data)
        analysis["biotoolsID"] = self._check_biotools_id(tool_data)
        
        # MINIMAL tier fields
        analysis["toolType"] = self._check_tool_type(tool_data)
        analysis["topic"] = self._check_scientific_topics(tool_data)
        analysis["publication"] = self._check_publications(tool_data)
        analysis["support"] = self._check_support(tool_data)
        
        # DETAILED tier fields
        analysis["function"] = self._check_scientific_operations(tool_data)
        analysis["documentation"] = self._check_documentation(tool_data)
        analysis["operatingSystem"] = self._check_operating_system(tool_data)
        analysis["language"] = self._check_language(tool_data)
        analysis["license"] = self._check_license(tool_data)
        analysis["input_output"] = self._check_input_output_data(tool_data)
        
        # COMPLETE tier fields
        analysis["accessibility"] = self._check_accessibility(tool_data)
        analysis["code_availability"] = self._check_code_availability(tool_data)
        analysis["downloads"] = self._check_downloads(tool_data)
        analysis["supported_data_formats"] = self._check_supported_data_formats(tool_data)
        
        # COMPREHENSIVE tier fields
        analysis["scientific_benchmark"] = self._check_scientific_benchmark(tool_data)
        analysis["technical_monitoring"] = self._check_technical_monitoring(tool_data)
        
        return analysis

    def _check_name(self, tool_data: Dict) -> Dict:
        """Check if tool name is present and valid."""
        name = tool_data.get("name")
        return {
            "present": bool(name and name.strip()),
            "value": name,
            "quality_score": 1.0 if name and len(name.strip()) >= 1 else 0.0,
            "issues": [] if name and len(name.strip()) >= 1 else ["Missing or empty tool name"]
        }

    def _check_description(self, tool_data: Dict) -> Dict:
        """Check if description is present and adequate."""
        description = tool_data.get("description")
        issues = []
        quality_score = 0.0
        
        if not description or not description.strip():
            issues.append("Missing description")
        else:
            desc_length = len(description.strip())
            if desc_length < 10:
                issues.append("Description too short (minimum 10 characters)")
            elif desc_length < 50:
                issues.append("Description could be more detailed")
                quality_score = 0.5
            elif desc_length > 1000:
                issues.append("Description exceeds maximum length (1000 characters)")
                quality_score = 0.8
            else:
                quality_score = 1.0
        
        return {
            "present": bool(description and description.strip()),
            "value": description,
            "quality_score": quality_score,
            "issues": issues
        }

    def _check_homepage(self, tool_data: Dict) -> Dict:
        """Check if homepage URL is present and valid."""
        homepage = tool_data.get("homepage")
        issues = []
        quality_score = 0.0
        
        if not homepage or not homepage.strip():
            issues.append("Missing homepage URL")
        else:
            homepage = homepage.strip()
            if not (homepage.startswith("http://") or homepage.startswith("https://")):
                issues.append("Homepage should be a valid HTTP/HTTPS URL")
                quality_score = 0.5
            else:
                quality_score = 1.0
        
        return {
            "present": bool(homepage and homepage.strip()),
            "value": homepage,
            "quality_score": quality_score,
            "issues": issues
        }

    def _check_biotools_id(self, tool_data: Dict) -> Dict:
        """Check if biotoolsID is present."""
        biotools_id = tool_data.get("biotoolsID")
        return {
            "present": bool(biotools_id and biotools_id.strip()),
            "value": biotools_id,
            "quality_score": 1.0 if biotools_id and biotools_id.strip() else 0.0,
            "issues": [] if biotools_id and biotools_id.strip() else ["Missing biotoolsID"]
        }

    def _check_tool_type(self, tool_data: Dict) -> Dict:
        """Check if tool type is present."""
        tool_type = tool_data.get("toolType")
        present = bool(tool_type and len(tool_type) > 0)
        
        return {
            "present": present,
            "value": tool_type,
            "quality_score": 1.0 if present else 0.0,
            "issues": [] if present else ["Missing tool type"]
        }

    def _check_scientific_topics(self, tool_data: Dict) -> Dict:
        """Check if scientific topics are present."""
        topics = tool_data.get("topic", [])
        present = bool(topics and len(topics) > 0)
        issues = []
        
        if not present:
            issues.append("Missing scientific topics")
        elif len(topics) < 2:
            issues.append("Consider adding more specific topics")
        
        return {
            "present": present,
            "value": topics,
            "count": len(topics) if topics else 0,
            "quality_score": 1.0 if present else 0.0,
            "issues": issues
        }

    def _check_publications(self, tool_data: Dict) -> Dict:
        """Check if publications are present with valid identifiers (requirement 1)."""
        publications = tool_data.get("publication", [])
        valid_pubs = []
        issues = []
        
        for pub in publications:
            # Check for valid identifier (DOI, PMID, PMCID) or "Unpublished"
            has_doi = bool(pub.get("doi"))
            has_pmid = bool(pub.get("pmid"))
            has_pmcid = bool(pub.get("pmcid"))
            
            if has_doi or has_pmid or has_pmcid:
                valid_pubs.append(pub)
            else:
                issues.append("Publication missing valid identifier (DOI, PMID, or PMCID)")
        
        present = len(valid_pubs) > 0
        if not publications:
            issues.append("Missing publications")
        
        return {
            "present": present,
            "value": publications,
            "valid_count": len(valid_pubs),
            "total_count": len(publications),
            "quality_score": 1.0 if present else 0.0,
            "issues": issues
        }

    def _check_support(self, tool_data: Dict) -> Dict:
        """Check if support information is present (requirement 2)."""
        # Support can come from multiple sources: credit with contact info, or link with support types
        credits = tool_data.get("credit", [])
        links = tool_data.get("link", [])
        
        # Check for primary contact in credits
        primary_contacts = []
        for credit in credits:
            if "Primary contact" in credit.get("typeRole", []):
                if credit.get("email") or credit.get("url"):
                    primary_contacts.append(credit)
        
        # Check for support links (helpdesk, issue tracker, mailing list)
        support_links = []
        support_types = ["Helpdesk", "Issue tracker", "Mailing list"]
        for link in links:
            link_types = link.get("type", [])
            if any(stype in link_types for stype in support_types):
                support_links.append(link)
        
        has_support = len(primary_contacts) > 0 or len(support_links) > 0
        issues = []
        
        if not has_support:
            issues.append("Missing support information (primary contact or support links)")
        
        return {
            "present": has_support,
            "primary_contacts": len(primary_contacts),
            "support_links": len(support_links),
            "quality_score": 1.0 if has_support else 0.0,
            "issues": issues
        }

    def _check_scientific_operations(self, tool_data: Dict) -> Dict:
        """Check if scientific operations are present in functions."""
        functions = tool_data.get("function", [])
        operations_count = 0
        
        for func in functions:
            operations = func.get("operation", [])
            operations_count += len(operations)
        
        present = operations_count > 0
        issues = []
        
        if not present:
            issues.append("Missing scientific operations in function descriptions")
        
        return {
            "present": present,
            "value": functions,
            "operations_count": operations_count,
            "functions_count": len(functions),
            "quality_score": 1.0 if present else 0.0,
            "issues": issues
        }

    def _check_documentation(self, tool_data: Dict) -> Dict:
        """Check if documentation links are present (requirement 3)."""
        documentation = tool_data.get("documentation", [])
        present = len(documentation) > 0
        issues = []
        
        if not present:
            issues.append("Missing documentation links")
        
        # Check for different types of documentation
        doc_types = {}
        for doc in documentation:
            for doc_type in doc.get("type", []):
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            "present": present,
            "value": documentation,
            "count": len(documentation),
            "types": doc_types,
            "quality_score": 1.0 if present else 0.0,
            "issues": issues
        }

    def _check_operating_system(self, tool_data: Dict) -> Dict:
        """Check if operating system is specified."""
        os_list = tool_data.get("operatingSystem", [])
        present = len(os_list) > 0
        
        return {
            "present": present,
            "value": os_list,
            "count": len(os_list),
            "quality_score": 1.0 if present else 0.0,
            "issues": [] if present else ["Missing operating system information"]
        }

    def _check_language(self, tool_data: Dict) -> Dict:
        """Check if programming language is specified."""
        languages = tool_data.get("language", [])
        present = len(languages) > 0
        
        return {
            "present": present,
            "value": languages,
            "count": len(languages),
            "quality_score": 1.0 if present else 0.0,
            "issues": [] if present else ["Missing programming language information"]
        }

    def _check_license(self, tool_data: Dict) -> Dict:
        """Check if license is specified (requirement 4)."""
        license_info = tool_data.get("license")
        present = bool(license_info and license_info.strip())
        issues = []
        
        if not present:
            issues.append("Missing license information")
        elif license_info in ["Unlicensed", "Not licensed"]:
            # These are valid but should be noted
            issues.append("Tool is unlicensed")
        
        return {
            "present": present,
            "value": license_info,
            "quality_score": 1.0 if present else 0.0,
            "issues": issues
        }

    def _check_input_output_data(self, tool_data: Dict) -> Dict:
        """Check if input/output data types are specified (requirement 5)."""
        functions = tool_data.get("function", [])
        input_count = 0
        output_count = 0
        
        for func in functions:
            inputs = func.get("input", [])
            outputs = func.get("output", [])
            input_count += len(inputs)
            output_count += len(outputs)
        
        has_io = input_count > 0 or output_count > 0
        issues = []
        
        if input_count == 0 and output_count == 0:
            issues.append("Missing input and output data specifications")
        elif input_count == 0:
            issues.append("Missing input data specifications")
        elif output_count == 0:
            issues.append("Missing output data specifications")
        
        return {
            "present": has_io,
            "input_count": input_count,
            "output_count": output_count,
            "quality_score": 1.0 if has_io else 0.0,
            "issues": issues
        }

    def _check_accessibility(self, tool_data: Dict) -> Dict:
        """Check if accessibility information is present."""
        accessibility = tool_data.get("accessibility")
        cost = tool_data.get("cost")
        
        # Check terms of use in documentation
        terms_of_use = False
        documentation = tool_data.get("documentation", [])
        for doc in documentation:
            if "Terms of use" in doc.get("type", []):
                terms_of_use = True
                break
        
        has_accessibility_info = bool(accessibility or cost or terms_of_use)
        issues = []
        
        if not has_accessibility_info:
            issues.append("Missing accessibility information (accessibility, cost, or terms of use)")
        
        return {
            "present": has_accessibility_info,
            "accessibility": accessibility,
            "cost": cost,
            "terms_of_use": terms_of_use,
            "quality_score": 1.0 if has_accessibility_info else 0.0,
            "issues": issues
        }

    def _check_code_availability(self, tool_data: Dict) -> Dict:
        """Check if code availability information is present (requirement 3)."""
        links = tool_data.get("link", [])
        downloads = tool_data.get("download", [])
        
        # Check for repository links
        repository_links = []
        for link in links:
            if "Repository" in link.get("type", []):
                repository_links.append(link)
        
        # Check for source code downloads
        source_downloads = []
        for download in downloads:
            if download.get("type") in ["Source code", "Software package"]:
                source_downloads.append(download)
        
        has_code_availability = len(repository_links) > 0 or len(source_downloads) > 0
        issues = []
        
        if not has_code_availability:
            issues.append("Missing code availability (repository link or source code download)")
        
        return {
            "present": has_code_availability,
            "repository_links": len(repository_links),
            "source_downloads": len(source_downloads),
            "quality_score": 1.0 if has_code_availability else 0.0,
            "issues": issues
        }

    def _check_downloads(self, tool_data: Dict) -> Dict:
        """Check if download links are present (requirement 3)."""
        downloads = tool_data.get("download", [])
        present = len(downloads) > 0
        issues = []
        
        if not present:
            issues.append("Missing download links")
        
        # Categorize download types
        download_types = {}
        for download in downloads:
            dtype = download.get("type")
            if dtype:
                download_types[dtype] = download_types.get(dtype, 0) + 1
        
        return {
            "present": present,
            "value": downloads,
            "count": len(downloads),
            "types": download_types,
            "quality_score": 1.0 if present else 0.0,
            "issues": issues
        }

    def _check_supported_data_formats(self, tool_data: Dict) -> Dict:
        """Check if data formats are specified for inputs/outputs (requirement 6)."""
        functions = tool_data.get("function", [])
        inputs_with_formats = 0
        outputs_with_formats = 0
        total_inputs = 0
        total_outputs = 0
        
        for func in functions:
            inputs = func.get("input", [])
            outputs = func.get("output", [])
            
            for inp in inputs:
                total_inputs += 1
                if inp.get("format") and len(inp["format"]) > 0:
                    inputs_with_formats += 1
            
            for out in outputs:
                total_outputs += 1
                if out.get("format") and len(out["format"]) > 0:
                    outputs_with_formats += 1
        
        # Need formats for all inputs and outputs
        has_all_formats = (total_inputs > 0 and inputs_with_formats == total_inputs and 
                          total_outputs > 0 and outputs_with_formats == total_outputs)
        
        issues = []
        if total_inputs == 0 and total_outputs == 0:
            issues.append("No input/output data specified")
        elif inputs_with_formats < total_inputs:
            issues.append(f"Missing formats for {total_inputs - inputs_with_formats} input(s)")
        elif outputs_with_formats < total_outputs:
            issues.append(f"Missing formats for {total_outputs - outputs_with_formats} output(s)")
        
        return {
            "present": has_all_formats,
            "inputs_with_formats": inputs_with_formats,
            "total_inputs": total_inputs,
            "outputs_with_formats": outputs_with_formats,
            "total_outputs": total_outputs,
            "quality_score": 1.0 if has_all_formats else 0.0,
            "issues": issues
        }

    def _check_scientific_benchmark(self, tool_data: Dict) -> Dict:
        """Check if scientific benchmark information is present (requirement 3)."""
        # Look for benchmark-related publications
        publications = tool_data.get("publication", [])
        benchmark_pubs = []
        
        for pub in publications:
            pub_types = pub.get("type", [])
            if "Benchmarking study" in pub_types:
                benchmark_pubs.append(pub)
        
        # Look for benchmark-related links or documentation
        links = tool_data.get("link", [])
        documentation = tool_data.get("documentation", [])
        
        benchmark_links = []
        for link in links:
            if "benchmark" in link.get("url", "").lower() or "benchmark" in link.get("note", "").lower():
                benchmark_links.append(link)
        
        benchmark_docs = []
        for doc in documentation:
            if "benchmark" in doc.get("url", "").lower() or "benchmark" in doc.get("note", "").lower():
                benchmark_docs.append(doc)
        
        has_benchmark = len(benchmark_pubs) > 0 or len(benchmark_links) > 0 or len(benchmark_docs) > 0
        issues = []
        
        if not has_benchmark:
            issues.append("Missing scientific benchmark information")
        
        return {
            "present": has_benchmark,
            "benchmark_publications": len(benchmark_pubs),
            "benchmark_links": len(benchmark_links),
            "benchmark_docs": len(benchmark_docs),
            "quality_score": 1.0 if has_benchmark else 0.0,
            "issues": issues
        }

    def _check_technical_monitoring(self, tool_data: Dict) -> Dict:
        """Check if technical monitoring information is present (requirement 3)."""
        # Look for technical monitoring links
        links = tool_data.get("link", [])
        monitoring_links = []
        
        for link in links:
            if "Technical monitoring" in link.get("type", []):
                monitoring_links.append(link)
        
        # Look for status/monitoring related links
        status_links = []
        for link in links:
            url = link.get("url", "").lower()
            note = link.get("note", "").lower()
            if any(term in url or term in note for term in ["status", "monitoring", "uptime", "health"]):
                status_links.append(link)
        
        has_monitoring = len(monitoring_links) > 0 or len(status_links) > 0
        issues = []
        
        if not has_monitoring:
            issues.append("Missing technical monitoring information")
        
        return {
            "present": has_monitoring,
            "monitoring_links": len(monitoring_links),
            "status_links": len(status_links),
            "quality_score": 1.0 if has_monitoring else 0.0,
            "issues": issues
        }

    def _evaluate_all_tiers(self, field_analysis: Dict) -> Dict:
        """Evaluate achievement of all tiers."""
        tier_results = {}
        
        for tier in CompletnessTier:
            tier_results[tier] = self._evaluate_tier(tier, field_analysis)
            
        return tier_results

    def _evaluate_tier(self, tier: CompletnessTier, field_analysis: Dict) -> Dict:
        """Evaluate if a specific tier is achieved."""
        required_fields = self._get_inherited_fields(tier)
        
        satisfied = True
        missing_fields = []
        field_results = {}
        
        for field_name, requirement in required_fields.items():
            field_data = field_analysis.get(field_name, {})
            
            if requirement == "at_least_one":
                # Need at least one type/option for this field
                field_satisfied = field_data.get("present", False)
                # Additional check for fields that need specific counts
                if field_name == "support":
                    field_satisfied = (field_data.get("primary_contacts", 0) > 0 or 
                                     field_data.get("support_links", 0) > 0)
                elif field_name == "documentation":
                    field_satisfied = field_data.get("count", 0) > 0
                elif field_name == "accessibility":
                    field_satisfied = (field_data.get("accessibility") or 
                                     field_data.get("cost") or 
                                     field_data.get("terms_of_use", False))
                elif field_name == "code_availability":
                    field_satisfied = (field_data.get("repository_links", 0) > 0 or 
                                     field_data.get("source_downloads", 0) > 0)
                elif field_name == "downloads":
                    field_satisfied = field_data.get("count", 0) > 0
            else:
                # Standard boolean requirement
                field_satisfied = field_data.get("present", False)
            
            field_results[field_name] = {
                "satisfied": field_satisfied,
                "requirement": requirement,
                "data": field_data
            }
            
            if not field_satisfied:
                satisfied = False
                missing_fields.append(field_name)
        
        return {
            "satisfied": satisfied,
            "missing_fields": missing_fields,
            "field_results": field_results,
            "total_fields": len(required_fields),
            "satisfied_fields": len(required_fields) - len(missing_fields)
        }

    def _get_inherited_fields(self, tier: CompletnessTier) -> Dict:
        """Get all field requirements for a tier, including inherited ones."""
        inherited_fields = {}
        
        # Add fields from all previous tiers and current tier
        for t in CompletnessTier:
            if t.value <= tier.value:
                tier_fields = self.TIER_FIELDS.get(t, {})
                inherited_fields.update(tier_fields)
        
        return inherited_fields

    def _get_highest_tier(self, tier_results: Dict) -> Optional[CompletnessTier]:
        """Get the highest achieved tier."""
        for tier in reversed(list(CompletnessTier)):
            if tier_results[tier]["satisfied"]:
                return tier
        return None

    def _calculate_completeness_score(self, tier_results: Dict) -> float:
        """Calculate overall completeness percentage."""
        # Base scoring: 20 points per tier achieved
        tier_score = 0
        for tier in CompletnessTier:
            if tier_results[tier]["satisfied"]:
                tier_score = tier.value * 20
                
        # Bonus points for partial completion of next tier
        highest_tier = self._get_highest_tier(tier_results)
        if highest_tier and highest_tier.value < 5:
            next_tier = CompletnessTier(highest_tier.value + 1)
            next_tier_result = tier_results[next_tier]
            
            total_fields = next_tier_result["total_fields"]
            satisfied_fields = next_tier_result["satisfied_fields"]
            
            if total_fields > 0:
                partial_bonus = (satisfied_fields / total_fields) * 20
                tier_score += partial_bonus
                
        return min(100.0, round(tier_score, 1))

    def _generate_recommendations(self, tier_results: Dict, field_analysis: Dict) -> List[str]:
        """Generate comprehensive recommendations for all tiers."""
        recommendations = []
        
        # Find current highest achieved tier
        highest_tier = self._get_highest_tier(tier_results)
        
        if highest_tier and highest_tier.value == 5:
            recommendations.append("🎉 Congratulations! Tool has achieved COMPREHENSIVE tier - excellent completeness!")
            return recommendations
        
        # Focus on next 2-3 tiers to avoid overwhelming users
        start_tier = 1 if highest_tier is None else highest_tier.value + 1
        max_tiers_to_show = min(3, 6 - start_tier)  # Show max 3 tiers ahead
        
        for i, tier_value in enumerate(range(start_tier, start_tier + max_tiers_to_show)):
            if tier_value > 5:
                break
                
            tier = CompletnessTier(tier_value)
            tier_result = tier_results[tier]
            missing_fields = tier_result["missing_fields"]
            
            if missing_fields:
                # Add priority indicator for next tier
                priority_indicator = " 🎯 **NEXT GOAL**" if i == 0 else ""
                recommendations.append(f"\n**📈 To achieve {tier.name} tier ({self._get_tier_description(tier)}):{priority_indicator}**")
                
                # Group fields by priority/difficulty for better UX
                high_priority = []
                medium_priority = []
                
                for field in missing_fields:
                    field_data = field_analysis.get(field, {})
                    issues = field_data.get("issues", [])
                    description = self._get_field_description(field)
                    
                    # Determine if this is a high-priority/easy field
                    if field in ["publication", "license", "operatingSystem", "language"]:
                        if issues:
                            high_priority.append(f"  • **{field}**: {issues[0]}")
                        else:
                            high_priority.append(f"  • **{field}**: {description}")
                    else:
                        if issues:
                            medium_priority.append(f"  • **{field}**: {issues[0]}")
                        else:
                            medium_priority.append(f"  • **{field}**: {description}")
                
                # Add high priority items first
                recommendations.extend(high_priority)
                recommendations.extend(medium_priority)
                
                # Add helpful tip for next tier only
                if i == 0:
                    recommendations.append(f"  💡 *Complete these {len(missing_fields)} fields to reach {tier.name} tier*")
                    
        return recommendations
    
    def _get_tier_description(self, tier: CompletnessTier) -> str:
        """Get user-friendly description for each tier."""
        descriptions = {
            CompletnessTier.SPARSE: "Basic tool information",
            CompletnessTier.MINIMAL: "Essential details for findability", 
            CompletnessTier.DETAILED: "Comprehensive tool information",
            CompletnessTier.COMPLETE: "Full metadata with accessibility info",
            CompletnessTier.COMPREHENSIVE: "Complete with quality metrics"
        }
        return descriptions.get(tier, "Enhanced tool information")
    
    def _get_field_description(self, field: str) -> str:
        """Get user-friendly description for missing fields."""
        descriptions = {
            "name": "Tool name/title",
            "description": "Clear description of tool purpose", 
            "homepage": "Tool website URL",
            "biotoolsID": "Unique bio.tools identifier",
            "toolType": "Type of tool (e.g., Command-line tool, Web application)",
            "topic": "Scientific topics/domains the tool addresses",
            "publication": "Associated publication(s)",
            "support": "Support information (help desk, documentation, etc.)",
            "function": "Scientific operations the tool performs",
            "documentation": "Documentation resources (manual, tutorial, etc.)",
            "operatingSystem": "Supported operating systems",
            "language": "Programming language(s)",
            "license": "Software license information",
            "input_output": "Data input and output formats/types",
            "accessibility": "Tool accessibility information",
            "code_availability": "Source code availability",
            "downloads": "Download statistics/information", 
            "supported_data_formats": "Specific supported file formats",
            "scientific_benchmark": "Scientific benchmarking information",
            "technical_monitoring": "Technical monitoring/uptime data"
        }
        return descriptions.get(field, f"Add {field} information")

    def _generate_summary(self, achieved_tier: Optional[CompletnessTier], 
                         completeness_score: float, tier_results: Dict) -> str:
        """Generate human-readable summary."""
        if achieved_tier:
            return (f"Tool achieves {achieved_tier.name} tier "
                   f"(completeness: {completeness_score:.1f}%)")
        else:
            return f"Tool does not achieve any tier (completeness: {completeness_score:.1f}%)"
