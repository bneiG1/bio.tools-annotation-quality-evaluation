# Systematic Evaluation and Enhancement of bio.tools Annotation Quality

## Overview

The quality of metadata in the ELIXIR bio.tools registry affects its usability for both end users and developers. However, the completeness and consistency of tool annotations vary significantly. This project investigates the current state of metadata quality and proposes a systematic framework to assess and improve it.

## Project Structure

```
bio.tools-annotation-quality-evaluation/
├── README.md
├── requirements.txt
├── config/
│   ├── scoring_config.yaml
│   └── biotoolsschema.json
├── src/
│   ├── __init__.py
│   ├── data_collection/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── data_parser.py
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── completeness_scorer.py
│   │   └── tier_classifier.py
│   ├── linter/
│   │   ├── __init__.py
│   │   ├── linter_integration.py
│   │   └── error_analyzer.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── statistics.py
│   │   └── pattern_analysis.py
│   └── visualization/
│       ├── __init__.py
│       ├── charts.py
│       └── reports.py
├── tests/
│   ├── __init__.py
│   ├── test_data_collection.py
│   ├── test_scoring.py
│   └── test_analysis.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── reports/
├── notebooks/
│   ├── exploration.ipynb
│   ├── analysis.ipynb
│   └── visualization.ipynb
└── scripts/
    ├── run_evaluation.py
    └── generate_reports.py
```

## Key Components

### 1. Data Collection
- **API Client**: Retrieves tool entries from the bio.tools API
- **Data Parser**: Parses JSON metadata and validates against schema

### 2. Scoring System
- **Completeness Scorer**: Implements tier-based scoring system (1-5)
- **Tier Classifier**: Maps Tool Information Standards to scoring metrics

### 3. Linter Integration
- **Linter Integration**: Processes bio.tools linter results
- **Error Analyzer**: Identifies recurring structural issues

### 4. Analysis & Visualization
- **Statistics**: Generates completeness metrics per tier and domain
- **Pattern Analysis**: Identifies frequently missing attributes
- **Charts**: Creates radar charts, heatmaps, and visual summaries
- **Reports**: Generates comprehensive evaluation reports

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/bio.tools-annotation-quality-evaluation.git
cd bio.tools-annotation-quality-evaluation
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. Run the complete evaluation pipeline:
```bash
python scripts/run_evaluation.py --collection proteomics --limit 100
```

2. Generate reports:
```bash
python scripts/generate_reports.py --input data/processed/results.json --output data/reports/
```

### Custom Analysis

```python
from src.data_collection.api_client import BioToolsAPIClient
from src.scoring.completeness_scorer import CompletenessScorer
from src.visualization.charts import QualityVisualizer

# Initialize components
client = BioToolsAPIClient()
scorer = CompletenessScorer()
visualizer = QualityVisualizer()

# Collect data
tools = client.get_tools_by_collection("proteomics", limit=50)

# Score tools
results = scorer.score_tools(tools)

# Generate visualizations
visualizer.create_tier_distribution_chart(results)
visualizer.create_completeness_heatmap(results)
```

## Configuration

The scoring system can be customized through `config/scoring_config.yaml`:

```yaml
scoring:
  weights:
    basic_info: 20
    detailed_description: 15
    technical_details: 25
    documentation: 20
    accessibility: 10
    community: 10
  
  tiers:
    tier_1: 0-20
    tier_2: 21-40
    tier_3: 41-60
    tier_4: 61-80
    tier_5: 81-100
```

## Key Objectives

1. **Implement a scoring pipeline** to classify tools into annotation quality tiers
2. **Analyze completeness patterns** across tool collections and domains
3. **Identify frequently missing attributes** and structural issues
4. **Propose revisions** to the Tool Information Standards
5. **Integrate linter output** into the quality assessment framework

## Expected Outcomes

- A comprehensive scoring and analysis pipeline for bio.tools metadata evaluation
- Visual and tabular reports highlighting completeness metrics per tier and domain
- An integrated dataset combining scoring, linter results, and tool metadata
- A revised version of the Tool Information Standards based on empirical findings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- ELIXIR bio.tools registry team
- Tool Information Standards working group
- biotoolsSchema contributors