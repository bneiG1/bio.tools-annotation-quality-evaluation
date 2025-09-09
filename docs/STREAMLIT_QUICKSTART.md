# Bio.tools Quality Dashboard - Quick Start Guide

## 🚀 Getting Started with Streamlit Dashboard

### Installation

1. **Install Dependencies**:
   ```bash
   pip install streamlit streamlit-aggrid plotly pandas matplotlib seaborn
   ```

2. **Launch Dashboard**:
   ```bash
   # Quick demo (recommended for first time)
   python dashboard.py --demo
   
   # Custom sample data
   python dashboard.py --sample --count 200
   
   # Load from existing file
   python dashboard.py --file your_data.json
   
   # Windows PowerShell launcher
   .\launch_dashboard.ps1
   ```

### Dashboard Features

- **📊 Interactive Overview**: Key metrics, quality distributions, content analysis
- **🔍 Tools Browser**: Searchable table with advanced filtering
- **📈 Quality Analysis**: Score distributions, correlations, validation reports
- **🔍 Tool Details**: Individual tool deep-dive with recommendations
- **📋 Export & Reports**: Download JSON, CSV, view statistics

### Data Sources

1. **Sample Data**: Generated synthetic bio.tools data for demonstration
2. **File Upload**: Upload JSON files with analysis results via web interface
3. **Cached Data**: Load previously saved analysis results

### Web Interface

Once launched, open your browser to:
- **URL**: http://localhost:8501
- **Mobile-friendly**: Responsive design works on tablets and phones
- **Real-time**: Interactive charts with zoom, filter, and export capabilities

### Example Usage

```bash
# Generate 500 sample tools and launch dashboard
python dashboard.py --sample --count 500

# Load your own analysis results
python dashboard.py --file data/processed/analysis_results.json

# Quick demo with default settings
python dashboard.py --demo
```

### Integration with Existing Pipeline

The dashboard can be integrated with your existing bio.tools analysis pipeline:

```python
from src.visualization.streamlit_integration import run_streamlit_dashboard

# Your analysis results
tools_data = [...]  # List of tool analysis results
statistics = {...}  # Analysis statistics
config = {...}      # Configuration

# Launch dashboard
run_streamlit_dashboard(tools_data, statistics, config)
```

### Troubleshooting

- **Port in use**: Change port with `--port 8502`
- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Data format errors**: Check JSON structure matches expected format

---

For detailed documentation, see `docs/STREAMLIT_DASHBOARD.md`
