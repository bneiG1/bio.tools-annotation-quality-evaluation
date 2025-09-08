"""
Tool Information Standards scoring module.

This module implements the bio.tools Tool Information Standards tiers
for evaluating tool metadata completeness and quality.
"""

from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


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
    presence and quality of specific metadata attributes.
    """
    
    # Define tier requirements based on Tool Information Standards
    TIER_REQUIREMENTS = {
        Tier.SPARSE: {
            "required_fields": ["name", "description", "homepage", "biotoolsID"],
            "required_groups": []
        },
        Tier.MINIMAL: {
            "required_fields": ["name", "description", "homepage", "biotoolsID", "topic", "toolType"],
            "required_groups": ["function_basic"]
        },
        Tier.DETAILED: {
            "required_fields": [
                "name", "description", "homepage", "biotoolsID", 
                "topic", "toolType", "operatingSystem", "language"
            ],
            "required_groups": ["function_detailed", "documentation"]
        },
        Tier.COMPLETE: {
            "required_fields": [
                "name", "description", "homepage", "biotoolsID",
                "topic", "toolType", "operatingSystem", "language",
                "license", "maturity", "cost"
            ],
            "required_groups": [
                "function_complete", "documentation", "download", 
                "link", "publication", "contact"
            ]
        },
        Tier.COMPREHENSIVE: {
            "required_fields": [
                "name", "description", "homepage", "biotoolsID",
                "topic", "toolType", "operatingSystem", "language",
                "license", "maturity", "cost", "accessibility"
            ],
            "required_groups": [
                "function_comprehensive", "documentation_comprehensive",
                "download", "link", "publication", "contact_comprehensive",
                "relation", "credit"
            ]
        }
    }
    
    # Define field groups that satisfy certain requirements
    FIELD_GROUPS = {
        "function_basic": ["function"],
        "function_detailed": ["function"],  # With operations and basic input/output
        "function_complete": ["function"],  # With detailed input/output and formats
        "function_comprehensive": ["function"],  # Complete function descriptions
        
        "documentation": ["documentation"],
        "documentation_comprehensive": ["documentation"],  # Multiple doc types
        
        "download": ["download"],
        "link": ["link"],
        "publication": ["publication"],
        "contact": ["credit"],
        "contact_comprehensive": ["credit"],  # Multiple contacts with ORCID
        "relation": ["relation"],
        "credit": ["credit"]
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
        achieved_tier = self._determine_tier(field_analysis)
        
        # Calculate numerical score
        score = self._calculate_score(field_analysis, achieved_tier)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(field_analysis, achieved_tier)
        
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
            "license", "maturity", "cost", "accessibility"
        ]
        
        for field in basic_fields:
            if self._is_field_present(tool_data, field):
                analysis["present_fields"].add(field)
                analysis["field_quality"][field] = self._assess_field_quality(tool_data, field)
            else:
                analysis["missing_fields"].add(field)
        
        # Check complex fields and groups
        for group_name, group_fields in self.FIELD_GROUPS.items():
            analysis["group_satisfaction"][group_name] = self._check_group_satisfaction(
                tool_data, group_name, group_fields
            )
        
        return analysis
    
    def _is_field_present(self, tool_data: Dict, field: str) -> bool:
        """Check if a field is present and non-empty."""
        value = tool_data.get(field)
        
        if value is None:
            return False
        
        # Handle different data types
        if isinstance(value, str):
            return bool(value.strip())
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
            quality["completeness"] = min(1.0, len(value) / 100) if value else 0.0
            if value and len(value) < 50:
                quality["issues"].append("Description is quite short")
        
        elif field == "topic":
            if isinstance(value, list) and value:
                quality["completeness"] = min(1.0, len(value) / 3)  # Ideal: 3+ topics
                # Check if topics have both term and URI
                complete_topics = sum(1 for topic in value 
                                    if isinstance(topic, dict) and 
                                    topic.get("term") and topic.get("uri"))
                if complete_topics < len(value):
                    quality["issues"].append("Some topics missing term or URI")
            else:
                quality["completeness"] = 0.0
        
        elif field == "function":
            if isinstance(value, list):
                quality.update(self._assess_function_quality(value))
            else:
                quality["completeness"] = 0.0
                quality["issues"] = ["Function field is not a list"]
        
        elif field in ["documentation", "download", "link", "publication", "credit"]:
            if isinstance(value, list) and value:
                quality["completeness"] = min(1.0, len(value) / 2)  # Ideal: 2+ items
            else:
                quality["completeness"] = 0.0
        
        else:
            # Basic presence check for other fields
            quality["completeness"] = 1.0 if value else 0.0
        
        return quality
    
    def _assess_function_quality(self, functions: List[Dict]) -> Dict:
        """Assess quality of function descriptions."""
        if not functions:
            return {"completeness": 0.0, "issues": ["No functions defined"]}
        
        total_score = 0
        issues = []
        
        for func in functions:
            func_score = 0
            
            # Check operation presence
            operations = func.get("operation", [])
            if operations:
                func_score += 0.4
                # Check if operations have URIs
                ops_with_uri = sum(1 for op in operations if op.get("uri"))
                if ops_with_uri < len(operations):
                    issues.append("Some operations missing URI")
            
            # Check input/output presence
            inputs = func.get("input", [])
            outputs = func.get("output", [])
            
            if inputs:
                func_score += 0.3
            if outputs:
                func_score += 0.3
            
            total_score += func_score
        
        avg_score = total_score / len(functions)
        
        return {
            "completeness": avg_score,
            "issues": issues
        }
    
    def _check_group_satisfaction(self, tool_data: Dict, group_name: str, group_fields: List[str]) -> Dict:
        """Check if a field group requirement is satisfied."""
        satisfaction = {
            "satisfied": False,
            "completeness": 0.0,
            "details": {}
        }
        
        if group_name.startswith("function"):
            satisfaction.update(self._check_function_group(tool_data, group_name))
        elif group_name.startswith("documentation"):
            satisfaction.update(self._check_documentation_group(tool_data, group_name))
        elif group_name.startswith("contact"):
            satisfaction.update(self._check_contact_group(tool_data, group_name))
        else:
            # Basic group check - just need the field to be present
            for field in group_fields:
                if self._is_field_present(tool_data, field):
                    satisfaction["satisfied"] = True
                    satisfaction["completeness"] = 1.0
                    break
        
        return satisfaction
    
    def _check_function_group(self, tool_data: Dict, group_name: str) -> Dict:
        """Check function group satisfaction based on tier requirements."""
        functions = tool_data.get("function", [])
        
        if not functions:
            return {"satisfied": False, "completeness": 0.0}
        
        if group_name == "function_basic":
            # Just need at least one function with operation
            for func in functions:
                if func.get("operation"):
                    return {"satisfied": True, "completeness": 1.0}
        
        elif group_name == "function_detailed":
            # Need operations and some input/output
            complete_functions = 0
            for func in functions:
                if (func.get("operation") and 
                    (func.get("input") or func.get("output"))):
                    complete_functions += 1
            
            if complete_functions > 0:
                completeness = min(1.0, complete_functions / len(functions))
                return {"satisfied": True, "completeness": completeness}
        
        # More detailed checks for higher tiers...
        
        return {"satisfied": False, "completeness": 0.0}
    
    def _check_documentation_group(self, tool_data: Dict, group_name: str) -> Dict:
        """Check documentation group satisfaction."""
        docs = tool_data.get("documentation", [])
        
        if not docs:
            return {"satisfied": False, "completeness": 0.0}
        
        if group_name == "documentation":
            return {"satisfied": True, "completeness": 1.0}
        
        elif group_name == "documentation_comprehensive":
            # Need multiple types of documentation
            doc_types = set()
            for doc in docs:
                doc_type = doc.get("type", [])
                if isinstance(doc_type, list):
                    doc_types.update(doc_type)
                else:
                    doc_types.add(doc_type)
            
            completeness = min(1.0, len(doc_types) / 3)  # Ideal: 3+ doc types
            return {
                "satisfied": len(doc_types) >= 2,
                "completeness": completeness
            }
        
        return {"satisfied": False, "completeness": 0.0}
    
    def _check_contact_group(self, tool_data: Dict, group_name: str) -> Dict:
        """Check contact/credit group satisfaction."""
        credits = tool_data.get("credit", [])
        
        if not credits:
            return {"satisfied": False, "completeness": 0.0}
        
        if group_name == "contact":
            return {"satisfied": True, "completeness": 1.0}
        
        elif group_name == "contact_comprehensive":
            # Need contacts with ORCID or detailed info
            detailed_contacts = sum(1 for credit in credits 
                                  if credit.get("orcidid") or 
                                  (credit.get("email") and credit.get("typeRole")))
            
            if detailed_contacts > 0:
                completeness = min(1.0, detailed_contacts / len(credits))
                return {"satisfied": True, "completeness": completeness}
        
        return {"satisfied": False, "completeness": 0.0}
    
    def _determine_tier(self, field_analysis: Dict) -> Tier:
        """Determine the achieved tier based on field analysis."""
        for tier in reversed(list(Tier)):  # Start from highest tier
            requirements = self.TIER_REQUIREMENTS[tier]
            
            # Check required fields
            required_fields = set(requirements["required_fields"])
            present_fields = field_analysis["present_fields"]
            
            if not required_fields.issubset(present_fields):
                continue
            
            # Check required groups
            required_groups = requirements["required_groups"]
            satisfied_groups = [
                group for group, satisfaction in field_analysis["group_satisfaction"].items()
                if satisfaction["satisfied"]
            ]
            
            if all(group in satisfied_groups for group in required_groups):
                return tier
        
        # If no tier is satisfied, return the lowest
        return Tier.SPARSE
    
    def _calculate_score(self, field_analysis: Dict, achieved_tier: Tier) -> float:
        """Calculate numerical score (0-100) based on analysis."""
        # Base score from tier achievement
        tier_scores = {
            Tier.SPARSE: 20,
            Tier.MINIMAL: 40,
            Tier.DETAILED: 60,
            Tier.COMPLETE: 80,
            Tier.COMPREHENSIVE: 100
        }
        
        base_score = tier_scores[achieved_tier]
        
        # Add bonus points for field quality within the tier
        quality_bonus = 0
        total_quality = sum(
            quality.get("completeness", 0) 
            for quality in field_analysis["field_quality"].values()
        )
        
        if field_analysis["field_quality"]:
            avg_quality = total_quality / len(field_analysis["field_quality"])
            quality_bonus = avg_quality * 10  # Max 10 bonus points
        
        final_score = min(100, base_score + quality_bonus)
        return round(final_score, 1)
    
    def _generate_recommendations(self, field_analysis: Dict, achieved_tier: Tier) -> List[str]:
        """Generate recommendations for improving the tool entry."""
        recommendations = []
        
        # Recommend next tier requirements
        next_tier_value = achieved_tier.value + 1
        if next_tier_value <= 5:
            next_tier = Tier(next_tier_value)
            next_requirements = self.TIER_REQUIREMENTS[next_tier]
            
            # Missing fields for next tier
            missing_for_next = (
                set(next_requirements["required_fields"]) - 
                field_analysis["present_fields"]
            )
            
            if missing_for_next:
                recommendations.append(
                    f"To reach {next_tier.name} tier, add: {', '.join(sorted(missing_for_next))}"
                )
            
            # Missing groups for next tier
            missing_groups = [
                group for group in next_requirements["required_groups"]
                if not field_analysis["group_satisfaction"].get(group, {}).get("satisfied", False)
            ]
            
            if missing_groups:
                recommendations.append(
                    f"To reach {next_tier.name} tier, improve: {', '.join(missing_groups)}"
                )
        
        # Field quality recommendations
        for field, quality in field_analysis["field_quality"].items():
            if quality["completeness"] < 0.8 and quality["issues"]:
                recommendations.extend([
                    f"{field}: {issue}" for issue in quality["issues"]
                ])
        
        return recommendations
    
    def _generate_summary(self, tier: Tier, score: float, field_analysis: Dict) -> str:
        """Generate a human-readable summary of the scoring."""
        total_fields = len(field_analysis["present_fields"]) + len(field_analysis["missing_fields"])
        present_count = len(field_analysis["present_fields"])
        
        return (
            f"Tool achieves {tier.name} tier (score: {score}/100). "
            f"Has {present_count}/{total_fields} key fields present."
        )
