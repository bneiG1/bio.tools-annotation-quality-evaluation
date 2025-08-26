# bio.tools Annotation Quality Evaluation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

The **bio.tools Annotation Quality Evaluation** system provides a comprehensive framework for assessing and improving metadata quality in the [ELIXIR bio.tools](https://bio.tools) registry. This tool addresses the critical need for standardized evaluation of scientific tool annotations, enabling researchers and maintainers to identify quality gaps and enhance discoverability.

### Key Features

- 🎯 **Tier-based scoring system** (1-5 tiers) aligned with [Tool Information Standards](https://bio-tools.github.io/Tool-Information-Standards/use_cases.html)
- 📊 **Comprehensive quality metrics** and statistical analysis
- 🔍 **Integration with bio.tools linter** for automated diagnostics  
- 📈 **Rich visualizations** including charts, heatmaps, and interactive dashboards
- 🛠️ **Flexible configuration** for custom scoring criteria
- 🔄 **Batch processing** capabilities for large-scale analysis
- 📋 **Detailed reporting** with actionable insights
- 💾 **Local data storage** - save each biotool as individual JSON files
- 🏠 **Offline evaluation** - run evaluations on locally stored data
- 📂 **Data organization** - tools organized by collection, topic, and query

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
cd bio.tools-annotation-quality-evaluation

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run evaluation on proteomics tools (saves tools locally by default)
python scripts/run_evaluation.py --topic Proteomics --limit 100 --visualize

# Use locally stored data instead of API
python scripts/run_evaluation.py --topic Proteomics --use-local --visualize

# Run evaluation on specific collection
python scripts/run_evaluation.py --collection Galaxy --limit 50 --log-level DEBUG

# Local storage management commands
python scripts/run_evaluation.py --storage-info
python scripts/run_evaluation.py --list-local-tools
python scripts/run_evaluation.py --clear-local-data all

# Manage local data with dedicated tool
python scripts/manage_local_data.py info
python scripts/manage_local_data.py download --collection proteomics --limit 100

# Generate dashboard
python scripts/generate_dashboard.py
```

### Local Data Storage

The system now supports local storage of individual biotools:

- **Individual JSON files** for each tool (better for version control)
- **Organized storage** by collection, topic, and query
- **Offline evaluation** capabilities
- **Faster repeated evaluations**

See [Local Storage Documentation](docs/local-storage.md) for detailed information.

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
src/
├── data_collection/     # API clients and data parsing
├── scoring/            # Completeness scoring and tier classification  
├── linter/             # Integration with bio.tools linter
├── analysis/           # Statistical analysis and metrics
└── visualization/      # Charts, plots, and dashboards
```

## Documentation

Comprehensive documentation is available in the `docs/` folder:

### Getting Started
- 📖 **[User Guide](docs/user-guide.md)** - Installation, basic usage, and common workflows
- 🚀 **[Examples](docs/examples.md)** - Practical examples and use cases for different scenarios
- ❓ **[FAQ](docs/faq.md)** - Frequently asked questions and quick answers

### System Understanding  
- 🏗️ **[Architecture Guide](docs/architecture.md)** - System design, components, and data flow
- ⚙️ **[Configuration Guide](docs/configuration.md)** - Customizing scoring, thresholds, and behavior
- 📊 **[Scoring Methodology](docs/scoring-methodology.md)** - Detailed explanation of the tier-based scoring system

### Advanced Usage
- 🔌 **[API Reference](docs/api-reference.md)** - Complete API documentation for programmatic usage
- � **[Standards Mapping](docs/standards-mapping.md)** - How the system aligns with ELIXIR and community standards
- � **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions

### Development & Contributing
- 👨‍💻 **[Development Guide](docs/development.md)** - Setting up development environment and contributing
- 📝 **[Changelog](CHANGELOG.md)** - Version history and release notes

## Key Concepts

### Tier Classification System

Tools are classified into 5 tiers based on metadata completeness:

- **Tier 1 (SPARSE)**: Basic information only (0-15 points)
- **Tier 2 (BASIC DETAILS)**: Essential metadata (16-40 points)  
- **Tier 3 (DETAILED)**: Comprehensive core information (41-65 points)
- **Tier 4 (HIGHLY DETAILED)**: Rich metadata (66-85 points)
- **Tier 5 (COMPREHENSIVE)**: Complete tool profile (86-100 points)

### Scoring Categories

- **Basic Information** (15%): Name, description, homepage, IDs
- **Core Metadata** (25%): Tool type, topics, publications  
- **Technical Information** (20%): Operations, documentation, platform info
- **Accessibility** (20%): I/O formats, downloads, code availability
- **Advanced Features** (15%): Benchmarks, monitoring, community features
- **Community** (5%): Credits, contact information

## Usage Examples

### Command Line Interface

```bash
# Evaluate tools by topic with visualization
python scripts/run_evaluation.py --topic "Sequence analysis" --limit 200 --visualize

# Evaluate specific collection with custom output
python scripts/run_evaluation.py --collection Galaxy --output-dir results/galaxy --log-level INFO

# Query-based evaluation with URL accessibility checking
python scripts/run_evaluation.py --query "protein folding" --limit 50 --check-urls

# Comprehensive evaluation with URL checking and visualization
python scripts/run_evaluation.py --topic "Proteomics" --limit 100 --check-urls --visualize
```

### Programmatic Usage

```python
from src.data_collection.api_client import BioToolsAPIClient
from src.scoring.completeness_scorer import CompletenessScorer
from src.scoring.tier_classifier import TierClassifier

# Initialize components with URL checking enabled
api_client = BioToolsAPIClient()
scorer = CompletenessScorer('config/scoring_config.yaml', enable_url_checking=True)
classifier = TierClassifier('config/scoring_config.yaml')

# Fetch and score tools
tools = api_client.get_tools_by_topic("Proteomics", limit=100)
for tool in tools:
    score = scorer.score_tool(tool)
    tier = classifier.classify_tool(score)
    
    # Check URL accessibility results
    url_info = score['details']['accessibility'].get('url_accessibility')
    homepage_ok = url_info['summary']['homepage_accessible'] if url_info else 'N/A'
    
    print(f"{tool['name']}: Score {score['total_score']:.1f}, Tier {tier}, Homepage: {homepage_ok}")
```

## Configuration

The system is highly configurable via `config/scoring_config.yaml`. You can customize:

- Scoring weights for different metadata categories
- Tier thresholds and classification rules  
- Required fields and validation criteria
- Output formats and visualization settings

See the [Configuration Guide](docs/configuration.md) for detailed information.

## URL Accessibility Checking

The system includes optional URL accessibility checking to validate that homepage URLs and other links are still functional:

- **Homepage Validation**: Checks if the primary homepage URL is accessible
- **Link Validation**: Validates all URLs found in tool metadata  
- **Smart Scoring**: Adjusts accessibility scores based on URL health
- **Performance Optimized**: Uses concurrent checking with caching and rate limiting

Enable URL checking with the `--check-urls` flag:

```bash
python scripts/run_evaluation.py --topic "Proteomics" --limit 50 --check-urls
```

See the [URL Checking Guide](docs/url-checking.md) for detailed information.

## Output and Reports

The evaluation generates comprehensive outputs:

- **Scoring Results**: JSON files with detailed scores and classifications
- **Statistical Reports**: Summary statistics and quality metrics
- **Visualizations**: Charts, heatmaps, and distribution plots
- **Interactive Dashboard**: Web-based interface for exploring results
- **CSV Exports**: Tabular data for further analysis

## Contributing

We welcome contributions! Please see our [Development Guide](docs/development.md) for information on:

- Setting up the development environment
- Code style and standards
- Testing procedures
- Submitting pull requests

## Research and Citations

This tool supports research into metadata quality in scientific registries. If you use this system in your research, please cite:

```bibtex
@software{biotools_quality_eval,
  title = {bio.tools Annotation Quality Evaluation},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/bneiG1/bio.tools-annotation-quality-evaluation}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [ELIXIR bio.tools](https://bio.tools) for providing the registry and API
- [Tool Information Standards](https://bio-tools.github.io/Tool-Information-Standards/) community
- [bio.tools linter](https://github.com/3top1a/biotools-linter) project
- ELIXIR community for metadata standardization efforts

## Support

- 📖 Check the [documentation](docs/)
- 🐛 [Report issues](https://github.com/bneiG1/bio.tools-annotation-quality-evaluation/issues)
- 💬 [Start a discussion](https://github.com/bneiG1/bio.tools-annotation-quality-evaluation/discussions)

---
