# API Reference

Complete API documentation for the bio.tools Annotation Quality Evaluation system.

## Table of Contents
1. [Data Collection APIs](#data-collection-apis)
2. [Scoring APIs](#scoring-apis)
3. [Analysis APIs](#analysis-apis)
4. [Visualization APIs](#visualization-apis)
5. [Utility APIs](#utility-apis)
6. [Configuration APIs](#configuration-apis)

## Data Collection APIs

### BioToolsAPIClient

Main client for interacting with the bio.tools API.

#### Constructor

```python
BioToolsAPIClient(
    base_url: str = "https://bio.tools/api",
    timeout: int = 30,
    max_retries: int = 3
)
```

**Parameters:**
- `base_url`: Base URL for the bio.tools API
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum number of retry attempts

#### Methods

##### get_tools_by_topic()

```python
get_tools_by_topic(
    topic: str,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]
```

Retrieve tools by scientific topic.

**Parameters:**
- `topic`: Scientific topic name (e.g., "Proteomics", "Genomics")
- `limit`: Maximum number of tools to retrieve (0 for no limit)  
- `offset`: Starting offset for pagination

**Returns:**
- `List[Dict]`: List of tool metadata dictionaries

**Example:**
```python
client = BioToolsAPIClient()
tools = client.get_tools_by_topic("Proteomics", limit=50)
print(f"Retrieved {len(tools)} proteomics tools")
```

##### get_tools_by_collection()

```python
get_tools_by_collection(
    collection: str,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]
```

Retrieve tools from a specific collection.

**Parameters:**
- `collection`: Collection name (e.g., "Galaxy", "BioConda")
- `limit`: Maximum number of tools to retrieve
- `offset`: Starting offset for pagination

**Returns:**
- `List[Dict]`: List of tool metadata dictionaries

##### search_tools()

```python
search_tools(
    query: str,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]
```

Search tools using free-text query.

**Parameters:**
- `query`: Search query string
- `limit`: Maximum number of tools to retrieve
- `offset`: Starting offset for pagination

**Returns:**
- `List[Dict]`: List of matching tool metadata dictionaries

##### get_tool_details()

```python
get_tool_details(biotools_id: str) -> Dict
```

Get detailed information for a specific tool.

**Parameters:**
- `biotools_id`: Unique bio.tools identifier

**Returns:**
- `Dict`: Complete tool metadata

**Raises:**
- `ToolNotFoundError`: If tool doesn't exist
- `APIError`: If API request fails

### BioToolsDataParser

Parser for normalizing and validating bio.tools data.

#### Constructor

```python
BioToolsDataParser(schema_path: Optional[str] = None)
```

**Parameters:**
- `schema_path`: Path to biotoolsSchema JSON schema file

#### Methods

##### parse_tool_data()

```python
parse_tool_data(raw_data: Dict) -> Dict
```

Parse and normalize raw tool data from API.

**Parameters:**
- `raw_data`: Raw tool data from bio.tools API

**Returns:**
- `Dict`: Normalized tool data

**Example:**
```python
parser = BioToolsDataParser()
normalized = parser.parse_tool_data(raw_tool_data)
```

##### validate_tool_data()

```python
validate_tool_data(tool_data: Dict) -> Tuple[bool, List[str]]
```

Validate tool data against biotoolsSchema.

**Parameters:**
- `tool_data`: Tool data to validate

**Returns:**
- `Tuple[bool, List[str]]`: (is_valid, list_of_errors)

## Scoring APIs

### CompletenessScorer

Main scorer for evaluating annotation completeness.

#### Constructor

```python
CompletenessScorer(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path`: Path to scoring configuration YAML file

#### Methods

##### score_tool()

```python
score_tool(tool_data: Dict) -> float
```

Calculate overall completeness score for a tool.

**Parameters:**
- `tool_data`: Normalized tool metadata

**Returns:**
- `float`: Overall score (0-100)

**Example:**
```python
scorer = CompletenessScorer('config/scoring_config.yaml')
score = scorer.score_tool(tool_data)
print(f"Tool score: {score:.1f}")
```

##### get_detailed_score()

```python
get_detailed_score(tool_data: Dict) -> Dict
```

Get detailed scoring breakdown by category.

**Parameters:**
- `tool_data`: Normalized tool metadata

**Returns:**
- `Dict`: Detailed scoring information

**Example:**
```python
detailed = scorer.get_detailed_score(tool_data)
print(f"Category scores: {detailed['category_scores']}")
print(f"Missing fields: {detailed['missing_fields']}")
```

##### score_basic_info()

```python
score_basic_info(tool_data: Dict) -> Tuple[float, Dict[str, Any]]
```

Score basic information category.

**Parameters:**
- `tool_data`: Tool metadata

**Returns:**
- `Tuple[float, Dict]`: (category_score, details)

##### score_detailed_description()

```python
score_detailed_description(tool_data: Dict) -> Tuple[float, Dict[str, Any]]
```

Score core metadata category.

##### score_technical_details()

```python
score_technical_details(tool_data: Dict) -> Tuple[float, Dict[str, Any]]
```

Score technical information category.

##### score_accessibility()

```python
score_accessibility(tool_data: Dict) -> Tuple[float, Dict[str, Any]]
```

Score accessibility category.

##### score_documentation()

```python
score_documentation(tool_data: Dict) -> Tuple[float, Dict[str, Any]]
```

Score advanced features category.

##### score_community()

```python
score_community(tool_data: Dict) -> Tuple[float, Dict[str, Any]]
```

Score community category.

### TierClassifier

Classifier for mapping scores to tier levels.

#### Constructor

```python
TierClassifier(config_path: Optional[str] = None)
```

#### Methods

##### classify_tool()

```python
classify_tool(score: float) -> int
```

Classify tool score into tier level.

**Parameters:**
- `score`: Tool completeness score (0-100)

**Returns:**
- `int`: Tier level (1-5)

##### get_tier_name()

```python
get_tier_name(tier: int) -> str
```

Get descriptive name for tier level.

**Parameters:**
- `tier`: Tier level (1-5)

**Returns:**
- `str`: Tier name (e.g., "SPARSE", "COMPREHENSIVE")

### GroupBasedScorer

Scorer with group-specific rules and requirements.

#### Constructor

```python
GroupBasedScorer(
    config_path: Optional[str] = None,
    group_rules: Optional[Dict] = None
)
```

#### Methods

##### score_with_groups()

```python
score_with_groups(
    tool_data: Dict,
    group_context: Optional[str] = None
) -> Dict
```

Score tool with group-specific rules applied.

**Parameters:**
- `tool_data`: Tool metadata
- `group_context`: Group context (e.g., "proteomics", "genomics")

**Returns:**
- `Dict`: Detailed scoring with group-specific adjustments

## Analysis APIs

### QualityStatistics

Statistical analysis of quality evaluation results.

#### Constructor

```python
QualityStatistics()
```

#### Methods

##### calculate_summary_stats()

```python
calculate_summary_stats(scoring_results: List[Dict]) -> Dict
```

Calculate summary statistics for a set of scoring results.

**Parameters:**
- `scoring_results`: List of detailed scoring dictionaries

**Returns:**
- `Dict`: Summary statistics

**Example:**
```python
stats = QualityStatistics()
summary = stats.calculate_summary_stats(results)
print(f"Mean score: {summary['mean_score']:.1f}")
print(f"Tier distribution: {summary['tier_distribution']}")
```

##### analyze_field_completeness()

```python
analyze_field_completeness(scoring_results: List[Dict]) -> Dict
```

Analyze completeness rates for individual fields.

**Returns:**
- `Dict`: Field completeness statistics

##### compare_collections()

```python
compare_collections(
    results_by_collection: Dict[str, List[Dict]]
) -> Dict
```

Compare quality metrics across different collections.

**Parameters:**
- `results_by_collection`: Results grouped by collection name

**Returns:**
- `Dict`: Comparative analysis

##### generate_quality_report()

```python
generate_quality_report(
    scoring_results: List[Dict],
    output_path: str
) -> None
```

Generate comprehensive quality report.

**Parameters:**
- `scoring_results`: Scoring results to analyze
- `output_path`: Path for output report

## Visualization APIs

### QualityVisualizer

Visualization generator for quality evaluation results.

#### Constructor

```python
QualityVisualizer(
    style: str = "default",
    figure_size: Tuple[int, int] = (10, 8)
)
```

**Parameters:**
- `style`: Visualization style ("default", "publication", "presentation")
- `figure_size`: Default figure size in inches

#### Methods

##### create_tier_distribution_chart()

```python
create_tier_distribution_chart(
    scoring_results: List[Dict],
    save_path: Optional[str] = None,
    show_percentages: bool = True
) -> None
```

Create pie chart showing tier distribution.

**Parameters:**
- `scoring_results`: List of scoring results
- `save_path`: Path to save chart (optional)
- `show_percentages`: Whether to show percentage labels

##### create_score_histogram()

```python
create_score_histogram(
    scores: List[float],
    save_path: Optional[str] = None,
    bins: int = 20
) -> None
```

Create histogram of score distribution.

##### create_category_radar_chart()

```python
create_category_radar_chart(
    category_scores: Dict[str, float],
    save_path: Optional[str] = None
) -> None
```

Create radar chart for category scores.

##### create_completeness_heatmap()

```python
create_completeness_heatmap(
    field_completeness: Dict[str, float],
    save_path: Optional[str] = None
) -> None
```

Create heatmap of field completeness rates.

##### create_comparison_chart()

```python
create_comparison_chart(
    comparison_data: Dict[str, Dict],
    metric: str = "mean_score",
    save_path: Optional[str] = None
) -> None
```

Create comparison chart across collections or time periods.

**Parameters:**
- `comparison_data`: Data to compare
- `metric`: Metric to compare ("mean_score", "tier_distribution", etc.)
- `save_path`: Path to save chart

##### create_dashboard()

```python
create_dashboard(
    scoring_results: List[Dict],
    output_dir: str
) -> None
```

Create interactive HTML dashboard.

**Parameters:**
- `scoring_results`: Complete scoring results
- `output_dir`: Directory for dashboard files

## Utility APIs

### ConfigurationLoader

Utility for loading and validating configuration files.

#### Static Methods

##### load_config()

```python
@staticmethod
load_config(config_path: str) -> Dict
```

Load configuration from YAML file.

**Parameters:**
- `config_path`: Path to configuration file

**Returns:**
- `Dict`: Configuration dictionary

**Raises:**
- `ConfigurationError`: If configuration is invalid

##### validate_config()

```python
@staticmethod  
validate_config(config: Dict) -> List[str]
```

Validate configuration structure and values.

**Parameters:**
- `config`: Configuration dictionary

**Returns:**
- `List[str]`: List of validation errors (empty if valid)

### DataExporter

Utility for exporting results in various formats.

#### Methods

##### export_to_csv()

```python
export_to_csv(
    scoring_results: List[Dict],
    output_path: str,
    include_details: bool = True
) -> None
```

Export results to CSV format.

##### export_to_json()

```python
export_to_json(
    scoring_results: List[Dict],
    output_path: str,
    pretty: bool = True
) -> None
```

Export results to JSON format.

##### export_summary_report()

```python
export_summary_report(
    scoring_results: List[Dict],
    output_path: str,
    template: str = "default"
) -> None
```

Export human-readable summary report.

### Logger

Centralized logging utility.

#### Static Methods

##### setup_logging()

```python
@staticmethod
setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> None
```

Set up application logging.

**Parameters:**
- `level`: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
- `log_file`: Optional log file path
- `console`: Whether to log to console

##### get_logger()

```python
@staticmethod
get_logger(name: str) -> logging.Logger
```

Get logger instance for a module.

## Configuration APIs

### ScoringConfig

Configuration manager for scoring parameters.

#### Constructor

```python
ScoringConfig(config_path: Optional[str] = None)
```

#### Methods

##### get_category_weights()

```python
get_category_weights() -> Dict[str, float]
```

Get scoring category weights.

**Returns:**
- `Dict[str, float]`: Category weight mapping

##### get_field_weights()

```python
get_field_weights() -> Dict[str, float]  
```

Get individual field weights.

##### get_tier_thresholds()

```python
get_tier_thresholds() -> Dict[str, List[int]]
```

Get tier classification thresholds.

##### update_weights()

```python
update_weights(new_weights: Dict[str, float]) -> None
```

Update category weights.

**Parameters:**
- `new_weights`: New weight values

**Raises:**
- `ValueError`: If weights don't sum to 100

## Error Classes

### APIError

```python
class APIError(Exception):
    """Raised when API requests fail."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
```

### ConfigurationError

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
```

### ScoringError

```python
class ScoringError(Exception):
    """Raised when scoring calculation fails."""
    def __init__(self, message: str, tool_id: Optional[str] = None):
        self.message = message
        self.tool_id = tool_id
```

### ValidationError

```python
class ValidationError(Exception):
    """Raised when data validation fails."""
    def __init__(self, message: str, errors: List[str] = None):
        self.message = message
        self.errors = errors or []
```

## Usage Examples

### Complete Evaluation Pipeline

```python
from src.data_collection.api_client import BioToolsAPIClient
from src.data_collection.data_parser import BioToolsDataParser
from src.scoring.completeness_scorer import CompletenessScorer
from src.scoring.tier_classifier import TierClassifier
from src.analysis.statistics import QualityStatistics
from src.visualization.charts import QualityVisualizer

# Initialize components
api_client = BioToolsAPIClient()
parser = BioToolsDataParser()
scorer = CompletenessScorer('config/scoring_config.yaml')
classifier = TierClassifier('config/scoring_config.yaml')
stats = QualityStatistics()
visualizer = QualityVisualizer()

# Fetch and process data
raw_tools = api_client.get_tools_by_topic("Proteomics", limit=100)
parsed_tools = [parser.parse_tool_data(tool) for tool in raw_tools]

# Score tools
results = []
for tool in parsed_tools:
    score = scorer.score_tool(tool)
    tier = classifier.classify_tool(score)
    detailed = scorer.get_detailed_score(tool)
    
    results.append({
        'tool_id': tool.get('biotoolsID'),
        'name': tool.get('name'),
        'total_score': score,
        'tier': tier,
        'category_scores': detailed['category_scores'],
        'missing_fields': detailed['missing_fields']
    })

# Analyze results
summary = stats.calculate_summary_stats(results)
print(f"Average score: {summary['mean_score']:.1f}")

# Create visualizations
visualizer.create_tier_distribution_chart(results, 'tier_distribution.png')
visualizer.create_score_histogram([r['total_score'] for r in results], 'score_histogram.png')
```

### Custom Scoring Configuration

```python
# Create custom scorer with modified weights
custom_config = {
    'scoring': {
        'weights': {
            'basic_info': 20,
            'core_metadata': 30,
            'technical_info': 25,
            'accessibility': 20,
            'advanced_features': 5,
            'community': 0
        }
    }
}

# Save custom configuration
import yaml
with open('custom_config.yaml', 'w') as f:
    yaml.dump(custom_config, f)

# Use custom configuration
custom_scorer = CompletenessScorer('custom_config.yaml')
```

This API reference provides complete documentation for programmatically using the bio.tools annotation quality evaluation system.
