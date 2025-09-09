#!/usr/bin/env python3
"""
Bio.tools Quality Dashboard - Streamlit Web Application
Interactive web interface for bio.tools annotation quality evaluation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Try to import existing modules, fall back to mock data if not available
try:
    from src.reporters.visualizer import QualityReporter
    from src.analyzers.quality_analyzer import QualityReport, QualityMetrics
    MODULES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")
    MODULES_AVAILABLE = False

# Configure Streamlit page
st.set_page_config(
    page_title="Bio.tools Quality Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .tier-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .tier-1 { background-color: #ff4d4d; color: white; }
    .tier-2 { background-color: #ff9933; color: white; }
    .tier-3 { background-color: #ffcc00; color: black; }
    .tier-4 { background-color: #66cc00; color: white; }
    .tier-5 { background-color: #00cc66; color: white; }
</style>
""", unsafe_allow_html=True)

class StreamlitDashboard:
    """Main Streamlit dashboard class for bio.tools quality analysis."""
    
    def __init__(self):
        self.tier_colors = {
            1: '#ff4d4d', 2: '#ff9933', 3: '#ffcc00', 
            4: '#66cc00', 5: '#00cc66'
        }
        self.tier_names = {
            1: 'SPARSE', 2: 'BASIC DETAILS', 3: 'DETAILED', 
            4: 'HIGHLY DETAILED', 5: 'COMPREHENSIVE'
        }
        
        # Grade colors for quality grades
        self.grade_colors = {
            'A': '#00cc66', 'B': '#66cc00', 'C': '#ffcc00',
            'D': '#ff9933', 'F': '#ff4d4d'
        }
    
    def load_data_from_file(self, file_path: str = "data/temp_dashboard_data.json") -> tuple:
        """Load data from a JSON file if it exists."""
        data_path = Path(file_path)
        if data_path.exists():
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return (
                    data.get('tools', []),
                    data.get('statistics', {}),
                    data.get('config', {})
                )
            except Exception as e:
                st.error(f"Error loading data file: {e}")
        
        return [], {}, {}
    
    def load_sample_data(self, limit: int = 100) -> tuple:
        """Load sample data for demonstration."""
        try:
            tools_data = []
            for i in range(limit):
                # Create realistic sample data based on actual bio.tools structure
                tool = {
                    'tool_id': f'tool_{i:03d}',
                    'tool_name': f'Sample Tool {i}',
                    'metrics': {
                        'overall_score': 50 + (i % 50),
                        'quality_grade': ['A', 'B', 'C', 'D', 'F'][i % 5],
                        'standards_tier': f'Tier {(i % 5) + 1}',
                        'completeness_tier': f'Tier {(i % 5) + 1}',
                        'standards_score': 40 + (i % 60),
                        'completeness_score': 45 + (i % 55),
                        'schema_valid': i % 3 != 0,
                        'schema_errors': (i % 3),
                        'schema_warnings': (i % 2),
                        'lint_issues': i % 5,
                        'critical_issues': i % 10 if i % 10 < 2 else 0,
                        'error_issues': (i % 3),
                        'warning_issues': (i % 4),
                        'info_issues': (i % 2),
                        'field_completeness': 0.3 + (i % 70) / 100,
                        'required_fields_complete': i % 2 == 0,
                        'recommended_fields_complete': 0.2 + (i % 80) / 100,
                        'url_health': 0.5 + (i % 50) / 100,
                        'edam_consistency': 0.4 + (i % 60) / 100,
                        'publication_quality': 0.3 + (i % 70) / 100,
                        'has_functions': i % 3 != 0,
                        'has_documentation': i % 4 != 0,
                        'has_publications': i % 5 != 0,
                        'has_contacts': i % 6 != 0,
                        'analysis_date': '2024-01-01'
                    },
                    'summary': f'Sample tool analysis for tool {i}',
                    'recommendations': [
                        'Add more detailed documentation',
                        'Include additional EDAM terms',
                        'Update publication information'
                    ][:((i % 3) + 1)]
                }
                tools_data.append(tool)
            
            # Calculate statistics
            total_tools = len(tools_data)
            grade_counts = {}
            tier_counts = {}
            
            for tool in tools_data:
                grade = tool['metrics']['quality_grade']
                tier = tool['metrics']['standards_tier']
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            statistics = {
                'total_tools': total_tools,
                'grade_distribution': grade_counts,
                'tier_distribution': tier_counts,
                'average_score': sum(t['metrics']['overall_score'] for t in tools_data) / total_tools,
                'validation_stats': {
                    'valid': sum(1 for t in tools_data if t['metrics']['schema_valid']),
                    'with_errors': sum(1 for t in tools_data if t['metrics']['schema_errors'] > 0),
                    'with_warnings': sum(1 for t in tools_data if t['metrics']['schema_warnings'] > 0)
                },
                'content_stats': {
                    'with_functions': sum(1 for t in tools_data if t['metrics']['has_functions']),
                    'with_documentation': sum(1 for t in tools_data if t['metrics']['has_documentation']),
                    'with_publications': sum(1 for t in tools_data if t['metrics']['has_publications']),
                    'with_contacts': sum(1 for t in tools_data if t['metrics']['has_contacts'])
                }
            }
            
            return tools_data, statistics, {}
            
        except Exception as e:
            st.error(f"Error generating sample data: {e}")
            return [], {}, {}
    
    def render_header(self):
        """Render the main header."""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🔬 Bio.tools Quality Dashboard</h1>
            <p style="color: #f0f0f0; margin: 0;">Interactive Analysis of Tool Annotation Quality</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_overview_metrics(self, statistics: Dict[str, Any]):
        """Render overview metrics cards."""
        st.subheader("📊 Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tools = statistics.get('total_tools', 0)
            st.metric(
                label="Total Tools Analyzed",
                value=f"{total_tools:,}",
                delta=None
            )
        
        with col2:
            avg_score = statistics.get('average_score', 0)
            st.metric(
                label="Average Quality Score",
                value=f"{avg_score:.1f}/100",
                delta=None
            )
        
        with col3:
            validation_stats = statistics.get('validation_stats', {})
            valid_count = validation_stats.get('valid', 0)
            st.metric(
                label="Schema Valid Tools",
                value=f"{valid_count:,}",
                delta=None
            )
        
        with col4:
            tier_dist = statistics.get('tier_distribution', {})
            high_quality = tier_dist.get('Tier 4', 0) + tier_dist.get('Tier 5', 0)
            st.metric(
                label="High Quality Tools",
                value=f"{high_quality:,}",
                delta=None
            )
    
    def render_quality_grades_distribution(self, statistics: Dict[str, Any]):
        """Render quality grade distribution."""
        st.subheader("📊 Quality Grade Distribution")
        
        grade_dist = statistics.get('grade_distribution', {})
        if not grade_dist:
            st.warning("No grade distribution data available")
            return
        
        # Create DataFrame for plotly
        df_grades = pd.DataFrame([
            {
                'Grade': grade,
                'Count': count,
                'Color': self.grade_colors.get(grade, '#cccccc')
            }
            for grade, count in grade_dist.items()
        ])
        
        if not df_grades.empty:
            # Sort by grade
            grade_order = ['A', 'B', 'C', 'D', 'F']
            df_grades['Grade'] = pd.Categorical(df_grades['Grade'], categories=grade_order, ordered=True)
            df_grades = df_grades.sort_values('Grade')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig_pie = px.pie(
                    df_grades, 
                    values='Count', 
                    names='Grade',
                    color='Grade',
                    color_discrete_map={row['Grade']: row['Color'] for _, row in df_grades.iterrows()},
                    title="Grade Distribution"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                fig_bar = px.bar(
                    df_grades,
                    x='Grade',
                    y='Count',
                    color='Grade',
                    color_discrete_map={row['Grade']: row['Color'] for _, row in df_grades.iterrows()},
                    title="Tools Count by Grade"
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
    
    def render_tier_distribution(self, statistics: Dict[str, Any]):
        """Render tier distribution chart."""
        st.subheader("🏆 Standards Tier Distribution")
        
        tier_dist = statistics.get('tier_distribution', {})
        if not tier_dist:
            st.warning("No tier distribution data available")
            return
        
        # Create DataFrame for plotly
        df_tiers = pd.DataFrame([
            {
                'Tier': tier,
                'Count': count,
                'Tier_Num': int(tier.split()[-1]) if tier.startswith('Tier') else 1,
                'Color': self.tier_colors.get(int(tier.split()[-1]) if tier.startswith('Tier') else 1, '#cccccc')
            }
            for tier, count in tier_dist.items()
        ])
        
        if not df_tiers.empty:
            # Sort by tier number
            df_tiers = df_tiers.sort_values('Tier_Num')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Pie chart
                fig_pie = px.pie(
                    df_tiers, 
                    values='Count', 
                    names='Tier',
                    color='Tier',
                    color_discrete_map={row['Tier']: row['Color'] for _, row in df_tiers.iterrows()},
                    title="Distribution of Tools by Quality Tier"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Bar chart
                fig_bar = px.bar(
                    df_tiers,
                    x='Tier',
                    y='Count',
                    color='Tier',
                    color_discrete_map={row['Tier']: row['Color'] for _, row in df_tiers.iterrows()},
                    title="Tool Count by Quality Tier"
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
    
    def render_content_quality_metrics(self, statistics: Dict[str, Any]):
        """Render content quality metrics."""
        st.subheader("📋 Content Quality Analysis")
        
        content_stats = statistics.get('content_stats', {})
        total_tools = statistics.get('total_tools', 1)
        
        if content_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                functions_pct = (content_stats.get('with_functions', 0) / total_tools) * 100
                st.metric(
                    label="Tools with Functions",
                    value=f"{content_stats.get('with_functions', 0):,}",
                    delta=f"{functions_pct:.1f}%"
                )
            
            with col2:
                docs_pct = (content_stats.get('with_documentation', 0) / total_tools) * 100
                st.metric(
                    label="Tools with Documentation",
                    value=f"{content_stats.get('with_documentation', 0):,}",
                    delta=f"{docs_pct:.1f}%"
                )
            
            with col3:
                pubs_pct = (content_stats.get('with_publications', 0) / total_tools) * 100
                st.metric(
                    label="Tools with Publications",
                    value=f"{content_stats.get('with_publications', 0):,}",
                    delta=f"{pubs_pct:.1f}%"
                )
            
            with col4:
                contacts_pct = (content_stats.get('with_contacts', 0) / total_tools) * 100
                st.metric(
                    label="Tools with Contacts",
                    value=f"{content_stats.get('with_contacts', 0):,}",
                    delta=f"{contacts_pct:.1f}%"
                )
            
            # Content completeness bar chart
            content_data = {
                'Functions': content_stats.get('with_functions', 0),
                'Documentation': content_stats.get('with_documentation', 0),
                'Publications': content_stats.get('with_publications', 0),
                'Contacts': content_stats.get('with_contacts', 0)
            }
            
            df_content = pd.DataFrame([
                {'Content Type': k, 'Count': v, 'Percentage': (v/total_tools)*100}
                for k, v in content_data.items()
            ])
            
            fig_content = px.bar(
                df_content,
                x='Content Type',
                y='Percentage',
                title="Content Completeness by Type",
                labels={'Percentage': 'Percentage of Tools (%)'}
            )
            fig_content.update_layout(yaxis_range=[0, 100])
            st.plotly_chart(fig_content, use_container_width=True)
    
    def render_tools_table(self, tools_data: List[Dict[str, Any]]):
        """Render interactive tools table."""
        st.subheader("🔍 Tools Overview")
        
        if not tools_data:
            st.warning("No tools data available")
            return
        
        # Convert to DataFrame with flattened metrics
        df_data = []
        for tool in tools_data:
            metrics = tool.get('metrics', {})
            row = {
                'Tool ID': tool.get('tool_id', 'Unknown'),
                'Tool Name': tool.get('tool_name', 'Unknown'),
                'Overall Score': metrics.get('overall_score', 0),
                'Quality Grade': metrics.get('quality_grade', 'F'),
                'Standards Tier': metrics.get('standards_tier', 'Tier 1'),
                'Completeness Score': metrics.get('completeness_score', 0),
                'Schema Valid': '✅' if metrics.get('schema_valid', False) else '❌',
                'Lint Issues': metrics.get('lint_issues', 0),
                'Field Completeness': f"{metrics.get('field_completeness', 0)*100:.1f}%",
                'Has Functions': '✅' if metrics.get('has_functions', False) else '❌',
                'Has Documentation': '✅' if metrics.get('has_documentation', False) else '❌',
                'Has Publications': '✅' if metrics.get('has_publications', False) else '❌'
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        
        # Add filters
        st.markdown("**🔧 Filters**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            grade_filter = st.selectbox(
                "Filter by Grade",
                options=['All'] + list(df['Quality Grade'].unique()),
                index=0
            )
        
        with col2:
            tier_filter = st.selectbox(
                "Filter by Tier",
                options=['All'] + list(df['Standards Tier'].unique()),
                index=0
            )
        
        with col3:
            min_score = st.slider("Minimum Overall Score", 0, 100, 0)
        
        with col4:
            max_issues = st.slider("Maximum Lint Issues", 0, 20, 20)
        
        # Apply filters
        filtered_df = df.copy()
        
        if grade_filter != 'All':
            filtered_df = filtered_df[filtered_df['Quality Grade'] == grade_filter]
        
        if tier_filter != 'All':
            filtered_df = filtered_df[filtered_df['Standards Tier'] == tier_filter]
        
        filtered_df = filtered_df[
            (filtered_df['Overall Score'] >= min_score) & 
            (filtered_df['Lint Issues'] <= max_issues)
        ]
        
        # Display table
        st.markdown("**📊 Results Table**")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Overall Score": st.column_config.ProgressColumn(
                    "Overall Score",
                    help="Overall quality score out of 100",
                    min_value=0,
                    max_value=100,
                ),
                "Completeness Score": st.column_config.ProgressColumn(
                    "Completeness Score", 
                    help="Completeness score out of 100",
                    min_value=0,
                    max_value=100,
                ),
                "Lint Issues": st.column_config.NumberColumn(
                    "Lint Issues",
                    help="Number of linting issues",
                    min_value=0,
                )
            }
        )
        
        st.info(f"Showing {len(filtered_df)} of {len(df)} tools")
    
    def render_quality_analysis(self, tools_data: List[Dict[str, Any]]):
        """Render quality analysis charts."""
        st.subheader("📈 Quality Analysis")
        
        if not tools_data:
            st.warning("No tools data available for analysis")
            return
        
        # Extract metrics data
        metrics_data = []
        for tool in tools_data:
            metrics = tool.get('metrics', {})
            metrics_data.append({
                'overall_score': metrics.get('overall_score', 0),
                'completeness_score': metrics.get('completeness_score', 0),
                'standards_score': metrics.get('standards_score', 0),
                'quality_grade': metrics.get('quality_grade', 'F'),
                'standards_tier': metrics.get('standards_tier', 'Tier 1'),
                'field_completeness': metrics.get('field_completeness', 0),
                'lint_issues': metrics.get('lint_issues', 0),
                'schema_valid': metrics.get('schema_valid', False),
                'url_health': metrics.get('url_health', 0),
                'edam_consistency': metrics.get('edam_consistency', 0),
                'publication_quality': metrics.get('publication_quality', 0)
            })
        
        df = pd.DataFrame(metrics_data)
        
        # Score distribution histograms
        col1, col2 = st.columns(2)
        
        with col1:
            fig_overall = px.histogram(
                df,
                x='overall_score',
                nbins=20,
                title="Distribution of Overall Scores",
                labels={'overall_score': 'Overall Score', 'count': 'Number of Tools'}
            )
            fig_overall.update_layout(bargap=0.1)
            st.plotly_chart(fig_overall, use_container_width=True)
        
        with col2:
            fig_completeness = px.histogram(
                df,
                x='completeness_score',
                nbins=20,
                title="Distribution of Completeness Scores",
                labels={'completeness_score': 'Completeness Score', 'count': 'Number of Tools'}
            )
            fig_completeness.update_layout(bargap=0.1)
            st.plotly_chart(fig_completeness, use_container_width=True)
        
        # Grade vs Score analysis
        col1, col2 = st.columns(2)
        
        with col1:
            fig_grade_box = px.box(
                df,
                x='quality_grade',
                y='overall_score',
                title="Score Distribution by Quality Grade",
                labels={'quality_grade': 'Quality Grade', 'overall_score': 'Overall Score'}
            )
            st.plotly_chart(fig_grade_box, use_container_width=True)
        
        with col2:
            # Field completeness vs overall score scatter
            fig_scatter = px.scatter(
                df,
                x='field_completeness',
                y='overall_score',
                color='quality_grade',
                title="Field Completeness vs Overall Score",
                labels={
                    'field_completeness': 'Field Completeness',
                    'overall_score': 'Overall Score',
                    'quality_grade': 'Grade'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Quality metrics comparison
        quality_metrics = ['url_health', 'edam_consistency', 'publication_quality', 'field_completeness']
        avg_metrics = {metric: df[metric].mean() for metric in quality_metrics}
        
        fig_metrics = px.bar(
            x=list(avg_metrics.keys()),
            y=list(avg_metrics.values()),
            title="Average Quality Metrics",
            labels={'x': 'Metric', 'y': 'Average Score (0-1)'}
        )
        fig_metrics.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig_metrics, use_container_width=True)
        
        # Validation and lint issues analysis
        col1, col2 = st.columns(2)
        
        with col1:
            validation_counts = df['schema_valid'].value_counts()
            fig_validation = px.pie(
                values=validation_counts.values,
                names=['Valid' if x else 'Invalid' for x in validation_counts.index],
                title="Schema Validation Results"
            )
            st.plotly_chart(fig_validation, use_container_width=True)
        
        with col2:
            if 'lint_issues' in df.columns:
                # Group lint issues into bins
                df['lint_issues_bin'] = pd.cut(
                    df['lint_issues'], 
                    bins=[0, 1, 3, 5, 10, float('inf')], 
                    labels=['0', '1-2', '3-4', '5-9', '10+'],
                    right=False
                )
                lint_counts = df['lint_issues_bin'].value_counts()
                
                fig_lint = px.bar(
                    x=lint_counts.index.astype(str),
                    y=lint_counts.values,
                    title="Distribution of Lint Issues",
                    labels={'x': 'Number of Lint Issues', 'y': 'Number of Tools'}
                )
                st.plotly_chart(fig_lint, use_container_width=True)
    
    def render_tool_details(self, tools_data: List[Dict[str, Any]]):
        """Render individual tool details."""
        st.subheader("🔍 Tool Details")
        
        if not tools_data:
            st.warning("No tools data available")
            return
        
        # Tool selector
        tool_names = [f"{tool.get('tool_id', 'unknown')} - {tool.get('tool_name', 'Unknown')}" for tool in tools_data]
        selected_tool_name = st.selectbox("Select a tool to view details", tool_names)
        
        if selected_tool_name:
            # Find selected tool
            tool_id = selected_tool_name.split(' - ')[0]
            selected_tool = next((tool for tool in tools_data if tool.get('tool_id') == tool_id), None)
            
            if selected_tool:
                metrics = selected_tool.get('metrics', {})
                
                # Tool header
                st.markdown(f"### {selected_tool.get('tool_name', 'Unknown Tool')}")
                st.markdown(f"**ID:** {selected_tool.get('tool_id', 'Unknown')}")
                
                # Summary
                if 'summary' in selected_tool:
                    st.markdown(f"**Summary:** {selected_tool['summary']}")
                
                # Key metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    overall_score = metrics.get('overall_score', 0)
                    st.metric("Overall Score", f"{overall_score}/100")
                
                with col2:
                    quality_grade = metrics.get('quality_grade', 'F')
                    st.metric("Quality Grade", quality_grade)
                
                with col3:
                    standards_tier = metrics.get('standards_tier', 'Tier 1')
                    st.metric("Standards Tier", standards_tier)
                
                with col4:
                    lint_issues = metrics.get('lint_issues', 0)
                    st.metric("Lint Issues", lint_issues)
                
                # Detailed metrics in tabs
                tab1, tab2, tab3 = st.tabs(["📊 Scores", "✅ Validation", "📋 Content"])
                
                with tab1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Score Breakdown**")
                        completeness_score = metrics.get('completeness_score', 0)
                        standards_score = metrics.get('standards_score', 0)
                        field_completeness = metrics.get('field_completeness', 0) * 100
                        
                        st.metric("Completeness Score", f"{completeness_score}/100")
                        st.metric("Standards Score", f"{standards_score}/100") 
                        st.metric("Field Completeness", f"{field_completeness:.1f}%")
                    
                    with col2:
                        # Quality gauge chart
                        fig_gauge = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=overall_score,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "Overall Quality Score"},
                            delta={'reference': 70},
                            gauge={
                                'axis': {'range': [None, 100]},
                                'bar': {'color': self.grade_colors.get(quality_grade, '#cccccc')},
                                'steps': [
                                    {'range': [0, 20], 'color': '#ff4d4d'},
                                    {'range': [20, 40], 'color': '#ff9933'},
                                    {'range': [40, 60], 'color': '#ffcc00'},
                                    {'range': [60, 80], 'color': '#66cc00'},
                                    {'range': [80, 100], 'color': '#00cc66'}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        fig_gauge.update_layout(height=400)
                        st.plotly_chart(fig_gauge, use_container_width=True)
                
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Schema Validation**")
                        schema_valid = metrics.get('schema_valid', False)
                        schema_errors = metrics.get('schema_errors', 0)
                        schema_warnings = metrics.get('schema_warnings', 0)
                        
                        st.metric("Schema Valid", "✅ Yes" if schema_valid else "❌ No")
                        st.metric("Schema Errors", schema_errors)
                        st.metric("Schema Warnings", schema_warnings)
                    
                    with col2:
                        st.markdown("**Linting Issues**")
                        critical_issues = metrics.get('critical_issues', 0)
                        error_issues = metrics.get('error_issues', 0)
                        warning_issues = metrics.get('warning_issues', 0)
                        info_issues = metrics.get('info_issues', 0)
                        
                        st.metric("Critical Issues", critical_issues)
                        st.metric("Error Issues", error_issues)
                        st.metric("Warning Issues", warning_issues)
                        st.metric("Info Issues", info_issues)
                
                with tab3:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Content Presence**")
                        has_functions = metrics.get('has_functions', False)
                        has_documentation = metrics.get('has_documentation', False)
                        has_publications = metrics.get('has_publications', False)
                        has_contacts = metrics.get('has_contacts', False)
                        
                        st.metric("Functions", "✅ Yes" if has_functions else "❌ No")
                        st.metric("Documentation", "✅ Yes" if has_documentation else "❌ No")
                        st.metric("Publications", "✅ Yes" if has_publications else "❌ No")
                        st.metric("Contacts", "✅ Yes" if has_contacts else "❌ No")
                    
                    with col2:
                        st.markdown("**Quality Metrics**")
                        url_health = metrics.get('url_health', 0) * 100
                        edam_consistency = metrics.get('edam_consistency', 0) * 100
                        publication_quality = metrics.get('publication_quality', 0) * 100
                        
                        st.metric("URL Health", f"{url_health:.1f}%")
                        st.metric("EDAM Consistency", f"{edam_consistency:.1f}%")
                        st.metric("Publication Quality", f"{publication_quality:.1f}%")
                
                # Recommendations
                if 'recommendations' in selected_tool and selected_tool['recommendations']:
                    st.markdown("**🎯 Recommendations**")
                    for i, rec in enumerate(selected_tool['recommendations'], 1):
                        st.markdown(f"{i}. {rec}")
    
    def render_file_upload_section(self):
        """Render file upload section for loading existing results."""
        st.subheader("📂 Load Data from File")
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file with analysis results",
            type="json",
            help="Upload a JSON file containing bio.tools quality analysis results"
        )
        
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                
                # Try to extract data in different expected formats
                if 'tools' in data:
                    # Dashboard data format
                    tools_data = data.get('tools', [])
                    statistics = data.get('statistics', {})
                    config = data.get('config', {})
                elif isinstance(data, list):
                    # Direct list of tools
                    tools_data = data
                    statistics = self._calculate_statistics_from_tools(tools_data)
                    config = {}
                elif 'results' in data:
                    # Analysis results format
                    tools_data = data.get('results', [])
                    statistics = data.get('statistics', {})
                    config = data.get('config', {})
                else:
                    st.error("Unrecognized data format in uploaded file")
                    return None, None, None
                
                st.success(f"✅ Loaded {len(tools_data)} tools from file")
                return tools_data, statistics, config
                
            except Exception as e:
                st.error(f"Error loading file: {e}")
                return None, None, None
        
        return None, None, None
    
    def _calculate_statistics_from_tools(self, tools_data: List[Dict]) -> Dict:
        """Calculate statistics from tools data."""
        if not tools_data:
            return {}
        
        total = len(tools_data)
        
        # Extract metrics or create basic stats
        if tools_data and 'metrics' in tools_data[0]:
            # New format with metrics
            grades = [tool['metrics'].get('quality_grade', 'F') for tool in tools_data]
            tiers = [tool['metrics'].get('standards_tier', 'Tier 1') for tool in tools_data]
            scores = [tool['metrics'].get('overall_score', 0) for tool in tools_data]
        else:
            # Fallback for other formats
            grades = ['F'] * total
            tiers = ['Tier 1'] * total  
            scores = [50] * total
        
        return {
            'total_tools': total,
            'grade_distribution': {grade: grades.count(grade) for grade in set(grades)},
            'tier_distribution': {tier: tiers.count(tier) for tier in set(tiers)},
            'average_score': sum(scores) / len(scores) if scores else 0
        }
    
    def run(self):
        """Main application runner."""
        self.render_header()
        
        # Sidebar for controls
        with st.sidebar:
            st.header("🔧 Controls")
            
            # Data loading options
            st.subheader("Data Source")
            data_source = st.radio(
                "Select data source:",
                ["Sample Data", "Load from File", "Load Cached Data"]
            )
            
            tools_data, statistics, config = [], {}, {}
            
            if data_source == "Sample Data":
                st.subheader("Sample Data Options")
                limit = st.slider("Number of tools", 10, 500, 100)
                if st.button("🔄 Generate Sample Data"):
                    with st.spinner("Generating sample data..."):
                        tools_data, statistics, config = self.load_sample_data(limit)
                        st.success(f"Generated {len(tools_data)} sample tools")
                else:
                    # Load default sample data
                    tools_data, statistics, config = self.load_sample_data(limit)
            
            elif data_source == "Load from File":
                st.subheader("File Upload")
                uploaded_tools, uploaded_stats, uploaded_config = self.render_file_upload_section()
                if uploaded_tools is not None:
                    tools_data, statistics, config = uploaded_tools, uploaded_stats, uploaded_config
            
            elif data_source == "Load Cached Data":
                st.subheader("Cached Data")
                if st.button("🔄 Load Cached Data"):
                    with st.spinner("Loading cached data..."):
                        tools_data, statistics, config = self.load_data_from_file()
                        if tools_data:
                            st.success(f"Loaded {len(tools_data)} tools from cache")
                        else:
                            st.warning("No cached data found")
                else:
                    tools_data, statistics, config = self.load_data_from_file()
            
            # Data info
            if tools_data and statistics:
                st.divider()
                st.markdown("**📊 Data Summary**")
                st.markdown(f"• **Tools:** {len(tools_data):,}")
                avg_score = statistics.get('average_score', 0) if statistics else 0
                st.markdown(f"• **Avg Score:** {avg_score:.1f}")
                
                # Quick stats
                grade_dist = statistics.get('grade_distribution', {}) if statistics else {}
                if grade_dist:
                    high_quality = grade_dist.get('A', 0) + grade_dist.get('B', 0)
                    st.markdown(f"• **High Quality:** {high_quality:,}")
        
        # Main content
        if tools_data and statistics:
            # Main tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview", 
                "🔍 Tools Browser", 
                "📈 Quality Analysis", 
                "🔍 Tool Details",
                "📋 Export & Reports"
            ])
            
            with tab1:
                self.render_overview_metrics(statistics)
                st.divider()
                
                # Create columns for different visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    self.render_quality_grades_distribution(statistics)
                
                with col2:
                    self.render_tier_distribution(statistics)
                
                st.divider()
                self.render_content_quality_metrics(statistics)
            
            with tab2:
                self.render_tools_table(tools_data)
            
            with tab3:
                self.render_quality_analysis(tools_data)
            
            with tab4:
                self.render_tool_details(tools_data)
            
            with tab5:
                st.subheader("📋 Export Options")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📥 Download JSON"):
                        export_data = {
                            "tools": tools_data,
                            "statistics": statistics,
                            "config": config,
                            "export_timestamp": datetime.now().isoformat()
                        }
                        st.download_button(
                            label="Download JSON Data",
                            data=json.dumps(export_data, indent=2, default=str),
                            file_name=f"biotools_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("📊 Download CSV"):
                        # Convert tools data to CSV
                        csv_data = []
                        for tool in tools_data:
                            metrics = tool.get('metrics', {})
                            row = {
                                'tool_id': tool.get('tool_id', ''),
                                'tool_name': tool.get('tool_name', ''),
                                'overall_score': metrics.get('overall_score', 0),
                                'quality_grade': metrics.get('quality_grade', ''),
                                'standards_tier': metrics.get('standards_tier', ''),
                                'completeness_score': metrics.get('completeness_score', 0),
                                'schema_valid': metrics.get('schema_valid', False),
                                'lint_issues': metrics.get('lint_issues', 0)
                            }
                            csv_data.append(row)
                        
                        df_export = pd.DataFrame(csv_data)
                        csv_string = df_export.to_csv(index=False)
                        
                        st.download_button(
                            label="Download CSV Data",
                            data=csv_string,
                            file_name=f"biotools_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                
                with col3:
                    st.markdown("**Report Options**")
                    st.info("HTML report generation coming soon!")
                
                # Statistics display
                st.divider()
                st.subheader("📊 Analysis Statistics")
                st.json(statistics)
        
        else:
            # Landing page when no data is loaded
            st.markdown("""
            ## � Welcome to Bio.tools Quality Dashboard
            
            This interactive dashboard provides comprehensive analysis of bio.tools annotation quality.
            
            ### 🚀 Getting Started
            1. **Select a data source** from the sidebar
            2. **Choose sample data** for a quick demo
            3. **Upload your own data** in JSON format
            4. **Explore the analysis** across different tabs
            
            ### 📊 What You'll Find
            - **Overview**: Key metrics and quality distributions
            - **Tools Browser**: Interactive table with filters
            - **Quality Analysis**: Detailed charts and correlations  
            - **Tool Details**: Individual tool deep-dive
            - **Export & Reports**: Download results and generate reports
            
            ### 🔧 Features
            - Real-time filtering and sorting
            - Interactive visualizations with Plotly
            - Export to JSON, CSV formats
            - Responsive design for all screen sizes
            
            **👈 Start by selecting a data source in the sidebar!**
            """)
            
            # Sample screenshots or demo content could go here
            st.info("💡 Tip: Try the 'Sample Data' option for a quick demonstration of the dashboard capabilities.")

def main():
    """Main application entry point.""" 
    try:
        dashboard = StreamlitDashboard()
        dashboard.run()
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please check the logs for more details and ensure all dependencies are installed.")

if __name__ == "__main__":
    main()
