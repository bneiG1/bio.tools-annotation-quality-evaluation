# User Guide

This guide will help you get started with the bio.tools Annotation Quality Evaluation system, from installation through advanced usage scenarios.

## Table of Contents
1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Command Line Interface](#command-line-interface)
4. [Configuration](#configuration)
5. [Understanding Results](#understanding-results)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- Internet connection (for accessing bio.tools API)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
   cd bio.tools-annotation-quality-evaluation
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate it (Linux/Mac)
   source .venv/bin/activate
   
   # Activate it (Windows)
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python scripts/run_evaluation.py --help
   ```

### Docker Installation (Alternative)

```bash
# Build the Docker image
docker build -t biotools-quality .

# Run evaluation
docker run -v $(pwd)/data:/app/data biotools-quality --topic Proteomics --limit 50
```

## Basic Usage

### Quick Evaluation

To perform a basic evaluation of proteomics tools:

```bash
python scripts/run_evaluation.py --topic Proteomics --limit 100 --visualize
```

This command will:
- Fetch 100 tools related to proteomics from bio.tools API
- Score each tool using the tier-based system
- Generate visualization charts
- Save results to `data/processed/`

### Understanding the Output

After running an evaluation, you'll find:

```
data/processed/
├── evaluation_results_YYYYMMDD_HHMMSS.json    # Raw scoring data
├── summary_report_YYYYMMDD_HHMMSS.txt         # Human-readable summary
└── statistics_YYYYMMDD_HHMMSS.json            # Statistical analysis

data/visualizations/
├── tier_distribution.png                       # Tier distribution chart
├── score_distribution.png                      # Score histogram  
├── category_scores.png                         # Scores by category
└── completeness_heatmap.png                    # Field completeness heatmap
```

## Command Line Interface

### Core Commands

#### `run_evaluation.py`
Main script for running evaluations.

**Basic syntax:**
```bash
python scripts/run_evaluation.py [OPTIONS]
```

**Selection options (choose one):**
- `--topic TOPIC`: Evaluate tools by scientific topic (e.g., "Proteomics", "Genomics")
- `--collection COLLECTION`: Evaluate tools from a specific collection (e.g., "Galaxy")  
- `--query QUERY`: Free-text search query

**Common options:**
- `--limit N`: Maximum number of tools to evaluate (default: 100)
- `--visualize`: Generate visualization charts
- `--output-dir DIR`: Custom output directory
- `--log-level LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

**Examples:**
```bash
# Evaluate 50 tools from Galaxy collection with detailed logging
python scripts/run_evaluation.py --collection Galaxy --limit 50 --log-level DEBUG

# Search for tools related to machine learning
python scripts/run_evaluation.py --query "machine learning" --limit 200 --visualize

# Evaluate all genomics tools (no limit)
python scripts/run_evaluation.py --topic Genomics --limit 0
```

#### `generate_dashboard.py`
Creates an interactive HTML dashboard.

```bash
python scripts/generate_dashboard.py [--data-dir DIR] [--output-dir DIR]
```

### Advanced Options

#### Custom Configuration
```bash
python scripts/run_evaluation.py --config config/custom_scoring.yaml --topic Proteomics
```

#### Batch Processing
```bash
# Process multiple topics
for topic in "Proteomics" "Genomics" "Transcriptomics"; do
    python scripts/run_evaluation.py --topic "$topic" --limit 100 --output-dir "results/$topic"
done
```

## Configuration

### Basic Configuration

The system uses `config/scoring_config.yaml` for configuration. Key sections:

```yaml
scoring:
  # Weights for different aspects (must sum to 100)
  weights:
    basic_info: 15
    core_metadata: 25  
    technical_info: 20
    accessibility: 20
    advanced_features: 15
    community: 5

  # Tier thresholds
  tiers:
    tier_1: [0, 15]      # SPARSE
    tier_2: [16, 40]     # BASIC DETAILS  
    tier_3: [41, 65]     # DETAILED
    tier_4: [66, 85]     # HIGHLY DETAILED
    tier_5: [86, 100]    # COMPREHENSIVE
```

### Custom Scoring Profiles

Create custom profiles for different evaluation scenarios:

**config/research_focused.yaml:**
```yaml
scoring:
  weights:
    basic_info: 10
    core_metadata: 30      # Emphasize publications
    technical_info: 25     # Emphasize technical details
    accessibility: 25      # Important for reproducibility
    advanced_features: 10
    community: 0          # Less important for research
```

**Usage:**
```bash
python scripts/run_evaluation.py --config config/research_focused.yaml --topic Proteomics
```

## Understanding Results

### Tier Classification

Tools are classified into 5 tiers:

| Tier | Name | Score Range | Description |
|------|------|-------------|-------------|
| 1 | SPARSE | 0-15 | Minimal viable entry with basic information |
| 2 | BASIC DETAILS | 16-40 | Essential metadata for discoverability |
| 3 | DETAILED | 41-65 | Comprehensive core information |
| 4 | HIGHLY DETAILED | 66-85 | Rich metadata for full understanding |
| 5 | COMPREHENSIVE | 86-100 | Complete tool profile with all details |

### Score Categories

Each tool receives scores in six categories:

1. **Basic Information (15%)**: Name, description, homepage, unique identifiers
2. **Core Metadata (25%)**: Tool type, scientific topics, publications
3. **Technical Information (20%)**: Operations, documentation, platform compatibility
4. **Accessibility (20%)**: Input/output formats, downloads, code availability  
5. **Advanced Features (15%)**: Benchmarks, monitoring, community features
6. **Community (5%)**: Credits, contact information

### Result Files Explained

#### `evaluation_results_*.json`
Raw scoring data for each tool:
```json
{
  "biotoolsID": "example_tool",
  "name": "Example Tool",
  "total_score": 67.5,
  "tier": 4,
  "category_scores": {
    "basic_info": 14.2,
    "core_metadata": 18.5,
    "technical_info": 16.3,
    "accessibility": 12.1,
    "advanced_features": 4.8,
    "community": 1.6
  },
  "missing_fields": ["license", "documentation"],
  "warnings": []
}
```

#### `summary_report_*.txt`
Human-readable summary:
```
bio.tools Annotation Quality Evaluation Report
==============================================

Evaluation Date: 2025-08-13 10:30:45
Topic/Collection: Proteomics
Total Tools Evaluated: 100

Tier Distribution:
- Tier 5 (COMPREHENSIVE): 8 tools (8%)
- Tier 4 (HIGHLY DETAILED): 22 tools (22%)  
- Tier 3 (DETAILED): 35 tools (35%)
- Tier 2 (BASIC DETAILS): 28 tools (28%)
- Tier 1 (SPARSE): 7 tools (7%)

Average Score: 52.3
Median Score: 51.0

Most Common Missing Fields:
1. license (45 tools missing)
2. documentation (38 tools missing)  
3. version (31 tools missing)
```

## Common Workflows

### 1. Domain-Specific Analysis

Analyze tools in a specific scientific domain:

```bash
# Step 1: Evaluate domain tools
python scripts/run_evaluation.py --topic "Sequence analysis" --limit 500 --visualize

# Step 2: Generate dashboard
python scripts/generate_dashboard.py --data-dir data/processed

# Step 3: Review results
open dashboard/index.html
```

### 2. Collection Comparison

Compare quality across different tool collections:

```bash
# Evaluate multiple collections
python scripts/run_evaluation.py --collection Galaxy --output-dir results/galaxy --visualize
python scripts/run_evaluation.py --collection BioConda --output-dir results/bioconda --visualize  
python scripts/run_evaluation.py --collection Debian --output-dir results/debian --visualize

# Generate comparative dashboard
python scripts/generate_dashboard.py --data-dir results --output-dir comparison_dashboard
```

### 3. Quality Improvement Workflow

Identify and prioritize quality improvements:

```bash
# Step 1: Baseline evaluation
python scripts/run_evaluation.py --topic Proteomics --limit 1000 --output-dir baseline

# Step 2: Identify low-quality tools
# Review summary_report_*.txt for Tier 1 and Tier 2 tools

# Step 3: Analyze common issues
# Check missing_fields in evaluation_results_*.json

# Step 4: Re-evaluate after improvements
python scripts/run_evaluation.py --topic Proteomics --limit 1000 --output-dir improved
```

### 4. Research and Publication

For research projects requiring quality assessment:

```bash
# Use research-focused configuration
python scripts/run_evaluation.py \
  --config config/research_focused.yaml \
  --topic "Computational biology" \
  --limit 0 \
  --output-dir research_data \
  --visualize \
  --log-level INFO

# Generate publication-ready figures
python scripts/create_publication_figures.py research_data/
```

## Troubleshooting

### Common Issues

#### "No tools found"
```bash
# Check API connectivity
python -c "import requests; print(requests.get('https://bio.tools/api/tool/').status_code)"

# Verify topic/collection name
python scripts/run_evaluation.py --query "proteomics" --limit 5
```

#### "Permission denied" errors
```bash
# Check directory permissions
chmod 755 data/
chmod 755 data/processed/
chmod 755 data/visualizations/
```

#### "Config file not found"
```bash
# Use absolute path
python scripts/run_evaluation.py --config /full/path/to/config.yaml

# Or copy config to current directory
cp config/scoring_config.yaml ./custom_config.yaml
python scripts/run_evaluation.py --config custom_config.yaml
```

#### Memory issues with large datasets
```bash
# Process in smaller batches
python scripts/run_evaluation.py --topic Proteomics --limit 100
python scripts/run_evaluation.py --topic Proteomics --limit 100 --offset 100
```

### Getting Help

1. **Check the logs**: Look at `evaluation.log` for detailed error messages
2. **Increase verbosity**: Use `--log-level DEBUG` for more information
3. **Test with small datasets**: Use `--limit 5` to test functionality
4. **Check configuration**: Validate YAML syntax and field names
5. **Report issues**: Create an issue on GitHub with:
   - Error message and full command used  
   - Operating system and Python version
   - Contents of `evaluation.log`

### Performance Tips

1. **Use appropriate limits**: Start with `--limit 100` for testing
2. **Cache results**: Results are automatically saved and can be reused
3. **Parallel processing**: Process different topics/collections simultaneously
4. **Monitor resources**: Large evaluations may require significant memory
5. **Use SSD storage**: I/O intensive operations benefit from fast storage

## Next Steps

- Read the [Configuration Guide](configuration.md) to customize scoring
- Explore the [API Reference](api-reference.md) for programmatic usage
- Check out [Examples](examples.md) for more detailed use cases
- Learn about the [Architecture](architecture.md) to understand the system design
