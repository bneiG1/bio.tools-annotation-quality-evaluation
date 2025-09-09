# Export & Reports

The Bio.tools Annotation Quality Evaluation Platform provides comprehensive export and reporting capabilities to help you work with analysis results, share findings, and integrate quality data into your workflows.

## Overview of Export Options

The platform supports multiple export formats and reporting features:

- **JSON Export**: Complete analysis data with full metadata
- **CSV Export**: Tabular data for spreadsheet analysis
- **Interactive Visualizations**: Downloadable charts and graphs
- **Report Generation**: Formatted analysis summaries
- **API Integration**: Programmatic access to results

## Export Formats

### JSON Export

#### Single Tool Analysis

JSON export provides the complete analysis result including all metadata, quality metrics, and recommendations.

**Structure**:
```json
{
  "tool_id": "blast",
  "tool_name": "BLAST",
  "analysis_timestamp": "2025-01-09T10:30:00Z",
  "analysis_version": "2.0.0",
  "tool_data": {
    // Complete bio.tools entry
  },
  "quality_metrics": {
    "overall_score": 85.2,
    "quality_grade": "B",
    "standards_tier": "Tier 3",
    "completeness_score": 78.5,
    // ... other metrics
  },
  "schema_validation": {
    "valid": true,
    "errors": [],
    "warnings": ["Minor formatting issue"]
  },
  "lint_analysis": {
    "total_issues": 12,
    "critical": 0,
    "error": 2,
    "warning": 8,
    "info": 2,
    "issues": [
      // Detailed issue list
    ]
  },
  "recommendations": [
    "Add missing download links",
    "Improve EDAM term coverage"
  ]
}
```

**Use Cases**:
- Programmatic analysis integration
- Detailed quality assessment storage
- Historical analysis tracking
- API consumption

#### Bulk Analysis (Search/Collection)

For multiple tools, JSON export provides an array of individual analyses plus summary statistics.

**Structure**:
```json
{
  "analysis_type": "search",
  "query": "phylogenetic analysis",
  "total_tools": 15,
  "analysis_timestamp": "2025-01-09T10:30:00Z",
  "summary_statistics": {
    "average_score": 72.3,
    "grade_distribution": {
      "A": 2, "B": 4, "C": 6, "D": 2, "F": 1
    },
    "tier_distribution": {
      "Tier 1": 3, "Tier 2": 7, "Tier 3": 4, "Tier 4": 1, "Tier 5": 0
    }
  },
  "tools": [
    // Array of individual tool analyses
  ]
}
```

### CSV Export

#### Single Tool Analysis

CSV export provides a flattened view of quality metrics suitable for spreadsheet analysis.

**Columns**:
- `tool_id`: Bio.tools identifier
- `tool_name`: Tool name
- `overall_score`: Numerical quality score (0-100)
- `quality_grade`: Letter grade (A-F)
- `standards_tier`: ELIXIR tier (1-5)
- `completeness_score`: Field completion percentage
- `schema_valid`: Schema validation status
- `schema_errors`: Number of schema errors
- `lint_issues_total`: Total linting issues
- `lint_critical`: Critical issues count
- `lint_error`: Error issues count
- `lint_warning`: Warning issues count
- `lint_info`: Info issues count
- `analysis_date`: Analysis timestamp

#### Bulk Analysis

For multiple tools, CSV provides one row per tool with consistent columns for easy comparison and analysis.

**Example**:
```csv
tool_id,tool_name,overall_score,quality_grade,standards_tier,completeness_score
blast,BLAST,85.2,B,3,78.5
clustalw,ClustalW,72.1,C,2,65.3
muscle,MUSCLE,88.7,B,3,82.1
```

**Use Cases**:
- Statistical analysis in R, Python, or Excel
- Quality trend analysis
- Comparative studies
- Report generation

## Interactive Visualizations

### Downloadable Charts

All visualizations in the platform can be downloaded in multiple formats:

#### Supported Formats
- **PNG**: High-quality raster images (300 DPI)
- **SVG**: Vector graphics for scalability
- **PDF**: Print-ready documents
- **HTML**: Interactive web elements

#### Chart Types

**Radar Charts**:
- Multi-dimensional quality visualization
- Customizable dimensions and scales
- Tool comparison overlays

**Distribution Charts**:
- Quality grade histograms
- Score distribution curves
- Tier compliance breakdowns

**Comparative Charts**:
- Side-by-side tool comparisons
- Trend analysis over time
- Domain-specific quality patterns

### Customization Options

#### Chart Appearance
- Color schemes and themes
- Axis labels and titles
- Legend positioning
- Size and resolution settings

#### Data Selection
- Metric filtering
- Time range selection
- Tool subset selection
- Aggregation levels

## Report Generation

### Automated Reports

The platform can generate comprehensive reports for different audiences:

#### Executive Summary
- High-level quality overview
- Key findings and recommendations
- Strategic improvement priorities
- Resource allocation suggestions

#### Technical Report
- Detailed methodology description
- Complete quality metrics breakdown
- Issue categorization and prioritization
- Implementation roadmap

#### Community Report
- Domain-specific quality assessment
- Benchmarking against registry average
- Best practice examples
- Collaboration opportunities

### Custom Reports

#### Report Builder
Users can create custom reports by selecting:

- **Scope**: Single tool, collection, or domain
- **Metrics**: Specific quality dimensions
- **Format**: PDF, HTML, or web-based
- **Audience**: Technical, managerial, or community

#### Template Options
- **Quality Assessment Template**: Standard quality evaluation
- **Improvement Plan Template**: Action-oriented recommendations
- **Benchmark Report Template**: Comparative analysis
- **Progress Report Template**: Change tracking over time

## Working with Exported Data

### Data Analysis Workflows

#### Statistical Analysis

**R Example**:
```r
# Load quality assessment data
quality_data <- read.csv("biotools_quality_analysis.csv")

# Basic statistics
summary(quality_data$overall_score)
table(quality_data$quality_grade)

# Quality score distribution
hist(quality_data$overall_score, 
     main="Bio.tools Quality Score Distribution",
     xlab="Quality Score", ylab="Frequency")

# Grade by tier analysis
library(ggplot2)
ggplot(quality_data, aes(x=standards_tier, fill=quality_grade)) +
  geom_bar(position="stack") +
  labs(title="Quality Grade Distribution by Standards Tier")
```

**Python Example**:
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load and analyze data
df = pd.read_csv('biotools_quality_analysis.csv')

# Basic statistics
print(df['overall_score'].describe())
print(df['quality_grade'].value_counts())

# Visualization
plt.figure(figsize=(12, 6))

# Score distribution
plt.subplot(1, 2, 1)
df['overall_score'].hist(bins=20)
plt.title('Quality Score Distribution')
plt.xlabel('Quality Score')
plt.ylabel('Frequency')

# Grade by completeness
plt.subplot(1, 2, 2)
sns.boxplot(data=df, x='quality_grade', y='completeness_score')
plt.title('Completeness Score by Quality Grade')

plt.tight_layout()
plt.show()
```

#### Integration with Other Tools

**Excel/Google Sheets**:
- Import CSV data for pivot tables
- Create dashboards with charts and graphs
- Use conditional formatting for quality highlighting
- Generate automated reports with formulas

**Database Integration**:
- Import JSON/CSV into PostgreSQL, MySQL, or MongoDB
- Create quality tracking databases
- Build historical analysis capabilities
- Implement automated quality monitoring

### Data Validation and Quality Checks

#### Data Integrity Verification
```python
import pandas as pd
import json

def validate_export_data(filepath):
    """Validate exported quality assessment data"""
    
    # Load data
    if filepath.endswith('.json'):
        with open(filepath) as f:
            data = json.load(f)
        # Validate JSON structure
        required_fields = ['tool_id', 'quality_metrics', 'analysis_timestamp']
        return all(field in data for field in required_fields)
    
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
        # Validate CSV structure
        required_columns = ['tool_id', 'overall_score', 'quality_grade']
        return all(col in df.columns for col in required_columns)
```

## API Integration

### Programmatic Access

The platform provides API endpoints for programmatic access to analysis results:

#### Endpoints
- `GET /api/analysis/{tool_id}`: Single tool analysis
- `GET /api/search`: Search and analysis results
- `GET /api/collection/{collection_id}`: Collection analysis
- `GET /api/export/{analysis_id}`: Export specific analysis

#### Authentication
```python
import requests

# API configuration
api_base = "https://biotools-quality-api.example.com"
headers = {"Authorization": "Bearer your_api_token"}

# Get analysis results
response = requests.get(
    f"{api_base}/api/analysis/blast",
    headers=headers
)

if response.status_code == 200:
    analysis_data = response.json()
    print(f"Quality Grade: {analysis_data['quality_metrics']['quality_grade']}")
```

### Batch Processing

#### Automated Analysis Pipeline
```python
import time
import json
from pathlib import Path

def batch_analyze_tools(tool_list, output_dir):
    """Analyze multiple tools and save results"""
    
    results = []
    for tool_id in tool_list:
        # Analyze tool (API call or direct function)
        analysis = analyze_tool(tool_id)
        results.append(analysis)
        
        # Save individual result
        output_file = Path(output_dir) / f"{tool_id}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Rate limiting
        time.sleep(1)
    
    # Save combined results
    combined_file = Path(output_dir) / "batch_analysis.json"
    with open(combined_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results
```

## Sharing and Collaboration

### Report Sharing

#### Web-based Sharing
- Generate shareable URLs for analysis results
- Embed interactive visualizations in websites
- Create public dashboards for community access
- Implement collaborative annotation features

#### Version Control Integration
```bash
# Add analysis results to Git repository
git add analysis_results/
git commit -m "Add quality analysis for tool collection X"
git push origin main

# Create analysis report branch
git checkout -b quality-report-2025-01
git add quality_report.pdf
git commit -m "Add comprehensive quality assessment report"
```

### Community Contributions

#### Quality Improvement Collaboration
- Share analysis results with tool developers
- Coordinate improvement efforts across communities
- Track progress on quality enhancement initiatives
- Facilitate knowledge sharing and best practices

#### Data Sharing Protocols
- Standardized export formats for cross-platform compatibility
- Metadata preservation for reproducibility
- Attribution and citation guidelines
- Privacy and data protection compliance

## Best Practices for Export and Reporting

### Data Management

#### File Organization
```
analysis_results/
├── single_tools/
│   ├── blast_2025-01-09.json
│   ├── clustalw_2025-01-09.json
│   └── ...
├── collections/
│   ├── covid19_tools_2025-01-09.csv
│   ├── phylogeny_tools_2025-01-09.json
│   └── ...
├── reports/
│   ├── monthly_quality_report_2025-01.pdf
│   ├── domain_comparison_2025-01.html
│   └── ...
└── visualizations/
    ├── quality_trends.png
    ├── tier_distribution.svg
    └── ...
```

#### Metadata Preservation
- Include analysis timestamps and version information
- Document analysis parameters and configuration
- Preserve original tool data alongside quality metrics
- Maintain audit trails for changes and updates

### Quality Assurance

#### Result Validation
- Cross-check exported data against source analysis
- Verify data completeness and accuracy
- Test import/export round-trip integrity
- Validate chart data consistency

#### Documentation Standards
- Include methodology descriptions in exports
- Document data schema and field definitions
- Provide usage examples and interpretation guides
- Maintain version compatibility information

### Performance Optimization

#### Large Dataset Handling
- Use streaming for large export operations
- Implement pagination for bulk data access
- Compress export files when appropriate
- Cache frequently accessed analysis results

#### Export Efficiency
```python
def efficient_bulk_export(tool_list, format='csv', chunk_size=100):
    """Efficiently export large numbers of tool analyses"""
    
    if format == 'csv':
        # Stream CSV writing for memory efficiency
        with open('bulk_analysis.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            
            for i in range(0, len(tool_list), chunk_size):
                chunk = tool_list[i:i+chunk_size]
                analyses = batch_analyze(chunk)
                for analysis in analyses:
                    writer.writerow(flatten_analysis(analysis))
    
    elif format == 'json':
        # Use JSON streaming for large datasets
        with open('bulk_analysis.json', 'w') as jsonfile:
            jsonfile.write('[\n')
            for i, tool_id in enumerate(tool_list):
                if i > 0:
                    jsonfile.write(',\n')
                analysis = analyze_tool(tool_id)
                json.dump(analysis, jsonfile, indent=2)
            jsonfile.write('\n]')
```

## Troubleshooting Export Issues

### Common Problems

#### Large File Exports
**Issue**: Export timeouts or memory errors with large datasets
**Solutions**:
- Use chunked/streaming exports
- Export subsets and combine manually
- Choose more efficient formats (CSV vs JSON)
- Contact support for enterprise solutions

#### Data Format Issues
**Issue**: Exported data not importing correctly into other tools
**Solutions**:
- Verify field mappings and data types
- Check character encoding (UTF-8 recommended)
- Validate JSON syntax before import
- Use standard CSV delimiters and quoting

#### Missing Data
**Issue**: Incomplete analysis results in exports
**Solutions**:
- Check analysis completion status
- Retry failed analyses
- Verify API access permissions
- Report persistent issues to support

### Support Resources

- **Documentation**: Detailed export format specifications
- **Examples**: Sample export files and import scripts
- **API Reference**: Complete endpoint documentation
- **Community Forum**: User discussions and solutions

## Next Steps

- **[Examples](../examples/basic-usage.md)**: See practical export and reporting examples
- **[API Documentation](../api/)**: Detailed technical reference
- **[Developer Guide](../developer/)**: Advanced integration techniques
