"""
Tool Information Standards scoring module.

This module implements the bio.tools Tool Information Standards tiers
for evaluating tool metadata completeness and quality.
"""

from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import logging

try:
    from ..utils.logger import Logger
except ImportError:
    from utils.logger import Logger

logger = Logger.get_logger(__name__)


class Tier(Enum):
    """Tool Information Standards tiers."""
    SPARSE = 1
    MINIMAL = 2
    DETAILED = 3
    COMPLETE = 4
    COMPREHENSIVE = 5


class ToolInformationStandardsScorer:
    """
    Scores bio.tools entries according to Tool Information Standards.
    
    Implements the 5-tier system (SPARSE to COMPREHENSIVE) based on
    presence and quality of specific metadata attributes following
    the exact requirements from the Tool Information Standards diagram.
    """
    
    # Define tier requirements based on Tool Information Standards diagram
    TIER_REQUIREMENTS = {
        Tier.SPARSE: {
            "required_fields": ["name", "description", "homepage", "biotoolsID"],
            "required_groups": []
        },
        Tier.MINIMAL: {
            "required_fields": ["name", "description", "homepage", "biotoolsID", "topic", "toolType"],
            "required_groups": ["publication", "support"]
        },
        Tier.DETAILED: {
            "required_fields": [
                "name", "description", "homepage", "biotoolsID", 
                "topic", "toolType", "operatingSystem", "language", "license"
            ],
            "required_groups": ["publication", "support", "function", "documentation", "input_output"]
        },
        Tier.COMPLETE: {
            "required_fields": [
                "name", "description", "homepage", "biotoolsID",
                "topic", "toolType", "operatingSystem", "language", "license"
            ],
            "required_groups": [
                "publication", "support", "function", "documentation", "input_output",
                "accessibility", "code_availability", "downloads", "data_formats"
            ]
        },
        Tier.COMPREHENSIVE: {
            "required_fields": [
                "name", "description", "homepage", "biotoolsID",
                "topic", "toolType", "operatingSystem", "language", "license"
            ],
            "required_groups": [
                "publication", "support", "function", "documentation", "input_output",
                "accessibility", "code_availability", "downloads", "data_formats",
                "scientific_benchmark", "technical_monitoring"
            ]
        }
    }
    
    def __init__(self):
        """Initialize the scorer."""
        pass
    
    def score_tool(self, tool_data: Dict) -> Dict:
        """
        Score a tool according to Tool Information Standards.
        
        Args:
            tool_data: Tool metadata from bio.tools API
            
        Returns:
            Dictionary with scoring results including:
            - tier: Achieved tier (Tier enum)
            - score: Numerical score (0-100)
            - missing_fields: List of missing required fields
            - field_completeness: Per-field completeness analysis
            - recommendations: Suggestions for improvement
        """
        # Analyze field presence and quality
        field_analysis = self._analyze_fields(tool_data)
        
        # Determine achieved tier
        achieved_tier = self._determine_tier(field_analysis, tool_data)
        
        # Calculate numerical score
        score = self._calculate_score(field_analysis, achieved_tier)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(field_analysis, achieved_tier, tool_data)
        
        return {
            "tier": achieved_tier,
            "tier_name": achieved_tier.name,
            "tier_value": achieved_tier.value,
            "score": score,
            "field_analysis": field_analysis,
            "recommendations": recommendations,
            "summary": self._generate_summary(achieved_tier, score, field_analysis)
        }
    
    def _analyze_fields(self, tool_data: Dict) -> Dict:
        """
        Analyze presence and quality of fields in tool data.
        
        Args:
            tool_data: Tool metadata
            
        Returns:
            Field analysis with presence, quality, and completeness info
        """
        analysis = {
            "present_fields": set(),
            "missing_fields": set(),
            "field_quality": {},
            "group_satisfaction": {}
        }
        
        # Check basic required fields
        basic_fields = [
            "name", "description", "homepage", "biotoolsID",
            "topic", "toolType", "operatingSystem", "language",
            "license"
        ]
        
        for field in basic_fields:
            is_present = self._is_field_present(tool_data, field)
            if is_present:
                analysis["present_fields"].add(field)
                analysis["field_quality"][field] = self._assess_field_quality(tool_data, field)
            else:
                analysis["missing_fields"].add(field)
                analysis["field_quality"][field] = {"present": False, "completeness": 0.0, "issues": [f"Missing {field}"]}
        
        # Check complex field groups
        groups = [
            "publication", "support", "function", "documentation", "input_output",
            "accessibility", "code_availability", "downloads", "data_formats",
            "scientific_benchmark", "technical_monitoring"
        ]
        
        for group_name in groups:
            analysis["group_satisfaction"][group_name] = self._check_group_satisfaction(tool_data, group_name)
        
        return analysis
    
    def _is_field_present(self, tool_data: Dict, field: str) -> bool:
        """Check if a field is present and non-empty."""
        value = tool_data.get(field)
        
        if value is None:
            return False
        
        # Handle different data types
        if isinstance(value, str):
            return len(value.strip()) > 0
        elif isinstance(value, list):
            return len(value) > 0
        elif isinstance(value, dict):
            return len(value) > 0
        
        return bool(value)
    
    def _assess_field_quality(self, tool_data: Dict, field: str) -> Dict:
        """
        Assess the quality of a specific field.
        
        Returns:
            Dictionary with quality metrics
        """
        value = tool_data.get(field)
        quality = {
            "present": True,
            "completeness": 0.0,
            "issues": []
        }
        
        if field == "description":
            desc_len = len(value.strip()) if value else 0
            if desc_len < 10:
                quality["completeness"] = 0.0
                quality["issues"].append("Description too short (minimum 10 characters)")
            elif desc_len < 50:
                quality["completeness"] = 0.5
                quality["issues"].append("Description could be more detailed")
            elif desc_len > 1000:
                quality["completeness"] = 0.8
                quality["issues"].append("Description exceeds recommended length")
            else:
                quality["completeness"] = 1.0
        
        elif field == "topic":
            if isinstance(value, list) and len(value) > 0:
                quality["completeness"] = 1.0
                if len(value) < 2:
                    quality["issues"].append("Consider adding more specific topics")
            else:
                quality["completeness"] = 0.0
                quality["issues"].append("No topics specified")
        
        elif field == "homepage":
            if value and (value.startswith("http://") or value.startswith("https://")):
                quality["completeness"] = 1.0
            else:
                quality["completeness"] = 0.5
                quality["issues"].append("Homepage should be a valid HTTP/HTTPS URL")
        
        else:
            # Default quality assessment
            quality["completeness"] = 1.0 if value else 0.0
        
        return quality
    
    def _check_group_satisfaction(self, tool_data: Dict, group_name: str) -> Dict:
        """Check if a field group requirement is satisfied."""
        satisfaction = {
            "satisfied": False,
            "completeness": 0.0,
            "details": {}
        }
        
        if group_name == "publication":
            # Requirement 1: Valid identifier (DOI, PMID, PMCID) or "Unpublished"
            publications = tool_data.get("publication", [])
            valid_pubs = []
            for pub in publications:
                if pub.get("doi") or pub.get("pmid") or pub.get("pmcid"):
                    valid_pubs.append(pub)
            
            satisfaction["satisfied"] = len(valid_pubs) > 0
            satisfaction["completeness"] = 1.0 if len(valid_pubs) > 0 else 0.0
            satisfaction["details"] = {
                "total_publications": len(publications),
                "valid_publications": len(valid_pubs)
            }
        
        elif group_name == "support":
            # Requirement 2: Primary contact with email/link or support links
            credits = tool_data.get("credit", [])
            links = tool_data.get("link", [])
            
            primary_contacts = []
            for credit in credits:
                if "Primary contact" in credit.get("typeRole", []):
                    if credit.get("email") or credit.get("url"):
                        primary_contacts.append(credit)
            
            support_links = []
            support_types = ["Helpdesk", "Issue tracker", "Mailing list"]
            for link in links:
                if any(stype in link.get("type", []) for stype in support_types):
                    support_links.append(link)
            
            satisfaction["satisfied"] = len(primary_contacts) > 0 or len(support_links) > 0
            satisfaction["completeness"] = 1.0 if satisfaction["satisfied"] else 0.0
            satisfaction["details"] = {
                "primary_contacts": len(primary_contacts),
                "support_links": len(support_links)
            }
        
        elif group_name == "function":
            # Scientific operations
            functions = tool_data.get("function", [])
            operations_count = sum(len(func.get("operation", [])) for func in functions)
            
            satisfaction["satisfied"] = operations_count > 0
            satisfaction["completeness"] = 1.0 if operations_count > 0 else 0.0
            satisfaction["details"] = {
                "functions": len(functions),
                "operations": operations_count
            }
        
        elif group_name == "documentation":
            # Requirement 3: Appropriate link
            docs = tool_data.get("documentation", [])
            satisfaction["satisfied"] = len(docs) > 0
            satisfaction["completeness"] = 1.0 if len(docs) > 0 else 0.0
            satisfaction["details"] = {"count": len(docs)}
        
        elif group_name == "input_output":
            # Requirement 5: At least one input or output
            functions = tool_data.get("function", [])
            input_count = sum(len(func.get("input", [])) for func in functions)
            output_count = sum(len(func.get("output", [])) for func in functions)
            
            satisfaction["satisfied"] = input_count > 0 or output_count > 0
            satisfaction["completeness"] = 1.0 if satisfaction["satisfied"] else 0.0
            satisfaction["details"] = {
                "inputs": input_count,
                "outputs": output_count
            }
        
        elif group_name == "accessibility":
            # Accessibility information
            accessibility = tool_data.get("accessibility")
            cost = tool_data.get("cost")
            
            # Check for terms of use in documentation
            terms_of_use = False
            docs = tool_data.get("documentation", [])
            for doc in docs:
                if "Terms of use" in doc.get("type", []):
                    terms_of_use = True
                    break
            
            satisfaction["satisfied"] = bool(accessibility or cost or terms_of_use)
            satisfaction["completeness"] = 1.0 if satisfaction["satisfied"] else 0.0
            satisfaction["details"] = {
                "accessibility": bool(accessibility),
                "cost": bool(cost),
                "terms_of_use": terms_of_use
            }
        
        elif group_name == "code_availability":
            # Requirement 3: Appropriate link
            links = tool_data.get("link", [])
            downloads = tool_data.get("download", [])
            
            repo_links = [l for l in links if "Repository" in l.get("type", [])]
            source_downloads = [d for d in downloads if d.get("type") in ["Source code", "Software package"]]
            
            satisfaction["satisfied"] = len(repo_links) > 0 or len(source_downloads) > 0
            satisfaction["completeness"] = 1.0 if satisfaction["satisfied"] else 0.0
            satisfaction["details"] = {
                "repository_links": len(repo_links),
                "source_downloads": len(source_downloads)
            }
        
        elif group_name == "downloads":
            # Requirement 3: Appropriate link
            downloads = tool_data.get("download", [])
            satisfaction["satisfied"] = len(downloads) > 0
            satisfaction["completeness"] = 1.0 if len(downloads) > 0 else 0.0
            satisfaction["details"] = {"count": len(downloads)}
        
        elif group_name == "data_formats":
            # Requirement 6: At least one format for each input/output
            functions = tool_data.get("function", [])
            total_inputs = 0
            total_outputs = 0
            inputs_with_formats = 0
            outputs_with_formats = 0
            
            for func in functions:
                for inp in func.get("input", []):
                    total_inputs += 1
                    if inp.get("format") and len(inp["format"]) > 0:
                        inputs_with_formats += 1
                
                for out in func.get("output", []):
                    total_outputs += 1
                    if out.get("format") and len(out["format"]) > 0:
                        outputs_with_formats += 1
            
            all_formats_specified = (total_inputs > 0 and inputs_with_formats == total_inputs and 
                                   total_outputs > 0 and outputs_with_formats == total_outputs)
            
            satisfaction["satisfied"] = all_formats_specified
            satisfaction["completeness"] = 1.0 if all_formats_specified else 0.0
            satisfaction["details"] = {
                "total_inputs": total_inputs,
                "inputs_with_formats": inputs_with_formats,
                "total_outputs": total_outputs,
                "outputs_with_formats": outputs_with_formats
            }
        
        elif group_name == "scientific_benchmark":
            # Requirement 3: Appropriate link
            publications = tool_data.get("publication", [])
            benchmark_pubs = [p for p in publications if "Benchmarking study" in p.get("type", [])]
            
            links = tool_data.get("link", [])
            benchmark_links = [l for l in links if "benchmark" in l.get("url", "").lower()]
            
            satisfaction["satisfied"] = len(benchmark_pubs) > 0 or len(benchmark_links) > 0
            satisfaction["completeness"] = 1.0 if satisfaction["satisfied"] else 0.0
            satisfaction["details"] = {
                "benchmark_publications": len(benchmark_pubs),
                "benchmark_links": len(benchmark_links)
            }
        
        elif group_name == "technical_monitoring":
            # Requirement 3: Appropriate link
            links = tool_data.get("link", [])
            monitoring_links = [l for l in links if "Technical monitoring" in l.get("type", [])]
            
            satisfaction["satisfied"] = len(monitoring_links) > 0
            satisfaction["completeness"] = 1.0 if len(monitoring_links) > 0 else 0.0
            satisfaction["details"] = {"monitoring_links": len(monitoring_links)}
        
        return satisfaction
    
    def _determine_tier(self, field_analysis: Dict, tool_data: Dict) -> Tier:
        """Determine the highest achieved tier."""
        for tier in reversed(list(Tier)):
            if self._tier_satisfied(tier, field_analysis, tool_data):
                return tier
        return Tier.SPARSE  # Fallback to lowest tier
    
    def _tier_satisfied(self, tier: Tier, field_analysis: Dict, tool_data: Dict) -> bool:
        """Check if a specific tier is satisfied."""
        requirements = self.TIER_REQUIREMENTS[tier]
        
        # Check required fields
        for field in requirements["required_fields"]:
            if field not in field_analysis["present_fields"]:
                return False
        
        # Check required groups
        for group in requirements["required_groups"]:
            if not field_analysis["group_satisfaction"][group]["satisfied"]:
                return False
        
        return True
    
    def _calculate_score(self, field_analysis: Dict, achieved_tier: Tier) -> float:
        """Calculate numerical score based on completeness."""
        # Base score from achieved tier (20 points per tier)
        base_score = achieved_tier.value * 20
        
        # Add bonus points for field quality
        quality_bonus = 0
        total_fields = len(field_analysis["field_quality"])
        
        if total_fields > 0:
            quality_sum = sum(fq["completeness"] for fq in field_analysis["field_quality"].values())
            quality_bonus = (quality_sum / total_fields) * 20
        
        return min(100.0, round(base_score + quality_bonus, 1))
    
    def _generate_recommendations(self, field_analysis: Dict, achieved_tier: Tier, tool_data: Dict) -> List[str]:
        """Generate comprehensive recommendations for all tiers."""
        recommendations = []
        
        # If already at highest tier, congratulate
        if achieved_tier.value == 5:
            recommendations.append("🎉 Congratulations! Tool has achieved the highest tier (TIER 5) - excellent quality!")
            return recommendations
        
        # Generate recommendations for all higher tiers
        for tier_value in range(achieved_tier.value + 1, 6):  # Up to TIER 5
            next_tier = Tier(tier_value)
            next_requirements = self.TIER_REQUIREMENTS[next_tier]
            
            recommendations.append(f"\n**📈 To achieve {next_tier.name} ({self._get_tier_description(next_tier)}):**")
            
            # Check missing fields
            missing_fields = []
            for field in next_requirements["required_fields"]:
                if field not in field_analysis["present_fields"]:
                    missing_fields.append(field)
            
            # Check missing groups
            missing_groups = []
            for group in next_requirements["required_groups"]:
                if not field_analysis["group_satisfaction"][group]["satisfied"]:
                    missing_groups.append(group)
            
            # Add specific recommendations
            if missing_fields:
                for field in missing_fields:
                    recommendations.append(f"  • **{field}**: {self._get_field_description(field)}")
            
            if missing_groups:
                for group in missing_groups:
                    recommendations.append(f"  • **{group}**: {self._get_group_description(group)}")
        
        # Add specific quality improvements for current fields
        quality_issues = []
        for field, quality in field_analysis["field_quality"].items():
            if quality["issues"]:
                quality_issues.append(f"**{field}**: {quality['issues'][0]}")
        
        if quality_issues:
            recommendations.append(f"\n**🔧 Quality Improvements for Current Fields:**")
            for issue in quality_issues[:5]:  # Limit to top 5
                recommendations.append(f"  • {issue}")
        
        return recommendations
    
    def _get_tier_description(self, tier: Tier) -> str:
        """Get user-friendly description for each tier."""
        descriptions = {
            Tier.SPARSE: "Basic information",
            Tier.MINIMAL: "Essential details with some documentation",
            Tier.DETAILED: "Good coverage with comprehensive info",
            Tier.COMPLETE: "Very comprehensive with rich metadata",
            Tier.COMPREHENSIVE: "Exceptional quality with complete information"
        }
        return descriptions.get(tier, "Enhanced information")
    
    def _get_field_description(self, field: str) -> str:
        """Get user-friendly description for missing fields."""
        descriptions = {
            "name": "Tool name/title",
            "description": "Clear description of tool purpose",
            "homepage": "Tool website or main page",
            "biotoolsID": "Unique bio.tools identifier",
            "topic": "Scientific topics/domains",
            "function": "Scientific operations performed",
            "toolType": "Type of software tool",
            "operatingSystem": "Supported operating systems",
            "language": "Programming language(s)",
            "license": "Software license",
            "link": "Additional links (download, documentation, etc.)",
            "download": "Download information",
            "documentation": "Documentation resources",
            "publication": "Associated publications",
            "credit": "Credits and acknowledgments",
            "contact": "Contact information"
        }
        return descriptions.get(field, f"Add {field} information")
    
    def _get_group_description(self, group: str) -> str:
        """Get user-friendly description for missing groups."""
        descriptions = {
            "basic_info": "Complete basic information (name, description, homepage)",
            "scientific_info": "Scientific classification (topics, functions, tool type)",
            "technical_info": "Technical details (OS, language, license)",
            "resource_links": "Resource links (downloads, documentation)",
            "attribution": "Attribution information (publications, credits, contacts)"
        }
        return descriptions.get(group, f"Complete {group} requirements")
    
    def _generate_summary(self, tier: Tier, score: float, field_analysis: Dict) -> str:
        """Generate human-readable summary."""
        missing_count = len(field_analysis["missing_fields"])
        
        if missing_count == 0:
            return f"Achieved {tier.name} tier with {score:.1f}% completeness - excellent!"
        else:
            return f"Achieved {tier.name} tier with {score:.1f}% completeness ({missing_count} fields missing)"
