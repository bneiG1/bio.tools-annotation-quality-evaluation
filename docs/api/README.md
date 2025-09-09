# API Reference

The Bio.tools Annotation Quality Evaluation Platform provides both internal APIs for extending functionality and integration with external APIs for data collection and validation.

## Internal Application APIs

### Core Analysis Classes

#### `LiveBioToolsAnalyzer`

The main application class that orchestrates the analysis pipeline.

**Location**: `app.py`

**Key Methods**:

```python
class LiveBioToolsAnalyzer:
    def __init__(self):
        """Initialize the analyzer with required components."""
        
    def analyze_single_tool(self, tool_id: str) -> Dict[str, Any]:
        """
        Analyze a single tool by its bio.tools ID.
        
        Args:
            tool_id (str): The bio.tools tool identifier
            
        Returns:
            Dict containing analysis results, quality scores, and metrics
            
        Example:
            >>> analyzer = LiveBioToolsAnalyzer()
            >>> result = analyzer.analyze_single_tool("blast")
            >>> print(result['quality_grade'])
            'B'
        """
        
    def search_and_analyze_tools(self, 
                               query: str, 
                               fields: List[str], 
                               limit: int = 10) -> Dict[str, Any]:
        """
        Search for tools and analyze the results.
        
        Args:
            query (str): Search query
            fields (List[str]): Fields to search in
            limit (int): Maximum number of results
            
        Returns:
            Dict containing search results and bulk analysis
        """
        
    def analyze_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Analyze a predefined collection of tools.
        
        Args:
            collection_name (str): Name of the collection
            
        Returns:
            Dict containing collection analysis results
        """
```

### Data Collection APIs

#### `BioToolsAPIClient`

**Location**: `src/collectors/biotools_api.py`

**Purpose**: Interface to the bio.tools REST API

```python
class BioToolsAPIClient:
    def __init__(self, base_url: str = "https://bio.tools/api"):
        """Initialize the API client."""
        
    def get_tool(self, tool_id: str) -> Dict[str, Any]:
        """
        Fetch a single tool by ID.
        
        Args:
            tool_id (str): Tool identifier
            
        Returns:
            Tool data as JSON dict
            
        Raises:
            APIError: When tool not found or API error
        """
        
    def search_tools(self, 
                    query: str, 
                    fields: List[str] = None,
                    limit: int = 10,
                    offset: int = 0) -> Dict[str, Any]:
        """
        Search for tools using bio.tools search API.
        
        Args:
            query (str): Search query string
            fields (List[str]): Fields to search in
            limit (int): Results per page (max 100)
            offset (int): Results offset for pagination
            
        Returns:
            Search results with tools and metadata
        """
        
    def get_collection(self, collection_name: str) -> List[str]:
        """
        Get tool IDs from a predefined collection.
        
        Args:
            collection_name (str): Collection identifier
            
        Returns:
            List of tool IDs in the collection
        """
```

**API Endpoints Used**:

- `GET /api/tool/{id}` - Retrieve single tool
- `GET /api/tool/` - Search tools with parameters
- `GET /api/collection/{name}` - Get collection tools

**Authentication**: None required for public API

**Rate Limiting**: 
- 100 requests per minute per IP
- Automatic retry with exponential backoff
- Caching enabled to reduce API calls

**Error Handling**:

```python
from src.collectors.biotools_api import APIError, RateLimitError

try:
    client = BioToolsAPIClient()
    tool = client.get_tool("nonexistent-tool")
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
```

### Validation APIs

#### `SchemaValidator`

**Location**: `src/validators/schema_validator.py`

**Purpose**: Validate tools against biotoolsSchema

```python
class SchemaValidator:
    def __init__(self, schema_path: str = None):
        """Initialize with biotoolsSchema."""
        
    def validate_tool(self, tool_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a tool against the schema.
        
        Args:
            tool_data (Dict): Tool JSON data
            
        Returns:
            ValidationResult with is_valid, errors, warnings
        """
        
    def get_validation_errors(self, tool_data: Dict[str, Any]) -> List[str]:
        """Get list of validation errors."""
        
    def get_validation_warnings(self, tool_data: Dict[str, Any]) -> List[str]:
        """Get list of validation warnings."""
```

**ValidationResult Structure**:

```python
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    schema_version: str
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
        
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
```

#### `StandardsScorer`

**Location**: `src/validators/standards_scorer.py`

**Purpose**: Score tools against ELIXIR Tool Information Standards

```python
class StandardsScorer:
    def __init__(self):
        """Initialize with standards configuration."""
        
    def score_tool(self, tool_data: Dict[str, Any]) -> StandardsScore:
        """
        Score a tool against information standards.
        
        Args:
            tool_data (Dict): Tool JSON data
            
        Returns:
            StandardsScore with tier, percentage, breakdown
        """
        
    def get_tier(self, score_percentage: float) -> int:
        """Get standards tier (1-5) from percentage score."""
        
    def get_missing_fields(self, tool_data: Dict[str, Any]) -> List[str]:
        """Get list of missing required fields."""
```

**StandardsScore Structure**:

```python
@dataclass
class StandardsScore:
    tier: int                    # 1-5, higher is better
    percentage: float           # 0-100
    weighted_score: float       # Weighted calculation
    field_scores: Dict[str, float]  # Individual field scores
    missing_fields: List[str]   # Missing required fields
    recommendations: List[str]  # Improvement suggestions
```

#### `CompletenessScorer`

**Location**: `src/validators/completeness_scorer.py`

**Purpose**: Calculate overall completeness and quality grades

```python
class CompletenessScorer:
    def __init__(self):
        """Initialize scoring weights and thresholds."""
        
    def calculate_completeness(self, tool_data: Dict[str, Any]) -> CompletenessScore:
        """
        Calculate comprehensive completeness score.
        
        Args:
            tool_data (Dict): Tool JSON data
            
        Returns:
            CompletenessScore with grade, percentage, breakdown
        """
        
    def get_quality_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade (A-F)."""
        
    def get_improvement_priority(self, score: CompletenessScore) -> List[str]:
        """Get prioritized list of improvement recommendations."""
```

**CompletenessScore Structure**:

```python
@dataclass
class CompletenessScore:
    grade: str                  # A, B, C, D, F
    percentage: float          # 0-100
    category_scores: Dict[str, float]  # Scores by category
    weighted_total: float      # Final weighted score
    priority_improvements: List[str]  # Top 3 improvements
    detailed_breakdown: Dict[str, Any]  # Field-level analysis
```

### Analysis APIs

#### `QualityAnalyzer`

**Location**: `src/analyzers/quality_analyzer.py`

**Purpose**: Coordinate comprehensive quality analysis

```python
class QualityAnalyzer:
    def __init__(self):
        """Initialize with validators and scorers."""
        
    def analyze_tool_quality(self, tool_data: Dict[str, Any]) -> QualityAnalysis:
        """
        Perform comprehensive quality analysis.
        
        Args:
            tool_data (Dict): Tool JSON data
            
        Returns:
            QualityAnalysis with all metrics and scores
        """
        
    def bulk_analyze(self, tool_list: List[str]) -> BulkAnalysis:
        """
        Analyze multiple tools in batch.
        
        Args:
            tool_list (List[str]): List of tool IDs
            
        Returns:
            BulkAnalysis with summary statistics
        """
```

**QualityAnalysis Structure**:

```python
@dataclass
class QualityAnalysis:
    tool_id: str
    tool_name: str
    overall_grade: str
    overall_percentage: float
    
    # Component scores
    completeness: CompletenessScore
    standards: StandardsScore
    validation: ValidationResult
    linter_results: LinterResults
    
    # Aggregated metrics
    recommendations: List[str]
    quality_indicators: Dict[str, Any]
    improvement_priority: List[str]
    
    def export_summary(self) -> Dict[str, Any]:
        """Export summary for reporting."""
        
    def export_detailed(self) -> Dict[str, Any]:
        """Export detailed analysis data."""
```

#### `LinterAnalyzer`

**Location**: `src/analyzers/linter.py`

**Purpose**: Integration with biotools-linter

```python
class LinterAnalyzer:
    def __init__(self, linter_path: str = "./biotools-linter"):
        """Initialize with linter installation path."""
        
    def analyze_tool(self, tool_data: Dict[str, Any]) -> LinterResults:
        """
        Run linter analysis on tool data.
        
        Args:
            tool_data (Dict): Tool JSON data
            
        Returns:
            LinterResults with issues and recommendations
        """
        
    def get_severity_counts(self, results: LinterResults) -> Dict[str, int]:
        """Get count of issues by severity level."""
```

### Reporting APIs

#### `QualityReporter`

**Location**: `src/reporters/quality_reporter.py`

**Purpose**: Generate reports and visualizations

```python
class QualityReporter:
    def __init__(self):
        """Initialize reporter with visualization settings."""
        
    def generate_summary_report(self, 
                              analysis: QualityAnalysis) -> Dict[str, Any]:
        """Generate summary report for single tool."""
        
    def generate_bulk_report(self, 
                           bulk_analysis: BulkAnalysis) -> Dict[str, Any]:
        """Generate report for multiple tools."""
        
    def create_visualization(self, 
                           data: Dict[str, Any], 
                           chart_type: str) -> plotly.graph_objects.Figure:
        """Create Plotly visualization."""
        
    def export_csv(self, data: List[Dict[str, Any]], 
                   filename: str) -> str:
        """Export data to CSV format."""
        
    def export_json(self, data: Dict[str, Any], 
                    filename: str) -> str:
        """Export data to JSON format."""
```

## External API Integrations

### Bio.tools API

**Base URL**: `https://bio.tools/api/`

**Documentation**: https://biotools.readthedocs.io/en/latest/api_reference.html

**Authentication**: Not required for read operations

#### Tool Retrieval

```http
GET /api/tool/{id}
```

**Parameters**:
- `id` (required): Tool identifier
- `format`: Response format (json, xml)

**Response Example**:

```json
{
    "biotoolsID": "blast",
    "name": "BLAST",
    "description": "Basic Local Alignment Search Tool",
    "homepage": "https://blast.ncbi.nlm.nih.gov/",
    "version": ["2.12.0"],
    "function": [
        {
            "operation": [
                {"uri": "http://edamontology.org/operation_0292", "term": "Sequence alignment"}
            ],
            "input": [
                {"data": [{"uri": "http://edamontology.org/data_2044", "term": "Sequence"}]}
            ]
        }
    ]
}
```

#### Search Tools

```http
GET /api/tool/?q={query}&format=json&page=1&pageSize=10
```

**Parameters**:
- `q`: Search query
- `format`: Response format (json, xml)
- `page`: Page number (1-based)
- `pageSize`: Results per page (max 100)
- `sort`: Sort field and direction

**Advanced Search Parameters**:
- `topicID`: Filter by EDAM topic
- `operationID`: Filter by EDAM operation
- `typeID`: Filter by tool type
- `collectionID`: Filter by collection

**Response Structure**:

```json
{
    "count": 25,
    "next": "https://bio.tools/api/tool/?page=2",
    "previous": null,
    "list": [
        {
            "biotoolsID": "tool1",
            "name": "Tool Name",
            "description": "Tool description"
        }
    ]
}
```

### EDAM Ontology API

**Purpose**: Validate EDAM terms and get ontology structure

**Base URL**: `https://edamontology.org/`

**Usage in Application**:

```python
def validate_edam_term(term_uri: str) -> bool:
    """Validate if EDAM term URI exists in ontology."""
    
def get_edam_hierarchy(term_uri: str) -> List[str]:
    """Get parent terms in EDAM hierarchy."""
    
def suggest_edam_terms(description: str) -> List[str]:
    """Suggest relevant EDAM terms based on description."""
```

### biotoolsSchema API

**Purpose**: Access current schema versions and validation rules

**Repository**: https://github.com/bio-tools/biotoolsschema

**Usage**:

```python
def get_current_schema() -> Dict[str, Any]:
    """Fetch current biotoolsSchema from GitHub."""
    
def validate_against_schema(tool_data: Dict[str, Any], 
                          schema_version: str) -> ValidationResult:
    """Validate tool data against specific schema version."""
```

## Data Structures

### Tool Data Format

Standard tool data structure used throughout the application:

```python
ToolData = TypedDict('ToolData', {
    'biotoolsID': str,
    'name': str,
    'description': str,
    'homepage': Optional[str],
    'version': List[str],
    'function': List[Dict[str, Any]],
    'topic': List[Dict[str, str]],
    'publication': List[Dict[str, Any]],
    'download': List[Dict[str, str]],
    'documentation': List[Dict[str, str]],
    'relation': List[Dict[str, str]],
    'credit': List[Dict[str, Any]],
    'license': Optional[str],
    'maturity': Optional[str],
    'cost': Optional[str],
    'accessibility': List[str]
})
```

### Analysis Results Format

```python
AnalysisResult = TypedDict('AnalysisResult', {
    'tool_id': str,
    'timestamp': str,
    'quality_grade': str,
    'overall_score': float,
    'component_scores': Dict[str, float],
    'validation_result': ValidationResult,
    'standards_score': StandardsScore,
    'completeness_score': CompletenessScore,
    'linter_results': LinterResults,
    'recommendations': List[str],
    'metadata': Dict[str, Any]
})
```

## Error Handling

### Exception Hierarchy

```python
class BioToolsAnalysisError(Exception):
    """Base exception for analysis errors."""
    
class APIError(BioToolsAnalysisError):
    """API communication errors."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)
        
class ValidationError(BioToolsAnalysisError):
    """Data validation errors."""
    
class SchemaError(ValidationError):
    """Schema validation specific errors."""
    
class LinterError(BioToolsAnalysisError):
    """Linter integration errors."""
    
class RateLimitError(APIError):
    """API rate limiting errors."""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited. Retry after {retry_after} seconds")
```

### Error Response Format

```python
ErrorResponse = TypedDict('ErrorResponse', {
    'error': bool,
    'error_type': str,
    'message': str,
    'details': Optional[Dict[str, Any]],
    'timestamp': str,
    'request_id': Optional[str]
})
```

## Configuration

### Application Configuration

Configuration is managed through environment variables and config files:

```python
# Environment Variables
BIOTOOLS_API_BASE_URL = "https://bio.tools/api"
CACHE_TTL_HOURS = 24
MAX_CONCURRENT_REQUESTS = 5
LINTER_PATH = "./biotools-linter"
LOG_LEVEL = "INFO"

# Config File Structure (.streamlit/config.toml)
[server]
port = 8501
address = "localhost"

[global]
dataFrameSerialization = "arrow"

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

### Scoring Configuration

```python
# Scoring weights and thresholds
QUALITY_THRESHOLDS = {
    'A': 90,  # Excellent
    'B': 80,  # Good  
    'C': 70,  # Fair
    'D': 60,  # Poor
    'F': 0    # Fail
}

STANDARDS_TIERS = {
    1: 20,   # Minimal
    2: 40,   # Basic
    3: 60,   # Standard
    4: 80,   # Comprehensive
    5: 95    # Exemplary
}

FIELD_WEIGHTS = {
    'required_fields': 0.4,
    'recommended_fields': 0.3,
    'optional_fields': 0.2,
    'validation_quality': 0.1
}
```

## Usage Examples

### Basic Tool Analysis

```python
from src.analyzers.quality_analyzer import QualityAnalyzer
from src.collectors.biotools_api import BioToolsAPIClient

# Initialize components
api_client = BioToolsAPIClient()
analyzer = QualityAnalyzer()

# Analyze a single tool
tool_data = api_client.get_tool("blast")
analysis = analyzer.analyze_tool_quality(tool_data)

print(f"Tool: {analysis.tool_name}")
print(f"Grade: {analysis.overall_grade}")
print(f"Score: {analysis.overall_percentage:.1f}%")
```

### Bulk Analysis

```python
# Search and analyze multiple tools
search_results = api_client.search_tools("phylogenetic", limit=10)
tool_ids = [tool['biotoolsID'] for tool in search_results['list']]

bulk_analysis = analyzer.bulk_analyze(tool_ids)
print(f"Average quality: {bulk_analysis.average_score:.1f}%")
```

### Export Results

```python
from src.reporters.quality_reporter import QualityReporter

reporter = QualityReporter()

# Export to CSV
csv_file = reporter.export_csv(analysis.export_detailed(), "analysis_results.csv")

# Export to JSON
json_file = reporter.export_json(analysis.export_summary(), "analysis_summary.json")
```

For more detailed examples, see the [Basic Usage Examples](../examples/basic-usage.md) guide.
