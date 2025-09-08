# Bio.tools Data Collection - Command Line Usage

The `main.py` script now supports comprehensive command line arguments for flexible data collection from the bio.tools API.

## Quick Start Examples

### Basic Usage

```bash
# Collect first 100 tools for testing
python main.py --max-tools 100

# Collect all tools (~30,000+) with maximum efficiency
python main.py --page-size 100

# Dry run to see what would be collected
python main.py --dry-run --max-tools 1000
```

### Different Save Modes

```bash
# Save all tools in one large file (default)
python main.py --max-tools 100 --save-mode single

# Save each tool as individual JSON files
python main.py --max-tools 50 --save-mode individual --individual-format json

# Save each tool as individual XML files
python main.py --max-tools 50 --save-mode individual --individual-format xml

# Save tools in batches of 1000 (good for large collections)
python main.py --save-mode batch --batch-size 1000
```

### Advanced Usage

```bash
# Custom output file and slower API calls
python main.py --max-tools 500 --delay 1.0 --output my_biotools.json

# Debug mode with verbose logging
python main.py --max-tools 50 --log-level DEBUG

# Stats only mode (count tools without saving data)
python main.py --stats-only --max-tools 1000

# Resume from a specific page
python main.py --start-page 10 --max-tools 1000
```

## Complete Argument Reference

### Data Collection
- `--max-tools N`: Limit collection to N tools (default: all ~30,000)
- `--page-size N`: Tools per API page, 1-100 (default: 100)
- `--start-page N`: Start from page N (default: 1)
- `--base-url URL`: Custom API endpoint (default: bio.tools API)

### Output Control
- `--output FILE`, `-o FILE`: Save to specific file
- `--stats-only`: Count tools without saving data
- `--dry-run`: Show collection plan without API calls

### API Behavior
- `--delay N`: Seconds between requests (default: 0.5)
- `--timeout N`: Request timeout in seconds (default: 30)
- `--retries N`: Max retry attempts (default: 3)

### Logging
- `--log-level LEVEL`: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `--log-file FILE`: Custom log file path
- `--quiet`, `-q`: No console output (file logging only)

### Advanced
- `--resume FILE`: Resume from partial collection file (not yet implemented)

## Output Files

### Default Structure
```
data/raw/
├── biotools_complete_YYYYMMDD_HHMMSS.json  # Full tool data
├── collection_summary_YYYYMMDD_HHMMSS.json # Collection metadata
└── biotools_partial_XXpages.json           # Intermediate backups (every 10 pages)
```

### Summary File Contents
```json
{
  "collection_date": "2025-09-08 23:56:33",
  "total_tools": 1000,
  "api_total_count": 30538,
  "pages_fetched": 10,
  "data_file": "data/raw/biotools_complete_20250908_235633.json"
}
```

## Common Usage Patterns

### Development & Testing
```bash
# Quick test with 10 tools
python main.py --max-tools 10 --log-level DEBUG

# Profile API performance
python main.py --stats-only --max-tools 100 --delay 0.1
```

### Production Data Collection
```bash
# Collect all tools with conservative API usage
python main.py --page-size 100 --delay 1.0 --log-level INFO

# Collect specific domain subset (future feature)
python main.py --domain proteomics --max-tools 5000
```

### Large Scale Collection
```bash
# Full dataset with efficient settings
python main.py --page-size 100 --delay 0.5 --log-file full_collection.log

# Resume interrupted collection (future feature)
python main.py --resume data/raw/biotools_partial_150pages.json
```

## Error Handling

The tool includes robust error handling:
- Automatic retries for failed requests
- Exponential backoff for rate limiting
- Intermediate file saves every 10 pages
- Graceful handling of network interruptions
- Comprehensive logging for debugging

## Performance Notes

- **Page size**: Use 100 for maximum efficiency
- **Delay**: 0.5s is respectful to the API; increase if rate limited
- **Memory**: Full collection (~30K tools) uses ~500MB RAM
- **Time**: Full collection takes ~15-20 minutes with default settings
- **Disk**: Full dataset is approximately 50-100MB as JSON

## Integration with Pipeline

This data collection tool is the first stage of the bio.tools quality evaluation pipeline:

1. **Data Collection** ← You are here
2. Schema Validation
3. Quality Scoring
4. Linter Integration  
5. Report Generation

The collected JSON files can be directly used by the validation and scoring modules.
