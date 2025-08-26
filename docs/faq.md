# FAQ - Frequently Asked Questions

Common questions and answers about the bio.tools Annotation Quality Evaluation system.

## Table of Contents
1. [General Questions](#general-questions)
2. [Installation and Setup](#installation-and-setup)
3. [Usage and Configuration](#usage-and-configuration)
4. [Scoring and Methodology](#scoring-and-methodology)
5. [Performance and Troubleshooting](#performance-and-troubleshooting)
6. [Development and Customization](#development-and-customization)

## General Questions

### What is the bio.tools Annotation Quality Evaluation system?

The system is a comprehensive framework for assessing metadata quality in the ELIXIR bio.tools registry. It uses a tier-based scoring system (1-5 tiers) aligned with the Tool Information Standards to evaluate how complete and useful tool annotations are.

### Who should use this system?

- **Registry maintainers**: To assess overall quality and identify improvement areas
- **Tool developers**: To evaluate and improve their tool annotations
- **Researchers**: To find high-quality, well-documented tools
- **Community coordinators**: To track quality improvements over time
- **Standards developers**: To analyze metadata patterns and propose improvements

### How does this relate to the Tool Information Standards?

The scoring system directly maps to the five tiers defined in the ELIXIR Tool Information Standards:
- **Tier 1 (SPARSE)**: Minimal viable entry
- **Tier 2 (BASIC DETAILS)**: Essential discoverable information
- **Tier 3 (DETAILED)**: Comprehensive core metadata
- **Tier 4 (HIGHLY DETAILED)**: Rich, well-documented tools
- **Tier 5 (COMPREHENSIVE)**: Complete, exemplary tool profiles

### Is this system official ELIXIR software?

This is a community-developed tool that implements and supports ELIXIR standards. While it aligns with official ELIXIR Tool Information Standards, it is not officially endorsed by ELIXIR. However, it's designed to support the community's quality improvement efforts.

## Installation and Setup

### What are the system requirements?

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 2GB RAM (more for large-scale analysis)
- **Storage**: Varies by analysis size (1GB+ recommended)
- **Network**: Internet connection for API access

### Why do I get "Permission denied" errors during installation?

This usually happens when:
1. **Virtual environment issues**: Make sure you're in an activated virtual environment
2. **System Python conflicts**: Use a virtual environment instead of system Python
3. **File permissions**: Ensure you have write access to the installation directory

**Solution:**
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in virtual environment
pip install -r requirements.txt
```

### Can I run this system without internet access?

The system requires internet access to:
- Fetch tool metadata from the bio.tools API
- Download EDAM ontology files (if not cached)

For offline analysis:
1. Use cached data from previous runs
2. Export data while online, then analyze offline
3. Use local data files (requires custom configuration)

### How do I update to the latest version?

```bash
# Update from Git repository
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests to verify
pytest tests/
```

## Usage and Configuration

### How do I evaluate tools from a specific scientific domain?

Use the `--topic` parameter:
```bash
python scripts/run_evaluation.py --topic "Proteomics" --limit 100 --visualize
```

Common topics include:
- "Proteomics"
- "Genomics" 
- "Transcriptomics"
- "Metabolomics"
- "Sequence analysis"
- "Structure analysis"

### How do I customize the scoring weights?

Create a custom configuration file:

```yaml
# custom_config.yaml
scoring:
  weights:
    basic_info: 20          # Increase from default 15
    core_metadata: 30       # Increase from default 25
    technical_info: 20      # Same as default
    accessibility: 20       # Same as default  
    advanced_features: 10   # Decrease from default 15
    community: 0            # Decrease from default 5
```

Use it with:
```bash
python scripts/run_evaluation.py --config custom_config.yaml --topic Proteomics
```

### What's the difference between topic, collection, and query searches?

- **Topic** (`--topic`): Searches by scientific domain/field (uses EDAM topics)
- **Collection** (`--collection`): Searches within specific tool collections (Galaxy, BioConda, etc.)
- **Query** (`--query`): Free-text search across tool names, descriptions, and metadata

Examples:
```bash
# By topic
python scripts/run_evaluation.py --topic "Machine learning"

# By collection  
python scripts/run_evaluation.py --collection "Galaxy"

# By query
python scripts/run_evaluation.py --query "protein structure prediction"
```

### How do I analyze my evaluation results?

Results are saved in multiple formats:

1. **JSON files**: Machine-readable detailed results
2. **Text reports**: Human-readable summaries
3. **Visualizations**: Charts and plots (if `--visualize` used)
4. **Interactive dashboard**: Generated with `generate_dashboard.py`

Check the output directory (default: `data/processed/`) for:
- `evaluation_results_*.json`
- `summary_report_*.txt`
- Visualization PNG files

### Can I pause and resume long-running evaluations?

Currently, the system doesn't have built-in pause/resume functionality. For large evaluations:

1. **Use smaller batches**:
   ```bash
   python scripts/run_evaluation.py --topic Proteomics --limit 500
   ```

2. **Process in stages**:
   ```bash
   # Process first batch
   python scripts/run_evaluation.py --topic Proteomics --limit 100 --offset 0
   
   # Process second batch
   python scripts/run_evaluation.py --topic Proteomics --limit 100 --offset 100
   ```

3. **Use screen/tmux for long sessions**:
   ```bash
   screen -S biotools_eval
   python scripts/run_evaluation.py --topic Proteomics --limit 5000
   # Ctrl+A, D to detach
   ```

## Scoring and Methodology

### How are the scores calculated?

Scores are calculated using a weighted sum across six categories:

1. **Basic Information** (15%): Name, description, homepage, ID
2. **Core Metadata** (25%): Tool type, topics, publications
3. **Technical Information** (20%): Operations, platform, license
4. **Accessibility** (20%): Downloads, documentation, formats
5. **Advanced Features** (15%): Community features, monitoring
6. **Community** (5%): Contact info, credits

Each category contains multiple fields with individual weights. The final score (0-100) is mapped to tiers 1-5.

### Why did my tool get a lower score than expected?

Common reasons for lower scores:

1. **Missing key fields**: Check the `missing_fields` in results
2. **Incomplete information**: Short descriptions, missing URLs
3. **Invalid data**: Broken links, malformed entries
4. **Different priorities**: The scoring emphasizes scientific credibility and accessibility

Review the detailed scoring breakdown in the JSON results to see specific category scores.

### How do tier thresholds work?

Default tier thresholds:
- **Tier 1**: 0-15 points (SPARSE)
- **Tier 2**: 16-40 points (BASIC DETAILS)
- **Tier 3**: 41-65 points (DETAILED)
- **Tier 4**: 66-85 points (HIGHLY DETAILED)
- **Tier 5**: 86-100 points (COMPREHENSIVE)

These can be customized in your configuration file.

### Can I create domain-specific scoring criteria?

Yes! Create custom configurations for different domains:

```yaml
# proteomics_config.yaml
scoring:
  weights:
    core_metadata: 35       # Publications more important in proteomics
    accessibility: 25       # Wet-lab researchers need clear instructions
  
  field_weights:
    publication: 20         # Higher weight for publications
    documentation: 15       # Essential for complex protocols
```

### Are there penalties for missing information?

The system uses positive scoring (presence-based) rather than penalties. Missing fields contribute 0 points rather than negative points. However, some advanced configurations can include penalty rules for critical missing information.

### How does the system handle malformed or invalid data?

The system includes robust error handling:

1. **Data validation**: Checks for proper formats and structures
2. **Graceful degradation**: Continues processing even with some invalid data
3. **Error logging**: Records issues for review
4. **Partial scoring**: Scores available fields even if some data is invalid

Invalid data typically receives 0 points for that field.

## Performance and Troubleshooting

### The evaluation is running very slowly. How can I speed it up?

Several optimization strategies:

1. **Reduce batch size**: Use `--limit` to process fewer tools
2. **Enable caching**: Responses are cached automatically
3. **Use specific queries**: More targeted searches are faster
4. **Check network connection**: API calls require good connectivity
5. **Run during off-peak hours**: Avoid high API traffic periods

```bash
# Faster evaluation with smaller batch
python scripts/run_evaluation.py --topic Proteomics --limit 50
```

### I'm getting "API rate limit exceeded" errors

The bio.tools API has rate limits. Solutions:

1. **Built-in retry logic**: The system automatically retries with backoff
2. **Reduce concurrency**: The system is designed to be API-friendly
3. **Check API status**: Verify bio.tools API is operational
4. **Use caching**: Results are cached to reduce repeat requests

If issues persist:
```bash
# Run with debug logging to see detailed API interactions
python scripts/run_evaluation.py --log-level DEBUG --topic Test --limit 10
```

### The system is using too much memory

For large datasets:

1. **Process in batches**: Use smaller limits
2. **Clear cache periodically**: Remove old cached data
3. **Use streaming processing**: Process tools individually
4. **Monitor memory usage**: Check system resources

```bash
# Monitor memory usage
python scripts/run_evaluation.py --topic Proteomics --limit 100 --log-level INFO
```

### My visualization charts look weird or are missing

Common visualization issues:

1. **Missing dependencies**: Ensure all visualization packages are installed
2. **Display issues**: Use `--save-only` for server environments
3. **Data formatting**: Check that results data is complete
4. **File permissions**: Ensure write access to visualization directory

```bash
# Reinstall visualization dependencies
pip install matplotlib seaborn plotly kaleido --upgrade

# Test visualization with small dataset
python scripts/run_evaluation.py --topic Test --limit 5 --visualize
```

### Configuration file errors

Common configuration issues:

1. **YAML syntax errors**: Validate YAML format
2. **Weight sum errors**: Category weights must sum to 100
3. **Invalid field names**: Check field names match expected values
4. **Path issues**: Use absolute paths for file references

Validate configuration:
```python
# Test configuration loading
python -c "
import yaml
with open('config/my_config.yaml') as f:
    config = yaml.safe_load(f)
print('Configuration valid!')
"
```

## Development and Customization

### How do I add a new scoring category?

1. **Extend the CompletenessScorer class**:
   ```python
   def score_my_category(self, tool_data):
       # Your scoring logic
       return score, details
   ```

2. **Update the configuration schema** to include your category
3. **Add the category to the main scoring method**
4. **Write tests** for the new functionality
5. **Update documentation**

See the [Development Guide](development.md) for detailed instructions.

### Can I integrate with other tool registries?

Yes! The system is designed to be extensible:

1. **Implement the APIClient interface** for new data sources
2. **Create data parsers** for different metadata formats  
3. **Adapt scoring criteria** for different standards
4. **Configure field mappings** for different schemas

### How do I contribute to the project?

1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes
3. **Write tests** for new functionality
4. **Follow code style guidelines** (Black, Flake8)
5. **Submit a pull request** with clear description
6. **Respond to code review feedback**

See the [Contributing Guidelines](development.md#contributing-guidelines) for details.

### Can I use this system for commercial purposes?

The system is released under the MIT License, which permits commercial use. However:

1. **Respect API terms**: Follow bio.tools API usage guidelines
2. **Attribution**: Include appropriate citations and acknowledgments
3. **Data licensing**: Consider licensing of the metadata you analyze
4. **Community benefit**: Consider contributing improvements back to the community

### How do I report bugs or request features?

1. **Search existing issues** on GitHub to avoid duplicates
2. **Create detailed bug reports** with:
   - Error messages and logs
   - Steps to reproduce
   - System information
   - Sample data (if relevant)
3. **Feature requests** should include:
   - Use case description
   - Proposed implementation approach
   - Benefits to the community

### Is there a public API for this system?

Currently, the system is designed as a command-line tool and Python library. A web API is not available, but the system can be integrated into web applications using the Python API.

For programmatic access, see the [API Reference](api-reference.md).

---

## Still need help?

If your question isn't answered here:

1. **Check the documentation**: Browse other docs in the `/docs` folder
2. **Search GitHub issues**: Look for similar problems
3. **Create a new issue**: Ask your question on GitHub
4. **Join discussions**: Participate in GitHub Discussions
5. **Contact maintainers**: Reach out via GitHub or email

We're here to help make tool quality evaluation accessible and useful for the entire community!
