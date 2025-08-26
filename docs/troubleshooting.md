# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the bio.tools Annotation Quality Evaluation system.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [API Connection Problems](#api-connection-problems)
3. [Configuration Errors](#configuration-errors)
4. [Performance Issues](#performance-issues)
5. [Visualization Problems](#visualization-problems)
6. [Data Quality Issues](#data-quality-issues)
7. [Getting Help](#getting-help)

## Installation Issues

### Python Version Incompatibility

**Symptoms:**
```
ERROR: This package requires Python >=3.8
SyntaxError: invalid syntax
```

**Solution:**
```bash
# Check Python version
python --version

# If too old, install newer Python or use pyenv
pyenv install 3.9.0
pyenv local 3.9.0
```

### Permission Denied During Installation

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. **Use virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Use user installation:**
   ```bash
   pip install --user -r requirements.txt
   ```

### Missing System Dependencies

**Symptoms:**
```
ImportError: cannot import name 'xxx' from 'xxx'
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
# Update pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# For visualization issues on Linux:
sudo apt-get install python3-tk

# For macOS:
brew install python-tk
```

## API Connection Problems

### Bio.tools API Not Responding

**Symptoms:**
```
requests.exceptions.ConnectionError: Failed to establish a new connection
requests.exceptions.Timeout: Read timed out
```

**Diagnosis:**
```bash
# Test API connectivity
curl -I "https://bio.tools/api/tool/"

# Or in Python:
python -c "import requests; print(requests.get('https://bio.tools/api/tool/').status_code)"
```

**Solutions:**
1. **Check internet connection**
2. **Verify bio.tools API status**: Visit https://bio.tools/api/
3. **Increase timeout settings**: Modify configuration
4. **Use proxy settings** if behind corporate firewall

### Rate Limiting Issues

**Symptoms:**
```
HTTP 429: Too Many Requests
Rate limit exceeded
```

**Solutions:**
1. **Built-in retry logic**: The system handles this automatically
2. **Reduce batch size**:
   ```bash
   python scripts/run_evaluation.py --topic Test --limit 10
   ```
3. **Increase delays** in configuration:
   ```yaml
   system:
     api:
       rate_limit_delay: 1.0  # Increase from default 0.1
   ```

### SSL/TLS Certificate Issues

**Symptoms:**
```
requests.exceptions.SSLError: certificate verify failed
```

**Solutions:**
1. **Update certificates**:
   ```bash
   pip install --upgrade certifi
   ```
2. **Temporary workaround** (not recommended for production):
   ```python
   import urllib3
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
   ```

## Configuration Errors

### Invalid YAML Syntax

**Symptoms:**
```
yaml.scanner.ScannerError: while parsing a block mapping
ParserError: while parsing a block collection
```

**Diagnosis:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/my_config.yaml'))"
```

**Solutions:**
1. **Check indentation**: Use spaces, not tabs
2. **Validate structure**: Ensure proper nesting
3. **Use YAML validator**: Online tools or IDE plugins

### Weight Configuration Errors

**Symptoms:**
```
ValueError: Category weights must sum to 100, got 95.0
ConfigurationError: Invalid tier thresholds
```

**Solutions:**
1. **Check weight sum**:
   ```yaml
   scoring:
     weights:
       basic_info: 15
       core_metadata: 25
       technical_info: 20
       accessibility: 20
       advanced_features: 15
       community: 5        # Total = 100
   ```

2. **Validate tier ranges**:
   ```yaml
   tiers:
     tier_1: [0, 15]      # No gaps or overlaps
     tier_2: [16, 40]
     # etc.
   ```

### File Path Issues

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory
```

**Solutions:**
1. **Use absolute paths**:
   ```bash
   python scripts/run_evaluation.py --config /full/path/to/config.yaml
   ```
2. **Check current directory**:
   ```bash
   pwd  # Should be in project root
   ```
3. **Verify file exists**:
   ```bash
   ls -la config/scoring_config.yaml
   ```

## Performance Issues

### Slow Evaluation Speed

**Symptoms:**
- Long wait times between API calls
- High memory usage
- Slow processing of results

**Diagnosis:**
```bash
# Run with timing and debugging
time python scripts/run_evaluation.py --topic Test --limit 10 --log-level DEBUG
```

**Solutions:**
1. **Reduce batch size**:
   ```bash
   python scripts/run_evaluation.py --topic Test --limit 50
   ```

2. **Check network latency**:
   ```bash
   ping bio.tools
   ```

3. **Monitor system resources**:
   ```bash
   # Linux/Mac
   top -p $(pgrep python)
   
   # Windows
   tasklist | findstr python
   ```

4. **Use caching** (enabled by default)
5. **Process during off-peak hours**

### Memory Usage Issues

**Symptoms:**
```
MemoryError: Unable to allocate array
Process killed (out of memory)
```

**Solutions:**
1. **Process smaller batches**:
   ```python
   # Custom batch processing
   for i in range(0, total_tools, 100):
       batch = tools[i:i+100]
       process_batch(batch)
   ```

2. **Clear cache periodically**:
   ```bash
   rm -rf .cache/
   ```

3. **Use streaming processing** for large datasets
4. **Increase system memory** or use cloud instance

### Disk Space Issues

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Solutions:**
1. **Clean old results**:
   ```bash
   find data/processed -name "*.json" -mtime +30 -delete
   ```

2. **Compress large files**:
   ```bash
   gzip data/processed/*.json
   ```

3. **Use external storage** for large analyses

## Visualization Problems

### Charts Not Displaying

**Symptoms:**
- Empty visualization files
- "No display available" errors
- Missing chart files

**Solutions:**
1. **Install display dependencies**:
   ```bash
   # Linux
   sudo apt-get install xvfb
   export DISPLAY=:0
   
   # Or use headless backend
   export MPLBACKEND=Agg
   ```

2. **Check plotting backend**:
   ```python
   import matplotlib
   print(matplotlib.get_backend())
   matplotlib.use('Agg')  # For headless environments
   ```

3. **Verify output permissions**:
   ```bash
   mkdir -p data/visualizations
   chmod 755 data/visualizations
   ```

### Chart Formatting Issues

**Symptoms:**
- Overlapping text
- Cut-off labels
- Poor quality images

**Solutions:**
1. **Adjust figure size** in code
2. **Increase DPI** for better quality:
   ```python
   plt.savefig('chart.png', dpi=300, bbox_inches='tight')
   ```
3. **Use different file format**:
   ```bash
   # Generate SVG instead of PNG
   python scripts/run_evaluation.py --visualize --chart-format svg
   ```

### Interactive Dashboard Issues

**Symptoms:**
- Dashboard won't load
- JavaScript errors
- Missing interactive features

**Solutions:**
1. **Check browser compatibility**: Use modern browser
2. **Enable JavaScript**: Required for interactivity
3. **Check file paths**: Ensure relative paths are correct
4. **Test locally**:
   ```bash
   python -m http.server 8000
   # Open http://localhost:8000/dashboard/
   ```

## Data Quality Issues

### Inconsistent Results

**Symptoms:**
- Scores varying between runs
- Missing tools in results
- Unexpected tier assignments

**Diagnosis:**
```bash
# Run with detailed logging
python scripts/run_evaluation.py --log-level DEBUG --topic Test --limit 5
```

**Solutions:**
1. **Check API data consistency**: bio.tools data may change
2. **Verify configuration**: Ensure consistent scoring settings
3. **Clear cache** if using stale data:
   ```bash
   rm -rf .cache/
   ```

### Missing Tool Data

**Symptoms:**
```
KeyError: 'biotoolsID'
Tool data incomplete or malformed
```

**Solutions:**
1. **Enable graceful error handling**: Built-in by default
2. **Filter incomplete tools**:
   ```python
   valid_tools = [tool for tool in tools if 'biotoolsID' in tool]
   ```
3. **Report data issues** to bio.tools maintainers

### Scoring Anomalies

**Symptoms:**
- Unexpectedly high/low scores
- Inconsistent tier assignments
- Missing category scores

**Solutions:**
1. **Review detailed scoring breakdown**:
   ```python
   detailed = scorer.get_detailed_score(tool_data)
   print(json.dumps(detailed, indent=2))
   ```
2. **Validate tool data structure**
3. **Check configuration weights**
4. **Compare with manual assessment**

## Getting Help

### Enable Debug Logging

Always enable debug logging when troubleshooting:
```bash
python scripts/run_evaluation.py --log-level DEBUG --topic Test --limit 5
```

Check the log file:
```bash
tail -f evaluation.log
```

### Collect System Information

When reporting issues, include:

```bash
# System information
python --version
pip list | grep -E "(requests|pandas|matplotlib|seaborn)"
uname -a  # Linux/Mac

# Error details
cat evaluation.log | tail -50

# Configuration
cat config/scoring_config.yaml
```

### Test with Minimal Example

Isolate issues with minimal test:
```bash
# Test API connectivity
python -c "
from src.data_collection.api_client import BioToolsAPIClient
client = BioToolsAPIClient()
tools = client.get_tools_by_topic('Test', limit=1)
print(f'Retrieved {len(tools)} tools')
"

# Test scoring
python -c "
from src.scoring.completeness_scorer import CompletenessScorer
scorer = CompletenessScorer()
score = scorer.score_tool({'name': 'Test', 'description': 'Test tool'})
print(f'Score: {score}')
"
```

### Common Quick Fixes

Before reporting issues, try these quick fixes:

1. **Restart the process**: Kill any hanging processes
2. **Clear cache**: `rm -rf .cache/`
3. **Update dependencies**: `pip install -r requirements.txt --upgrade`
4. **Check disk space**: `df -h`
5. **Verify network**: `ping bio.tools`
6. **Test with small dataset**: Use `--limit 5`

### When to Report Issues

Report issues on GitHub when:
- Error persists after trying troubleshooting steps
- System behavior is inconsistent or unexpected
- Documentation is unclear or incorrect
- Feature is missing or broken

Include in your issue report:
1. **Clear description** of the problem
2. **Steps to reproduce** the issue
3. **Expected vs. actual behavior**
4. **System information** and logs
5. **Configuration files** (if relevant)
6. **Sample data** (if applicable)

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and get help
- **Documentation**: Check other docs for detailed information
- **Code Examples**: Review examples in `docs/examples.md`

Remember: The community is here to help! Don't hesitate to ask questions or report issues.
