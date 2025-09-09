# Per-Tool Analysis Guide

This guide explains how to generate individual files for each bio.tools entry analyzed, providing comprehensive quality assessment data for each tool separately in multiple formats.

## Features

- **Multiple file formats**: JSON, CSV, Excel, and HTML outputs
- **Individual files**: Each tool gets its own detailed analysis file
- **Comprehensive analysis**: Includes all quality metrics, linting results, standards compliance, and recommendations
- **Structured output**: Files are organized in a dedicated `per_tool_analysis` subdirectory
- **Flexible input**: Analyze specific tools, collections, search results, or cached data
- **Batch export**: Generate files in multiple formats simultaneously

## Supported File Formats

### 1. JSON Format
- **Purpose**: Machine-readable structured data
- **Content**: Complete analysis data including nested objects
- **Use case**: API integration, automated processing, data analysis

### 2. CSV Format  
- **Purpose**: Tabular data for spreadsheets and data analysis
- **Content**: Flattened metrics and summary data
- **Use case**: Excel analysis, database import, statistical analysis

### 3. Excel Format (.xlsx)
- **Purpose**: Rich multi-sheet reports
- **Content**: Multiple sheets with different data views:
  - Quality_Metrics: Main quality scores
  - Tool_Details: Detailed tool information
  - Lint_Issues: Quality issues with suggestions
  - Recommendations: Improvement suggestions
  - Standards_Analysis: Field-by-field compliance
- **Use case**: Detailed manual review, formatted reporting

### 4. HTML Format
- **Purpose**: Human-readable visual reports
- **Content**: Styled web pages with charts and visual elements
- **Use case**: Web viewing, presentations, visual review

## Methods to Generate Per-Tool Files

### Method 1: Dedicated Per-Tool Analysis Command

Use the `per-tool-analysis` command specifically designed for this purpose:

```bash
# Single format (JSON, CSV, Excel, or HTML)
python main.py per-tool-analysis -t blast --format json
python main.py per-tool-analysis -t blast --format csv
python main.py per-tool-analysis -t blast --format excel
python main.py per-tool-analysis -t blast --format html

# All formats at once
python main.py per-tool-analysis -t blast --format all

# Multiple tools in specific format
python main.py per-tool-analysis -t blast -t clustalw --format excel

# Analyze tools from a collection
python main.py per-tool-analysis -c "Sequence analysis" --format all

# Search and analyze tools
python main.py per-tool-analysis -q "phylogeny" --max-tools 10 --format csv

# Specify custom output directory
python main.py per-tool-analysis -t blast --output-dir my_analysis --format html
```

### Method 2: Add Per-Tool Options to Existing Commands

Add per-tool export options to existing analysis commands:

```bash
# Legacy per-tool JSON option (for backward compatibility)
python main.py analyze -t blast --format json --per-tool-json

# New multi-format per-tool option
python main.py analyze -t blast --format json --per-tool-formats csv
python main.py analyze -t blast --format json --per-tool-formats csv --per-tool-formats html
python main.py analyze -t blast --format json --per-tool-formats excel --per-tool-formats json

# Batch analysis with per-tool exports
python main.py analyze --query "sequence alignment" --max-tools 20 --per-tool-formats html --per-tool-formats excel

# Process cached data with per-tool files
python main.py process-cache --per-tool-formats json --per-tool-formats csv --max-tools 100
```

## Output Structure

Individual files are saved in the `per_tool_analysis` subdirectory with format-specific extensions:

```
data/reports/
├── per_tool_analysis/
│   ├── blast_20250909_040710.json
│   ├── blast_20250909_040558.csv  
│   ├── blast_20250909_040710.html
│   ├── clustalw_20250909_040616.xlsx
│   ├── clustalw_20250909_040739.json
│   ├── clustalw_20250909_040739.csv
│   ├── clustalw_20250909_040739.html
│   └── clustalw_20250909_040739.xlsx
└── combined_analysis_files...
```

## File Content by Format

### JSON Files
Complete structured data with all analysis components:

```json
{
  "tool_id": "blast",
  "tool_name": "BLAST", 
  "metrics": {
    "overall_score": 72.8,
    "quality_grade": "C",
    "standards_tier": "MINIMAL",
    "completeness_score": 57.1,
    "schema_valid": true,
    "lint_issues": 1,
    "field_completeness": 0.7,
    "has_functions": true,
    "has_documentation": true,
    "has_publications": true,
    "has_contacts": true,
    "analysis_date": "2025-09-09T03:59:47.181860"
  },
  "standards_analysis": { /* detailed standards compliance */ },
  "completeness_analysis": { /* Tool Information Standards analysis */ },
  "schema_results": { /* schema validation details */ },
  "lint_issues": [ /* detailed linting results */ ],
  "recommendations": [ /* improvement suggestions */ ],
  "priority_fixes": [ /* urgent issues to address */ ],
  "summary": "Tool blast has fair quality (Grade C, Score: 72.8/100)..."
}
```

### CSV Files
Flattened tabular data with key metrics:

```csv
tool_id,tool_name,overall_score,quality_grade,standards_tier,standards_score,schema_valid,field_completeness,has_functions,has_documentation,has_publications,has_contacts,analysis_date
blast,BLAST,72.8,C,MINIMAL,55.6,True,0.7,True,True,True,True,2025-09-09T04:05:58.644843
```

### Excel Files (.xlsx)
Multi-sheet workbooks with organized data:

- **Quality_Metrics**: Main quality scores and metrics
- **Tool_Details**: Detailed tool information and metadata  
- **Lint_Issues**: Quality issues with levels, codes, messages, and suggestions
- **Recommendations**: Improvement suggestions categorized by priority
- **Standards_Analysis**: Field-by-field compliance analysis

### HTML Files
Styled visual reports with:

- **Quality Overview**: Score cards with color-coded grades
- **Field Completeness**: Progress bars and percentages
- **Content Quality**: Feature status table
- **Schema Validation**: Validation results
- **Quality Issues**: Categorized issue list with suggestions
- **Recommendations**: Priority fixes and improvement suggestions
- **Summary**: Executive summary of findings

## Key Analysis Components

### 1. Quality Metrics

- Overall quality score (0-100)
- Quality grade (A, B, C, D, F)
- Standards tier compliance
- Tool Information Standards completeness score
- Field completeness rates
- Content quality indicators

### 2. Standards Analysis

- Field presence and quality assessment
- Missing field identification
- Standards tier achievement details
- Specific field-level recommendations

### 3. Completeness Analysis (New)

- Based on Tool Information Standards tiers
- Detailed tier progression analysis
- Specific completeness recommendations
- Required vs recommended field analysis

### 4. Schema Validation

- JSON schema compliance
- Detailed error and warning messages
- Structural validation results

### 5. Linting Results

- Comprehensive quality checks
- Issue categorization (critical, error, warning, info)
- Specific suggestions for improvements
- URL validation, EDAM term checking, publication validation

### 6. Recommendations

- Prioritized improvement suggestions
- Critical issues requiring immediate attention
- General quality enhancement recommendations

## Use Cases by Format

### JSON Format Use Cases

```bash
# API integration and automated processing
python main.py per-tool-analysis -t my_tool_id --format json

# Data analysis and machine learning
python main.py per-tool-analysis -c "My Collection" --format json --max-tools 100

# Programmatic quality monitoring
python main.py process-cache --per-tool-formats json --max-tools 1000
```

### CSV Format Use Cases

```bash
# Statistical analysis and database import
python main.py per-tool-analysis -q "sequence analysis" --format csv --max-tools 50

# Spreadsheet analysis
python main.py analyze --query "phylogeny" --per-tool-formats csv --max-tools 20
```

### Excel Format Use Cases

```bash
# Detailed manual review with multiple data views
python main.py per-tool-analysis -t my_tool_id --format excel

# Formatted reporting for stakeholders
python main.py per-tool-analysis -c "Important Tools" --format excel
```

### HTML Format Use Cases

```bash
# Visual review and presentations
python main.py per-tool-analysis -t blast --format html

# Web-based quality dashboards
python main.py per-tool-analysis -q "genomics" --format html --max-tools 10
```

### Multi-Format Use Cases

```bash
# Complete analysis suite for important tools
python main.py per-tool-analysis -t blast -t clustalw --format all

# Comprehensive collection analysis
python main.py per-tool-analysis -c "Core Tools" --format all

# Mixed format export for different audiences
python main.py analyze -t my_tool --per-tool-formats json --per-tool-formats html --per-tool-formats excel
```

## Benefits by Format

### JSON Benefits
1. **Machine-readable**: Easy automated processing
2. **Complete data**: All analysis details included
3. **API integration**: Direct import into other systems
4. **Version control**: Text-based format for tracking changes

### CSV Benefits  
1. **Spreadsheet compatible**: Direct Excel/Google Sheets import
2. **Database ready**: Easy database table import
3. **Statistical analysis**: R, Python pandas compatibility
4. **Lightweight**: Minimal file size

### Excel Benefits
1. **Multi-dimensional**: Multiple sheets with different views
2. **Professional reports**: Formatted for business use
3. **Interactive**: Built-in Excel analysis capabilities  
4. **Comprehensive**: All data organized in logical sheets

### HTML Benefits
1. **Visual appeal**: Styled reports with charts and colors
2. **No software required**: View in any web browser
3. **Presentation ready**: Professional appearance
4. **Interactive elements**: Progress bars, color-coded grades

## File Naming Convention

Files are named using the pattern: `{tool_id}_{timestamp}.{extension}`

- `tool_id`: The bio.tools ID (sanitized for filesystem compatibility)
- `timestamp`: Analysis timestamp (YYYYMMDD_HHMMSS)
- `extension`: Format-specific extension (json, csv, xlsx, html)

Special characters in tool IDs are replaced with underscores for file system compatibility.

## Advanced Usage Examples

### Comprehensive Multi-Tool Analysis
```bash
# Generate all formats for multiple specific tools
python main.py per-tool-analysis -t blast -t clustalw -t muscle --format all

# Generate specific formats for a collection
python main.py per-tool-analysis -c "Sequence Analysis" --format excel --format html

# Mixed approach: combined + individual files
python main.py analyze -c "Important Tools" --format excel --per-tool-formats json --per-tool-formats html
```

### Large-Scale Processing
```bash
# Process cached data with multiple per-tool formats
python main.py process-cache --per-tool-formats json --per-tool-formats csv --chunk-size 500

# Search and export specific formats
python main.py per-tool-analysis -q "machine learning" --format csv --max-tools 100
```

### Custom Output Organization
```bash
# Custom output directory for different projects
python main.py per-tool-analysis -t blast --format all --output-dir projects/blast_analysis

# Project-specific analysis with multiple formats
python main.py per-tool-analysis -c "Project Tools" --format html --format excel --output-dir project_reports
```

## Next Steps

After generating per-tool files in various formats, you can:

1. **JSON files**: Import into analysis tools, APIs, or databases
2. **CSV files**: Load into spreadsheets, R, Python for statistical analysis
3. **Excel files**: Share with stakeholders, perform manual detailed review
4. **HTML files**: Host on web servers, include in presentations
5. **Mixed formats**: Use different formats for different audiences and purposes
6. **Automation**: Integrate file generation into CI/CD pipelines for continuous quality monitoring
7. **Comparison**: Track quality improvements over time across all formats
8. **Reporting**: Generate executive summaries from multiple per-tool analyses
