#!/usr/bin/env python3
"""
Bio.tools Data Dashboard Generator
Creates a comprehensive Streamlit dashboard using real bio.tools data from cache.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from collections import Counter
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="Bio.tools Real Data Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2E86AB;
    }
    .category-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        margin: 0.1rem;
        border-radius: 15px;
        background-color: #E3F2FD;
        color: #1976D2;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .quality-high { background-color: #E8F5E8; color: #2E7D32; }
    .quality-medium { background-color: #FFF3E0; color: #F57C00; }
    .quality-low { background-color: #FFEBEE; color: #D32F2F; }
</style>
""", unsafe_allow_html=True)

class BioToolsDataDashboard:
    """Dashboard for analyzing real bio.tools data."""
    
    def __init__(self, data_dir: str = "data/cache"):
        self.data_dir = Path(data_dir)
        self.tools_data = []
        self.stats_data = {}
        self.loaded = False
        
    @st.cache_data
    def load_biotools_data(_self):
        """Load all bio.tools data from cache directory."""
        tools_data = []
        stats_data = {}
        
        # Load general stats
        stats_file = _self.data_dir / "stats.json"
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
        
        # Load all tool files
        tool_files = list(_self.data_dir.glob("tool*.json"))
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, tool_file in enumerate(tool_files):
            try:
                status_text.text(f"Loading {tool_file.name}...")
                with open(tool_file, 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                    # Validate that we have basic required fields
                    if not isinstance(tool_data, dict):
                        st.warning(f"Invalid data format in {tool_file.name}: not a dictionary")
                        continue
                    
                    # Ensure we have a biotoolsID
                    if not tool_data.get('biotoolsID'):
                        tool_data['biotoolsID'] = tool_file.stem.replace('tool', '')
                    
                    # Add quality analysis metrics
                    analyzed_tool = _self._analyze_tool_quality(tool_data)
                    tools_data.append(analyzed_tool)
                
                progress_bar.progress((i + 1) / len(tool_files))
                
            except json.JSONDecodeError as e:
                st.warning(f"JSON decode error in {tool_file.name}: {e}")
                continue
            except Exception as e:
                st.warning(f"Error loading {tool_file.name}: {e}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        return tools_data, stats_data
    
    def _analyze_tool_quality(self, tool_data: Dict) -> Dict:
        """Analyze quality metrics for a tool with safe field access."""
        quality_score = 0
        quality_factors = []
        
        # Basic information completeness (0-30 points)
        if tool_data.get('name'): 
            quality_score += 5
            quality_factors.append("Has name")
        if tool_data.get('description'): 
            quality_score += 10
            quality_factors.append("Has description")
        if tool_data.get('homepage'): 
            quality_score += 10
            quality_factors.append("Has homepage")
        if tool_data.get('version'): 
            quality_score += 5
            quality_factors.append("Has version info")
        
        # Function annotations (0-25 points)
        functions = tool_data.get('function', [])
        if functions:
            quality_score += 15
            quality_factors.append("Has function annotations")
            # Extra points for detailed functions
            total_operations = sum(len(f.get('operation', [])) for f in functions if isinstance(f, dict))
            if total_operations >= 3:
                quality_score += 5
                quality_factors.append("Multiple operations defined")
            if any(f.get('input') for f in functions if isinstance(f, dict)):
                quality_score += 3
                quality_factors.append("Has input specifications")
            if any(f.get('output') for f in functions if isinstance(f, dict)):
                quality_score += 2
                quality_factors.append("Has output specifications")
        
        # Topic annotations (0-15 points)
        topics = tool_data.get('topic', [])
        if topics:
            quality_score += 10
            quality_factors.append("Has topic annotations")
            if len(topics) >= 3:
                quality_score += 5
                quality_factors.append("Multiple topics defined")
        
        # Publications (0-15 points)
        publications = tool_data.get('publication', [])
        if publications:
            quality_score += 10
            quality_factors.append("Has publications")
            if len(publications) >= 2:
                quality_score += 5
                quality_factors.append("Multiple publications")
        
        # Contact information (0-10 points)
        contacts = tool_data.get('credit', [])
        if contacts:
            quality_score += 5
            quality_factors.append("Has contact info")
            if any(c.get('email') for c in contacts if isinstance(c, dict)):
                quality_score += 5
                quality_factors.append("Has email contact")
        
        # Documentation (0-5 points)
        docs = tool_data.get('documentation', [])
        if docs:
            quality_score += 5
            quality_factors.append("Has documentation")
        
        # Determine quality tier
        if quality_score >= 80:
            quality_tier = "Excellent"
            quality_grade = "A"
        elif quality_score >= 65:
            quality_tier = "Good"
            quality_grade = "B"
        elif quality_score >= 50:
            quality_tier = "Fair"
            quality_grade = "C"
        elif quality_score >= 35:
            quality_tier = "Poor"
            quality_grade = "D"
        else:
            quality_tier = "Needs Improvement"
            quality_grade = "F"
        
        # Add computed metrics to tool data with safe counts
        tool_data['quality_metrics'] = {
            'overall_score': quality_score,
            'quality_grade': quality_grade,
            'quality_tier': quality_tier,
            'quality_factors': quality_factors,
            'function_count': len(functions),
            'topic_count': len(topics),
            'publication_count': len(publications),
            'contact_count': len(contacts),
            'documentation_count': len(docs),
            'has_homepage': bool(tool_data.get('homepage')),
            'has_version': bool(tool_data.get('version')),
            'edam_operations': sum(len(f.get('operation', [])) for f in functions if isinstance(f, dict)),
            'edam_topics': len(topics)
        }
        
        return tool_data
    
    def render_header(self):
        """Render the main header."""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🧬 Bio.tools Real Data Dashboard</h1>
            <p style="color: #f0f0f0; margin: 0;">Comprehensive Analysis of Bio.tools Registry Data</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_overview_metrics(self):
        """Render overview metrics from real data."""
        st.subheader("📊 Registry Overview")
        
        if not self.tools_data:
            st.warning("No data loaded")
            return
        
        # Calculate metrics
        total_tools = len(self.tools_data)
        avg_score = np.mean([t['quality_metrics']['overall_score'] for t in self.tools_data])
        
        # Quality distribution
        grades = [t['quality_metrics']['quality_grade'] for t in self.tools_data]
        grade_counts = Counter(grades)
        
        # Content statistics
        with_functions = sum(1 for t in self.tools_data if t['quality_metrics']['function_count'] > 0)
        with_publications = sum(1 for t in self.tools_data if t['quality_metrics']['publication_count'] > 0)
        with_contacts = sum(1 for t in self.tools_data if t['quality_metrics']['contact_count'] > 0)
        with_docs = sum(1 for t in self.tools_data if t['quality_metrics']['documentation_count'] > 0)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Tools",
                value=f"{total_tools:,}",
                help="Number of tools loaded from cache"
            )
        
        with col2:
            st.metric(
                label="Average Quality Score",
                value=f"{avg_score:.1f}/100",
                help="Average quality score based on completeness analysis"
            )
        
        with col3:
            high_quality = grade_counts.get('A', 0) + grade_counts.get('B', 0)
            st.metric(
                label="High Quality Tools",
                value=f"{high_quality:,}",
                delta=f"{(high_quality/total_tools)*100:.1f}%"
            )
        
        with col4:
            st.metric(
                label="Tools with Functions",
                value=f"{with_functions:,}",
                delta=f"{(with_functions/total_tools)*100:.1f}%"
            )
        
        # Additional stats row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="With Publications",
                value=f"{with_publications:,}",
                delta=f"{(with_publications/total_tools)*100:.1f}%"
            )
        
        with col2:
            st.metric(
                label="With Contacts", 
                value=f"{with_contacts:,}",
                delta=f"{(with_contacts/total_tools)*100:.1f}%"
            )
        
        with col3:
            st.metric(
                label="With Documentation",
                value=f"{with_docs:,}",
                delta=f"{(with_docs/total_tools)*100:.1f}%"
            )
        
        with col4:
            # From stats.json if available
            total_registry = self.stats_data.get('totalEntries', 'Unknown')
            st.metric(
                label="Total Registry Size",
                value=f"{total_registry:,}" if isinstance(total_registry, int) else total_registry,
                help="Total tools in bio.tools registry"
            )
    
    def render_quality_analysis(self):
        """Render quality analysis charts."""
        st.subheader("📈 Quality Analysis")
        
        if not self.tools_data:
            return
        
        # Prepare data with safe field access
        df_tools = pd.DataFrame([
            {
                'Tool': tool.get('name', tool.get('biotoolsID', 'Unknown')),
                'ID': tool.get('biotoolsID', 'Unknown'),
                'Score': tool['quality_metrics']['overall_score'],
                'Grade': tool['quality_metrics']['quality_grade'],
                'Tier': tool['quality_metrics']['quality_tier'],
                'Functions': tool['quality_metrics']['function_count'],
                'Topics': tool['quality_metrics']['topic_count'],
                'Publications': tool['quality_metrics']['publication_count'],
                'EDAM Operations': tool['quality_metrics']['edam_operations'],
                'Has Homepage': tool['quality_metrics']['has_homepage']
            }
            for tool in self.tools_data
        ])
        
        # Quality grade distribution
        col1, col2 = st.columns(2)
        
        with col1:
            grade_counts = df_tools['Grade'].value_counts()
            fig_grades = px.pie(
                values=grade_counts.values,
                names=grade_counts.index,
                title="Quality Grade Distribution",
                color_discrete_map={
                    'A': '#2E7D32', 'B': '#66BB6A', 'C': '#FFA726',
                    'D': '#FF7043', 'F': '#E53935'
                }
            )
            fig_grades.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_grades, use_container_width=True)
        
        with col2:
            # Score distribution histogram
            fig_scores = px.histogram(
                df_tools,
                x='Score',
                nbins=20,
                title="Quality Score Distribution",
                labels={'Score': 'Quality Score', 'count': 'Number of Tools'}
            )
            fig_scores.add_vline(x=df_tools['Score'].mean(), line_dash="dash", 
                                line_color="red", annotation_text="Average")
            st.plotly_chart(fig_scores, use_container_width=True)
        
        # Correlation analysis
        st.subheader("🔗 Quality Correlations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Functions vs Score
            fig_func = px.scatter(
                df_tools,
                x='Functions',
                y='Score',
                color='Grade',
                title="Functions vs Quality Score",
                labels={'Functions': 'Number of Functions', 'Score': 'Quality Score'},
                hover_data=['Tool']
            )
            st.plotly_chart(fig_func, use_container_width=True)
        
        with col2:
            # Publications vs Score
            fig_pub = px.scatter(
                df_tools,
                x='Publications',
                y='Score',
                color='Grade',
                title="Publications vs Quality Score",
                labels={'Publications': 'Number of Publications', 'Score': 'Quality Score'},
                hover_data=['Tool']
            )
            st.plotly_chart(fig_pub, use_container_width=True)
    
    def render_topic_analysis(self):
        """Render topic and functional analysis."""
        st.subheader("🏷️ Topic & Function Analysis")
        
        if not self.tools_data:
            return
        
        # Extract all topics
        all_topics = []
        all_operations = []
        
        for tool in self.tools_data:
            topics = tool.get('topic', [])
            for topic in topics:
                if isinstance(topic, dict) and 'term' in topic:
                    all_topics.append(topic['term'])
            
            functions = tool.get('function', [])
            for func in functions:
                operations = func.get('operation', [])
                for op in operations:
                    if isinstance(op, dict) and 'term' in op:
                        all_operations.append(op['term'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top topics
            if all_topics:
                topic_counts = Counter(all_topics)
                top_topics = dict(topic_counts.most_common(15))
                
                fig_topics = px.bar(
                    x=list(top_topics.values()),
                    y=list(top_topics.keys()),
                    orientation='h',
                    title="Top 15 Topics",
                    labels={'x': 'Number of Tools', 'y': 'Topics'}
                )
                fig_topics.update_layout(height=500)
                st.plotly_chart(fig_topics, use_container_width=True)
        
        with col2:
            # Top operations
            if all_operations:
                op_counts = Counter(all_operations)
                top_ops = dict(op_counts.most_common(15))
                
                fig_ops = px.bar(
                    x=list(top_ops.values()),
                    y=list(top_ops.keys()),
                    orientation='h',
                    title="Top 15 Operations",
                    labels={'x': 'Number of Tools', 'y': 'Operations'}
                )
                fig_ops.update_layout(height=500)
                st.plotly_chart(fig_ops, use_container_width=True)
        
        # Registry stats from stats.json
        if self.stats_data.get('topTopics'):
            st.subheader("📊 Registry-wide Topic Statistics")
            
            registry_topics = pd.DataFrame(self.stats_data['topTopics'])
            
            fig_registry = px.bar(
                registry_topics.head(20),
                x='count',
                y='topic',
                orientation='h',
                title="Top 20 Topics in Bio.tools Registry",
                labels={'count': 'Number of Tools', 'topic': 'Topics'}
            )
            fig_registry.update_layout(height=600)
            st.plotly_chart(fig_registry, use_container_width=True)
    
    def render_tools_browser(self):
        """Render interactive tools browser."""
        st.subheader("🔍 Tools Browser")
        
        if not self.tools_data:
            return
        
        # Prepare data for table with safe field access
        table_data = []
        for tool in self.tools_data:
            description = tool.get('description', '')
            if description and len(description) > 100:
                description = description[:100] + '...'
            elif not description:
                description = 'No description'
            
            row = {
                'Tool Name': tool.get('name', tool.get('biotoolsID', 'Unknown')),
                'ID': tool.get('biotoolsID', 'Unknown'),
                'Quality Score': tool['quality_metrics']['overall_score'],
                'Grade': tool['quality_metrics']['quality_grade'],
                'Functions': tool['quality_metrics']['function_count'],
                'Topics': tool['quality_metrics']['topic_count'],
                'Publications': tool['quality_metrics']['publication_count'],
                'Homepage': '✅' if tool['quality_metrics']['has_homepage'] else '❌',
                'Description': description
            }
            table_data.append(row)
        
        df_table = pd.DataFrame(table_data)
        
        # Filters
        st.markdown("**🔧 Filters**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            grade_filter = st.selectbox(
                "Quality Grade",
                options=['All'] + sorted(df_table['Grade'].unique().tolist()),
                index=0
            )
        
        with col2:
            min_score = st.slider("Minimum Score", 0, 100, 0)
        
        with col3:
            min_functions = st.slider("Minimum Functions", 0, df_table['Functions'].max(), 0)
        
        with col4:
            has_homepage = st.selectbox(
                "Has Homepage",
                options=['All', 'Yes', 'No'],
                index=0
            )
        
        # Apply filters
        filtered_df = df_table.copy()
        
        if grade_filter != 'All':
            filtered_df = filtered_df[filtered_df['Grade'] == grade_filter]
        
        filtered_df = filtered_df[filtered_df['Quality Score'] >= min_score]
        filtered_df = filtered_df[filtered_df['Functions'] >= min_functions]
        
        if has_homepage == 'Yes':
            filtered_df = filtered_df[filtered_df['Homepage'] == '✅']
        elif has_homepage == 'No':
            filtered_df = filtered_df[filtered_df['Homepage'] == '❌']
        
        # Display table
        st.markdown(f"**📊 Showing {len(filtered_df)} of {len(df_table)} tools**")
        
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Quality Score": st.column_config.ProgressColumn(
                    "Quality Score",
                    help="Quality score out of 100",
                    min_value=0,
                    max_value=100,
                ),
                "Functions": st.column_config.NumberColumn(
                    "Functions",
                    help="Number of function annotations",
                    min_value=0,
                ),
                "Topics": st.column_config.NumberColumn(
                    "Topics", 
                    help="Number of topic annotations",
                    min_value=0,
                ),
                "Publications": st.column_config.NumberColumn(
                    "Publications",
                    help="Number of publications",
                    min_value=0,
                )
            }
        )
    
    def render_detailed_tool_view(self):
        """Render detailed view for individual tools."""
        st.subheader("🔍 Tool Details")
        
        if not self.tools_data:
            return
        
        # Tool selector with safe access
        tool_names = [
            f"{tool.get('biotoolsID', 'unknown')} - {tool.get('name', 'Unknown Tool')}" 
            for tool in self.tools_data
        ]
        selected_tool_name = st.selectbox("Select a tool for detailed analysis", tool_names)
        
        if selected_tool_name:
            tool_id = selected_tool_name.split(' - ')[0]
            selected_tool = next((tool for tool in self.tools_data if tool.get('biotoolsID') == tool_id), None)
            
            if selected_tool:
                metrics = selected_tool['quality_metrics']
                
                # Tool header with safe access
                st.markdown(f"### {selected_tool.get('name', 'Unknown Tool')}")
                st.markdown(f"**Bio.tools ID:** {selected_tool.get('biotoolsID', 'Unknown')}")
                
                if selected_tool.get('description'):
                    st.markdown(f"**Description:** {selected_tool['description']}")
                
                if selected_tool.get('homepage'):
                    st.markdown(f"**Homepage:** [{selected_tool['homepage']}]({selected_tool['homepage']})")
                
                # Quality metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Quality Score", f"{metrics['overall_score']}/100")
                
                with col2:
                    st.metric("Quality Grade", metrics['quality_grade'])
                
                with col3:
                    st.metric("Quality Tier", metrics['quality_tier'])
                
                with col4:
                    st.metric("EDAM Operations", metrics['edam_operations'])
                
                # Detailed analysis tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 Quality Factors", "🔧 Functions", "🏷️ Topics", "📚 Publications"])
                
                with tab1:
                    st.markdown("**Quality Contributing Factors:**")
                    for factor in metrics['quality_factors']:
                        st.markdown(f"✅ {factor}")
                    
                    # Quality breakdown chart
                    quality_data = {
                        'Functions': metrics['function_count'],
                        'Topics': metrics['topic_count'],
                        'Publications': metrics['publication_count'],
                        'Documentation': metrics['documentation_count'],
                        'Contacts': metrics['contact_count']
                    }
                    
                    fig_quality = px.bar(
                        x=list(quality_data.keys()),
                        y=list(quality_data.values()),
                        title="Content Completeness Breakdown"
                    )
                    st.plotly_chart(fig_quality, use_container_width=True)
                
                with tab2:
                    functions = selected_tool.get('function', [])
                    if functions:
                        for i, func in enumerate(functions):
                            st.markdown(f"**Function {i+1}:**")
                            
                            operations = func.get('operation', [])
                            if operations:
                                st.markdown("**Operations:**")
                                for op in operations:
                                    st.markdown(f"- {op.get('term', 'Unknown')} ({op.get('uri', 'No URI')})")
                            
                            inputs = func.get('input', [])
                            if inputs:
                                st.markdown("**Inputs:**")
                                for inp in inputs:
                                    data_term = inp.get('data', {}).get('term', 'Unknown')
                                    formats = inp.get('format', [])
                                    format_terms = [f.get('term', 'Unknown') for f in formats]
                                    st.markdown(f"- {data_term} (Formats: {', '.join(format_terms)})")
                            
                            st.divider()
                    else:
                        st.info("No function information available")
                
                with tab3:
                    topics = selected_tool.get('topic', [])
                    if topics:
                        for topic in topics:
                            st.markdown(f"- **{topic.get('term', 'Unknown')}** ({topic.get('uri', 'No URI')})")
                    else:
                        st.info("No topic annotations available")
                
                with tab4:
                    publications = selected_tool.get('publication', [])
                    if publications:
                        for pub in publications:
                            st.markdown(f"**{pub.get('type', 'Publication')}:**")
                            if pub.get('pmid'):
                                st.markdown(f"- PMID: {pub['pmid']}")
                            if pub.get('doi'):
                                st.markdown(f"- DOI: {pub['doi']}")
                            if pub.get('pmcid'):
                                st.markdown(f"- PMC: {pub['pmcid']}")
                            st.divider()
                    else:
                        st.info("No publication information available")
    
    def run(self):
        """Main dashboard runner."""
        self.render_header()
        
        # Load data
        if not self.loaded:
            with st.spinner("Loading bio.tools data from cache..."):
                self.tools_data, self.stats_data = self.load_biotools_data()
                self.loaded = True
            
            if self.tools_data:
                st.success(f"✅ Loaded {len(self.tools_data)} tools from cache")
            else:
                st.error("❌ No data could be loaded from cache")
                return
        
        # Sidebar info
        with st.sidebar:
            st.header("📊 Data Summary")
            st.markdown(f"**Loaded Tools:** {len(self.tools_data):,}")
            
            if self.stats_data:
                st.markdown(f"**Registry Total:** {self.stats_data.get('totalEntries', 'Unknown'):,}")
                st.markdown(f"**Registry Date:** {self.stats_data.get('date', 'Unknown')}")
            
            st.divider()
            st.markdown("**Data Source:** Bio.tools cache directory")
            st.markdown("**Last Updated:** Cache files timestamp")
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "📈 Quality Analysis", 
            "🏷️ Topics & Functions",
            "🔍 Tools Browser",
            "🔍 Tool Details"
        ])
        
        with tab1:
            self.render_overview_metrics()
        
        with tab2:
            self.render_quality_analysis()
        
        with tab3:
            self.render_topic_analysis()
        
        with tab4:
            self.render_tools_browser()
        
        with tab5:
            self.render_detailed_tool_view()

def main():
    """Main application entry point."""
    dashboard = BioToolsDataDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
