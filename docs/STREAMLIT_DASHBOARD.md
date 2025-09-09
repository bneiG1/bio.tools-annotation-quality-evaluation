# Streamlit Web Dashboard for Bio.tools Quality Analysis

## Overview

This project now includes a comprehensive Streamlit-based web dashboard that provides an interactive interface for exploring bio.tools annotation quality analysis results. The dashboard replaces static HTML reports with a dynamic, real-time web application.

## Features

### 🔬 Interactive Web Interface
- **Modern UI**: Clean, responsive design optimized for bioinformatics data analysis
- **Real-time Filtering**: Filter tools by quality grade, tier, score ranges, and validation status
- **Interactive Charts**: Plotly-powered visualizations with zoom, pan, and hover capabilities
- **Multi-format Export**: Download results as JSON, CSV, or generate HTML reports

### 📊 Comprehensive Visualizations
- **Quality Overview**: Key metrics dashboard with statistics cards
- **Grade Distribution**: Pie charts and bar graphs showing quality grade distribution (A-F)
- **Tier Analysis**: Standards tier distribution (Tier 1-5) with color-coded visualization
- **Content Quality**: Analysis of function presence, documentation, publications, and contacts
- **Score Correlations**: Scatter plots showing relationships between different quality metrics

### 🔍 Detailed Analysis Tools
- **Tools Browser**: Searchable, sortable table with advanced filtering options
- **Individual Tool Analysis**: Deep-dive view for each tool with gauge charts and metrics breakdown
- **Quality Trends**: Distribution analysis and correlation studies
- **Validation Reports**: Schema validation status and linting issue analysis

## Getting Started

### Prerequisites

1. **Python 3.8+** with pip
2. **Required packages** (install with pip):
   ```bash
   pip install -r requirements.txt
   ```

### Installation

1. **Install Dependencies**:
   ```powershell
   pip install streamlit streamlit-aggrid plotly pandas matplotlib seaborn
   ```

2. **Launch Dashboard**:
   ```powershell
   # Option 1: Using the launcher script
   .\start_dashboard.bat
   
   # Option 2: Direct launch
   python launch_dashboard.py
   
   # Option 3: Streamlit command
   streamlit run streamlit_app.py
   ```

3. **Access Dashboard**:
   - Open your web browser to `http://localhost:8501`
   - The dashboard will automatically open in your default browser

## Usage Guide

### Data Sources

The dashboard supports multiple data input methods:

1. **Sample Data**: 
   - Generate synthetic bio.tools data for demonstration
   - Configurable number of tools (10-500)
   - Realistic quality metrics and distributions

2. **File Upload**:
   - Upload JSON files with analysis results
   - Supports multiple JSON formats:
     - Dashboard export format (`{tools: [], statistics: {}, config: {}}`)
     - Direct tool arrays (`[{tool1}, {tool2}, ...]`)
     - Analysis results format (`{results: [], statistics: {}}`)

3. **Cached Data**:
   - Load previously saved analysis results from `data/temp_dashboard_data.json`
   - Automatically generated when running integrated analysis pipelines

### Dashboard Sections

#### 📊 Overview Tab
- **Key Metrics**: Total tools, average scores, validation statistics
- **Quality Distribution**: Interactive charts showing grade and tier distributions
- **Content Analysis**: Metrics for documentation, publications, and metadata completeness

#### 🔍 Tools Browser Tab
- **Interactive Table**: All tools with sortable columns and progress bars
- **Advanced Filters**: Filter by grade, tier, score ranges, and issue counts
- **Quick Actions**: Direct links to individual tool analysis

#### 📈 Quality Analysis Tab
- **Score Distributions**: Histograms for overall and completeness scores
- **Grade Analysis**: Box plots showing score distributions by quality grade
- **Correlation Studies**: Field completeness vs overall score relationships
- **Validation Analysis**: Schema validation and linting issue distributions

#### 🔍 Tool Details Tab
- **Individual Analysis**: Deep-dive view for any selected tool
- **Quality Gauge**: Visual quality score representation
- **Metrics Breakdown**: Detailed scoring across all quality dimensions
- **Recommendations**: Actionable suggestions for quality improvement

#### 📋 Export & Reports Tab
- **JSON Export**: Complete analysis data in structured format
- **CSV Export**: Tabular data for external analysis tools
- **Statistics View**: Raw statistics in JSON format

### Data Format

#### Tool Data Structure
```json
{
  "tool_id": "blast",
  "tool_name": "BLAST",
  "metrics": {
    "overall_score": 85.5,
    "quality_grade": "B",
    "standards_tier": "Tier 4",
    "completeness_score": 82.0,
    "standards_score": 78.5,
    "schema_valid": true,
    "schema_errors": 0,
    "schema_warnings": 1,
    "lint_issues": 2,
    "field_completeness": 0.75,
    "has_functions": true,
    "has_documentation": true,
    "has_publications": true,
    "url_health": 0.95,
    "edam_consistency": 0.88
  },
  "summary": "High-quality tool with comprehensive metadata",
  "recommendations": [
    "Add missing EDAM terms",
    "Update documentation links"
  ]
}
```

#### Statistics Structure
```json
{
  "total_tools": 1500,
  "average_score": 67.2,
  "grade_distribution": {
    "A": 125, "B": 320, "C": 450, "D": 385, "F": 220
  },
  "tier_distribution": {
    "Tier 1": 180, "Tier 2": 290, "Tier 3": 385, "Tier 4": 425, "Tier 5": 220
  },
  "validation_stats": {
    "valid": 1245,
    "with_errors": 185,
    "with_warnings": 70
  },
  "content_stats": {
    "with_functions": 1320,
    "with_documentation": 890,
    "with_publications": 756,
    "with_contacts": 1120
  }
}
```

## Integration with Existing Pipeline

### Programmatic Launch
```python
from src.visualization.streamlit_integration import run_streamlit_dashboard

# Your analysis results
tools_data = [...]  # List of tool analysis results
statistics = {...}  # Analysis statistics
config = {...}      # Configuration

# Launch dashboard
run_streamlit_dashboard(tools_data, statistics, config)
```

### Command Line Integration
```bash
# Run analysis and launch dashboard
python main.py analyze --launch-dashboard

# Launch dashboard with existing results
python main.py dashboard --results-file data/processed/results.json
```

## Configuration

### Streamlit Configuration
The dashboard uses `.streamlit/config.toml` for customization:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
headless = false
```

### Custom Styling
The dashboard includes custom CSS for:
- Bio.tools branding colors
- Quality grade color coding
- Responsive layout design
- Professional card layouts

## Performance Considerations

### Large Datasets
- **Pagination**: Built-in Streamlit pagination for large tool lists
- **Lazy Loading**: Charts and visualizations load on-demand
- **Filtering**: Client-side filtering for responsive interaction
- **Caching**: Automatic caching of expensive computations

### Memory Usage
- **Data Streaming**: Large datasets can be loaded incrementally
- **Selective Display**: Only render visible components
- **Export Optimization**: Large exports handled efficiently

## Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment
```bash
# Using Streamlit Cloud
streamlit run streamlit_app.py --server.headless true

# Using Docker
docker run -p 8501:8501 biotools-dashboard

# Using reverse proxy (nginx)
proxy_pass http://localhost:8501;
```

### Cloud Deployment
- **Streamlit Cloud**: Direct GitHub integration
- **Heroku**: Web dyno deployment
- **AWS/GCP**: Container or serverless deployment
- **Docker**: Containerized deployment

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Data Loading Errors**:
   - Check JSON format compliance
   - Verify file permissions
   - Review error messages in browser console

4. **Performance Issues**:
   - Reduce dataset size for testing
   - Use filtering to limit displayed data
   - Check system memory usage

### Debug Mode
```bash
# Enable debug logging
streamlit run streamlit_app.py --logger.level debug

# Check system status
streamlit --help
```

## Contributing

### Adding New Visualizations
1. Create new render method in `StreamlitDashboard` class
2. Add to appropriate tab in `run()` method
3. Test with sample data
4. Update documentation

### Custom Metrics
1. Extend tool data structure
2. Update statistics calculation
3. Add visualization components
4. Include in export formats

## Future Enhancements

### Planned Features
- **Real-time API Integration**: Live data from bio.tools API
- **User Authentication**: Multi-user dashboard with saved sessions
- **Advanced Analytics**: Machine learning insights and predictions
- **Report Scheduling**: Automated report generation and distribution
- **Custom Dashboards**: User-configurable dashboard layouts

### Extension Points
- **Plugin Architecture**: Custom analysis modules
- **Theme System**: Multiple visual themes
- **Export Formats**: Additional export options (PDF, PowerBI)
- **Mobile Optimization**: Enhanced mobile interface

---

## Support

For issues, questions, or contributions:
1. Check existing documentation
2. Search GitHub issues
3. Create new issue with reproduction steps
4. Include system information and error logs

The Streamlit dashboard provides a modern, interactive alternative to static HTML reports while maintaining all the analytical power of the bio.tools quality evaluation system.
