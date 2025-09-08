# Bio.tools Annotation Quality Evaluation

A comprehensive bioinformatics data analysis pipeline for evaluating metadata quality in the ELIXIR bio.tools registry. This tool implements the Tool Information Standards framework to assess and improve the quality of tool annotations in bio.tools.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Standards-Based Assessment**: Implements the 5-tier Tool Information Standards (SPARSE to COMPREHENSIVE)
- **Schema Validation**: Validates entries against the official biotoolsSchema
- **Comprehensive Linting**: Extensive quality checks including URL validation, EDAM term consistency, and metadata completeness
- **Interactive Visualizations**: Rich dashboards and charts for quality analysis
- **Multiple Output Formats**: JSON, CSV, Excel, and HTML reports
- **Batch Processing**: Analyze individual tools, collections, or entire registry subsets
- **Caching Support**: Efficient API response caching to minimize requests

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/bio.tools-annotation-quality-evaluation.git
cd bio.tools-annotation-quality-evaluation
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create necessary directories:

```bash
mkdir -p data/{raw,processed,reports,cache}
```

## Quick Start

### Analyze a Single Tool

```bash
python main.py validate --tool-id signalp --show-details
```

### Analyze a Collection

```bash
python main.py analyze --collection "ELIXIR Tools" --generate-charts --create-dashboard
```

### Search and Analyze Tools

```bash
python main.py analyze --query "protein sequence analysis" --max-tools 50 --format excel
```

### Compare Tools

```bash
python main.py compare --query "blast" --max-tools 20
```

### Registry Statistics

```bash
python main.py stats
```

## Command Reference

### Main Commands

- `analyze` - Comprehensive quality analysis of bio.tools entries
- `validate` - Quick validation of a single tool
- `compare` - Comparative analysis across multiple tools
- `batch` - Analyze tools from a local JSON file
- `stats` - Show bio.tools registry statistics

### Options

- `--tool-id, -t` - Specific bio.tools ID to analyze
- `--collection, -c` - Collection ID to analyze
- `--query, -q` - Search query for tools
- `--max-tools, -m` - Maximum number of tools to analyze
- `--output-dir, -o` - Output directory for reports
- `--format, -f` - Output format (json, csv, excel, html)
- `--generate-charts` - Generate visualization charts
- `--create-dashboard` - Create interactive HTML dashboard
- `--verbose, -v` - Enable verbose logging

## Quality Assessment Framework

### Tool Information Standards Tiers

The tool implements the official bio.tools Tool Information Standards with 5 tiers:

1. **SPARSE** - Minimum requirements (name, description, homepage, biotoolsID)
2. **MINIMAL** - Basic scientific context (+ topic, toolType, function)
3. **DETAILED** - Technical details (+ operatingSystem, language, documentation)
4. **COMPLETE** - Comprehensive metadata (+ license, maturity, cost, downloads, publications)
5. **COMPREHENSIVE** - Full richness (+ multiple contacts, relations, detailed credits)

### Quality Metrics

Each tool receives:

- **Overall Score** (0-100) - Weighted combination of all quality factors
- **Quality Grade** (A-F) - Letter grade based on overall score
- **Standards Tier** - Achieved tier in the Tool Information Standards
- **Field Completeness** - Percentage of recommended fields present
- **Content Quality Scores** - URL health, EDAM consistency, publication quality

### Validation Checks

- **Schema Validation** - Compliance with biotoolsSchema
- **EDAM Term Validation** - Correct format and consistency of EDAM ontology terms
- **URL Validation** - Format checking and accessibility hints
- **Publication Validation** - DOI, PMID, PMCID format validation
- **Completeness Analysis** - Missing required and recommended fields
- **Consistency Checks** - Internal metadata consistency

## Output Formats

### JSON Export
Detailed analysis data with complete metrics and recommendations:
```json
{
  "tool_id": "signalp",
  "tool_name": "SignalP",
  "metrics": {
    "overall_score": 85.4,
    "quality_grade": "B",
    "standards_tier": "COMPLETE"
  },
  "recommendations": [...]
}
```

### CSV Export
Tabular data suitable for statistical analysis and plotting.

### Excel Export
Multi-sheet workbook with:
- Quality metrics summary
- Detailed analysis results
- Summary statistics
- Top issues across tools

### HTML Dashboard
Interactive visualizations including:
- Quality distribution charts
- Standards tier analysis
- Issue categorization
- Comparative metrics

## Architecture

```
bio.tools-annotation-quality-evaluation/
├── src/
│   ├── collectors/          # Data collection from bio.tools API
│   ├── validators/          # Schema validation and standards scoring
│   ├── analyzers/           # Quality analysis and linting
│   └── reporters/           # Visualization and reporting
├── data/
│   ├── raw/                 # Raw data from API
│   ├── processed/           # Processed analysis results
│   ├── reports/             # Generated reports and charts
│   └── cache/               # API response cache
├── tests/                   # Unit and integration tests
├── notebooks/               # Jupyter notebooks for analysis
└── main.py                  # CLI application
```

### Core Modules

- **BioToolsAPIClient** - Handles API interactions with rate limiting and caching
- **ToolInformationStandardsScorer** - Implements the 5-tier quality framework
- **BiotoolsSchemaValidator** - Validates against official schema
- **BiotoolsLinter** - Comprehensive quality checks and issue detection
- **QualityAnalyzer** - Combines all analysis methods
- **QualityReporter** - Generates reports and visualizations

## Examples

### Example 1: Analyze ELIXIR Tools Collection

```bash
python main.py analyze --collection "ELIXIR Tools" --format excel --generate-charts
```

This will:
- Fetch all tools in the ELIXIR Tools collection
- Perform comprehensive quality analysis
- Generate an Excel report with multiple sheets
- Create visualization charts

### Example 2: Compare Sequence Analysis Tools

```bash
python main.py compare --query "sequence analysis" --max-tools 30
```

This will:
- Search for sequence analysis tools
- Analyze up to 30 tools
- Generate comparative visualizations
- Create an interactive dashboard

### Example 3: Detailed Validation

```bash
python main.py validate --tool-id blast --show-details
```

Output:
```
==================================================
QUALITY REPORT FOR BLAST
==================================================
Overall Quality: Grade B (82.5/100)
Standards Tier: COMPLETE (78.0/100)
Schema Valid: ✅ Yes
⚠️  Warning Issues: 3
ℹ️  Info Issues: 5
Field Completeness: 85.0%
Required Fields: ✅
Content Features: Functions, Documentation, Publications

🔧 PRIORITY FIXES:
  • Add contact information with email
  • Update operating system compatibility

💡 RECOMMENDATIONS:
  • Add more detailed function descriptions
  • Include software license information
  • Add download links for different versions
```

## API Integration

The tool integrates with the bio.tools API to fetch tool metadata. All API interactions include:

- **Rate Limiting** - Respects API limits with configurable delays
- **Caching** - Local caching to avoid repeated requests
- **Error Handling** - Robust error handling and retry logic
- **Authentication Support** - Ready for authenticated requests when needed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 src/
black src/

# Generate coverage report
pytest --cov=src tests/
```

## Related Projects

- [bio.tools](https://bio.tools/) - The ELIXIR Tools and Data Services Registry
- [biotoolsSchema](https://github.com/bio-tools/biotoolsSchema) - Official schema for bio.tools
- [biotools-linter](https://github.com/3top1a/biotools-linter) - Rule-based linter for bio.tools
- [Tool Information Standards](https://bio-tools.github.io/Tool-Information-Standards/) - Quality guidelines

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{biotools_quality_eval,
  title={Bio.tools Annotation Quality Evaluation},
  author={Bio.tools Quality Evaluation Team},
  year={2024},
  url={https://github.com/your-username/bio.tools-annotation-quality-evaluation}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-username/bio.tools-annotation-quality-evaluation/issues)
- **Documentation**: [Project Wiki](https://github.com/your-username/bio.tools-annotation-quality-evaluation/wiki)
- **Email**: your-email@domain.com

## Acknowledgments

- [ELIXIR](https://elixir-europe.org/) for the bio.tools registry
- [Bio.tools team](https://bio.tools/) for the API and schema
- Contributors to the Tool Information Standards
- Open source community for the foundational libraries

## Prerequisites

- Python 3.8+ and basic familiarity with virtual environments
- Experience with JSON handling and data visualization (matplotlib, seaborn, plotly, etc.)

## Getting started (suggested)

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if a requirements file is added):

```powershell
pip install -r requirements.txt
```

3. Run the main pipeline (TBD — implement script entrypoints):

```powershell
python -m src.main --help
```

Note: This repository currently contains planning and scope material. Implementation files (scripts, modules, requirements) should be added to follow the project structure.

## Contribution & project structure

Recommended structure when implementing:

- src/ — Python package for pipeline code
- data/ — raw and processed JSON/CSV outputs
- notebooks/ — exploratory analysis and figures
- tests/ — unit and integration tests
- docs/ — additional documentation and the proposed revision drafts

If you'd like help scaffolding the codebase (project layout, starter scripts, tests, and a minimal working pipeline), open an issue or request a scaffold in this repository and I'll create it.

## Resources

- Tool Information Standards: https://bio-tools.github.io/Tool-Information-Standards/use_cases.html
- biotoolsSchema: https://github.com/bio-tools/biotoolsschema
- bio.tools linter: https://github.com/3top1a/biotools-linter/tree/main

## License

See the `LICENSE` file for licensing details.

---

Maintainers: bneiG1
