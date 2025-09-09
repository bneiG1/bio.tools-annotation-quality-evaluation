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
import uuid
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
    from src.reporters.quality_reporter import QualityReporter
    from src.utils.logger import Logger
    MODULES_AVAILABLE = True
    BioToolsAPIClientType = BioToolsAPIClient
    QualityAnalyzerType = QualityAnalyzer
    QualityReporterType = QualityReporter
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")
    MODULES_AVAILABLE = False
    BioToolsAPIClientType = None
    QualityAnalyzerType = None
    QualityReporterType = None

# Configure Streamlit page
st.set_page_config(
    page_title="Bio.tools Live Quality Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add health check for deployment platforms
if 'health_check' not in st.session_state:
    st.session_state.health_check = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules_available': MODULES_AVAILABLE
    }

# Custom CSS for bio.tools-inspired styling
st.markdown("""
<style>
    /* Import similar font to bio.tools */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Global styling */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Avenir Next", Avenir,
            "Nimbus Sans L", Roboto, "Noto Sans", "Segoe UI", Arial, Helvetica,
            "Helvetica Neue", sans-serif;
        background-color: #fff;
    }
    
    /* Navigation header similar to bio.tools */
    .biotools-nav {
        background-color: #f9faff;
        border-bottom: 1px solid #898EA4;
        padding: 1rem 0;
        margin: -1rem -1rem 2rem -1rem;
        position: relative;
        z-index: 1000;
    }
    
    .nav-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
    }
    
    .nav-logo {
        font-size: 1.5rem;
        font-weight: 600;
        color: #212121;
        text-decoration: none;
    }
    
    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: #212121;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.95rem;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: background-color 0.2s;
    }
    
    .nav-link:hover {
        background-color: #e8ebff;
    }
    
    .nav-search {
        position: relative;
        margin: 0 2rem;
    }
    
    /* Main content area */
    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        margin-bottom: 3rem;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #f9faff 0%, #e8ebff 100%);
        border-radius: 10px;
        border: 1px solid #e0e4e7;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 600;
        color: #212121;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #585858;
        margin-bottom: 2rem;
        line-height: 1.5;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Card styling */
    .tool-card {
        background: #fff;
        border: 1px solid #e0e4e7;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s, border-color 0.2s;
    }
    
    .tool-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-color: #f47d21;
    }
    
    /* Quality badges */
    .quality-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-weight: 500;
        font-size: 0.85rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
    }
    
    .grade-A { background-color: #74c365; color: white; }
    .grade-B { background-color: #4a90e2; color: white; }
    .grade-C { background-color: #f39c12; color: white; }
    .grade-D { background-color: #e67e22; color: white; }
    .grade-F { background-color: #e74c3c; color: white; }
    
    /* Metrics section */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: #fff;
        border: 1px solid #e0e4e7;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        border-left: 4px solid #f47d21;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #212121;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #585858;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Section headers */
    .section-header {
        font-size: 2rem;
        font-weight: 600;
        color: #212121;
        margin: 3rem 0 1.5rem 0;
        border-bottom: 2px solid #f47d21;
        padding-bottom: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #f47d21;
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 5px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #e06a1a;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f9faff;
    }
    
    /* Progress bars */
    .stProgress .stProgress-bar {
        background-color: #f47d21;
    }
    
    /* Footer section */
    .footer-section {
        background-color: #f9faff;
        border-top: 1px solid #e0e4e7;
        padding: 3rem 2rem 2rem 2rem;
        margin: 4rem -2rem -2rem -2rem;
        text-align: center;
    }
    
    .footer-links {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 2rem;
        max-width: 1000px;
        margin: 0 auto 2rem auto;
        text-align: left;
    }
    
    .footer-column h4 {
        color: #212121;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    .footer-column a {
        color: #585858;
        text-decoration: none;
        display: block;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    
    .footer-column a:hover {
        color: #f47d21;
    }
    
    /* Responsive design */
    @media only screen and (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .nav-container {
            flex-direction: column;
            gap: 1rem;
        }
        
        .main-content {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def render_footer():
    """Render the bio.tools-inspired footer."""
    st.markdown("""
    <div class="footer-section">
        <div class="footer-links">
            <div class="footer-column">
                <h4>Tools</h4>
                <a href="https://bio.tools" target="_blank">Bio.tools</a>
                <a href="https://biotools.readthedocs.io/" target="_blank">Documentation</a>
                <a href="https://biotools.readthedocs.io/en/latest/api_reference.html" target="_blank">API Reference</a>
                <a href="https://github.com/bio-tools/biotoolsregistry" target="_blank">Source Code</a>
            </div>
            <div class="footer-column">
                <h4>Analysis</h4>
                <a href="#" onclick="return false;">Quality Scoring</a>
                <a href="#" onclick="return false;">Standards Compliance</a>
                <a href="#" onclick="return false;">Schema Validation</a>
                <a href="#" onclick="return false;">Completeness Metrics</a>
            </div>
            <div class="footer-column">
                <h4>Support</h4>
                <a href="https://github.com/bio-tools/biotoolsRegistry/issues" target="_blank">Issues</a>
                <a href="mailto:support-bio-tools@sdu.dk">Email Support</a>
                <a href="https://biotools.readthedocs.io/en/latest/what_is_biotools.html#getting-involved-a-quick-start-guide" target="_blank">Getting Involved</a>
                <a href="https://biotools.readthedocs.io/en/latest/contributors.html" target="_blank">Contributors</a>
            </div>
            <div class="footer-column">
                <h4>About</h4>
                <a href="https://bio.tools/about" target="_blank">About Bio.tools</a>
                <a href="https://bio.tools/stats" target="_blank">Statistics</a>
                <a href="https://biotools.readthedocs.io/en/latest/license.html" target="_blank">Licensing</a>
                <a href="https://www.elixir-europe.org/" target="_blank">ELIXIR</a>
            </div>
        </div>
        <p style="color: #585858; font-size: 0.85rem; margin-top: 2rem;">
            Bio.tools Quality Analyzer - Real-time tool quality analysis powered by the bio.tools API
        </p>
    </div>
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
        """Render the bio.tools-inspired navigation header."""
        st.markdown("""
        <div class="biotools-nav">
            <div class="nav-container">
                <div class="nav-logo">
                    🔬 Bio.tools Quality Analyzer
                </div>
                <div class="nav-search">
                    <!-- Search will be in main content -->
                </div>
                <div class="nav-links">
                    <a href="#" class="nav-link">Analyze</a>
                    <a href="#" class="nav-link">About</a>
                    <a href="https://bio.tools" target="_blank" class="nav-link">Bio.tools</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hero section
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">Bio.tools Quality Analyzer</h1>
            <p class="hero-subtitle">
                Real-time quality analysis for bioinformatics tools and services. 
                Analyze tool metadata completeness, standards compliance, and overall quality scores.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_system_warnings(self):
        """Render system warnings and status messages."""
        try:
            # Check if quality analyzer is available and get any warnings
            if MODULES_AVAILABLE and QualityAnalyzerType:
                analyzer = self.get_quality_analyzer()
                linter_warning = analyzer.get_linter_warning()
                
                if linter_warning:
                    st.warning(f"⚠️ **Linter Warning**: {linter_warning}")
                    with st.expander("ℹ️ What does this mean?"):
                        st.markdown("""
                        The bio.tools linter is an external tool that provides additional quality checks for tool metadata.
                        Without it, the analysis will still work but will have fewer quality insights.
                        
                        **To enable the linter:**
                        1. Clone the biotools-linter repository to your project root:
                           ```
                           git clone https://github.com/3top1a/biotools-linter.git
                           ```
                        2. Restart the application
                        
                        **What you're missing:**
                        - EDAM ontology validation
                        - URL accessibility checks
                        - Advanced metadata validation rules
                        """)
        except Exception as e:
            # Don't show errors for warning checks
            pass
    
    def render_search_interface(self):
        """Render the search and analysis interface."""
        
        # Create columns for the interface
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<h2 class="section-header">Analyze Tools</h2>', unsafe_allow_html=True)
            
            # Analysis mode selection with tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🔍 Single Tool", "🔎 Search Tools", "🎲 Random Tools", "📊 Collection"])
            
            with tab1:
                return self.render_single_tool_interface()
            
            with tab2:
                return self.render_search_tools_interface()
                
            with tab3:
                return self.render_random_tools_interface()
                
            with tab4:
                return self.render_collection_interface()
        
        return None
    
    def render_single_tool_interface(self):
        """Render single tool analysis interface."""
        st.markdown("### Single Tool Analysis")
        st.write("Analyze a specific tool by its bio.tools ID")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            tool_id = st.text_input(
                "Bio.tools ID",
                placeholder="e.g., blast, clustalw, galaxy",
                help="Enter the exact bio.tools ID of the tool you want to analyze",
                label_visibility="collapsed"
            )
        
        with col2:
            analyze_btn = st.button("🔍 Analyze Tool", disabled=not tool_id, use_container_width=True)
        
        if analyze_btn and tool_id:
            return self.analyze_single_tool(tool_id)
        
        return None
    
    def render_search_tools_interface(self):
        """Render search tools interface."""
        st.markdown("### Search and Analyze Tools")
        st.write("Search for tools by keywords and analyze multiple results")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            query = st.text_input(
                "Search Query",
                placeholder="e.g., alignment, genome, protein",
                help="Search for tools by name, description, or keywords",
                label_visibility="collapsed"
            )
        
        with col2:
            max_tools = st.number_input(
                "Max Tools",
                min_value=1,
                max_value=50,
                value=10,
                help="Maximum number of tools to analyze"
            )
        
        with col3:
            search_btn = st.button("🔍 Search & Analyze", disabled=not query, use_container_width=True)
        
        # Advanced search options in expander
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                sort_by = st.selectbox(
                    "Sort by",
                    ["lastUpdate", "additionDate", "name", "score"],
                    help="How to sort the search results"
                )
            
            with col2:
                sort_order = st.selectbox(
                    "Sort order",
                    ["desc", "asc"],
                    help="Ascending or descending order"
                )
        
        if search_btn and query:
            return self.search_and_analyze_tools(query, max_tools, sort_by, sort_order)
        
        return None
    
    def render_random_tools_interface(self):
        """Render random tools analysis interface."""
        st.markdown("### Random Tools Analysis")
        st.write("Analyze a random sample of tools from bio.tools")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            num_tools = st.number_input(
                "Number of Tools",
                min_value=1,
                max_value=20,
                value=5,
                help="Number of random tools to analyze"
            )
        
        with col2:
            random_btn = st.button("🎲 Analyze Random Tools", use_container_width=True)
        
        if random_btn:
            return self.analyze_random_tools(num_tools)
        
        return None
    
    def render_collection_interface(self):
        """Render collection analysis interface."""
        st.markdown("### Collection Analysis")
        st.write("Analyze tools from predefined collections or domains")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            collection_option = st.selectbox(
                "Collection Type",
                ["COVID-19 Tools", "Recent Tools", "Popular Tools", "Custom Collection"],
                help="Choose a predefined collection or create a custom one"
            )
        
        with col2:
            collection_btn = st.button("📊 Analyze Collection", use_container_width=True)
        
        if collection_option == "Custom Collection":
            st.text_area(
                "Tool IDs (one per line)",
                placeholder="blast\nclustalw\ngalaxy",
                help="Enter bio.tools IDs, one per line"
            )
        
        if collection_btn:
            if collection_option == "COVID-19 Tools":
                # Use search for COVID-19 related tools
                return self.search_and_analyze_tools("covid", 10, "lastUpdate", "desc")
            elif collection_option == "Recent Tools":
                # Use search for recent tools
                return self.search_and_analyze_tools("*", 10, "lastUpdate", "desc")
            elif collection_option == "Popular Tools":
                # Use search for popular tools
                return self.search_and_analyze_tools("*", 10, "score", "desc")
            # Add custom collection handling later
        
        return None
        
        collection_id = st.sidebar.text_input(
            "Custom Collection ID",
            placeholder="e.g., COVID-19, Galaxy, Bioconductor",
            help="Enter a bio.tools collection ID. Check bio.tools for available collections."
        )
        
        # Analysis options
        max_tools = st.sidebar.slider(
            "Maximum Tools to Analyze",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
            help="Limit the number of tools to analyze for performance"
        )
        
        if st.sidebar.button("🔍 Analyze Collection", disabled=not collection_id):
            return self.analyze_collection(collection_id, max_tools)
        
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
            
            if report and hasattr(report, 'metrics'):
                return {
                    'tool_id': tool_data.get('biotoolsID', 'unknown'),
                    'tool_name': tool_data.get('name', 'Unknown Tool'),
                    'report': report,
                    'raw_data': tool_data
                }
            else:
                st.warning(f"No valid report generated for tool: {tool_data.get('name', 'Unknown')}")
                return None
            
        except Exception as e:
            st.error(f"Error analyzing tool {tool_data.get('name', 'Unknown')}: {str(e)}")
            import traceback
            st.text(traceback.format_exc())
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
                    # Don't display here - let the main run() method handle display
                
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
                st.session_state.current_analysis = None  # Clear single analysis to show bulk results
            
            return analyses
    
    def analyze_random_tools(self, num_tools: int):
        """Analyze random tools."""
        with st.spinner("Fetching random tools..."):
            # Get random tools by searching with an empty query and random sorting
            tools = self.search_tools("", num_tools, "lastUpdate", "desc")
            
            if not tools:
                st.warning("Could not fetch random tools.")
                return None
            
            st.success(f"Found {len(tools)} random tools. Starting analysis...")
            
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
                st.session_state.current_analysis = None  # Clear single analysis to show bulk results
            
            return analyses
    
    def analyze_collection(self, collection_id: str, max_tools: int = 50):
        """Analyze tools in a collection."""
        if not collection_id:
            st.error("Please enter a collection ID")
            return
        
        # Clear previous session state to avoid conflicts
        st.session_state.analysis_results = []
        st.session_state.current_analysis = None
        
        st.title(f"📚 Collection Analysis: {collection_id}")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Fetch tools from collection
            status_text.text(f"🔍 Searching for tools in '{collection_id}' collection...")
            progress_bar.progress(10)
            
            api_client = self.get_api_client()
            response = api_client.search_by_collection(
                collection_id=collection_id,
                size=max_tools
            )
            
            # Extract tools from API response
            tools = response.get('list', []) if response else []
            total_count = response.get('count', 0) if response else 0
            
            if not tools:
                st.warning(f"No tools found in collection '{collection_id}'. Please check the collection ID.")
                return
            
            # Limit the number of tools to analyze
            tools = tools[:max_tools]
            
            progress_bar.progress(30)
            status_text.text(f"📊 Found {total_count} tools in collection, analyzing {len(tools)}...")
            
            # Analyze each tool
            results = []
            for i, tool in enumerate(tools):
                try:
                    # Update progress
                    progress = 30 + int((i / len(tools)) * 60)
                    progress_bar.progress(progress)
                    status_text.text(f"🔍 Analyzing tool {i+1}/{len(tools)}: {tool.get('name', 'Unknown')}")
                    
                    # Get full tool data
                    full_tool = api_client.get_tool(tool['biotoolsID'])
                    
                    if full_tool:
                        # Run quality analysis
                        analysis = self.analyze_tool_quality(full_tool)
                        
                        if analysis and analysis.get('report'):
                            # Add collection context
                            analysis['collection_id'] = collection_id
                            analysis['collection_name'] = collection_id
                            results.append(analysis)
                            print(f"DEBUG: Added analysis for {analysis.get('tool_name', 'Unknown')} to results. Total results: {len(results)}")
                        else:
                            print(f"DEBUG: No valid analysis generated for {tool.get('name', 'Unknown')}")
                            if analysis:
                                print(f"DEBUG: Analysis exists but missing report: {list(analysis.keys())}")
                            else:
                                print(f"DEBUG: Analysis is None")
                    else:
                        print(f"DEBUG: Failed to fetch full tool data for {tool.get('name', 'Unknown')}")
                
                except Exception as e:
                    st.warning(f"Error analyzing tool {tool.get('name', 'Unknown')}: {str(e)}")
                    continue
            
            progress_bar.progress(90)
            status_text.text("� Generating collection report...")
            
            if not results:
                st.error("No tools could be analyzed successfully.")
                st.info("**Possible reasons:**")
                st.write("- Tools may have invalid metadata that prevents analysis")
                st.write("- Network issues when fetching tool data")  
                st.write("- Quality analyzer configuration issues")
                st.write("- Try reducing the number of tools to analyze")
                return
            
            # Generate collection summary
            print(f"DEBUG: Generated analysis for {len(results)} results")
            
            progress_bar.progress(100)
            status_text.text("✅ Collection analysis complete!")
            
            # Store results in session state - display will be handled by main run() method
            st.session_state.current_analysis = {
                'type': 'collection',
                'collection_id': collection_id,
                'results': results,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            st.error(f"Error analyzing collection '{collection_id}': {str(e)}")
            # Simple logging without accessing analyzer attributes
            print(f"Collection analysis error: {str(e)}")
    
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
            st.subheader("💡 Comprehensive Improvement Recommendations")
            
            # Parse different types of recommendations
            tier_sections = []
            current_section = []
            critical_issues = []
            warnings = []
            
            for rec in report.recommendations:
                if not rec.strip():
                    continue
                    
                if "**📈 To achieve" in rec:
                    # Start new tier section
                    if current_section:
                        tier_sections.append(current_section)
                    current_section = [rec]
                elif "**� Critical Issues" in rec:
                    critical_issues.append(rec)
                elif "**⚠️ Additional Improvements" in rec:
                    warnings.append(rec)
                elif current_section:
                    # Add to current tier section
                    current_section.append(rec)
                else:
                    # General recommendation
                    if not critical_issues and not warnings:
                        current_section.append(rec)
            
            # Add last section
            if current_section:
                tier_sections.append(current_section)
            
            # Display tier roadmap
            if tier_sections:
                st.markdown("### 🎯 Tier Advancement Roadmap")
                st.markdown("Follow this roadmap to systematically improve your tool's metadata quality:")
                
                with st.expander("📈 Complete Roadmap (Click to expand)", expanded=len(tier_sections) <= 2):
                    for section in tier_sections:
                        for line in section:
                            if "**📈" in line:
                                st.markdown(line, unsafe_allow_html=True)
                            else:
                                st.markdown(line, unsafe_allow_html=True)
                        st.markdown("")  # Add spacing between tiers
            
            # Display critical issues
            if critical_issues:
                st.markdown("### � Critical Issues")
                st.error("These issues should be addressed first as they significantly impact tool quality:")
                for issue in critical_issues:
                    if issue.strip():
                        st.markdown(issue, unsafe_allow_html=True)
            
            # Display warnings
            if warnings:
                st.markdown("### ⚠️ Additional Improvements")
                st.warning("These improvements will further enhance your tool's quality:")
                for warning in warnings:
                    if warning.strip():
                        st.markdown(warning, unsafe_allow_html=True)
            
            # Add helpful guidance
            st.markdown("### � How to Use These Recommendations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **🎯 Prioritization Strategy:**
                1. **Critical Issues** - Fix these first
                2. **Next Tier Fields** - Focus on the next tier you want to achieve
                3. **Quality Improvements** - Enhance existing fields
                4. **Additional Warnings** - Address when time permits
                """)
            
            with col2:
                st.markdown("""
                **📈 Tier Benefits:**
                - **MINIMAL**: Better findability in searches
                - **DETAILED**: Complete technical information
                - **COMPLETE**: Full accessibility metadata
                - **COMPREHENSIVE**: Publication-ready quality
                """)
            
            st.info("""
            💡 **Pro Tips:**
            - Complete one tier at a time for systematic improvement
            - Each tier builds on the previous one - don't skip ahead
            - Quality improvements can boost your score even within the same tier  
            - Check back after updates to see your progress!
            """)
        else:
            st.info("No specific recommendations available - tool appears to be well-documented!")
        
        # Download options for single tool
        st.markdown("### 📥 Download Analysis Results")
        st.markdown("Export this tool's analysis in various formats:")
        
        try:
            if MODULES_AVAILABLE and QualityReporterType:
                reporter = QualityReporterType()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # JSON download
                    json_data = reporter.export_single_tool_data(report, format="json")
                    st.download_button(
                        label="📄 Download JSON",
                        data=json_data,
                        file_name=f"{tool_id}_analysis.json",
                        mime="application/json",
                        help="Complete analysis data in JSON format"
                    )
                
                with col2:
                    # CSV download
                    csv_data = reporter.export_single_tool_data(report, format="csv")
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_data,
                        file_name=f"{tool_id}_analysis.csv",
                        mime="text/csv",
                        help="Analysis metrics in spreadsheet format"
                    )
                
                with col3:
                    # Excel download
                    excel_data = reporter.export_single_tool_data(report, format="excel")
                    st.download_button(
                        label="📋 Download Excel",
                        data=excel_data,
                        file_name=f"{tool_id}_analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Detailed analysis with multiple sheets"
                    )
            else:
                st.info("📥 Download functionality requires complete module installation")
        
        except Exception as e:
            st.warning(f"Download functionality temporarily unavailable: {str(e)}")
        
        # Raw data
        with st.expander("📄 Raw Tool Data"):
            st.json(analysis['raw_data'])
    
    def display_bulk_analysis_results(self, analyses: List[dict]):
        """Display results for bulk analysis."""
        if not analyses:
            st.warning("No analysis results to display")
            return
        
        # Initialize reporter for export functionality
        reporter = None
        try:
            from src.reporters.quality_reporter import QualityReporter
            reporter = QualityReporter()
        except ImportError:
            st.warning("Export functionality unavailable - QualityReporter module not found")
        
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
                st.plotly_chart(fig, width='stretch', key=f"bulk_grade_distribution_pie_{uuid.uuid4().hex[:8]}")
            
            with col2:
                st.subheader("Score Distribution")
                fig = px.histogram(x=scores, nbins=10, title="Quality Scores")
                fig.update_layout(
                    xaxis_title="Quality Score",
                    yaxis_title="Number of Tools"
                )
                st.plotly_chart(fig, width='stretch', key=f"bulk_score_distribution_hist_{uuid.uuid4().hex[:8]}")
        
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
            st.dataframe(df, width='stretch', key=f"bulk_dataframe_{uuid.uuid4().hex[:8]}")
            
            # Download section with multiple formats
            st.markdown("### 📥 Download Analysis Results")
            
            # Filter valid analyses for detailed export
            valid_analyses = [a for a in analyses if a and a.get('quality_report')]
            valid_reports = [a['quality_report'] for a in valid_analyses if a.get('quality_report')]
            
            if valid_reports:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    # Summary CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="� Summary CSV",
                        data=csv,
                        file_name=f"biotools_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"bulk_summary_csv_{uuid.uuid4().hex[:8]}"
                    )
                
                if reporter:
                    with col2:
                        # Detailed analysis export
                        try:
                            detailed_data = reporter.export_detailed_data(
                                valid_reports, 
                                format='csv'
                            )
                            st.download_button(
                                label="📋 Detailed CSV",
                                data=detailed_data,
                                file_name=f"biotools_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key=f"bulk_detailed_csv_{uuid.uuid4().hex[:8]}"
                            )
                        except Exception as e:
                            st.error(f"Error generating detailed CSV: {str(e)}")
                    
                    with col3:
                        # JSON export
                        try:
                            json_data = reporter.export_detailed_data(
                                valid_reports, 
                                format='json'
                            )
                            st.download_button(
                                label="📄 JSON Export",
                                data=json_data,
                                file_name=f"biotools_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                key=f"bulk_json_{uuid.uuid4().hex[:8]}"
                            )
                        except Exception as e:
                            st.error(f"Error generating JSON: {str(e)}")
                    
                    with col4:
                        # Excel export
                        try:
                            excel_data = reporter.export_detailed_data(
                                valid_reports, 
                                format='excel'
                            )
                            st.download_button(
                                label="📈 Excel Report",
                                data=excel_data,
                                file_name=f"biotools_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"bulk_excel_{uuid.uuid4().hex[:8]}"
                            )
                        except Exception as e:
                            st.error(f"Error generating Excel: {str(e)}")
                
                # Add information about export formats
                with st.expander("ℹ️ Export Format Information"):
                    st.markdown("""
                    **Summary CSV**: Basic overview table with grades, scores, and key metrics
                    
                    **Detailed CSV**: Comprehensive analysis including all recommendations and detailed scores
                    
                    **JSON Export**: Complete analysis data in structured format for programmatic use
                    
                    **Excel Report**: Multi-sheet workbook with summary, detailed analysis, and recommendations
                    """)
            else:
                st.info("No valid analyses available for detailed export.")
        
        # Individual tool details
        st.subheader("🔍 Individual Tool Details")
        tool_options = [f"{a['tool_id']} - {a['tool_name']}" for a in analyses if a]
        
        if tool_options:
            selected_tool = st.selectbox("Select a tool to view details:", tool_options, key=f"bulk_tool_select_{uuid.uuid4().hex[:8]}")
            
            if selected_tool:
                tool_id = selected_tool.split(' - ')[0]
                selected_analysis = next((a for a in analyses if a and a['tool_id'] == tool_id), None)
                
                if selected_analysis:
                    self.display_single_tool_results(selected_analysis)
    
    def display_collection_results(self, analyses: List[dict], collection_id: str):
        """Display results for collection analysis."""
        if not analyses:
            st.warning("No analysis results to display")
            return
        
        st.header(f"📚 Collection Analysis: {collection_id}")
        st.markdown(f"**{len(analyses)} tools analyzed**")
        
        # Create summary statistics
        grades = []
        scores = []
        tiers = []
        schema_valid_count = 0
        lint_issues_total = 0
        
        for analysis in analyses:
            if analysis and analysis.get('report') and hasattr(analysis['report'], 'metrics'):
                metrics = analysis['report'].metrics
                grades.append(getattr(metrics, 'quality_grade', 'F'))
                scores.append(getattr(metrics, 'overall_score', 0))
                tiers.append(getattr(metrics, 'standards_tier', 'Tier 1'))
                
                if getattr(metrics, 'schema_valid', False):
                    schema_valid_count += 1
                    
                lint_issues_total += getattr(metrics, 'lint_issues', 0)
        
        # Collection overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Tools Analyzed", len(analyses))
        
        with col2:
            avg_score = sum(scores) / len(scores) if scores else 0
            st.metric("⭐ Average Quality", f"{avg_score:.1f}/100")
        
        with col3:
            high_quality = sum(1 for g in grades if g in ['A', 'B'])
            quality_pct = (high_quality / len(grades) * 100) if grades else 0
            st.metric("🏆 High Quality", f"{quality_pct:.1f}%")
        
        with col4:
            schema_pct = (schema_valid_count / len(analyses) * 100) if analyses else 0
            st.metric("✅ Schema Valid", f"{schema_pct:.1f}%")
        
        # Additional collection insights
        col1, col2 = st.columns(2)
        
        with col1:
            # Tier distribution
            if tiers:
                tier_counts = pd.Series(tiers).value_counts()
                st.subheader("📊 Standards Tier Distribution")
                tier_df = pd.DataFrame({
                    'Tier': tier_counts.index,
                    'Count': tier_counts.values,
                    'Percentage': [round(count / len(tiers) * 100, 1) for count in tier_counts.values]
                })
                st.dataframe(tier_df, width='stretch', key=f"collection_tier_dataframe_{uuid.uuid4().hex[:8]}")
        
        with col2:
            # Quality metrics
            st.subheader("🔍 Quality Metrics")
            st.markdown(f"""
            - **Total Lint Issues:** {lint_issues_total}
            - **Avg Issues per Tool:** {lint_issues_total / len(analyses):.1f}
            - **Tools with Issues:** {sum(1 for a in analyses if a.get('report') and hasattr(a['report'], 'metrics') and getattr(a['report'].metrics, 'lint_issues', 0) > 0)}
            """)
        
        # Visualizations
        if grades and len(grades) > 1:
            st.subheader("📈 Collection Quality Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Grade distribution pie chart
                grade_counts = pd.Series(grades).value_counts()
                fig = px.pie(
                    values=grade_counts.values, 
                    names=grade_counts.index,
                    title=f"Quality Grade Distribution - {collection_id}",
                    color_discrete_map={
                        'A': '#28a745', 'B': '#6f42c1', 'C': '#ffc107', 
                        'D': '#fd7e14', 'F': '#dc3545'
                    }
                )
                st.plotly_chart(fig, width='stretch', key=f"collection_grade_pie_{uuid.uuid4().hex[:8]}")
            
            with col2:
                # Score distribution histogram
                fig = px.histogram(
                    x=scores, 
                    nbins=min(10, len(scores)),
                    title=f"Quality Score Distribution - {collection_id}",
                    labels={'x': 'Quality Score', 'y': 'Number of Tools'}
                )
                fig.update_layout(
                    xaxis_title="Quality Score (0-100)",
                    yaxis_title="Number of Tools"
                )
                st.plotly_chart(fig, width='stretch', key=f"collection_score_hist_{uuid.uuid4().hex[:8]}")
        
        # Detailed results table
        st.subheader("📋 Detailed Tool Analysis")
        
        table_data = []
        for analysis in analyses:
            if analysis and analysis.get('report'):
                report = analysis['report']
                metrics = getattr(report, 'metrics', None)
                
                if metrics:
                    tool_name = analysis.get('tool_name', 'Unknown')
                    table_data.append({
                        'Tool ID': analysis['tool_id'],
                        'Tool Name': tool_name[:40] + ('...' if len(tool_name) > 40 else ''),
                        'Quality Grade': getattr(metrics, 'quality_grade', 'N/A'),
                        'Overall Score': f"{getattr(metrics, 'overall_score', 0):.1f}",
                        'Standards Tier': getattr(metrics, 'standards_tier', 'N/A'),
                        'Schema Valid': '✅' if getattr(metrics, 'schema_valid', False) else '❌',
                        'Lint Issues': getattr(metrics, 'lint_issues', 0),
                        'Last Updated': getattr(metrics, 'last_update', 'N/A')
                    })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Add sorting options
            sort_col1, sort_col2 = st.columns(2)
            with sort_col1:
                sort_by = st.selectbox(
                    "Sort by:",
                    ['Quality Grade', 'Overall Score', 'Standards Tier', 'Lint Issues', 'Tool Name'],
                    key=f"collection_sort_{uuid.uuid4().hex[:8]}"
                )
            with sort_col2:
                ascending = st.checkbox("Ascending", key=f"collection_sort_asc_{uuid.uuid4().hex[:8]}")
            
            # Sort dataframe
            if sort_by in df.columns:
                if sort_by in ['Overall Score', 'Lint Issues']:
                    df[sort_by] = pd.to_numeric(df[sort_by], errors='coerce')
                df = df.sort_values(sort_by, ascending=ascending)
            
            st.dataframe(df, width='stretch', key=f"collection_main_dataframe_{uuid.uuid4().hex[:8]}")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"biotools_collection_{collection_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key=f"collection_download_csv_{uuid.uuid4().hex[:8]}"
                )
            
            with col2:
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_data,
                    file_name=f"biotools_collection_{collection_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"collection_download_json_{uuid.uuid4().hex[:8]}"
                )
        
        # Individual tool inspection
        st.subheader("🔍 Individual Tool Details")
        
        if analyses:
            tool_options = [f"{a['tool_id']} - {a['tool_name']}" for a in analyses if a]
            
            selected_tool = st.selectbox(
                "Select a tool to view detailed analysis:",
                [''] + tool_options,
                key=f"collection_tool_select_{collection_id.replace(' ', '_').replace('-', '_')}"
            )
            
            if selected_tool:
                tool_id = selected_tool.split(' - ')[0]
                selected_analysis = next((a for a in analyses if a and a['tool_id'] == tool_id), None)
                
                if selected_analysis:
                    st.markdown("---")  # Separator line
                    st.markdown("## 📊 Individual Tool Analysis")
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
        self.render_system_warnings()
        
        # Main content area
        if not MODULES_AVAILABLE:
            st.error("Required analysis modules are not available. Please check your installation.")
            return
        
        # Sidebar navigation
        self.render_search_interface()
        self.render_analysis_history()
        
        # Main content
        if st.session_state.current_analysis:
            # Check if this is a collection analysis
            if (isinstance(st.session_state.current_analysis, dict) and 
                st.session_state.current_analysis.get('type') == 'collection'):
                # Collection analysis - display results including dropdown interactions
                collection_data = st.session_state.current_analysis
                self.display_collection_results(
                    collection_data.get('results', []), 
                    collection_data.get('collection_id', 'Unknown')
                )
            else:
                # Single tool analysis
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
        
        # Add footer
        render_footer()


def main():
    """Main application entry point."""
    try:
        # Log startup information
        import os
        print(f"🔬 Starting Bio.tools Live Quality Analyzer...")
        print(f"📍 Working directory: {os.getcwd()}")
        print(f"🐍 Python: {sys.version}")
        print(f"📦 Modules available: {MODULES_AVAILABLE}")
        
        # Check if running in deployment
        if 'STREAMLIT_SERVER_PORT' in os.environ:
            print(f"🚀 Deployment mode detected")
        else:
            print(f"💻 Local mode detected")
        
        app = LiveBioToolsAnalyzer()
        app.run()
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")
        # Still try to show a basic Streamlit page
        st.error(f"Application startup failed: {e}")
        st.text("Check the server logs for more details.")
        raise


if __name__ == "__main__":
    main()
