# Bio.tools Live Quality Analyzer

A **Streamlit web application** for real-time analysis of bio.tools registry entries. This tool evaluates metadata quality, performs schema validation, and provides comprehensive quality scoring for bioinformatics tools.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Internet connection (for bio.tools API access)

### Installation
```bash
git clone <repository-url>
cd bio.tools-annotation-quality-evaluation
pip install -r requirements.txt
```

### Launch the Application
**Option 1: Using Python**
```bash
python run_app.py
```

**Option 2: Using Launcher Scripts**
- Windows: Double-click `launch.bat`
- PowerShell: `.\launch.ps1`

The application will open in your default web browser at `http://localhost:8501`

## 🎯 Features

### Analysis Modes
- **Single Tool Analysis**: Analyze specific tools by bio.tools ID
- **Search & Analyze**: Search for tools and analyze multiple results
- **Random Tool Analysis**: Discover and analyze random tools
- **Collection Analysis**: Analyze tools from specific bio.tools collections

### Quality Metrics
- **Overall Grade**: A-F scoring based on comprehensive analysis
- **Standards Tier**: Compliance with Tool Information Standards (Tier 1-5)
- **Schema Validation**: Structural validation against biotoolsSchema
- **Lint Analysis**: Issues and recommendations for improvement
- **Completeness Score**: Percentage of required/recommended fields filled
- **Content Quality**: URL health, EDAM term consistency, documentation quality

### Interactive Visualizations
- **Radar Charts**: Multi-dimensional quality visualization
- **Progress Bars**: Quick quality metric overview
- **Data Tables**: Detailed results with filtering and sorting
- **Download Options**: Export results as JSON or CSV

## 🔧 Technical Architecture

### Core Components
```
app.py                    # Main Streamlit application
src/
├── collectors/
│   └── biotools_api.py  # Bio.tools API client
├── analyzers/
│   ├── quality_analyzer.py  # Quality scoring orchestration
│   └── linter.py        # Linting integration
├── validators/
│   ├── schema_validator.py    # Schema validation
│   ├── standards_scorer.py    # Standards compliance
│   └── completeness_scorer.py # Completeness metrics
└── utils/
    ├── logger.py        # Logging configuration
    └── data_cleaner.py  # Data preprocessing
```

### Data Flow
1. **API Request**: Fetch tool data from bio.tools API
2. **Preprocessing**: Clean and normalize data
3. **Validation**: Schema validation against biotoolsSchema
4. **Scoring**: Calculate quality metrics and grades
5. **Linting**: Analyze with biotools-linter for issues
6. **Visualization**: Generate interactive charts and reports

## 📊 Quality Scoring System

### Grading Scale
- **A (90-100%)**: Excellent - Comprehensive, high-quality annotation
- **B (80-89%)**: Good - Well-annotated with minor gaps
- **C (70-79%)**: Satisfactory - Adequate annotation, some improvements needed
- **D (60-69%)**: Needs Improvement - Basic annotation, missing key information
- **F (<60%)**: Poor - Significant gaps in annotation

### Standards Tiers (ELIXIR Tool Information Standards)
- **Tier 1**: Minimal viable annotation
- **Tier 2**: Basic descriptive information
- **Tier 3**: Comprehensive metadata
- **Tier 4**: Enhanced discoverability
- **Tier 5**: Exemplary annotation with all optional fields

## 🧪 Testing

Run API connectivity tests:
```bash
python test_api.py
```

Run unit tests:
```bash
pytest tests/
```

## 📁 Project Structure

### Essential Files
- `app.py` - Main Streamlit application
- `run_app.py` - Application launcher
- `test_api.py` - API connectivity testing
- `requirements.txt` - Python dependencies

### Data Directories
- `data/cache/` - Cached API responses for faster repeated access
- `logs/` - Application logs
- `docs/` - Technical documentation

### External Components
- `biotools-linter/` - Integrated linter for metadata validation
- `EDAM.csv`, `EDAM.owl` - EDAM ontology files for term validation

## 🔗 External Dependencies

- **bio.tools API**: Live registry data from https://bio.tools/api/
- **biotoolsSchema**: JSON schema validation
- **biotools-linter**: Metadata quality checking
- **EDAM Ontology**: Bioinformatics ontology for term validation

## 🛠️ Development

### Environment Setup
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\Activate.ps1
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### Key Technologies
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **Requests**: HTTP API client
- **JSONSchema**: Data validation

## 📝 License

This project is licensed under the terms specified in the LICENSE file.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📞 Support

For questions or support, please refer to the documentation in the `docs/` directory or open an issue on the project repository.
