# Bio.tools CLI Documentation

## Overview

The Bio.tools Quality Analysis CLI provides a command-line interface for fetching bio.tools data, performing quality analysis, and exporting results in multiple formats (JSON, CSV, Excel).

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd bio.tools-annotation-quality-evaluation
   ```

2. **Set up Python environment**:
   ```powershell
   # PowerShell (Windows)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```powershell
   python biotools_cli.py --help
   ```

## Usage

### Basic Syntax

```bash
python biotools_cli.py [OPTIONS]
```

Or use the convenience scripts:
- **PowerShell**: `.\biotools-cli.ps1 [OPTIONS]`
- **Batch**: `biotools-cli.bat [OPTIONS]`
- **Python module**: `python -m src [OPTIONS]`

### Options

#### Data Fetching
- `--tool-id TOOL_ID`: Fetch specific tool(s) by ID (can be used multiple times)
- `--search QUERY`: Search tools by query string
- `--domain DOMAIN`: Filter by scientific domain (e.g., "Genomics", "Proteomics")
- `--format FORMAT`: Filter by data format
- `--limit N`: Limit number of tools to fetch

#### Processing
- `--analyze`: Perform quality analysis (default: True)
- `--no-analyze`: Skip quality analysis, only fetch raw data
- `--save-raw`: Save raw API data (default: True)
- `--cache`: Use local caching for API requests (default: True)

#### Export Formats
- `--export-csv`: Export analysis results to CSV
- `--export-excel`: Export analysis results to Excel (with multiple sheets)
- `--export-json`: Export analysis results to JSON
- `--export-all`: Export to all formats (CSV, Excel, JSON)

#### Output
- `--output-dir DIR`: Base output directory (default: ./data)

## Examples

### 1. Fetch Specific Tools

```powershell
# Fetch and analyze specific tools
python biotools_cli.py --tool-id blast --tool-id clustalw --analyze --export-all

# Using PowerShell wrapper
.\biotools-cli.ps1 --tool-id blast --tool-id clustalw --analyze --export-all
```

### 2. Search and Analyze Tools

```powershell
# Search for alignment tools, limit to 10, export to CSV
python biotools_cli.py --search "alignment" --limit 10 --analyze --export-csv

# Search by domain and export to Excel
python biotools_cli.py --domain "Genomics" --limit 50 --analyze --export-excel
```

### 3. Fetch Raw Data Only

```powershell
# Just fetch and save raw data without analysis
python biotools_cli.py --search "phylogeny" --save-raw --no-analyze
```

### 4. Complex Query

```powershell
# Search for tools with specific format, analyze, and export all formats
python biotools_cli.py --search "protein structure" --format "PDB" --limit 20 --analyze --export-all --output-dir ./my_analysis
```

## Output Structure

The CLI creates the following directory structure:

```
data/                           # Base output directory
├── raw/                        # Raw JSON data from bio.tools API
│   ├── cache/                  # Cached API responses
│   └── biotools_raw_YYYYMMDD_HHMMSS.json
├── processed/                  # Processed data (future use)
├── reports/                    # Generated visualizations (future use)
└── exports/                    # Final export files
    ├── biotools_quality_YYYYMMDD_HHMMSS.csv
    ├── biotools_quality_YYYYMMDD_HHMMSS.xlsx
    └── biotools_quality_YYYYMMDD_HHMMSS.json
```

## Export Formats

### CSV Export
Single CSV file with flattened quality metrics for easy analysis in spreadsheet applications.

**Columns include:**
- Tool identification (tool_id, tool_name)
- Quality scores (overall_score, quality_grade, standards_score, completeness_score)
- Validation results (schema_valid, schema_errors, lint_issues)
- Completeness metrics (field_completeness, required_fields_complete)
- Content quality indicators (url_health, edam_consistency, publication_quality)

### Excel Export
Multi-sheet Excel workbook with organized data:

1. **Summary Sheet**: High-level overview of all tools
2. **Detailed Metrics Sheet**: Complete quality metrics for each tool
3. **Issues Summary Sheet**: Detailed breakdown of validation issues

### JSON Export
Structured JSON with complete analysis results including:
- Full quality reports for each tool
- Detailed recommendations and priority fixes
- Metadata about the analysis run

## Common Use Cases

### 1. Quality Assessment of Tool Collection

```powershell
# Analyze tools from a specific domain
python biotools_cli.py --domain "Proteomics" --limit 100 --analyze --export-excel
```

### 2. Monitoring Tool Quality Over Time

```powershell
# Regular quality check with timestamped output
python biotools_cli.py --search "your_tools_query" --analyze --export-all --output-dir ./quality_monitoring
```

### 3. Data Export for External Analysis

```powershell
# Export to CSV for analysis in R, Python, or other tools
python biotools_cli.py --tool-id tool1 --tool-id tool2 --analyze --export-csv
```

### 4. Bulk Data Collection

```powershell
# Collect large dataset with caching
python biotools_cli.py --search "*" --limit 1000 --save-raw --cache --no-analyze
```

## Advanced Features

### Caching
The CLI automatically caches API responses to avoid repeated requests:
- Cache files are stored in `data/raw/cache/`
- Cache files are named based on request parameters
- Individual tool requests are cached by tool ID

### Logging
The CLI generates detailed logs:
- Console output shows progress and key information
- Detailed logs are saved to `biotools_cli.log`
- Log level can be controlled through the logging configuration

### Error Handling
- Network issues are handled gracefully with retries
- Missing tools are logged as warnings but don't stop processing
- Analysis errors for individual tools are logged but processing continues

## Troubleshooting

### Common Issues

1. **Python not found**:
   - Ensure Python 3.8+ is installed
   - Verify Python is in your system PATH

2. **Import errors**:
   - Activate your virtual environment
   - Run `pip install -r requirements.txt`

3. **Network timeouts**:
   - Check internet connection
   - The CLI will retry failed requests automatically

4. **No data returned**:
   - Verify your search criteria
   - Check if the tools exist in bio.tools
   - Use broader search terms

### Getting Help

```powershell
# Show help message
python biotools_cli.py --help

# Show version and detailed examples
python biotools_cli.py --help
```

## Integration with Other Tools

The CLI can be integrated into automated workflows:

### PowerShell Automation
```powershell
# Automated daily quality check
$date = Get-Date -Format "yyyyMMdd"
python biotools_cli.py --domain "Genomics" --limit 50 --analyze --export-all --output-dir "./daily_reports/$date"
```

### Batch Processing
```batch
REM Process multiple domains
for %%d in ("Genomics" "Proteomics" "Phylogenetics") do (
    python biotools_cli.py --domain %%d --limit 100 --analyze --export-csv --output-dir "./domain_analysis/%%d"
)
```

## Performance Considerations

- **Rate Limiting**: The CLI respects bio.tools API rate limits
- **Caching**: Use `--cache` to avoid repeated API calls
- **Batch Size**: For large datasets, consider using `--limit` to process in chunks
- **Memory Usage**: Analysis of very large datasets may require significant memory

## API Rate Limits

The bio.tools API has rate limits:
- The CLI includes automatic rate limiting (1 second between requests by default)
- For large datasets, expect longer processing times
- Use caching to minimize API calls during development/testing
