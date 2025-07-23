"""
Visualization charts for bio.tools annotation quality evaluation.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

class QualityVisualizer:
    """Visualizer for bio.tools annotation quality results."""
    
    def __init__(self, style: str = 'whitegrid'):
        """
        Initialize the visualizer.
        
        Args:
            style: Seaborn style for matplotlib plots
        """
        self.logger = logging.getLogger(__name__)
        
        # Set up plotting styles
        sns.set_style(style)
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        
        # Color schemes
        self.tier_colors = {
            1: '#ff4d4d',  # Red - Minimal
            2: '#ff9933',  # Orange - Basic  
            3: '#ffcc00',  # Yellow - Moderate
            4: '#66cc00',  # Light Green - Good
            5: '#00cc66'   # Green - Excellent
        }
        
        self.component_colors = {
            'basic_info': '#1f77b4',
            'detailed_description': '#ff7f0e', 
            'technical_details': '#2ca02c',
            'documentation': '#d62728',
            'accessibility': '#9467bd',
            'community': '#8c564b'
        }
    
    def _safe_save_plotly(self, fig: go.Figure, save_path: str) -> None:
        """
        Safely save a Plotly figure as HTML.
        PNG export disabled due to Kaleido reliability issues on Windows.
        
        Args:
            fig: Plotly figure to save
            save_path: Path for HTML file
        """
        try:
            # Save HTML version (reliable, doesn't require kaleido)
            fig.write_html(save_path)
            self.logger.info(f"Saved HTML visualization: {save_path}")
            
            # Skip PNG generation to avoid Kaleido hanging issues
            self.logger.debug("PNG export skipped to avoid Kaleido issues")
            
        except Exception as e:
            self.logger.error(f"Failed to save visualization: {e}")
            raise
    
    def create_tier_distribution_chart(self, results: List[Dict[str, Any]], 
                                     save_path: Optional[str] = None) -> go.Figure:
        """
        Create a pie chart showing tier distribution.
        
        Args:
            results: List of scoring results
            save_path: Path to save the chart
            
        Returns:
            Plotly figure
        """
        # Count tiers
        tier_counts = {}
        tier_names = {
            1: 'Tier 1 (Minimal)', 2: 'Tier 2 (Basic)', 3: 'Tier 3 (Moderate)',
            4: 'Tier 4 (Good)', 5: 'Tier 5 (Excellent)'
        }
        
        for result in results:
            if 'error' not in result:
                tier = result.get('tier', 1)
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        # Create pie chart
        labels = [tier_names[tier] for tier in sorted(tier_counts.keys())]
        values = [tier_counts[tier] for tier in sorted(tier_counts.keys())]
        colors = [self.tier_colors[tier] for tier in sorted(tier_counts.keys())]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent+value',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Count: %{value}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'bio.tools Annotation Quality Tier Distribution',
                'x': 0.5,
                'font': {'size': 20}
            },
            font=dict(size=14),
            width=800,
            height=600
        )
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
    
    def create_score_distribution_histogram(self, results: List[Dict[str, Any]], 
                                          save_path: Optional[str] = None) -> go.Figure:
        """
        Create histogram of score distribution.
        
        Args:
            results: List of scoring results
            save_path: Path to save the chart
            
        Returns:
            Plotly figure
        """
        scores = [r.get('total_score', 0) for r in results if 'error' not in r]
        
        fig = go.Figure(data=[go.Histogram(
            x=scores,
            nbinsx=30,
            marker_color='lightblue',
            marker_line=dict(color='black', width=1),
            opacity=0.7
        )])
        
        # Add vertical lines for tier boundaries
        tier_boundaries = [20, 40, 60, 80]
        for boundary in tier_boundaries:
            fig.add_vline(
                x=boundary, 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Tier boundary ({boundary})",
                annotation_position="top"
            )
        
        fig.update_layout(
            title={
                'text': 'Distribution of bio.tools Annotation Quality Scores',
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title='Total Score',
            yaxis_title='Number of Tools',
            width=900,
            height=600,
            showlegend=False
        )
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
    
    def create_component_radar_chart(self, results: List[Dict[str, Any]], 
                                   by_tier: bool = True,
                                   save_path: Optional[str] = None) -> go.Figure:
        """
        Create radar chart showing component scores.
        
        Args:
            results: List of scoring results
            by_tier: Whether to show average by tier
            save_path: Path to save the chart
            
        Returns:
            Plotly figure
        """
        components = ['basic_info', 'detailed_description', 'technical_details',
                     'documentation', 'accessibility', 'community']
        
        component_labels = {
            'basic_info': 'Basic Info',
            'detailed_description': 'Description',
            'technical_details': 'Technical',
            'documentation': 'Documentation',
            'accessibility': 'Accessibility',
            'community': 'Community'
        }
        
        fig = go.Figure()
        
        if by_tier:
            # Calculate average scores by tier
            tier_data = {}
            for tier in range(1, 6):
                tier_results = [r for r in results if r.get('tier') == tier and 'error' not in r]
                if tier_results:
                    tier_scores = []
                    for component in components:
                        scores = [r.get('scores', {}).get(component, 0) for r in tier_results]
                        tier_scores.append(np.mean(scores) if scores else 0)
                    tier_data[tier] = tier_scores
            
            # Add trace for each tier
            for tier, scores in tier_data.items():
                fig.add_trace(go.Scatterpolar(
                    r=scores,
                    theta=[component_labels[c] for c in components],
                    fill='toself',
                    name=f'Tier {tier}',
                    line_color=self.tier_colors[tier],
                    marker_color=self.tier_colors[tier]
                ))
        else:
            # Show overall average
            overall_scores = []
            for component in components:
                scores = [r.get('scores', {}).get(component, 0) for r in results if 'error' not in r]
                overall_scores.append(np.mean(scores) if scores else 0)
            
            fig.add_trace(go.Scatterpolar(
                r=overall_scores,
                theta=[component_labels[c] for c in components],
                fill='toself',
                name='Overall Average',
                line_color='blue'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max([20, 15, 25, 20, 10, 10])]  # Max possible scores
                )
            ),
            title={
                'text': f'bio.tools Annotation Quality by Component {"(by Tier)" if by_tier else ""}',
                'x': 0.5,
                'font': {'size': 18}
            },
            width=800,
            height=600
        )
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
    
    def create_completeness_heatmap(self, completeness_analysis: Dict[str, Any],
                                  save_path: Optional[str] = None) -> go.Figure:
        """
        Create heatmap showing field completeness percentages.
        
        Args:
            completeness_analysis: Result from analyze_completeness_patterns
            save_path: Path to save the chart
            
        Returns:
            Plotly figure
        """
        field_completeness = completeness_analysis.get('field_completeness', {})
        
        # Prepare data for heatmap
        fields = list(field_completeness.keys())
        percentages = [field_completeness[field]['completeness_percentage'] for field in fields]
        
        # Sort by completeness percentage
        sorted_data = sorted(zip(fields, percentages), key=lambda x: x[1], reverse=True)
        fields, percentages = zip(*sorted_data)
        
        # Create heatmap data (single row)
        z = [percentages]
        
        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=fields,
            y=['Completeness %'],
            colorscale='RdYlGn',
            text=[[f'{p:.1f}%' for p in percentages]],
            texttemplate='%{text}',
            textfont={'size': 10},
            hovertemplate='Field: %{x}<br>Completeness: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title={
                'text': 'Field Completeness Heatmap',
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title='Fields',
            xaxis={'tickangle': 45},
            width=1200,
            height=400
        )
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
    
    def create_collection_comparison_chart(self, collection_analysis: Dict[str, Any],
                                         save_path: Optional[str] = None) -> go.Figure:
        """
        Create bar chart comparing quality across collections/topics.
        
        Args:
            collection_analysis: Result from analyze_by_collection
            save_path: Path to save the chart
            
        Returns:
            Plotly figure
        """
        # Separate collections and topics
        collections = {k: v for k, v in collection_analysis.items() if k.startswith('collection_')}
        topics = {k: v for k, v in collection_analysis.items() if k.startswith('topic_')}
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Quality by Collection', 'Quality by Topic'),
            vertical_spacing=0.1
        )
        
        # Collections chart
        if collections:
            coll_names = [k.replace('collection_', '') for k in collections.keys()]
            coll_scores = [v['average_score'] for v in collections.values()]
            coll_counts = [v['tool_count'] for v in collections.values()]
            
            fig.add_trace(
                go.Bar(
                    x=coll_names,
                    y=coll_scores,
                    text=[f'n={count}' for count in coll_counts],
                    textposition='outside',
                    name='Collections',
                    marker_color='lightblue'
                ),
                row=1, col=1
            )
        
        # Topics chart
        if topics:
            # Show only top 10 topics by tool count
            topic_items = list(topics.items())
            topic_items.sort(key=lambda x: x[1]['tool_count'], reverse=True)
            top_topics = topic_items[:10]
            
            topic_names = [k.replace('topic_', '') for k, v in top_topics]
            topic_scores = [v['average_score'] for k, v in top_topics]
            topic_counts = [v['tool_count'] for k, v in top_topics]
            
            fig.add_trace(
                go.Bar(
                    x=topic_names,
                    y=topic_scores,
                    text=[f'n={count}' for count in topic_counts],
                    textposition='outside',
                    name='Topics',
                    marker_color='lightcoral'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title={
                'text': 'Average Quality Scores by Collection and Topic',
                'x': 0.5,
                'font': {'size': 18}
            },
            height=800,
            showlegend=False
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(title_text='Average Score', range=[0, 100])
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
    
    def create_improvement_opportunities_chart(self, gap_analysis: Dict[str, Any],
                                             save_path: Optional[str] = None) -> go.Figure:
        """
        Create chart showing improvement opportunities.
        
        Args:
            gap_analysis: Result from identify_quality_gaps
            save_path: Path to save the chart
            
        Returns:
            Plotly figure
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Component Weaknesses', 'Most Missing Fields',
                'Tier Upgrade Opportunities', 'Field Completeness Issues'
            ),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'pie'}]]
        )
        
        # Component weaknesses
        comp_weak = gap_analysis.get('component_weaknesses', {})
        if comp_weak:
            fig.add_trace(
                go.Bar(
                    x=list(comp_weak.keys()),
                    y=list(comp_weak.values()),
                    name='Weak Components',
                    marker_color='red'
                ),
                row=1, col=1
            )
        
        # Missing fields
        missing_fields = gap_analysis.get('most_common_missing_fields', [])[:10]
        if missing_fields:
            fields, counts = zip(*missing_fields)
            fig.add_trace(
                go.Bar(
                    x=list(fields),
                    y=list(counts),
                    name='Missing Fields',
                    marker_color='orange'
                ),
                row=1, col=2
            )
        
        # Tier upgrade opportunities
        tier_opps = gap_analysis.get('tier_upgrade_opportunities', {})
        if tier_opps:
            upgrade_counts = {k: len(v) for k, v in tier_opps.items()}
            fig.add_trace(
                go.Bar(
                    x=list(upgrade_counts.keys()),
                    y=list(upgrade_counts.values()),
                    name='Upgrade Opportunities',
                    marker_color='green'
                ),
                row=2, col=1
            )
        
        # Summary pie chart of issues
        issue_counts = {
            'Component Weaknesses': sum(comp_weak.values()) if comp_weak else 0,
            'Missing Fields': sum(count for _, count in missing_fields) if missing_fields else 0,
            'Upgrade Opportunities': sum(len(v) for v in tier_opps.values()) if tier_opps else 0
        }
        
        if any(issue_counts.values()):
            fig.add_trace(
                go.Pie(
                    labels=list(issue_counts.keys()),
                    values=list(issue_counts.values()),
                    name='Issue Distribution'
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title={
                'text': 'Quality Improvement Opportunities',
                'x': 0.5,
                'font': {'size': 18}
            },
            height=800,
            showlegend=False
        )
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
    
    def create_summary_dashboard(self, results: List[Dict[str, Any]], 
                               statistics: Dict[str, Any],
                               save_path: Optional[str] = None) -> go.Figure:
        """
        Create a comprehensive summary dashboard.
        
        Args:
            results: List of scoring results
            statistics: Basic statistics
            save_path: Path to save the dashboard
            
        Returns:
            Plotly figure
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Score Distribution', 'Tier Distribution',
                'Component Scores', 'Quality Metrics'
            ),
            specs=[[{'type': 'histogram'}, {'type': 'pie'}],
                   [{'type': 'bar'}, {'type': 'indicator'}]]
        )
        
        # Score distribution
        scores = [r.get('total_score', 0) for r in results if 'error' not in r]
        fig.add_trace(
            go.Histogram(x=scores, nbinsx=20, name='Scores'),
            row=1, col=1
        )
        
        # Tier distribution
        tier_dist = statistics.get('tier_distribution', {})
        if tier_dist:
            fig.add_trace(
                go.Pie(
                    labels=[f'Tier {t}' for t in tier_dist.keys()],
                    values=list(tier_dist.values()),
                    name='Tiers'
                ),
                row=1, col=2
            )
        
        # Component scores
        component_stats = {}
        components = ['basic_info', 'detailed_description', 'technical_details',
                     'documentation', 'accessibility', 'community']
        
        for component in components:
            comp_scores = [r.get('scores', {}).get(component, 0) for r in results if 'error' not in r]
            component_stats[component] = np.mean(comp_scores) if comp_scores else 0
        
        fig.add_trace(
            go.Bar(
                x=list(component_stats.keys()),
                y=list(component_stats.values()),
                name='Component Averages'
            ),
            row=2, col=1
        )
        
        # Summary metrics
        score_stats = statistics.get('score_statistics', {})
        avg_score = score_stats.get('mean', 0)
        
        fig.add_trace(
            go.Indicator(
                mode='gauge+number+delta',
                value=avg_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Average Quality Score"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 20], 'color': "lightgray"},
                        {'range': [20, 40], 'color': "gray"},
                        {'range': [40, 60], 'color': "yellow"},
                        {'range': [60, 80], 'color': "lightgreen"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title={
                'text': 'bio.tools Annotation Quality Dashboard',
                'x': 0.5,
                'font': {'size': 20}
            },
            height=800,
            showlegend=False
        )
        
        if save_path:
            self._safe_save_plotly(fig, save_path)
        
        return fig
