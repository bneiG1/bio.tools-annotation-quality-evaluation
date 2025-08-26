"""
Completeness scorer for bio.tools annotations based on Tool Information Standards.
"""

import yaml
from typing import Dict, List, Any, Optional, Tuple
import logging
from pathlib import Path

try:
    from ..validation.url_checker import URLChecker
    URLChecker = URLChecker
    URL_CHECKING_AVAILABLE = True
except ImportError:
    try:
        # Alternative import for when script is run from different location
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from validation.url_checker import URLChecker
        URL_CHECKING_AVAILABLE = True
    except ImportError:
        URLChecker = None
        URL_CHECKING_AVAILABLE = False

class CompletenessScorer:
    """Scorer for evaluating completeness of bio.tools annotations."""
    
    def __init__(self, config_path: Optional[str] = None, enable_url_checking: bool = False):
        """
        Initialize the completeness scorer.
        
        Args:
            config_path: Path to scoring configuration file
            enable_url_checking: Whether to enable URL accessibility checking
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_default_config()
        
        if config_path and Path(config_path).exists():
            self.load_config(config_path)
            
        # Initialize URL checker if enabled and available
        self.url_checker = None
        self.enable_url_checking = enable_url_checking
        if enable_url_checking and URL_CHECKING_AVAILABLE and URLChecker is not None:
            self.url_checker = URLChecker(timeout=5, max_workers=3, delay_between_requests=0.3)
            self.logger.info("URL accessibility checking enabled")
        elif enable_url_checking:
            self.logger.warning("URL checking requested but URLChecker not available")
    
    def _load_default_config(self) -> Dict:
        """Load default scoring configuration."""
        return {
            'weights': {
                'basic_info': 15,
                'detailed_description': 25,  # Maps to core_metadata in new config
                'technical_details': 20,     # Maps to technical_info in new config  
                'documentation': 20,         # Part of technical_info in new config
                'accessibility': 15,         # Maps to accessibility in new config
                'community': 5               # Maps to community in new config
            },
            'field_weights': {
                'name': 4, 'description': 6, 'homepage': 3, 'biotoolsID': 2,
                'version': 4, 'function': 7, 'topic': 8, 'operation': 6,
                'toolType': 6, 'language': 3, 'operatingSystem': 3,
                'license': 4, 'documentation': 8, 'publication': 10,
                'download': 6, 'contact': 5, 'credit': 3, 'accessibility': 6,
                'cost': 3, 'maturity': 3, 'repository': 5, 'link': 4
            },
            'tiers': {
                'tier_1': [0, 15], 'tier_2': [16, 40], 'tier_3': [41, 65],
                'tier_4': [66, 85], 'tier_5': [86, 100]
            }
        }
    
    def load_config(self, config_path: str):
        """
        Load scoring configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update configuration
            if 'scoring' in config:
                scoring_config = config['scoring']
                
                # Map new weight categories to old method names for compatibility
                if 'weights' in scoring_config:
                    new_weights = scoring_config['weights']
                    # Map new categories to old method names
                    weight_mapping = {
                        'basic_info': 'basic_info',
                        'core_metadata': 'detailed_description',
                        'technical_info': 'technical_details', 
                        'accessibility': 'accessibility',
                        'advanced_features': 'documentation',  # Combine with documentation
                        'community': 'community'
                    }
                    
                    mapped_weights = {}
                    for new_key, old_key in weight_mapping.items():
                        if new_key in new_weights:
                            mapped_weights[old_key] = new_weights[new_key]
                    
                    # Handle documentation separately - combine technical_info and advanced_features
                    if 'technical_info' in new_weights and 'advanced_features' in new_weights:
                        mapped_weights['documentation'] = new_weights['advanced_features']
                        mapped_weights['technical_details'] = new_weights['technical_info']
                    
                    scoring_config['weights'] = mapped_weights
                
                self.config.update(scoring_config)
            
            self.logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def score_basic_info(self, tool_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Score basic information completeness.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tuple of (score, details)
        """
        fields = ['name', 'description', 'homepage', 'biotoolsID', 'biotoolsCURIE', 'version']
        max_score = self.config['weights']['basic_info']
        
        present_fields = []
        missing_fields = []
        field_scores = {}
        
        total_field_weight = sum(self.config['field_weights'].get(field, 1) for field in fields)
        current_weight = 0
        
        for field in fields:
            weight = self.config['field_weights'].get(field, 1)
            
            if field in tool_data and not self._is_empty(tool_data[field]):
                present_fields.append(field)
                current_weight += weight
                field_scores[field] = weight
            else:
                missing_fields.append(field)
                field_scores[field] = 0
        
        score = (current_weight / total_field_weight) * max_score if total_field_weight > 0 else 0
        
        return score, {
            'max_score': max_score,
            'present_fields': present_fields,
            'missing_fields': missing_fields,
            'field_scores': field_scores,
            'completeness_ratio': len(present_fields) / len(fields)
        }
    
    def score_detailed_description(self, tool_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Score detailed description completeness.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tuple of (score, details)
        """
        max_score = self.config['weights']['detailed_description']
        
        # Check for function, topic, and operation
        function_score = 0
        topic_score = 0
        operation_score = 0
        
        details = {
            'max_score': max_score,
            'function_count': 0,
            'topic_count': 0,
            'operation_count': 0,
            'has_detailed_function': False
        }
        
        # Score functions
        if 'function' in tool_data and tool_data['function']:
            details['function_count'] = len(tool_data['function'])
            function_score = min(5, len(tool_data['function']) * 2)  # Max 5 points
            
            # Check for detailed function information
            for func in tool_data['function']:
                if (func.get('operation') and func.get('input') and func.get('output')):
                    details['has_detailed_function'] = True
                    function_score = 5
                    break
        
        # Score topics
        if 'topic' in tool_data and tool_data['topic']:
            details['topic_count'] = len(tool_data['topic'])
            topic_score = min(5, len(tool_data['topic']) * 2)  # Max 5 points
        
        # Score operations (from functions)
        operations = set()
        if 'function' in tool_data:
            for func in tool_data['function']:
                if 'operation' in func:
                    for op in func['operation']:
                        if isinstance(op, dict) and 'term' in op:
                            operations.add(op['term'])
        
        details['operation_count'] = len(operations)
        operation_score = min(5, len(operations))  # Max 5 points
        
        total_score = (function_score + topic_score + operation_score) / 15 * max_score
        
        details.update({
            'function_score': function_score,
            'topic_score': topic_score,
            'operation_score': operation_score
        })
        
        return total_score, details
    
    def score_technical_details(self, tool_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Score technical details completeness.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tuple of (score, details)
        """
        fields = ['toolType', 'language', 'operatingSystem', 'license', 'maturity', 'cost', 'accessibility']
        max_score = self.config['weights']['technical_details']
        
        present_fields = []
        missing_fields = []
        field_scores = {}
        
        total_field_weight = sum(self.config['field_weights'].get(field, 3) for field in fields)
        current_weight = 0
        
        for field in fields:
            weight = self.config['field_weights'].get(field, 3)
            
            if field in tool_data and not self._is_empty(tool_data[field]):
                present_fields.append(field)
                current_weight += weight
                field_scores[field] = weight
            else:
                missing_fields.append(field)
                field_scores[field] = 0
        
        score = (current_weight / total_field_weight) * max_score if total_field_weight > 0 else 0
        
        return score, {
            'max_score': max_score,
            'present_fields': present_fields,
            'missing_fields': missing_fields,
            'field_scores': field_scores,
            'completeness_ratio': len(present_fields) / len(fields)
        }
    
    def score_documentation(self, tool_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Score documentation completeness.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tuple of (score, details)
        """
        max_score = self.config['weights']['documentation']
        
        documentation_score = 0
        publication_score = 0
        
        details = {
            'max_score': max_score,
            'documentation_count': 0,
            'publication_count': 0,
            'has_primary_publication': False,
            'documentation_types': []
        }
        
        # Score documentation
        if 'documentation' in tool_data and tool_data['documentation']:
            details['documentation_count'] = len(tool_data['documentation'])
            documentation_score = min(6, len(tool_data['documentation']) * 2)  # Max 6 points
            
            # Track documentation types
            for doc in tool_data['documentation']:
                if isinstance(doc, dict) and 'type' in doc:
                    details['documentation_types'].append(doc['type'])
        
        # Score publications
        if 'publication' in tool_data and tool_data['publication']:
            details['publication_count'] = len(tool_data['publication'])
            publication_score = min(8, len(tool_data['publication']) * 4)  # Max 8 points
        
        # Check for primary publication ID
        if 'publicationsPrimaryID' in tool_data and tool_data['publicationsPrimaryID']:
            details['has_primary_publication'] = True
            publication_score = max(publication_score, 6)  # Ensure at least 6 points
        
        total_score = (documentation_score + publication_score) / 14 * max_score
        
        details.update({
            'documentation_score': documentation_score,
            'publication_score': publication_score
        })
        
        return total_score, details
    
    def score_accessibility(self, tool_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Score accessibility completeness with optional URL checking.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tuple of (score, details)
        """
        max_score = self.config['weights']['accessibility']
        
        download_score = 0
        link_score = 0
        repository_score = 0
        url_accessibility_score = 0
        
        details = {
            'max_score': max_score,
            'download_count': 0,
            'link_count': 0,
            'repository_count': 0,
            'link_types': [],
            'url_checking_enabled': self.enable_url_checking and self.url_checker is not None,
            'url_accessibility': None
        }
        
        # Score downloads
        if 'download' in tool_data and tool_data['download']:
            details['download_count'] = len(tool_data['download'])
            download_score = min(5, len(tool_data['download']) * 2)  # Max 5 points
        
        # Score links
        if 'link' in tool_data and tool_data['link']:
            details['link_count'] = len(tool_data['link'])
            link_score = min(3, len(tool_data['link']))  # Max 3 points
            
            # Track link types
            for link in tool_data['link']:
                if isinstance(link, dict) and 'type' in link:
                    details['link_types'].append(link['type'])
        
        # Score repositories
        if 'repository' in tool_data and tool_data['repository']:
            details['repository_count'] = len(tool_data['repository'])
            repository_score = min(2, len(tool_data['repository']))  # Max 2 points
        
        # URL accessibility checking (if enabled)
        if self.enable_url_checking and self.url_checker is not None:
            try:
                url_results = self.url_checker.check_tool_urls(tool_data)
                details['url_accessibility'] = url_results
                
                # Award points based on URL accessibility
                # Homepage accessibility: up to 3 points
                if url_results['homepage_result'] and url_results['homepage_result']['is_accessible']:
                    url_accessibility_score += 3
                elif url_results['homepage_result'] and not url_results['homepage_result']['is_accessible']:
                    # Deduct points for broken homepage
                    url_accessibility_score -= 1
                
                # Overall URL accessibility: up to 2 points based on percentage
                accessibility_rate = url_results['summary']['accessibility_rate']
                if accessibility_rate >= 0.8:  # 80%+ accessible
                    url_accessibility_score += 2
                elif accessibility_rate >= 0.6:  # 60-79% accessible
                    url_accessibility_score += 1
                elif accessibility_rate < 0.5:  # Less than 50% accessible
                    url_accessibility_score -= 1
                
                # Cap the URL accessibility score
                url_accessibility_score = max(-2, min(5, url_accessibility_score))
                
            except Exception as e:
                self.logger.warning(f"URL checking failed for tool: {e}")
                details['url_accessibility'] = {'error': str(e)}
        
        # Base score from traditional accessibility factors
        base_score = (download_score + link_score + repository_score) / 10 * max_score
        
        # Add URL accessibility bonus/penalty (up to 10% of max score)
        url_bonus = (url_accessibility_score / 5) * (max_score * 0.1) if self.enable_url_checking else 0
        
        total_score = min(max_score, base_score + url_bonus)
        
        details.update({
            'download_score': download_score,
            'link_score': link_score,
            'repository_score': repository_score,
            'url_accessibility_score': url_accessibility_score,
            'url_bonus': url_bonus,
            'base_score': base_score
        })
        
        return total_score, details
    
    def score_community(self, tool_data: Dict) -> Tuple[float, Dict[str, Any]]:
        """
        Score community information completeness.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tuple of (score, details)
        """
        max_score = self.config['weights'].get('community', 5)  # Default to 5 if not specified
        
        credit_score = 0
        contact_score = 0
        
        details = {
            'max_score': max_score,
            'credit_count': 0,
            'contact_count': 0,
            'has_maintainer': False,
            'credit_types': []
        }
        
        # Score credits
        if 'credit' in tool_data and tool_data['credit']:
            details['credit_count'] = len(tool_data['credit'])
            credit_score = min(4, len(tool_data['credit']) * 2)  # Max 4 points
            
            # Track credit types
            for credit in tool_data['credit']:
                if isinstance(credit, dict) and 'typeRole' in credit:
                    details['credit_types'].extend(credit['typeRole'])
        
        # Score contacts
        if 'contact' in tool_data and tool_data['contact']:
            details['contact_count'] = len(tool_data['contact'])
            contact_score = min(6, len(tool_data['contact']) * 3)  # Max 6 points
            
            # Check for maintainer contact
            for contact in tool_data['contact']:
                if isinstance(contact, dict) and 'typeRole' in contact:
                    if 'Maintainer' in contact['typeRole']:
                        details['has_maintainer'] = True
                        contact_score = max(contact_score, 4)  # Ensure at least 4 points
        
        total_score = (credit_score + contact_score) / 10 * max_score
        
        details.update({
            'credit_score': credit_score,
            'contact_score': contact_score
        })
        
        return total_score, details
    
    def score_tool(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a tool.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing scores and details
        """
        # Calculate individual scores
        basic_score, basic_details = self.score_basic_info(tool_data)
        description_score, description_details = self.score_detailed_description(tool_data)
        technical_score, technical_details = self.score_technical_details(tool_data)
        documentation_score, documentation_details = self.score_documentation(tool_data)
        accessibility_score, accessibility_details = self.score_accessibility(tool_data)
        community_score, community_details = self.score_community(tool_data)
        
        # Calculate total score
        total_score = (basic_score + description_score + technical_score + 
                      documentation_score + accessibility_score + community_score)
        
        # Determine tier
        tier = self.determine_tier(total_score)
        
        return {
            'biotoolsID': tool_data.get('biotoolsID', 'unknown'),
            'name': tool_data.get('name', 'unknown'),
            'total_score': round(total_score, 2),
            'tier': tier,
            'scores': {
                'basic_info': round(basic_score, 2),
                'detailed_description': round(description_score, 2),
                'technical_details': round(technical_score, 2),
                'documentation': round(documentation_score, 2),
                'accessibility': round(accessibility_score, 2),
                'community': round(community_score, 2)
            },
            'details': {
                'basic_info': basic_details,
                'detailed_description': description_details,
                'technical_details': technical_details,
                'documentation': documentation_details,
                'accessibility': accessibility_details,
                'community': community_details
            }
        }
    
    def determine_tier(self, score: float) -> int:
        """
        Determine tier based on score.
        
        Args:
            score: Total score
            
        Returns:
            Tier number (1-5)
        """
        for tier_name, (min_score, max_score) in self.config['tiers'].items():
            if min_score <= score <= max_score:
                return int(tier_name.split('_')[1])
        
        # Default to tier 1 if no match
        return 1
    
    def score_tools(self, tools_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Score multiple tools in batch.
        
        Args:
            tools_data: List of tool data dictionaries
            
        Returns:
            List of scoring results
        """
        results = []
        
        for i, tool_data in enumerate(tools_data):
            try:
                score_result = self.score_tool(tool_data)
                score_result['index'] = i
                results.append(score_result)
            except Exception as e:
                self.logger.error(f"Failed to score tool {i}: {e}")
                results.append({
                    'index': i,
                    'biotoolsID': tool_data.get('biotoolsID', 'unknown'),
                    'error': str(e),
                    'total_score': 0,
                    'tier': 1
                })
        
        return results
    
    def _is_empty(self, value: Any) -> bool:
        """
        Check if a value is considered empty.
        
        Args:
            value: Value to check
            
        Returns:
            True if empty, False otherwise
        """
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and not value:
            return True
        return False
