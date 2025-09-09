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
    from src.collectors.async_biotools_api import UnifiedBioToolsAPIClient
    from src.analyzers.quality_analyzer import QualityAnalyzer, QualityReport
    from src.reporters.quality_reporter import QualityReporter
    from src.utils.logger import Logger
    
    # Get logger instance
    logger = Logger.get_logger(__name__)
    
    MODULES_AVAILABLE = True
    BioToolsAPIClientType = UnifiedBioToolsAPIClient
    QualityAnalyzerType = QualityAnalyzer
    QualityReporterType = QualityReporter
except ImportError as e:
    logging.warning(f"Some modules not available: {e}")
    MODULES_AVAILABLE = False
    BioToolsAPIClientType = None
    QualityAnalyzerType = None
    QualityReporterType = None
    logger = logging.getLogger(__name__)  # Fallback logger

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

# Custom CSS for authentic bio.tools styling
st.markdown("""
<style>
    /* Import similar font to bio.tools */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600&display=swap');
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    .stSidebar {display: none;}
    
    /* Global styling */
    .stApp {
        font-family: 'Open Sans', sans-serif;
        background-color: #f5f5f5;
    }
    
    .content-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Tool cards matching bio.tools style */
    .tool-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.2s;
    }
    
    .tool-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .tool-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #337ab7;
        margin-bottom: 0.5rem;
        text-decoration: none;
    }
    
    .tool-title:hover {
        color: #23527c;
    }
    
    .tool-description {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.4;
        margin-bottom: 1rem;
    }
    
    /* Tag system matching bio.tools */
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.3rem;
        margin-bottom: 0.5rem;
    }
    
    .tag {
        padding: 0.2rem 0.6rem;
        border-radius: 3px;
        font-size: 0.8rem;
        font-weight: 500;
        text-decoration: none;
        color: white;
    }
    
    /* Bio.tools tag colors */
    .tag-bioinformatics { background-color: #5cb85c; }
    .tag-probes { background-color: #5bc0de; }
    .tag-command { background-color: #337ab7; }
    .tag-workflow { background-color: #f0ad4e; }
    .tag-cc0 { background-color: #777; }
    .tag-sequence { background-color: #5cb85c; }
    .tag-data { background-color: #5bc0de; }
    .tag-visualisation { background-color: #d9534f; }
    .tag-desktop { background-color: #337ab7; }
    .tag-gpl { background-color: #777; }
    .tag-elixir { background-color: #f0ad4e; }
    
    /* Default tag colors for quality badges */
    .quality-tag {
        padding: 0.3rem 0.7rem;
        border-radius: 3px;
        font-size: 0.85rem;
        font-weight: 500;
        color: white;
        display: inline-block;
        margin: 0.2rem 0.3rem 0.2rem 0;
    }
    
    .quality-badge {
        padding: 0.5rem;
        border-radius: 50%;
        font-size: 1rem;
        font-weight: 600;
        color: white;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 0.2rem 0.3rem 0.2rem 0;
        text-align: center;
        min-width: 2.5rem;
        min-height: 2.5rem;
        width: 2.5rem;
        height: 2.5rem;
    }

    .standard-badge {
        padding: 0.5rem;
        border-radius: 10%;
        font-size: 1rem;
        font-weight: 600;
        color: white;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 0.2rem 0.3rem 0.2rem 0;
        text-align: center;
        # min-width: 2.5rem;
        # min-height: 2.5rem;
        # width: 2.5rem;
        # height: 2.5rem;
    }
    
    
    .grade-A { background-color: #5cb85c; }
    .grade-B { background-color: #5bc0de; }
    .grade-C { background-color: #f0ad4e; }
    .grade-D { background-color: #d9534f; }
    .grade-F { background-color: #c9302c; }
    
    /* Standards Tier colors */
    .tier-1 { background-color: #d9534f; }  /* Sparse - Red */
    .tier-2 { background-color: #f0ad4e; }  /* Minimal - Orange */
    .tier-3 { background-color: #5bc0de; }  /* Detailed - Light Blue */
    .tier-4 { background-color: #5cb85c; }  /* Complete - Green */
    .tier-5 { background-color: #337ab7; }  /* Comprehensive - Blue */
    
    /* Sort/filter bar matching bio.tools */
    .filter-bar {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .filter-label {
        font-weight: 500;
        color: #666;
        font-size: 0.9rem;
    }
    
    .display-options {
        margin-left: auto;
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    /* Stats section */
    .stats-container {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .stats-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-top: 1rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 600;
        color: #2c5aa0;
        display: block;
    }
    
    .stat-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    
    /* Button styling to match bio.tools */
    .stButton > button {
        background-color: #337ab7;
        color: white;
        border: 1px solid #2e6da4;
        padding: 0.6rem 1.2rem;
        border-radius: 4px;
        font-weight: normal;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #286090;
        border-color: #204d74;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 4px 4px 0 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
        padding: 0.7rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: white;
        border-bottom: 1px solid white;
    }
    
    /* Progress bars */
    .stProgress .stProgress-bar {
        background-color: #337ab7;
    }
    
    /* Responsive design */
    @media only screen and (max-width: 768px) {
        .header-container {
            flex-direction: column;
            gap: 1rem;
        }
        
        .header-search {
            margin: 0;
            max-width: 100%;
        }
        
        .content-container {
            padding: 0 1rem;
        }
        
        .filter-bar {
            flex-direction: column;
            align-items: flex-start;
        }
        
        .display-options {
            margin-left: 0;
        }
    }
    
    /* Hide the welcome message initially */
    .welcome-section {
        display: none;
    }
    
    /* History section styling */
    .history-section {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    .history-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #337ab7;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .history-description {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* History button styling */
    .stButton > button {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        color: #495057;
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .stButton > button:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
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
        if 'search_active' not in st.session_state:
            st.session_state.search_active = False
        if 'search_cancelled' not in st.session_state:
            st.session_state.search_cancelled = False
    
    def show_auto_fade_message(self, message: str, message_type: str = "success", fade_seconds: int = 5):
        """Show a message that automatically fades out after specified seconds."""
        import uuid
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        # Define colors based on message type
        colors = {
            "success": "#d4edda",
            "info": "#d1ecf1", 
            "warning": "#fff3cd",
            "error": "#f8d7da"
        }
        
        text_colors = {
            "success": "#155724",
            "info": "#0c5460",
            "warning": "#856404", 
            "error": "#721c24"
        }
        
        bg_color = colors.get(message_type, colors["info"])
        text_color = text_colors.get(message_type, text_colors["info"])
        
        # Create the auto-fading message
        st.markdown(f"""
        <div id="{message_id}" style="
            background-color: {bg_color};
            color: {text_color};
            padding: 0.75rem 1rem;
            border: 1px solid;
            border-radius: 0.375rem;
            margin: 0.5rem 0;
            transition: opacity 0.5s ease-out;
            opacity: 1;
        ">
            {message}
        </div>
        <script>
            setTimeout(function() {{
                var element = document.getElementById('{message_id}');
                if (element) {{
                    element.style.opacity = '0';
                    setTimeout(function() {{
                        if (element.parentNode) {{
                            element.parentNode.removeChild(element);
                        }}
                    }}, 500);
                }}
            }}, {fade_seconds * 1000});
        </script>
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
        """Render the search and analysis interface with bio.tools styling."""
        
        # Main content container
        st.markdown('<div class="main-content"><div class="content-container">', unsafe_allow_html=True)
        
        # Get total biotools count for display
        total_biotools = self.get_total_biotools_count()
        
        # Stats/Welcome section
        st.markdown(f"""
        <div class="stats-container">
            <div class="stats-title">Systematic Evaluation and Enhancement of bio.tools Annotation Quality</div>
            <p style="color: #666; margin-bottom: 1.5rem;">
                Real-time quality analysis for bioinformatics tools and services.<br>
                Analyze tool metadata completeness, standards compliance, and overall quality scores.
            </p>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-value">{total_biotools:,}</span>
                    <div class="stat-label">Tools Available</div>
                </div>
                <div class="stat-item">
                    <span class="stat-value">A-F</span>
                    <div class="stat-label">Quality Grades</div>
                </div>
                <div class="stat-item">
                    <span class="stat-value">1-5</span>
                    <div class="stat-label">Tier Levels</div>
                </div>
                <div class="stat-item">
                    <span class="stat-value">Real-time</span>
                    <div class="stat-label">API Analysis</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Direct search interface (no tabs)
        self.render_search_tools_interface()
        
        # Add analysis history under the search interface
        self.render_analysis_history()
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        return None
    
    def render_single_tool_interface(self):
        """Render single tool analysis interface in card style."""
        st.markdown("""
        <div class="tool-card">
            <h3 class="tool-title">Single Tool Analysis</h3>
            <p class="tool-description">Analyze a specific tool by its bio.tools ID to get comprehensive quality metrics and improvement recommendations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            tool_id = st.text_input(
                "Enter Bio.tools ID",
                placeholder="e.g., blast, clustalw, galaxy",
                help="Enter the exact bio.tools ID of the tool you want to analyze",
                label_visibility="visible"
            )
        
        with col2:
            st.write("")  # Space for alignment
            analyze_btn = st.button("🔍 Analyze Tool", disabled=not tool_id, use_container_width=True)
        
        if analyze_btn and tool_id:
            self.analyze_single_tool(tool_id)
    
    def render_search_tools_interface(self):
        """Render search tools interface with bio.tools-style search filters."""
        
        # Page introduction matching other tabs' card style
        st.markdown("""
        <div class="tool-card">
            <h3 class="tool-title">Search Tools Analysis</h3>
            <p class="tool-description">Search for multiple tools by keywords and analyze their quality metrics in batch. Use advanced filters to refine your search and compare tools across different categories.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main search input
        query = st.text_input(
            "Search Query",
            placeholder="Search for tools (e.g., alignment, genome, protein, blast)",
            help="Search for tools by name, description, or keywords"
        )
        
        # Search filters section
        st.subheader("Search filters:")
        
        # Filter checkboxes in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            search_name = st.checkbox("Name", value=True, disabled=True)
            search_description = st.checkbox("Description", value=True)
        
        with col2:
            search_topics = st.checkbox("Topics", value=True)
            search_operations = st.checkbox("Operations", value=True)
        
        with col3:
            search_types = st.checkbox("Data Types", value=False)
            search_formats = st.checkbox("Formats", value=False)
        
        with col4:
            search_publications = st.checkbox("Publications", value=False)
            search_collections = st.checkbox("Collections", value=False)
        
        # Search options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Quality filter
            quality_filter = st.selectbox(
                "Quality Filter",
                ["All Tools", "High Quality (A-B)", "Medium Quality (C)", "Low Quality (D-F)"],
                help="Filter tools by quality grade"
            )
        
        with col2:
            # Get total count dynamically for max_value
            total_biotools = self.get_total_biotools_count()
            
            max_tools = st.number_input(
                "Max Tools",
                min_value=1,
                max_value=total_biotools,
                value=10,
                help=f"Maximum number of tools to analyze (bio.tools has ~{total_biotools:,} tools)"
            )
            
            # Show performance warning for large numbers
            if max_tools > 100:
                st.warning(f"⚠️ Analyzing {max_tools} tools may take several minutes and consume significant resources.")
        
        with col3:
            st.write("")  # Space for alignment
            
            # Conditional button based on search state
            search_btn = False
            if st.session_state.search_active:
                stop_btn = st.button("🛑 Stop Search", use_container_width=True, type="secondary")
                if stop_btn:
                    st.session_state.search_cancelled = True
                    st.session_state.search_active = False
                    self.show_auto_fade_message("Search cancelled by user.", "info", 3)
                    st.rerun()
            else:
                search_btn = st.button("🔍 Search & Analyze", use_container_width=True)
        
        # Advanced search options in expander
        with st.expander("🔧 Advanced Search Options"):
            col1, col2, col3 = st.columns(3)
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
            
            with col3:
                tool_type = st.selectbox(
                    "Tool Type",
                    ["All", "Command-line tool", "Web application", "Desktop application", "Library", "Workflow"],
                    help="Filter by tool type"
                )
        
        if search_btn:
            # Set search as active and rerun to update UI
            st.session_state.search_active = True
            st.session_state.search_cancelled = False
            
            # Store search parameters for execution
            search_query = query if query else "*"
            st.session_state.search_params = {
                'query': search_query,
                'max_tools': max_tools,
                'sort_by': sort_by,
                'sort_order': sort_order,
                'quality_filter': quality_filter,
                'tool_type': tool_type if tool_type != "All" else None,
                'search_fields': {
                    'name': search_name,
                    'description': search_description,
                    'topics': search_topics,
                    'operations': search_operations,
                    'types': search_types,
                    'formats': search_formats,
                    'publications': search_publications,
                    'collections': search_collections
                }
            }
            st.rerun()
        
        # Execute search if active and not cancelled
        if st.session_state.search_active and not st.session_state.search_cancelled and 'search_params' in st.session_state:
            # Execute the search
            self.search_and_analyze_tools_enhanced(st.session_state.search_params)
            
            # Reset search state after completion - this will cause a rerun and show the normal button
            st.session_state.search_active = False
            st.session_state.search_cancelled = False
            if 'search_params' in st.session_state:
                del st.session_state.search_params
            
            # Trigger rerun to update button state
            st.rerun()
    
    def render_random_tools_interface(self):
        """Render random tools analysis interface in card style."""
        st.markdown("""
        <div class="tool-card">
            <h3 class="tool-title">Random Tools Analysis</h3>
            <p class="tool-description">Analyze a random sample of tools from bio.tools to get insights into overall registry quality and discover interesting tools.</p>
        </div>
        """, unsafe_allow_html=True)
        
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
            st.write("")  # Space for alignment
            random_btn = st.button("🎲 Analyze Random Tools", use_container_width=True)
        
        if random_btn:
            self.analyze_random_tools(num_tools)
    
    def render_collection_interface(self):
        """Render collection analysis interface in card style."""
        st.markdown("""
        <div class="tool-card">
            <h3 class="tool-title">Collection Analysis</h3>
            <p class="tool-description">Analyze tools from predefined collections or domains. Compare quality metrics across different tool categories and communities.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            collection_option = st.selectbox(
                "Collection Type",
                ["COVID-19 Tools", "Recent Tools", "Popular Tools", "Custom Collection"],
                help="Choose a predefined collection or create a custom one"
            )
        
        with col2:
            st.write("")  # Space for alignment
            collection_btn = st.button("📊 Analyze Collection", use_container_width=True)
        
        if collection_option == "Custom Collection":
            custom_ids = st.text_area(
                "Tool IDs (one per line)",
                placeholder="blast\nclustalw\ngalaxy",
                help="Enter bio.tools IDs, one per line"
            )
        
        if collection_btn:
            if collection_option == "COVID-19 Tools":
                # Use search for COVID-19 related tools
                self.search_and_analyze_tools("covid", 10, "lastUpdate", "desc")
            elif collection_option == "Recent Tools":
                # Use search for recent tools
                self.search_and_analyze_tools("*", 10, "lastUpdate", "desc")
            elif collection_option == "Popular Tools":
                # Use search for popular tools
                self.search_and_analyze_tools("*", 10, "score", "desc")
            # Add custom collection handling later

    def get_api_client(self):
        """Get or create API client with proper cache configuration."""
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
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour since total count doesn't change frequently
    def get_total_biotools_count(_self) -> int:
        """Get the total number of tools in bio.tools registry."""
        try:
            api_client = _self.get_api_client()
            
            # Make a direct request to bio.tools API to get the total count
            if hasattr(api_client, '_session'):
                from urllib.parse import urljoin
                
                url = urljoin("https://bio.tools/api/", "tool/")
                params = {'format': 'json', 'page': 1, 'page_size': 1}  # Minimal request
                
                try:
                    response = api_client._session.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if 'count' in data:
                            count = data['count']
                            logger.info(f"Retrieved total bio.tools count: {count}")
                            return count
                        else:
                            logger.warning("No count field in bio.tools API response")
                    else:
                        logger.warning(f"bio.tools API request failed: HTTP {response.status_code}")
                except Exception as e:
                    logger.debug(f"Direct API count request failed: {e}")
            
            # Fallback to known approximate count (as of September 2024)
            logger.info("Using fallback count estimate")
            return 30538
            
        except Exception as e:
            logger.warning(f"Could not fetch total bio.tools count: {e}")
            return 30538  # Fallback default
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_tool_data(_self, tool_id: str):
        """Fetch tool data from bio.tools API with caching."""
        try:
            api_client = _self.get_api_client()
            
            result = api_client.fetch_tool(tool_id)
            
            return result
        except Exception as e:
            st.error(f"Error fetching tool data for {tool_id}: {str(e)}")
            return None
    
    @st.cache_data(ttl=300)
    def search_tools(_self, query: str, max_tools: int = 10, sort_by: str = "lastUpdate", sort_order: str = "desc"):
        """Search for tools using bio.tools API with caching and pagination support."""
        try:
            api_client = _self.get_api_client()
            
            # If requesting a large number of tools or all tools, use fetch_all_tools
            # Note: bio.tools API page size is 50, so use pagination for requests > 50
            if max_tools > 50 or query == "*":
                logger.info(f"Large request detected ({max_tools} tools), using fetch_all_tools with pagination")
                
                if hasattr(api_client, 'fetch_all_tools'):
                    # Use the pagination method for large requests
                    all_tools = api_client.fetch_all_tools(batch_size=min(1000, max_tools))
                    
                    # Apply query filtering if needed (since fetch_all_tools gets everything)
                    if query and query != "*":
                        # Simple filtering - in a real implementation you'd want more sophisticated search
                        filtered_tools = []
                        query_lower = query.lower()
                        for tool in all_tools:
                            tool_text = f"{tool.get('name', '')} {tool.get('description', '')}".lower()
                            if query_lower in tool_text:
                                filtered_tools.append(tool)
                        all_tools = filtered_tools
                    
                    # Apply limit
                    if max_tools and len(all_tools) > max_tools:
                        all_tools = all_tools[:max_tools]
                    
                    logger.info(f"Retrieved {len(all_tools)} tools using pagination")
                    return all_tools
                else:
                    logger.warning("fetch_all_tools method not available, falling back to search_tools")
            
            # For smaller requests, use the regular search method
            all_tools = api_client.search_tools(
                query=query,
                limit=max_tools
            )
            
            return all_tools[:max_tools] if all_tools else []
            
        except Exception as e:
            st.error(f"Error searching tools: {str(e)}")
            logger.error(f"Error in search_tools: {e}")
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
    
    def search_and_analyze_tools_enhanced(self, search_params: dict):
        """Enhanced search for tools with advanced filtering options."""
        query = search_params['query']
        max_tools = search_params['max_tools']
        quality_filter = search_params['quality_filter']
        
        with st.spinner(f"Searching for tools matching '{query}' with advanced filters..."):
            tools = self.search_tools(query, max_tools, search_params['sort_by'], search_params['sort_order'])
            
            if not tools:
                st.warning("No tools found matching your search criteria.")
                return None
            
            # Use auto-fading success message
            self.show_auto_fade_message(f"Found {len(tools)} tools. Starting quality analysis...", "success", 5)
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            analyses = []
            for i, tool_data in enumerate(tools):
                # Check for cancellation
                if st.session_state.search_cancelled:
                    status_text.text("Search cancelled by user.")
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Return partial results if any were collected
                    if analyses:
                        st.session_state.analysis_results = analyses
                        st.session_state.current_analysis = None  # Clear single analysis to show bulk results
                        self.show_auto_fade_message(f"Search was cancelled. Showing partial results: {len(analyses)} tools analyzed out of {len(tools)} found.", "warning", 7)
                        return analyses
                    else:
                        self.show_auto_fade_message("Search was cancelled before any tools could be analyzed.", "warning", 5)
                        return None
                
                tool_id = tool_data.get('biotoolsID', f'tool_{i}')
                status_text.text(f"Analyzing {tool_id} ({i+1}/{len(tools)})")
                
                analysis = self.analyze_tool_quality(tool_data)
                if analysis:
                    # Apply quality filter if specified
                    if quality_filter != "All Tools":
                        grade = analysis.get('overall_grade', 'F')
                        if quality_filter == "High Quality (A-B)" and grade not in ['A', 'B']:
                            continue
                        elif quality_filter == "Medium Quality (C)" and grade != 'C':
                            continue
                        elif quality_filter == "Low Quality (D-F)" and grade not in ['D', 'F']:
                            continue
                    
                    analyses.append(analysis)
                
                progress_bar.progress((i + 1) / len(tools))
                time.sleep(0.1)  # Small delay to show progress
            
            status_text.text("Analysis complete!")
            progress_bar.empty()
            status_text.empty()
            
            if analyses:
                st.session_state.analysis_results = analyses
                st.session_state.current_analysis = None  # Clear single analysis to show bulk results
                
                # Show filtered results summary with auto-fade
                self.show_auto_fade_message(f"Applied filters: {quality_filter}. Showing {len(analyses)} tools from {len(tools)} total results.", "info", 5)
            
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
            # Use search_tools with domain filter as approximation for collection search
            tools = api_client.search_tools(
                domain=collection_id,  # Use collection_id as domain filter
                limit=max_tools
            )
            
            # Extract tools from API response
            total_count = len(tools) if tools else 0
            
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
                    full_tool = api_client.fetch_tool(tool['biotoolsID'])
                    
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
                # Map tier names to numbers for CSS classes
                tier_map = {1: 'SPARSE', 2: 'MINIMAL', 3: 'DETAILED', 4: 'COMPLETE', 5: 'COMPREHENSIVE'}
                
                if tier != 'N/A':
                    # Handle different tier formats (e.g., "Tier 3", "3", "DETAILED", etc.)
                    if isinstance(tier, (int, float)):
                        tier_num = int(tier)
                        tier_display = tier_map.get(tier_num, 'SPARSE')
                    elif isinstance(tier, str) and tier.isdigit():
                        tier_num = int(tier)
                        tier_display = tier_map.get(tier_num, 'SPARSE')
                    elif isinstance(tier, str) and 'tier' in tier.lower():
                        # Extract number from "Tier X" format
                        parts = tier.split()
                        tier_num = int(parts[-1]) if parts[-1].isdigit() else 1
                        tier_display = tier_map.get(tier_num, 'SPARSE')
                    else:
                        # Map enum names to numbers using the tier_map by creating a reverse mapping
                        # tier_map is defined as {1: 'SPARSE', 2: 'MINIMAL', ...}
                        tier_name_to_num = {v.upper(): k for k, v in tier_map.items()}
                        if isinstance(tier, str):
                            tier_num = tier_name_to_num.get(tier.upper(), 1)
                            tier_display = tier.upper()
                        else:
                            tier_num = 1
                            tier_display = 'SPARSE'
                else:
                    tier_num = 1
                    tier_display = 'N/A'
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Standards Tier</h4>
                    <div class="standard-badge tier-{tier_num}">{tier_display}</div>
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
                
                for section in tier_sections:
                    for line in section:
                        if "**📈" in line:
                            st.markdown(line, unsafe_allow_html=True)
                        else:
                            st.markdown(line, unsafe_allow_html=True)
                    st.markdown("")  # Add spacing between tiers
            
            # Display critical issues
            if critical_issues:
                st.markdown("### 🚨 Critical Issues")
                st.error("These issues should be addressed first as they significantly impact tool quality:")
                for issue in critical_issues:
                    if issue.strip():
                        st.markdown(issue, unsafe_allow_html=True)
            
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
                st.subheader("Missing Fields to Reach Maximum Tier")
                
                # Calculate missing fields for each tool to reach COMPREHENSIVE tier
                tool_missing_data = []
                for analysis in analyses:
                    if analysis and analysis.get('report') and hasattr(analysis['report'], 'metrics'):
                        metrics = analysis['report'].metrics
                        tool_name = analysis.get('tool_name', 'Unknown')[:15] + ('...' if len(analysis.get('tool_name', '')) > 15 else '')
                        
                        # Get field completeness (0.0 to 1.0)
                        field_completeness = getattr(metrics, 'field_completeness', 0)
                        
                        # Estimate missing fields based on completeness
                        # Assuming maximum tier requires ~100% completeness across ~20 key fields
                        total_fields = 20  # Approximate number of key fields for COMPREHENSIVE tier
                        missing_fields = int(total_fields * (1 - field_completeness))
                        
                        tool_missing_data.append({
                            'Tool': tool_name,
                            'Missing Fields': missing_fields,
                            'Completeness': f"{field_completeness:.1%}"
                        })
                
                if tool_missing_data:
                    # Sort by missing fields (descending) to show tools that need most work first
                    tool_missing_data.sort(key=lambda x: x['Missing Fields'], reverse=True)
                    
                    # Create horizontal bar chart
                    df_missing = pd.DataFrame(tool_missing_data)
                    
                    fig = px.bar(
                        df_missing, 
                        x='Missing Fields', 
                        y='Tool',
                        orientation='h',
                        title="Fields Missing for Maximum Tier (COMPREHENSIVE)",
                        labels={'Missing Fields': 'Number of Missing Fields', 'Tool': 'Bio Tools'},
                        color='Missing Fields',
                        color_continuous_scale='Reds',
                        text='Completeness'
                    )
                    
                    fig.update_layout(
                        height=max(400, len(tool_missing_data) * 25),  # Dynamic height
                        yaxis={'categoryorder': 'total ascending'},  # Order by missing fields
                        showlegend=False
                    )
                    
                    fig.update_traces(textposition='outside')
                    
                    st.plotly_chart(fig, width='stretch', key=f"bulk_missing_fields_chart_{uuid.uuid4().hex[:8]}")
                else:
                    st.info("No completeness data available for visualization.")
            
            with col2:
                st.subheader("Standards Tier Distribution")
                # Clean tier data for better visualization
                tier_names = []
                tier_map = {1: 'SPARSE', 2: 'MINIMAL', 3: 'DETAILED', 4: 'COMPLETE', 5: 'COMPREHENSIVE'}
                
                for tier in tiers:
                    if isinstance(tier, (int, float)):
                        tier_names.append(tier_map.get(int(tier), 'SPARSE'))
                    elif isinstance(tier, str) and tier.isdigit():
                        tier_names.append(tier_map.get(int(tier), 'SPARSE'))
                    elif isinstance(tier, str) and 'tier' in tier.lower():
                        # Extract number from "Tier X" format
                        parts = tier.split()
                        tier_num = int(parts[-1]) if parts[-1].isdigit() else 1
                        tier_names.append(tier_map.get(tier_num, 'SPARSE'))
                    else:
                        # Already a tier name or unknown format
                        tier_names.append(tier.upper() if isinstance(tier, str) else 'SPARSE')
                
                tier_counts = pd.Series(tier_names).value_counts()
                fig = px.pie(values=tier_counts.values, names=tier_counts.index, 
                           title="Standards Tiers")
                st.plotly_chart(fig, width='stretch', key=f"bulk_tier_distribution_pie_{uuid.uuid4().hex[:8]}")
        
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
            valid_analyses = [a for a in analyses if a and a.get('report')]
            valid_reports = [a['report'] for a in valid_analyses if a.get('report')]
            
            if valid_reports:
                col1, col2, col3 = st.columns(3)
                if reporter:
                    with col1:
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
                    
                    with col2:
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
                    
                    with col3:
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
                
            else:
                st.info("No valid analyses available for detailed export.")
            
            # Individual file downloads section
            st.markdown("### 📁 Individual Tool Files")
            
            if valid_analyses:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📄 Raw Tool Data (Individual JSON files)**")
                    
                    # Create a ZIP file with individual raw tool files
                    if st.button("🗂️ Prepare Individual Raw Files", key="prepare_raw_files"):
                        with st.spinner("Preparing individual raw tool files..."):
                            try:
                                # Import the API client
                                from src.collectors.async_biotools_api import UnifiedBioToolsAPIClient
                                import zipfile
                                import io
                                
                                # Prepare raw tool data
                                raw_tools_data = []
                                for analysis in valid_analyses:
                                    if analysis.get('raw_data'):
                                        raw_tools_data.append(analysis['raw_data'])
                                
                                if raw_tools_data:
                                    # Create ZIP file in memory
                                    zip_buffer = io.BytesIO()
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    
                                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                        for tool_data in raw_tools_data:
                                            tool_id = tool_data.get('biotoolsID', 'unknown')
                                            tool_name = tool_data.get('name', tool_id)
                                            
                                            # Create filename from tool name or tool_id
                                            display_name = tool_name if tool_name and tool_name != tool_id else tool_id
                                            
                                            # Clean name for filename
                                            safe_name = "".join(c for c in display_name if c.isalnum() or c in ('_', '-', '.', ' ')).strip()
                                            safe_name = safe_name.replace(' ', '_')
                                            
                                            if not safe_name:
                                                safe_name = "".join(c for c in tool_id if c.isalnum() or c in ('_', '-', '.')).rstrip()
                                            
                                            filename = f"{safe_name}.json"
                                            
                                            # Add to ZIP
                                            zip_file.writestr(filename, json.dumps(tool_data, indent=2, ensure_ascii=False))
                                    
                                    zip_buffer.seek(0)
                                    
                                    # Provide download button
                                    st.download_button(
                                        label="💾 Download Raw Files ZIP",
                                        data=zip_buffer.getvalue(),
                                        file_name=f"biotools_raw_files_{timestamp}.zip",
                                        mime="application/zip",
                                        key=f"download_raw_zip_{uuid.uuid4().hex[:8]}"
                                    )
                                    
                                    st.success(f"✅ Prepared {len(raw_tools_data)} individual raw tool files")
                                else:
                                    st.warning("No raw tool data available")
                                    
                            except Exception as e:
                                st.error(f"Error preparing raw files: {str(e)}")
                
                with col2:
                    st.markdown("**📊 Processed Analysis Data (Individual JSON files)**")
                    
                    # Create a ZIP file with individual analysis files
                    if st.button("🗂️ Prepare Individual Analysis Files", key="prepare_analysis_files"):
                        with st.spinner("Preparing individual analysis files..."):
                            try:
                                import zipfile
                                import io
                                
                                if valid_reports:
                                    # Create ZIP file in memory
                                    zip_buffer = io.BytesIO()
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    
                                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                        for report in valid_reports:
                                            tool_id = report.tool_id
                                            tool_name = report.tool_name
                                            
                                            # Create filename from tool name or tool_id
                                            display_name = tool_name if tool_name and tool_name != tool_id else tool_id
                                            
                                            # Clean name for filename
                                            safe_name = "".join(c for c in display_name if c.isalnum() or c in ('_', '-', '.', ' ')).strip()
                                            safe_name = safe_name.replace(' ', '_')
                                            
                                            if not safe_name:
                                                safe_name = "".join(c for c in tool_id if c.isalnum() or c in ('_', '-', '.')).rstrip()
                                            
                                            filename = f"{safe_name}.json"
                                            
                                            # Add to ZIP
                                            zip_file.writestr(filename, json.dumps(report.to_dict(), indent=2, ensure_ascii=False, default=str))
                                    
                                    zip_buffer.seek(0)
                                    
                                    # Provide download button
                                    st.download_button(
                                        label="💾 Download Analysis Files ZIP",
                                        data=zip_buffer.getvalue(),
                                        file_name=f"biotools_analysis_files_{timestamp}.zip",
                                        mime="application/zip",
                                        key=f"download_analysis_zip_{uuid.uuid4().hex[:8]}"
                                    )
                                    
                                    st.success(f"✅ Prepared {len(valid_reports)} individual analysis files")
                                else:
                                    st.warning("No analysis reports available")
                                    
                            except Exception as e:
                                st.error(f"Error preparing analysis files: {str(e)}")
            else:
                st.info("No tools available for individual file downloads.")
        
        # Individual tool details
        st.subheader("🔍 Individual Tool Details")
        tool_options = [f"{a['tool_id']} - {a['tool_name']}" for a in analyses if a]
        
        if tool_options:
            # Use a more stable key for the selectbox
            selected_tool = st.selectbox(
                "Select a tool to view details:", 
                tool_options, 
                index=0,
                key="bulk_tool_selectbox"
            )
            
            if selected_tool:
                tool_id = selected_tool.split(' - ')[0]
                selected_analysis = next((a for a in analyses if a and a['tool_id'] == tool_id), None)
                
                if selected_analysis:
                    st.markdown("---")  # Add separator
                    self.display_single_tool_results(selected_analysis)
                else:
                    st.error(f"Could not find analysis for tool ID: {tool_id}")
        else:
            st.info("No tools available for individual analysis.")
    
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
        """Render analysis history under the search interface."""
        if st.session_state.analysis_history:
            st.markdown("""
            <div class="history-section">
                <div class="history-title">📚 Recent Analysis History</div>
                <div class="history-description">Click on any tool to view its previous analysis results</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display recent analyses in a more compact format
            history_items = list(reversed(st.session_state.analysis_history[-10:]))  # Show last 10
            
            # Create columns for better layout
            cols = st.columns(min(5, len(history_items)))  # Max 5 columns
            
            for i, analysis in enumerate(history_items):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    tool_name = analysis['tool_name'][:25] + ('...' if len(analysis['tool_name']) > 25 else '')
                    if st.button(
                        f"🔍 {tool_name}", 
                        key=f"history_{i}",
                        help=f"View analysis for {analysis['tool_name']}",
                        use_container_width=True
                    ):
                        st.session_state.current_analysis = analysis
                        st.rerun()  # Refresh to show the selected analysis
    
    def run(self):
        """Run the Streamlit application."""
        self.render_system_warnings()
        
        # Main content area
        if not MODULES_AVAILABLE:
            st.error("Required analysis modules are not available. Please check your installation.")
            return
        
        # Main interface
        analysis_result = self.render_search_interface()
        
        # Display current analysis results
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
