# Bio.tools Annotation Quality Evaluation Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://biotools-annotation-quality-evaluation.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive **bioinformatics data analysis platform** for evaluating metadata quality in the [ELIXIR bio.tools registry](https://bio.tools). This Streamlit web application provides real-time analysis of tool annotations, schema validation, and quality scoring to help improve bioinformatics tool discoverability and metadata standards.

## 🌟 Live Demo

**[Launch Application](https://biotools-annotation-quality-evaluation.streamlit.app)** - Try the live deployment

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Recommended: 3.9-3.11)
- **Internet connection** (for bio.tools API access)
- **4GB RAM minimum** (8GB recommended for large-scale analysis)

### Installation Options

#### Option 1: Direct Installation
```powershell
# Clone the repository
git clone https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
cd bio.tools-annotation-quality-evaluation

# Create virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### Option 2: Development Setup
```powershell
# Clone with submodules (includes biotools-linter)
git clone --recursive https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
cd bio.tools-annotation-quality-evaluation

# Setup development environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

### Launch Application

#### Method 1: Python Script
```powershell
python app.py
```

#### Method 2: Streamlit Command
```powershell
streamlit run app.py
```

#### Method 3: Convenience Scripts
- **Cross-platform**: `python run_app.py`

## 🎯 Features

### 🔍 Analysis Modes

- **Single Tool Analysis**: Deep-dive quality assessment for specific bio.tools entries
- **Search & Analyze**: Search the registry and analyze multiple tools simultaneously  
- **Random Tool Discovery**: Explore random tools to assess overall registry quality
- **Collection Analysis**: Batch analysis of tool collections and domains
- **Comparative Analysis**: Side-by-side comparison of multiple tools

### 📊 Quality Metrics

- **Overall Quality Grade**: A-F scoring based on comprehensive metadata analysis
- **Standards Tier Compliance**: ELIXIR Tool Information Standards (Tier 1-5) assessment
- **Schema Validation**: Structural validation against biotoolsSchema
- **Linting Analysis**: Automated detection of metadata issues and improvement suggestions
- **Completeness Scoring**: Percentage-based assessment of required/recommended field coverage
- **Content Quality Assessment**: URL health checks, EDAM term validation, documentation quality

### 📈 Interactive Visualizations

- **Multi-dimensional Radar Charts**: Comprehensive quality visualization across all metrics
- **Progress Indicators**: Quick visual overview of quality scores and compliance
- **Interactive Data Tables**: Sortable, filterable results with export capabilities
- **Distribution Charts**: Quality distribution across tool collections
- **Trend Analysis**: Quality patterns and insights

### 🔧 Data Export & Integration

- **JSON Export**: Complete analysis results with metadata
- **CSV Reports**: Tabular data for spreadsheet analysis
- **API Integration**: Programmatic access to quality metrics
- **Caching System**: Optimized performance with intelligent data caching

## 🏗️ Architecture & Technical Design

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Streamlit)                │
├─────────────────────────────────────────────────────────────┤
│                     Analysis Engine                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │  Collectors │ │ Validators  │ │       Analyzers         │ │
│  │             │ │             │ │                         │ │
│  │ • bio.tools │ │ • Schema    │ │ • Quality Scoring       │ │
│  │   API       │ │ • Standards │ │ • Linting Integration   │ │
│  │ • Caching   │ │ • Complete- │ │ • Report Generation     │ │
│  │ • Search    │ │   ness      │ │ • Recommendations       │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │    Cache    │ │    Logs     │ │       Reports           │ │
│  │             │ │             │ │                         │ │
│  │ • API       │ │ • Analysis  │ │ • JSON/CSV Export       │ │
│  │   Responses │ │ • Errors    │ │ • Visualizations        │ │
│  │ • Search    │ │ • Usage     │ │ • Quality Metrics       │ │
│  │   Results   │ │ • Debug     │ │ • Recommendations       │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

```
bio.tools-annotation-quality-evaluation/
├── 📱 app.py                          # Main Streamlit application
├── 🚀 run_app.py                      # Application launcher
├── 🧪 test_api.py                     # API connectivity testing
├── 📋 requirements.txt                # Python dependencies
├── ⚙️ .streamlit/                     # Streamlit configuration
│   └── config.toml
├── 📦 src/                            # Core analysis modules
│   ├── 🔌 collectors/                 # Data collection
│   │   ├── __init__.py
│   │   └── biotools_api.py           # bio.tools API client
│   ├── ✅ validators/                 # Validation & scoring
│   │   ├── __init__.py
│   │   ├── schema_validator.py       # biotoolsSchema validation
│   │   ├── standards_scorer.py       # ELIXIR standards compliance
│   │   └── completeness_scorer.py    # Field completeness scoring
│   ├── 🔍 analyzers/                 # Analysis engines
│   │   ├── __init__.py
│   │   ├── quality_analyzer.py       # Main analysis orchestration
│   │   └── linter.py                 # biotools-linter integration
│   ├── 📊 reporters/                 # Report generation
│   │   ├── __init__.py
│   │   └── quality_reporter.py       # Visualization & export
│   └── 🛠️ utils/                      # Utility modules
│       ├── __init__.py
│       ├── logger.py                 # Logging configuration
│       └── data_cleaner.py           # Data preprocessing
├── 💾 data/                          # Data storage
│   ├── cache/                        # API response cache
│   ├── processed/                    # Analysis results
│   └── reports/                      # Generated reports
├── 📜 logs/                          # Application logs
├── 📖 docs/                          # Documentation
│   ├── api/                          # API documentation
│   ├── user-guide/                   # User documentation
│   ├── developer/                    # Development documentation
│   └── examples/                     # Usage examples
├── 🧪 tests/                         # Test suite
├── 🔧 biotools-linter/               # Integrated linter (submodule)
└── 📄 EDAM.csv, EDAM.owl             # EDAM ontology files
```


## 📊 Quality Assessment Framework

### Scoring Methodology

#### Overall Quality Grade (A-F Scale)

- **A (90-100%)**: Exemplary annotation with comprehensive metadata
- **B (80-89%)**: High-quality annotation with minor gaps
- **C (70-79%)**: Good annotation with some missing elements
- **D (60-69%)**: Adequate annotation requiring improvement
- **F (<60%)**: Poor annotation with significant gaps

#### ELIXIR Tool Information Standards Tiers

- **Tier 1 (Essential)**: Minimal viable tool description
- **Tier 2 (Useful)**: Basic searchable information
- **Tier 3 (Better)**: Enhanced discoverability
- **Tier 4 (Excellent)**: Comprehensive tool documentation
- **Tier 5 (Exemplary)**: Gold standard annotation

#### Assessment Criteria

1. **Metadata Completeness**: Coverage of required and recommended fields
2. **Schema Compliance**: Adherence to biotoolsSchema structure
3. **Content Quality**: Accuracy and usefulness of descriptions
4. **Link Validity**: Accessibility of tool and documentation URLs
5. **EDAM Compliance**: Proper use of bioinformatics ontology terms
6. **Documentation Quality**: Completeness of help and tutorial materials

## 🔗 External Dependencies & APIs

### Core Dependencies

- **[bio.tools API](https://bio.tools/api/)**: Live registry data (Rate limit: ~1000 requests/hour)
- **[biotoolsSchema](https://github.com/bio-tools/biotoolsschema)**: JSON schema for validation
- **[biotools-linter](https://github.com/3top1a/biotools-linter)**: Metadata quality analysis
- **[EDAM Ontology](https://github.com/edamontology/edamontology)**: Bioinformatics terminology

### Technology Stack

- **Frontend**: Streamlit (1.49.0+) with Plotly visualizations
- **Backend**: Python 3.8+ with pandas, requests, jsonschema
- **Data Processing**: NumPy, pandas for large-scale analysis
- **Visualization**: Plotly, matplotlib for interactive charts
- **Caching**: Custom file-based caching for API responses
- **Logging**: Structured logging with rotation and filtering


#### Streamlit Configuration

Edit `.streamlit/config.toml` for custom settings:

```toml
[server]
port = 8501
maxUploadSize = 200

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
font = "sans serif"
```

## 📚 Documentation

Complete documentation is available in the [`docs/`](docs/) directory:

- **[User Guide](docs/user-guide/)**: How to use the application
- **[API Documentation](docs/api/)**: Technical API reference
- **[Developer Guide](docs/developer/)**: Contributing and development
- **[Examples](docs/examples/)**: Usage examples and tutorials

## � Troubleshooting

### Common Issues

#### Module Import Errors

```powershell
# Ensure src/ is in Python path
$env:PYTHONPATH = "$PWD\src;$env:PYTHONPATH"
python app.py
```

#### API Rate Limiting

- The application implements intelligent caching to minimize API calls
- Check `data/cache/` for stored responses
- Rate limits reset hourly

#### Performance Issues

- Large collection analysis may take several minutes
- Consider using smaller batch sizes for initial testing
- Monitor memory usage with Task Manager

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


<div align="center">

**[🚀 Launch Application](https://biotools-annotation-quality-evaluation.streamlit.app)** | **[📖 Documentation](docs/)** | **[🐛 Report Issues](https://github.com/bneiG1/bio.tools-annotation-quality-evaluation/issues)**

</div>
