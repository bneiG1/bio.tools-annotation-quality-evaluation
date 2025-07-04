"""
Tier classifier for categorizing tools based on annotation quality.
"""

from typing import Dict, List, Any, Optional
import logging
from collections import Counter

class TierClassifier:
    """Classifier for categorizing tools into quality tiers."""
    
    def __init__(self):
        """Initialize the tier classifier."""
        self.logger = logging.getLogger(__name__)
        
        # Define tier characteristics
        self.tier_definitions = {
            1: {
                'name': 'Minimal',
                'description': 'Basic information only',
                'requirements': ['name', 'description', 'homepage'],
                'score_range': (0, 20)
            },
            2: {
                'name': 'Basic',
                'description': 'Essential functional information',
                'requirements': ['name', 'description', 'homepage', 'function', 'topic'],
                'score_range': (21, 40)
            },
            3: {
                'name': 'Moderate',
                'description': 'Good functional and technical details',
                'requirements': ['name', 'description', 'homepage', 'function', 'topic', 
                               'operation', 'toolType'],
                'score_range': (41, 60)
            },
            4: {
                'name': 'Good',
                'description': 'Comprehensive information with documentation',
                'requirements': ['name', 'description', 'homepage', 'function', 'topic',
                               'operation', 'toolType', 'language', 'license', 'documentation'],
                'score_range': (61, 80)
            },
            5: {
                'name': 'Excellent',
                'description': 'Complete annotation with community information',
                'requirements': ['name', 'description', 'homepage', 'function', 'topic',
                               'operation', 'toolType', 'language', 'license', 'documentation',
                               'publication', 'contact', 'download'],
                'score_range': (81, 100)
            }
        }
    
    def classify_tool(self, score_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a tool based on its score result.
        
        Args:
            score_result: Result from completeness scorer
            
        Returns:
            Dictionary with classification details
        """
        tier = score_result.get('tier', 1)
        total_score = score_result.get('total_score', 0)
        
        tier_info = self.tier_definitions.get(tier, self.tier_definitions[1])
        
        # Check if tool meets tier requirements
        meets_requirements = self._check_tier_requirements(score_result, tier)
        
        # Suggest improvements
        suggestions = self._generate_improvement_suggestions(score_result, tier)
        
        return {
            'biotoolsID': score_result.get('biotoolsID'),
            'name': score_result.get('name'),
            'tier': tier,
            'tier_name': tier_info['name'],
            'tier_description': tier_info['description'],
            'score': total_score,
            'score_range': tier_info['score_range'],
            'meets_requirements': meets_requirements,
            'missing_requirements': self._get_missing_requirements(score_result, tier),
            'improvement_suggestions': suggestions,
            'score_breakdown': score_result.get('scores', {}),
            'next_tier_requirements': self._get_next_tier_requirements(tier)
        }
    
    def classify_tools(self, score_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify multiple tools.
        
        Args:
            score_results: List of score results
            
        Returns:
            List of classification results
        """
        classifications = []
        
        for score_result in score_results:
            try:
                classification = self.classify_tool(score_result)
                classifications.append(classification)
            except Exception as e:
                self.logger.error(f"Failed to classify tool: {e}")
                classifications.append({
                    'biotoolsID': score_result.get('biotoolsID', 'unknown'),
                    'error': str(e),
                    'tier': 1
                })
        
        return classifications
    
    def get_tier_statistics(self, classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate statistics about tier distribution.
        
        Args:
            classifications: List of classification results
            
        Returns:
            Dictionary with tier statistics
        """
        # Count tools per tier
        tier_counts = Counter()
        score_distribution = {}
        meets_requirements_count = 0
        
        for classification in classifications:
            if 'error' not in classification:
                tier = classification.get('tier', 1)
                tier_counts[tier] += 1
                
                # Track score distribution
                if tier not in score_distribution:
                    score_distribution[tier] = []
                score_distribution[tier].append(classification.get('score', 0))
                
                if classification.get('meets_requirements', False):
                    meets_requirements_count += 1
        
        total_tools = len([c for c in classifications if 'error' not in c])
        
        # Calculate statistics
        tier_percentages = {tier: (count / total_tools * 100) if total_tools > 0 else 0 
                           for tier, count in tier_counts.items()}
        
        average_scores = {tier: sum(scores) / len(scores) if scores else 0 
                         for tier, scores in score_distribution.items()}
        
        return {
            'total_tools': total_tools,
            'tier_counts': dict(tier_counts),
            'tier_percentages': tier_percentages,
            'average_scores_by_tier': average_scores,
            'meets_requirements_percentage': (meets_requirements_count / total_tools * 100) 
                                           if total_tools > 0 else 0,
            'tier_definitions': self.tier_definitions
        }
    
    def get_improvement_priorities(self, classifications: List[Dict[str, Any]],
                                 top_n: int = 10) -> Dict[str, Any]:
        """
        Identify priority areas for improvement across all tools.
        
        Args:
            classifications: List of classification results
            top_n: Number of top priorities to return
            
        Returns:
            Dictionary with improvement priorities
        """
        missing_fields = Counter()
        improvement_suggestions = Counter()
        
        for classification in classifications:
            if 'error' not in classification:
                # Count missing requirements
                for field in classification.get('missing_requirements', []):
                    missing_fields[field] += 1
                
                # Count improvement suggestions
                for suggestion in classification.get('improvement_suggestions', []):
                    improvement_suggestions[suggestion] += 1
        
        return {
            'most_missing_fields': missing_fields.most_common(top_n),
            'top_improvement_suggestions': improvement_suggestions.most_common(top_n),
            'total_classifications': len([c for c in classifications if 'error' not in c])
        }
    
    def _check_tier_requirements(self, score_result: Dict[str, Any], tier: int) -> bool:
        """
        Check if a tool meets the requirements for its tier.
        
        Args:
            score_result: Score result
            tier: Tier number
            
        Returns:
            True if requirements are met
        """
        tier_info = self.tier_definitions.get(tier, {})
        requirements = tier_info.get('requirements', [])
        
        details = score_result.get('details', {})
        
        for requirement in requirements:
            # Check in different detail sections
            found = False
            for section_details in details.values():
                if isinstance(section_details, dict):
                    present_fields = section_details.get('present_fields', [])
                    if requirement in present_fields:
                        found = True
                        break
            
            if not found:
                return False
        
        return True
    
    def _get_missing_requirements(self, score_result: Dict[str, Any], tier: int) -> List[str]:
        """
        Get missing requirements for a tier.
        
        Args:
            score_result: Score result
            tier: Tier number
            
        Returns:
            List of missing requirements
        """
        tier_info = self.tier_definitions.get(tier, {})
        requirements = tier_info.get('requirements', [])
        missing = []
        
        details = score_result.get('details', {})
        
        for requirement in requirements:
            found = False
            for section_details in details.values():
                if isinstance(section_details, dict):
                    present_fields = section_details.get('present_fields', [])
                    if requirement in present_fields:
                        found = True
                        break
            
            if not found:
                missing.append(requirement)
        
        return missing
    
    def _get_next_tier_requirements(self, current_tier: int) -> List[str]:
        """
        Get requirements for the next tier.
        
        Args:
            current_tier: Current tier number
            
        Returns:
            List of next tier requirements
        """
        if current_tier >= 5:
            return []
        
        next_tier = current_tier + 1
        next_tier_info = self.tier_definitions.get(next_tier, {})
        current_tier_info = self.tier_definitions.get(current_tier, {})
        
        next_requirements = set(next_tier_info.get('requirements', []))
        current_requirements = set(current_tier_info.get('requirements', []))
        
        return list(next_requirements - current_requirements)
    
    def _generate_improvement_suggestions(self, score_result: Dict[str, Any], 
                                        tier: int) -> List[str]:
        """
        Generate improvement suggestions for a tool.
        
        Args:
            score_result: Score result
            tier: Current tier
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        scores = score_result.get('scores', {})
        details = score_result.get('details', {})
        
        # Analyze weak areas
        if scores.get('basic_info', 0) < 15:
            suggestions.append("Complete basic information (name, description, homepage)")
        
        if scores.get('detailed_description', 0) < 10:
            suggestions.append("Add detailed function descriptions and topics")
        
        if scores.get('technical_details', 0) < 15:
            suggestions.append("Specify technical details (language, OS, license)")
        
        if scores.get('documentation', 0) < 15:
            suggestions.append("Add documentation links and publications")
        
        if scores.get('accessibility', 0) < 7:
            suggestions.append("Provide download links and repositories")
        
        if scores.get('community', 0) < 7:
            suggestions.append("Add contact information and credits")
        
        # Specific suggestions based on missing fields
        doc_details = details.get('documentation', {})
        if doc_details.get('publication_count', 0) == 0:
            suggestions.append("Add publication references")
        
        access_details = details.get('accessibility', {})
        if access_details.get('download_count', 0) == 0:
            suggestions.append("Provide download links")
        
        community_details = details.get('community', {})
        if not community_details.get('has_maintainer', False):
            suggestions.append("Add maintainer contact information")
        
        # Tier-specific suggestions
        if tier < 3:
            suggestions.append("Define tool operations and input/output types")
        
        if tier < 4:
            suggestions.append("Add comprehensive documentation")
        
        if tier < 5:
            suggestions.append("Complete community information")
        
        return list(set(suggestions))  # Remove duplicates
