#!/usr/bin/env python3
"""
Bio.tools Live Quality Analysis - Streamlit Application
Real-time tool quality analysis with live biotools API integration.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import sys
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import requests

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Import our analysis modules
try:
    from src.collectors.biotools_api import BioToolsAPIClient
    from src.analyzers.quality_analyzer import QualityAnalyzer, QualityReport
    from src.utils.logger import Logger
    MODULES_AVAILABLE = True
    BioToolsAPIClientType = BioToolsAPIClient
    QualityAnalyzerType = QualityAnalyzer
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")
    MODULES_AVAILABLE = False
    BioToolsAPIClientType = None
    QualityAnalyzerType = None

# Configure Streamlit page
st.set_page_config(
    page_title="Bio.tools Live Quality Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
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
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .quality-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        color: white;
        margin: 0.2rem;
    }
    .grade-A { background-color: #28a745; }
    .grade-B { background-color: #6f42c1; }
    .grade-C { background-color: #ffc107; color: black; }
    .grade-D { background-color: #fd7e14; }
    .grade-F { background-color: #dc3545; }
    .tier-1 { background-color: #ff4d4d; }
    .tier-2 { background-color: #ff9933; }
    .tier-3 { background-color: #ffcc00; color: black; }
    .tier-4 { background-color: #66cc00; }
    .tier-5 { background-color: #00cc66; }
    .stProgress .stProgress-bar {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

class LiveBioToolsAnalyzer:
    """Live bio.tools quality analyzer with real-time API integration."""
    
    def __init__(self):
        """Initialize the analyzer with caching directory."""
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = []
        if 'current_analysis' not in st.session_state:
            st.session_state.current_analysis = None
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
    
    def render_header(self):
        """Render the application header."""
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0;">🔬 Bio.tools Live Quality Analyzer</h1>
            <p style="color: #f0f0f0; margin: 0.5rem 0 0 0;">Real-time tool quality analysis with biotools API</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_search_interface(self):
        """Render the search and analysis interface."""
        st.sidebar.header("🔍 Analysis Options")
        
        # Analysis mode selection
        analysis_mode = st.sidebar.selectbox(
            "Analysis Mode",
            ["Single Tool", "Search Tools", "Random Tools", "Collection Analysis"],
            help="Choose how you want to analyze tools"
        )
        
        if analysis_mode == "Single Tool":
            return self.render_single_tool_interface()
        elif analysis_mode == "Search Tools":
            return self.render_search_tools_interface()
        elif analysis_mode == "Random Tools":
            return self.render_random_tools_interface()
        elif analysis_mode == "Collection Analysis":
            return self.render_collection_interface()
    
    def render_single_tool_interface(self):
        """Render single tool analysis interface."""
        st.sidebar.subheader("Single Tool Analysis")
        
        tool_id = st.sidebar.text_input(
            "Bio.tools ID",
            placeholder="e.g., blast, clustalw, galaxy",
            help="Enter the exact bio.tools ID of the tool you want to analyze"
        )
        
        if st.sidebar.button("🔍 Analyze Tool", disabled=not tool_id):
            return self.analyze_single_tool(tool_id)
        
        return None
    
    def render_search_tools_interface(self):
        """Render search tools interface."""
        st.sidebar.subheader("Search Tools")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            query = st.text_input(
                "Search Query",
                placeholder="e.g., alignment, genome",
                help="Search for tools by name, description, or keywords"
            )
        
        with col2:
            max_tools = st.number_input(
                "Max Tools",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of tools to analyze"
            )
        
        # Advanced search options
        with st.sidebar.expander("Advanced Options"):
            sort_by = st.selectbox(
                "Sort by",
                ["lastUpdate", "additionDate", "name", "score"],
                help="How to sort the search results"
            )
            
            sort_order = st.selectbox(
                "Sort order",
                ["desc", "asc"],
                help="Ascending or descending order"
            )
        
        if st.sidebar.button("🔍 Search & Analyze", disabled=not query):
            return self.search_and_analyze_tools(query, max_tools, sort_by, sort_order)
        
        return None
    
    def render_random_tools_interface(self):
        """Render random tools analysis interface."""
        st.sidebar.subheader("Random Tools Analysis")
        
        num_tools = st.sidebar.number_input(
            "Number of Tools",
            min_value=1,
            max_value=20,
            value=5,
            help="Number of random tools to analyze"
        )
        
        if st.sidebar.button("🎲 Analyze Random Tools"):
            return self.analyze_random_tools(num_tools)
        
        return None
    
    def render_collection_interface(self):
        """Render collection analysis interface."""
        st.sidebar.subheader("Collection Analysis")
        
        collection_id = st.sidebar.text_input(
            "Collection ID",
            placeholder="e.g., COVID-19",
            help="Enter a bio.tools collection ID"
        )
        
        if st.sidebar.button("📚 Analyze Collection", disabled=not collection_id):
            return self.analyze_collection(collection_id)
        
        return None
    
    def get_api_client(self):
        """Get or create API client."""
        if not hasattr(self, '_api_client'):
            if MODULES_AVAILABLE and BioToolsAPIClientType:
                self._api_client = BioToolsAPIClientType(cache_dir=self.cache_dir)
            else:
                raise ImportError("BioToolsAPIClient not available")
        return self._api_client
    
    def get_quality_analyzer(self):
        """Get or create quality analyzer."""
        if not hasattr(self, '_quality_analyzer'):
            if MODULES_AVAILABLE and QualityAnalyzerType:
                self._quality_analyzer = QualityAnalyzerType()
            else:
                raise ImportError("QualityAnalyzer not available")
        return self._quality_analyzer
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_tool_data(_self, tool_id: str):
        """Fetch tool data from bio.tools API with caching."""
        try:
            api_client = _self.get_api_client()
            return api_client.get_tool(tool_id)
        except Exception as e:
            st.error(f"Error fetching tool data for {tool_id}: {str(e)}")
            return None
    
    @st.cache_data(ttl=300)
    def search_tools(_self, query: str, max_tools: int = 10, sort_by: str = "lastUpdate", sort_order: str = "desc"):
        """Search for tools using bio.tools API with caching."""
        try:
            api_client = _self.get_api_client()
            
            # Calculate number of pages needed
            tools_per_page = 25  # bio.tools API default
            pages_needed = (max_tools + tools_per_page - 1) // tools_per_page
            
            all_tools = []
            for page in range(1, pages_needed + 1):
                result = api_client.list_tools(
                    page=page,
                    query=query,
                    sort=sort_by,
                    order=sort_order
                )
                
                tools = result.get('list', [])
                all_tools.extend(tools)
                
                # Stop if we have enough tools
                if len(all_tools) >= max_tools:
                    break
                
                # Stop if no more tools available
                if len(tools) < tools_per_page:
                    break
            
            return all_tools[:max_tools]
            
        except Exception as e:
            st.error(f"Error searching tools: {str(e)}")
            return []
    
    def analyze_tool_quality(self, tool_data: dict) -> Optional[dict]:
        """Analyze quality of a single tool."""
        try:
            analyzer = self.get_quality_analyzer()
            
            # Create a quality report
            report = analyzer.analyze_tool(tool_data)
            
            return {
                'tool_id': tool_data.get('biotoolsID', 'unknown'),
                'tool_name': tool_data.get('name', 'Unknown Tool'),
                'report': report,
                'raw_data': tool_data
            }
            
        except Exception as e:
            st.error(f"Error analyzing tool quality: {str(e)}")
            return None
    
    def analyze_single_tool(self, tool_id: str):
        """Analyze a single tool by ID."""
        with st.spinner(f"Fetching data for {tool_id}..."):
            tool_data = self.fetch_tool_data(tool_id)
            
            if not tool_data:
                st.error(f"Could not fetch data for tool: {tool_id}")
                return None
            
            with st.spinner("Analyzing tool quality..."):
                analysis = self.analyze_tool_quality(tool_data)
                
                if analysis:
                    st.session_state.current_analysis = analysis
                    st.session_state.analysis_history.append(analysis)
                    self.display_single_tool_results(analysis)
                
                return analysis
    
    def search_and_analyze_tools(self, query: str, max_tools: int, sort_by: str, sort_order: str):
        """Search for tools and analyze them."""
        with st.spinner(f"Searching for tools matching '{query}'..."):
            tools = self.search_tools(query, max_tools, sort_by, sort_order)
            
            if not tools:
                st.warning("No tools found matching your search criteria.")
                return None
            
            st.success(f"Found {len(tools)} tools. Starting analysis...")
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            analyses = []
            for i, tool_data in enumerate(tools):
                tool_id = tool_data.get('biotoolsID', f'tool_{i}')
                status_text.text(f"Analyzing {tool_id} ({i+1}/{len(tools)})")
                
                analysis = self.analyze_tool_quality(tool_data)
                if analysis:
                    analyses.append(analysis)
                
                progress_bar.progress((i + 1) / len(tools))
                time.sleep(0.1)  # Small delay to show progress
            
            status_text.text("Analysis complete!")
            progress_bar.empty()
            status_text.empty()
            
            if analyses:
                st.session_state.analysis_results = analyses
                self.display_bulk_analysis_results(analyses)
            
            return analyses
    
    def analyze_random_tools(self, num_tools: int):
        """Analyze random tools."""
        with st.spinner("Fetching random tools..."):
            # Get random tools by searching with an empty query and random sorting
            tools = self.search_tools("", num_tools, "lastUpdate", "desc")
            
            if not tools:
                st.warning("Could not fetch random tools.")
                return None
            
            return self.search_and_analyze_tools("", num_tools, "lastUpdate", "desc")
    
    def analyze_collection(self, collection_id: str):
        """Analyze tools in a collection."""
        st.info("Collection analysis feature coming soon!")
        return None
    
    def display_single_tool_results(self, analysis: dict):
        """Display results for a single tool analysis."""
        if not analysis or not analysis.get('report'):
            st.error("No analysis results to display")
            return
        
        tool_id = analysis['tool_id']
        tool_name = analysis['tool_name']
        report = analysis['report']
        
        # Header
        st.header(f"Analysis Results: {tool_name}")
        st.markdown(f"**Bio.tools ID:** `{tool_id}`")
        
        # Quality metrics overview
        if hasattr(report, 'metrics'):
            metrics = report.metrics
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                grade = getattr(metrics, 'quality_grade', 'N/A')
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Quality Grade</h4>
                    <div class="quality-badge grade-{grade}">{grade}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                score = getattr(metrics, 'overall_score', 0)
                st.metric("Overall Score", f"{score:.1f}/100")
            
            with col3:
                tier = getattr(metrics, 'standards_tier', 'N/A')
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Standards Tier</h4>
                    <div class="quality-badge tier-{tier.split()[-1] if tier != 'N/A' else '1'}">{tier}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                schema_valid = getattr(metrics, 'schema_valid', False)
                st.metric("Schema Valid", "✅ Yes" if schema_valid else "❌ No")
            
            # Detailed metrics
            st.subheader("📊 Detailed Metrics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Completeness Metrics**")
                field_completeness = getattr(metrics, 'field_completeness', 0)
                st.progress(field_completeness, text=f"Field Completeness: {field_completeness:.1%}")
                
                url_health = getattr(metrics, 'url_health', 0)
                st.progress(url_health, text=f"URL Health: {url_health:.1%}")
                
                edam_consistency = getattr(metrics, 'edam_consistency', 0)
                st.progress(edam_consistency, text=f"EDAM Consistency: {edam_consistency:.1%}")
            
            with col2:
                st.markdown("**Content Quality**")
                has_functions = getattr(metrics, 'has_functions', False)
                has_docs = getattr(metrics, 'has_documentation', False)
                has_pubs = getattr(metrics, 'has_publications', False)
                has_contacts = getattr(metrics, 'has_contacts', False)
                
                content_items = [
                    ("Functions", has_functions),
                    ("Documentation", has_docs),
                    ("Publications", has_pubs),
                    ("Contacts", has_contacts)
                ]
                
                for item, present in content_items:
                    icon = "✅" if present else "❌"
                    st.write(f"{icon} {item}")
        
        # Lint issues
        if hasattr(report, 'lint_issues') and report.lint_issues:
            st.subheader("🔍 Lint Issues")
            
            issues_by_level = {}
            for issue in report.lint_issues:
                level = issue.level.name if hasattr(issue.level, 'name') else str(issue.level)
                if level not in issues_by_level:
                    issues_by_level[level] = []
                issues_by_level[level].append(issue)
            
            for level, issues in issues_by_level.items():
                with st.expander(f"{level.title()} Issues ({len(issues)})"):
                    for issue in issues:
                        # Handle both old and new LintIssue formats
                        code = getattr(issue, 'code', getattr(issue, 'rule', 'Unknown'))
                        message = getattr(issue, 'message', str(issue))
                        st.write(f"- **{code}**: {message}")
        
        # Recommendations
        if hasattr(report, 'recommendations') and report.recommendations:
            st.subheader("💡 Recommendations")
            for rec in report.recommendations:
                st.write(f"- {rec}")
        
        # Raw data
        with st.expander("📄 Raw Tool Data"):
            st.json(analysis['raw_data'])
    
    def display_bulk_analysis_results(self, analyses: List[dict]):
        """Display results for bulk analysis."""
        if not analyses:
            st.warning("No analysis results to display")
            return
        
        st.header(f"Bulk Analysis Results ({len(analyses)} tools)")
        
        # Create summary statistics
        grades = []
        scores = []
        tiers = []
        
        for analysis in analyses:
            if analysis and analysis.get('report') and hasattr(analysis['report'], 'metrics'):
                metrics = analysis['report'].metrics
                grades.append(getattr(metrics, 'quality_grade', 'F'))
                scores.append(getattr(metrics, 'overall_score', 0))
                tiers.append(getattr(metrics, 'standards_tier', 'Tier 1'))
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tools Analyzed", len(analyses))
        
        with col2:
            avg_score = sum(scores) / len(scores) if scores else 0
            st.metric("Average Score", f"{avg_score:.1f}/100")
        
        with col3:
            high_quality = sum(1 for g in grades if g in ['A', 'B'])
            st.metric("High Quality (A/B)", f"{high_quality}/{len(grades)}")
        
        with col4:
            schema_valid = sum(1 for a in analyses 
                             if a and a.get('report') and hasattr(a['report'], 'metrics') 
                             and getattr(a['report'].metrics, 'schema_valid', False))
            st.metric("Schema Valid", f"{schema_valid}/{len(analyses)}")
        
        # Visualizations
        if grades:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Quality Grade Distribution")
                grade_counts = pd.Series(grades).value_counts()
                fig = px.pie(values=grade_counts.values, names=grade_counts.index, 
                           title="Quality Grades")
                st.plotly_chart(fig, width='stretch', key="grade_distribution_pie")
            
            with col2:
                st.subheader("Score Distribution")
                fig = px.histogram(x=scores, nbins=10, title="Quality Scores")
                fig.update_layout(
                    xaxis_title="Quality Score",
                    yaxis_title="Number of Tools"
                )
                st.plotly_chart(fig, width='stretch', key="score_distribution_hist")
        
        # Tools table
        st.subheader("📋 Analysis Summary Table")
        
        table_data = []
        for analysis in analyses:
            if analysis and analysis.get('report'):
                report = analysis['report']
                metrics = getattr(report, 'metrics', None)
                
                if metrics:
                    table_data.append({
                        'Tool ID': analysis['tool_id'],
                        'Tool Name': analysis['tool_name'][:30] + ('...' if len(analysis['tool_name']) > 30 else ''),
                        'Grade': getattr(metrics, 'quality_grade', 'N/A'),
                        'Score': f"{getattr(metrics, 'overall_score', 0):.1f}",
                        'Tier': getattr(metrics, 'standards_tier', 'N/A'),
                        'Schema Valid': '✅' if getattr(metrics, 'schema_valid', False) else '❌',
                        'Issues': getattr(metrics, 'lint_issues', 0)
                    })
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"biotools_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Individual tool details
        st.subheader("🔍 Individual Tool Details")
        tool_options = [f"{a['tool_id']} - {a['tool_name']}" for a in analyses if a]
        
        if tool_options:
            selected_tool = st.selectbox("Select a tool to view details:", tool_options)
            
            if selected_tool:
                tool_id = selected_tool.split(' - ')[0]
                selected_analysis = next((a for a in analyses if a and a['tool_id'] == tool_id), None)
                
                if selected_analysis:
                    self.display_single_tool_results(selected_analysis)
    
    def render_analysis_history(self):
        """Render analysis history sidebar."""
        if st.session_state.analysis_history:
            st.sidebar.subheader("📚 Analysis History")
            
            for i, analysis in enumerate(reversed(st.session_state.analysis_history[-5:])):
                if st.sidebar.button(f"{analysis['tool_name'][:20]}", key=f"history_{i}"):
                    st.session_state.current_analysis = analysis
                    self.display_single_tool_results(analysis)
    
    def run(self):
        """Run the Streamlit application."""
        self.render_header()
        
        # Main content area
        if not MODULES_AVAILABLE:
            st.error("Required analysis modules are not available. Please check your installation.")
            return
        
        # Sidebar navigation
        self.render_search_interface()
        self.render_analysis_history()
        
        # Main content
        if st.session_state.current_analysis:
            self.display_single_tool_results(st.session_state.current_analysis)
        elif st.session_state.analysis_results:
            self.display_bulk_analysis_results(st.session_state.analysis_results)
        else:
            # Welcome message
            st.markdown("""
            ## Welcome to Bio.tools Live Quality Analyzer! 🎉
            
            This application allows you to analyze bio.tools entries in real-time using the bio.tools API.
            
            ### 🚀 Getting Started
            
            1. **Choose an analysis mode** from the sidebar:
               - **Single Tool**: Analyze one specific tool by its bio.tools ID
               - **Search Tools**: Search for tools and analyze multiple results
               - **Random Tools**: Analyze a random selection of tools
               - **Collection Analysis**: Analyze tools from a specific collection
            
            2. **Enter your search criteria** and click the analyze button
            
            3. **View the results** with interactive charts and detailed metrics
            
            ### 📊 What You'll Get
            
            - **Quality Grades** (A-F) based on comprehensive analysis
            - **Standards Tier** compliance (Tier 1-5)
            - **Schema Validation** results
            - **Lint Issues** and recommendations for improvement
            - **Completeness Metrics** showing how complete the tool annotation is
            - **Content Quality** indicators (functions, documentation, etc.)
            
            ### 🔍 Analysis Features
            
            - Real-time API calls to bio.tools
            - Comprehensive quality scoring
            - Interactive visualizations
            - Downloadable results
            - Analysis history
            
            **Ready to start?** Choose an analysis mode from the sidebar! 👈
            """)


def main():
    """Main application entry point."""
    app = LiveBioToolsAnalyzer()
    app.run()


if __name__ == "__main__":
    main()
