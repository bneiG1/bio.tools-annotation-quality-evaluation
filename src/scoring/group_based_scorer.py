"""
Enhanced completeness scorer with group-based evaluation support.
This extends the existing scorer to handle "at least one" requirements.
"""

from src.scoring.completeness_scorer import CompletenessScorer
from typing import Dict, List, Any, Tuple, Optional
import logging


class GroupBasedScorer(CompletenessScorer):
    """Enhanced scorer that supports group-based "at least one" evaluation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the group-based scorer."""
        super().__init__(config_path)
        self.logger = logging.getLogger(__name__)
    
    def evaluate_field_group(self, tool_data: Dict, group_name: str, group_config: Dict) -> Tuple[bool, Dict]:
        """
        Evaluate if a field group requirement is met (at least one field present).
        
        Args:
            tool_data: Tool data dictionary
            group_name: Name of the group to evaluate
            group_config: Group configuration from config
            
        Returns:
            Tuple of (is_satisfied, details)
        """
        fields = group_config.get('fields', [])
        field_mappings = self.config.get('field_mappings', {})
        mapping = field_mappings.get(group_name, {})
        
        primary_fields = mapping.get('primary_fields', fields)
        secondary_fields = mapping.get('secondary_fields', [])
        all_fields = primary_fields + secondary_fields
        
        satisfied = False
        present_fields = []
        checked_content = {}
        type_matches = []
        
        # Check if this group has specific type requirements
        types_required = group_config.get('types_required', [])
        
        for field in all_fields:
            if field in tool_data:
                value = tool_data[field]
                checked_content[field] = value
                
                # Check if field has meaningful content
                if self._has_content(value):
                    # Check if this specific field requires type checking
                    field_needs_type_check = types_required and field in ['documentation', 'link', 'download', 'credit']
                    
                    if field_needs_type_check and isinstance(value, list):
                        # Check for specific types within array items
                        for item in value:
                            if isinstance(item, dict):
                                # Handle different type field names based on the field
                                type_field = None
                                if field == 'credit' and 'typeRole' in item:
                                    type_field = 'typeRole'
                                elif 'type' in item:
                                    type_field = 'type'
                                
                                if type_field:
                                    # Handle both array types and string types
                                    item_type_value = item[type_field]
                                    if isinstance(item_type_value, list):
                                        # Array of types (e.g., link.type = ["Repository", "Other"], credit.typeRole = ["Primary contact", "Support"])
                                        item_types = item_type_value
                                    else:
                                        # Single type string (e.g., download.type = "Source code")
                                        item_types = [item_type_value]
                                    
                                    for req_type in types_required:
                                        if req_type in item_types:
                                            satisfied = True
                                            present_fields.append(field)
                                            # Create field-specific type match identifier
                                            type_matches.append(f"{field}:{req_type}")
                                            break
                                    if satisfied:
                                        break
                                elif not field_needs_type_check:
                                    # Item doesn't have type field but has content - only accept if no type requirements for this field
                                    satisfied = True
                                    present_fields.append(field)
                                    break
                    else:
                        # No specific type requirements for this field - accept any content
                        satisfied = True
                        present_fields.append(field)
        
        return satisfied, {
            'present_fields': list(set(present_fields)),  # Remove duplicates
            'checked_fields': all_fields,
            'checked_content': checked_content,
            'group_weight': group_config.get('weight', 0),
            'description': group_config.get('description', ''),
            'satisfied': satisfied,
            'type_matches': type_matches,
            'types_required': types_required
        }
    
    def _has_content(self, value: Any) -> bool:
        """Check if a value has meaningful content."""
        if value is None or value == "":
            return False
        
        if isinstance(value, list):
            return len(value) > 0
        elif isinstance(value, str):
            return value.strip() != ""
        elif isinstance(value, dict):
            return len(value) > 0
        else:
            return bool(value)
    
    def score_with_groups(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Score a tool using both individual fields and group-based evaluation.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing scores and details including group evaluation
        """
        # Get base score using existing method
        base_result = self.score_tool(tool_data)
        
        # Add group-based evaluation
        field_groups = self.config.get('field_groups', {})
        group_results = {}
        total_group_score = 0
        max_group_score = 0
        
        for group_name, group_config in field_groups.items():
            is_satisfied, details = self.evaluate_field_group(tool_data, group_name, group_config)
            group_results[group_name] = details
            
            group_weight = group_config.get('weight', 0)
            max_group_score += group_weight
            
            if is_satisfied:
                total_group_score += group_weight
        
        # Combine with base result
        base_result['group_evaluation'] = {
            'total_group_score': total_group_score,
            'max_group_score': max_group_score,
            'group_percentage': (total_group_score / max_group_score * 100) if max_group_score > 0 else 0,
            'groups': group_results
        }
        
        # Calculate combined score (base + groups)
        if max_group_score > 0:
            # Adjust total score to include group scoring
            combined_score = base_result['total_score'] + (total_group_score / max_group_score * 30)  # Groups worth 30% of total
            base_result['combined_score'] = min(combined_score, 100)  # Cap at 100%
        
        return base_result
    
    def check_tier_requirements(self, tool_data: Dict, tier: str) -> Tuple[bool, Dict]:
        """
        Check if a tool meets the requirements for a specific tier.
        
        Args:
            tool_data: Tool data dictionary
            tier: Tier to check (e.g., 'tier_3')
            
        Returns:
            Tuple of (meets_requirements, details)
        """
        tier_requirements = self.config.get('tier_requirements', {})
        requirements = tier_requirements.get(tier, [])
        field_groups = self.config.get('field_groups', {})
        
        met_requirements = []
        missing_requirements = []
        group_details = {}
        
        for requirement in requirements:
            if requirement.endswith('_group'):
                # This is a group requirement
                group_config = field_groups.get(requirement, {})
                if group_config:
                    is_satisfied, details = self.evaluate_field_group(tool_data, requirement, group_config)
                    group_details[requirement] = details
                    
                    if is_satisfied:
                        met_requirements.append(requirement)
                    else:
                        missing_requirements.append(requirement)
                else:
                    missing_requirements.append(requirement)
            else:
                # Individual field requirement
                if requirement in tool_data and self._has_content(tool_data[requirement]):
                    met_requirements.append(requirement)
                else:
                    missing_requirements.append(requirement)
        
        meets_all = len(missing_requirements) == 0
        
        return meets_all, {
            'tier': tier,
            'total_requirements': len(requirements),
            'met_requirements': met_requirements,
            'missing_requirements': missing_requirements,
            'meets_all': meets_all,
            'group_details': group_details
        }
