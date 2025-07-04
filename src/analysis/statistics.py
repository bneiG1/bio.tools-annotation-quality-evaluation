"""
Statistical analysis for bio.tools annotation quality evaluation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import logging

class QualityStatistics:
    """Statistical analysis for bio.tools annotation quality."""
    
    def __init__(self):
        """Initialize the statistics analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def generate_basic_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate basic statistics from scoring results.
        
        Args:
            results: List of scoring results
            
        Returns:
            Dictionary containing basic statistics
        """
        if not results:
            return {}
        
        # Extract scores
        scores = [r.get('total_score', 0) for r in results if 'error' not in r]
        tiers = [r.get('tier', 1) for r in results if 'error' not in r]
        
        if not scores:
            return {}
        
        # Calculate basic statistics
        stats = {
            'total_tools': len(results),
            'valid_tools': len(scores),
            'error_count': len(results) - len(scores),
            'score_statistics': {
                'mean': np.mean(scores),
                'median': np.median(scores),
                'std': np.std(scores),
                'min': np.min(scores),
                'max': np.max(scores),
                'quartiles': {
                    'q1': np.percentile(scores, 25),
                    'q2': np.percentile(scores, 50),
                    'q3': np.percentile(scores, 75)
                }
            },
            'tier_distribution': dict(Counter(tiers)),
            'tier_percentages': {
                tier: count / len(tiers) * 100 
                for tier, count in Counter(tiers).items()
            }
        }
        
        return stats
    
    def analyze_score_components(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze individual score components.
        
        Args:
            results: List of scoring results
            
        Returns:
            Dictionary containing component analysis
        """
        components = [
            'basic_info', 'detailed_description', 'technical_details',
            'documentation', 'accessibility', 'community'
        ]
        
        component_scores = defaultdict(list)
        
        for result in results:
            if 'error' not in result and 'scores' in result:
                for component in components:
                    score = result['scores'].get(component, 0)
                    component_scores[component].append(score)
        
        analysis = {}
        for component, scores in component_scores.items():
            if scores:
                analysis[component] = {
                    'mean': np.mean(scores),
                    'median': np.median(scores),
                    'std': np.std(scores),
                    'min': np.min(scores),
                    'max': np.max(scores)
                }
        
        return analysis
    
    def analyze_completeness_patterns(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in field completeness.
        
        Args:
            results: List of scoring results
            
        Returns:
            Dictionary containing completeness patterns
        """
        # Count present and missing fields
        present_fields = Counter()
        missing_fields = Counter()
        
        for result in results:
            if 'error' not in result and 'details' in result:
                for section, details in result['details'].items():
                    if isinstance(details, dict):
                        for field in details.get('present_fields', []):
                            present_fields[field] += 1
                        for field in details.get('missing_fields', []):
                            missing_fields[field] += 1
        
        total_tools = len([r for r in results if 'error' not in r])
        
        # Calculate completeness percentages
        field_completeness = {}
        all_fields = set(present_fields.keys()) | set(missing_fields.keys())
        
        for field in all_fields:
            present_count = present_fields[field]
            missing_count = missing_fields[field]
            total_count = present_count + missing_count
            
            field_completeness[field] = {
                'present_count': present_count,
                'missing_count': missing_count,
                'total_count': total_count,
                'completeness_percentage': (present_count / total_count * 100) if total_count > 0 else 0
            }
        
        return {
            'field_completeness': field_completeness,
            'most_complete_fields': [(field, data['completeness_percentage']) 
                                   for field, data in sorted(field_completeness.items(), 
                                                            key=lambda x: x[1]['completeness_percentage'], 
                                                            reverse=True)],
            'least_complete_fields': [(field, data['completeness_percentage']) 
                                    for field, data in sorted(field_completeness.items(), 
                                                             key=lambda x: x[1]['completeness_percentage'])],
            'total_tools_analyzed': total_tools
        }
    
    def analyze_by_collection(self, results: List[Dict[str, Any]], 
                            tool_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze quality by collection or domain.
        
        Args:
            results: List of scoring results
            tool_data: Original tool data
            
        Returns:
            Dictionary containing collection analysis
        """
        # Map biotoolsID to collection
        tool_collections = {}
        for tool in tool_data:
            biotoolsid = tool.get('biotoolsID')
            collections = tool.get('collectionID', [])
            topics = tool.get('topic', [])
            
            if biotoolsid:
                tool_collections[biotoolsid] = {
                    'collections': collections,
                    'topics': [t.get('term', t) if isinstance(t, dict) else t for t in topics]
                }
        
        # Group results by collection
        collection_stats = defaultdict(lambda: {
            'tools': [],
            'scores': [],
            'tiers': []
        })
        
        for result in results:
            if 'error' not in result:
                biotoolsid = result.get('biotoolsID')
                if biotoolsid in tool_collections:
                    collections = tool_collections[biotoolsid]['collections']
                    topics = tool_collections[biotoolsid]['topics']
                    
                    # Add to collections
                    for collection in collections:
                        collection_stats[f"collection_{collection}"]['tools'].append(result)
                        collection_stats[f"collection_{collection}"]['scores'].append(result.get('total_score', 0))
                        collection_stats[f"collection_{collection}"]['tiers'].append(result.get('tier', 1))
                    
                    # Add to topics
                    for topic in topics:
                        collection_stats[f"topic_{topic}"]['tools'].append(result)
                        collection_stats[f"topic_{topic}"]['scores'].append(result.get('total_score', 0))
                        collection_stats[f"topic_{topic}"]['tiers'].append(result.get('tier', 1))
        
        # Calculate statistics for each collection/topic
        analysis = {}
        for key, data in collection_stats.items():
            if len(data['scores']) > 0:
                analysis[key] = {
                    'tool_count': len(data['tools']),
                    'average_score': np.mean(data['scores']),
                    'median_score': np.median(data['scores']),
                    'score_std': np.std(data['scores']),
                    'tier_distribution': dict(Counter(data['tiers'])),
                    'tier_percentages': {
                        tier: count / len(data['tiers']) * 100 
                        for tier, count in Counter(data['tiers']).items()
                    }
                }
        
        return analysis
    
    def identify_quality_gaps(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify common quality gaps and improvement opportunities.
        
        Args:
            results: List of scoring results
            
        Returns:
            Dictionary containing quality gap analysis
        """
        # Analyze low-scoring areas
        component_weaknesses = defaultdict(int)
        common_missing_fields = Counter()
        tier_upgrade_opportunities = defaultdict(list)
        
        for result in results:
            if 'error' not in result:
                # Identify weak components (below 50% of max score)
                scores = result.get('scores', {})
                for component, score in scores.items():
                    # Assume max scores: basic_info=20, detailed_description=15, etc.
                    max_scores = {
                        'basic_info': 20, 'detailed_description': 15, 'technical_details': 25,
                        'documentation': 20, 'accessibility': 10, 'community': 10
                    }
                    
                    max_score = max_scores.get(component, 10)
                    if score < max_score * 0.5:  # Less than 50% of max
                        component_weaknesses[component] += 1
                
                # Count missing fields
                details = result.get('details', {})
                for section_details in details.values():
                    if isinstance(section_details, dict):
                        for field in section_details.get('missing_fields', []):
                            common_missing_fields[field] += 1
                
                # Identify tier upgrade opportunities
                current_tier = result.get('tier', 1)
                total_score = result.get('total_score', 0)
                
                # Check if tool is close to next tier
                tier_thresholds = {1: 20, 2: 40, 3: 60, 4: 80, 5: 100}
                next_tier = current_tier + 1
                
                if next_tier <= 5:
                    next_threshold = tier_thresholds[next_tier]
                    score_gap = next_threshold - total_score
                    
                    if 0 < score_gap <= 10:  # Within 10 points of next tier
                        tier_upgrade_opportunities[f"tier_{current_tier}_to_{next_tier}"].append({
                            'biotoolsID': result.get('biotoolsID'),
                            'current_score': total_score,
                            'score_gap': score_gap
                        })
        
        return {
            'component_weaknesses': dict(component_weaknesses),
            'most_common_missing_fields': common_missing_fields.most_common(20),
            'tier_upgrade_opportunities': dict(tier_upgrade_opportunities),
            'total_tools_analyzed': len([r for r in results if 'error' not in r])
        }
    
    def generate_quality_trends(self, results: List[Dict[str, Any]], 
                              tool_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze quality trends based on tool metadata.
        
        Args:
            results: List of scoring results
            tool_data: Original tool data
            
        Returns:
            Dictionary containing trend analysis
        """
        # Map results to tool data
        tool_map = {tool.get('biotoolsID'): tool for tool in tool_data}
        
        # Analyze by different dimensions
        trends = {
            'by_addition_year': defaultdict(list),
            'by_tool_type': defaultdict(list),
            'by_language': defaultdict(list),
            'by_maturity': defaultdict(list)
        }
        
        for result in results:
            if 'error' not in result:
                biotoolsid = result.get('biotoolsID')
                tool = tool_map.get(biotoolsid, {})
                score = result.get('total_score', 0)
                
                # By addition year
                addition_date = tool.get('additionDate', '')
                if addition_date:
                    year = addition_date[:4] if len(addition_date) >= 4 else 'unknown'
                    trends['by_addition_year'][year].append(score)
                
                # By tool type
                tool_types = tool.get('toolType', [])
                for tool_type in tool_types:
                    trends['by_tool_type'][tool_type].append(score)
                
                # By language
                languages = tool.get('language', [])
                for language in languages:
                    trends['by_language'][language].append(score)
                
                # By maturity
                maturity = tool.get('maturity', 'unknown')
                trends['by_maturity'][maturity].append(score)
        
        # Calculate statistics for each trend
        trend_stats = {}
        for trend_type, trend_data in trends.items():
            trend_stats[trend_type] = {}
            for category, scores in trend_data.items():
                if scores:
                    trend_stats[trend_type][category] = {
                        'count': len(scores),
                        'average_score': np.mean(scores),
                        'median_score': np.median(scores),
                        'score_std': np.std(scores)
                    }
        
        return trend_stats
    
    def export_statistics_to_dataframe(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Export results to pandas DataFrame for further analysis.
        
        Args:
            results: List of scoring results
            
        Returns:
            pandas DataFrame with results
        """
        # Flatten results for DataFrame
        flattened_data = []
        
        for result in results:
            if 'error' not in result:
                row = {
                    'biotoolsID': result.get('biotoolsID'),
                    'name': result.get('name'),
                    'total_score': result.get('total_score', 0),
                    'tier': result.get('tier', 1)
                }
                
                # Add component scores
                scores = result.get('scores', {})
                for component, score in scores.items():
                    row[f'score_{component}'] = score
                
                # Add some detail flags
                details = result.get('details', {})
                doc_details = details.get('documentation', {})
                row['has_publications'] = doc_details.get('publication_count', 0) > 0
                row['has_documentation'] = doc_details.get('documentation_count', 0) > 0
                
                community_details = details.get('community', {})
                row['has_contact'] = community_details.get('contact_count', 0) > 0
                row['has_maintainer'] = community_details.get('has_maintainer', False)
                
                flattened_data.append(row)
        
        return pd.DataFrame(flattened_data)
