# Development Guide

This guide provides comprehensive information for developers who want to contribute to or extend the bio.tools Annotation Quality Evaluation system.

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Contributing Guidelines](#contributing-guidelines)
4. [Testing](#testing)
5. [Code Style and Standards](#code-style-and-standards)
6. [Adding New Features](#adding-new-features)
7. [Performance Optimization](#performance-optimization)
8. [Debugging and Troubleshooting](#debugging-and-troubleshooting)

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, or similar)
- Text editor or IDE (VS Code, PyCharm, etc.)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
   cd bio.tools-annotation-quality-evaluation
   ```

2. **Create development environment**
   ```bash
   # Using venv
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Or using conda
   conda create -n biotools-quality python=3.9
   conda activate biotools-quality
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Install package in development mode**
   ```bash
   pip install -e .
   ```

5. **Run tests to verify setup**
   ```bash
   pytest tests/
   ```

### Development Dependencies

Create `requirements-dev.txt` with additional development tools:

```text
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
pre-commit>=3.3.0
sphinx>=7.1.0
sphinx-rtd-theme>=1.3.0
```

### IDE Configuration

#### VS Code
Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### Pre-commit Hooks
Set up pre-commit hooks for code quality:

```bash
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

## Project Structure

### Directory Organization

```
bio.tools-annotation-quality-evaluation/
├── src/                        # Source code
│   ├── data_collection/        # API clients and data parsing
│   ├── scoring/               # Scoring algorithms and classification
│   ├── analysis/              # Statistical analysis
│   ├── visualization/         # Charts and dashboards
│   ├── linter/                # Linter integration
│   └── utils/                 # Utility functions
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data and fixtures
├── config/                    # Configuration files
├── scripts/                   # Command-line scripts
├── docs/                      # Documentation
├── notebooks/                 # Jupyter notebooks
└── data/                      # Data storage
    ├── raw/                   # Raw data from API
    ├── processed/             # Processed results
    └── visualizations/        # Generated charts
```

### Module Organization

Each module follows consistent structure:

```python
# module_name/__init__.py
"""Module description."""

from .main_class import MainClass
from .utils import utility_function

__all__ = ["MainClass", "utility_function"]

# module_name/main_class.py
"""Main class implementation."""

import logging
from typing import Dict, List, Optional

class MainClass:
    """Class description."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def public_method(self) -> str:
        """Public method with docstring."""
        return self._private_method()
    
    def _private_method(self) -> str:
        """Private method (internal use)."""
        return "result"
```

## Contributing Guidelines

### Git Workflow

1. **Create feature branch**
   ```bash
   git checkout -b feature/description-of-feature
   ```

2. **Make changes with clear commits**
   ```bash
   git add .
   git commit -m "Add: description of change"
   ```

3. **Push and create pull request**
   ```bash
   git push origin feature/description-of-feature
   ```

### Commit Message Convention

Follow conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(scoring): add group-based scoring functionality
fix(api): handle rate limiting in bio.tools API client
docs: update installation instructions
test(scoring): add tests for tier classification
```

### Pull Request Guidelines

1. **Clear title and description**
2. **Link related issues**
3. **Include tests for new features**
4. **Update documentation as needed**
5. **Ensure all tests pass**
6. **Request appropriate reviewers**

### Code Review Process

1. **Automated checks must pass**
2. **At least one approval required**
3. **Address all review comments**
4. **Squash commits before merging**

## Testing

### Test Organization

```
tests/
├── unit/                      # Fast, isolated tests
│   ├── test_scoring.py
│   ├── test_api_client.py
│   └── test_data_parser.py
├── integration/               # Component integration tests
│   ├── test_pipeline.py
│   └── test_end_to_end.py
├── fixtures/                  # Test data
│   ├── sample_tools.json
│   └── test_config.yaml
└── conftest.py               # Pytest configuration
```

### Writing Tests

#### Unit Tests

```python
# tests/unit/test_scoring.py
import pytest
from src.scoring.completeness_scorer import CompletenessScorer

class TestCompletenessScorer:
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = CompletenessScorer()
        self.sample_tool = {
            "name": "Test Tool",
            "description": "A test tool for unit testing",
            "homepage": "https://example.com"
        }
    
    def test_score_basic_info_complete(self):
        """Test scoring with complete basic information."""
        score, details = self.scorer.score_basic_info(self.sample_tool)
        assert score > 0
        assert "name" in details["present_fields"]
    
    def test_score_basic_info_incomplete(self):
        """Test scoring with incomplete basic information."""
        incomplete_tool = {"name": "Test Tool"}
        score, details = self.scorer.score_basic_info(incomplete_tool)
        assert score < self.scorer.score_basic_info(self.sample_tool)[0]
    
    @pytest.mark.parametrize("field,expected_present", [
        ("name", True),
        ("description", True),
        ("nonexistent", False)
    ])
    def test_field_presence_detection(self, field, expected_present):
        """Test field presence detection."""
        score, details = self.scorer.score_basic_info(self.sample_tool)
        assert (field in details["present_fields"]) == expected_present
```

#### Integration Tests

```python
# tests/integration/test_pipeline.py
import pytest
from src.data_collection.api_client import BioToolsAPIClient
from src.scoring.completeness_scorer import CompletenessScorer

class TestEvaluationPipeline:
    @pytest.mark.integration
    def test_full_evaluation_pipeline(self):
        """Test complete evaluation pipeline with real data."""
        # This test requires network access
        client = BioToolsAPIClient()
        scorer = CompletenessScorer()
        
        # Fetch small dataset
        tools = client.get_tools_by_topic("Proteomics", limit=5)
        assert len(tools) > 0
        
        # Score all tools
        scores = []
        for tool in tools:
            score = scorer.score_tool(tool)
            assert 0 <= score <= 100
            scores.append(score)
        
        # Verify reasonable results
        assert len(scores) == len(tools)
        assert any(score > 0 for score in scores)
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_tool_data():
    """Load sample tool data for testing."""
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_tools.json"
    with open(fixtures_path) as f:
        return json.load(f)

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "scoring": {
            "weights": {
                "basic_info": 15,
                "core_metadata": 25,
                "technical_info": 20,
                "accessibility": 20,
                "advanced_features": 15,
                "community": 5
            }
        }
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_scoring.py

# Run with coverage
pytest --cov=src tests/

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v

# Skip slow tests
pytest -m "not slow"
```

### Test Markers

```python
# tests/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API access"
    )
```

## Code Style and Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these specifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes preferred
- **Imports**: Organized and sorted

### Code Formatting

#### Black Configuration

Create `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

#### Flake8 Configuration

Create `.flake8`:

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    build,
    dist
```

### Type Hints

Use type hints for better code clarity and IDE support:

```python
from typing import Dict, List, Optional, Union, Any

def score_tool(
    self, 
    tool_data: Dict[str, Any], 
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Score a tool based on metadata completeness."""
    pass

def process_tools(tools: List[Dict]) -> List[Tuple[str, float]]:
    """Process multiple tools and return name-score pairs."""
    pass
```

### Documentation Standards

#### Docstring Format

Use Google-style docstrings:

```python
def calculate_score(tool_data: Dict, weights: Dict[str, float]) -> float:
    """Calculate completeness score for a tool.
    
    Args:
        tool_data: Dictionary containing tool metadata
        weights: Scoring weights for different categories
        
    Returns:
        Completeness score between 0 and 100
        
    Raises:
        ValueError: If weights don't sum to 100
        KeyError: If required fields are missing
        
    Example:
        >>> tool = {"name": "Example", "description": "Test tool"}
        >>> weights = {"basic_info": 50, "details": 50}
        >>> score = calculate_score(tool, weights)
        >>> print(score)
        25.0
    """
    pass
```

#### Class Documentation

```python
class CompletenessScorer:
    """Evaluates bio.tools annotation completeness.
    
    This class implements a weighted scoring system that evaluates
    tool metadata across multiple categories aligned with the Tool
    Information Standards.
    
    Attributes:
        config: Configuration dictionary with weights and thresholds
        logger: Logger instance for this scorer
        
    Example:
        >>> scorer = CompletenessScorer("config/scoring_config.yaml")
        >>> score = scorer.score_tool(tool_data)
        >>> tier = scorer.classify_tier(score)
    """
    pass
```

### Error Handling

#### Custom Exceptions

```python
# src/exceptions.py
class BioToolsQualityError(Exception):
    """Base exception for bio.tools quality evaluation."""
    pass

class ConfigurationError(BioToolsQualityError):
    """Raised when configuration is invalid."""
    def __init__(self, message: str, config_path: Optional[str] = None):
        self.config_path = config_path
        super().__init__(message)

class ScoringError(BioToolsQualityError):
    """Raised when scoring calculation fails."""
    def __init__(self, message: str, tool_id: Optional[str] = None):
        self.tool_id = tool_id
        super().__init__(message)
```

#### Error Handling Patterns

```python
def score_tool(self, tool_data: Dict) -> float:
    """Score tool with proper error handling."""
    try:
        # Validate input
        if not isinstance(tool_data, dict):
            raise ValueError("tool_data must be a dictionary")
        
        # Perform scoring
        score = self._calculate_score(tool_data)
        
        # Validate output
        if not 0 <= score <= 100:
            raise ScoringError(f"Invalid score: {score}")
        
        return score
        
    except KeyError as e:
        self.logger.error(f"Missing required field: {e}")
        raise ScoringError(f"Missing field: {e}") from e
    
    except Exception as e:
        self.logger.error(f"Unexpected error scoring tool: {e}")
        raise
```

### Logging Standards

```python
import logging

class MyClass:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_data(self, data):
        """Example of proper logging."""
        self.logger.info(f"Processing {len(data)} items")
        
        try:
            result = self._process(data)
            self.logger.debug(f"Processing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}", exc_info=True)
            raise
```

## Adding New Features

### Feature Development Workflow

1. **Create issue** describing the feature
2. **Design the API** and get feedback
3. **Write tests** for the new functionality
4. **Implement the feature** following TDD principles
5. **Update documentation** including API reference
6. **Submit pull request** with tests and documentation

### Adding New Scorers

#### Custom Scorer Interface

```python
# src/scoring/base_scorer.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseScorer(ABC):
    """Abstract base class for scorers."""
    
    @abstractmethod
    def score_tool(self, tool_data: Dict[str, Any]) -> float:
        """Calculate score for a tool.
        
        Args:
            tool_data: Tool metadata dictionary
            
        Returns:
            Score between 0 and 100
        """
        pass
    
    @abstractmethod
    def get_detailed_score(self, tool_data: Dict[str, Any]) -> Dict:
        """Get detailed scoring breakdown.
        
        Args:
            tool_data: Tool metadata dictionary
            
        Returns:
            Dictionary with detailed scoring information
        """
        pass
```

#### Custom Scorer Implementation

```python
# src/scoring/custom_scorer.py
from typing import Dict, Any
from .base_scorer import BaseScorer

class CustomScorer(BaseScorer):
    """Custom scoring implementation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)
    
    def score_tool(self, tool_data: Dict[str, Any]) -> float:
        """Implement custom scoring logic."""
        # Your custom scoring implementation
        pass
    
    def get_detailed_score(self, tool_data: Dict[str, Any]) -> Dict:
        """Provide detailed scoring breakdown."""
        # Your detailed scoring implementation
        pass
```

### Adding New Visualizations

#### Visualization Interface

```python
# src/visualization/base_visualizer.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class BaseVisualizer(ABC):
    """Abstract base class for visualizations."""
    
    @abstractmethod
    def create_chart(
        self, 
        data: List[Dict], 
        save_path: Optional[str] = None
    ) -> None:
        """Create and optionally save a chart."""
        pass
```

#### Custom Visualization

```python
# src/visualization/custom_viz.py
import matplotlib.pyplot as plt
from .base_visualizer import BaseVisualizer

class CustomVisualizer(BaseVisualizer):
    """Custom visualization implementation."""
    
    def create_chart(self, data: List[Dict], save_path: Optional[str] = None):
        """Create custom chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Your custom visualization logic
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
```

### Adding New Data Sources

#### API Client Interface

```python
# src/data_collection/base_client.py
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseAPIClient(ABC):
    """Abstract base class for API clients."""
    
    @abstractmethod
    def fetch_tools(self, query: str, limit: int = 100) -> List[Dict]:
        """Fetch tools from the data source."""
        pass
    
    @abstractmethod
    def get_tool_details(self, tool_id: str) -> Dict:
        """Get detailed information for a specific tool."""
        pass
```

## Performance Optimization

### Profiling

```python
# Performance profiling
import cProfile
import pstats

def profile_function():
    """Profile a specific function."""
    pr = cProfile.Profile()
    pr.enable()
    
    # Your code here
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

### Caching Strategies

```python
# src/utils/cache.py
from functools import lru_cache
import pickle
import hashlib
from pathlib import Path

class FileCache:
    """Simple file-based caching."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_path(self, key: str) -> Path:
        """Generate cache file path."""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.pkl"
    
    def get(self, key: str):
        """Get cached value."""
        cache_path = self.get_cache_path(key)
        if cache_path.exists():
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, key: str, value):
        """Set cached value."""
        cache_path = self.get_cache_path(key)
        with open(cache_path, 'wb') as f:
            pickle.dump(value, f)
```

### Memory Optimization

```python
# Use generators for large datasets
def process_tools_generator(tools):
    """Process tools using generator for memory efficiency."""
    for tool in tools:
        processed = process_single_tool(tool)
        yield processed

# Process in batches
def process_tools_in_batches(tools, batch_size=100):
    """Process tools in batches to manage memory."""
    for i in range(0, len(tools), batch_size):
        batch = tools[i:i + batch_size]
        yield process_batch(batch)
```

## Debugging and Troubleshooting

### Debugging Tools

#### Enhanced Logging

```python
# src/utils/debug.py
import logging
import functools
import time

def debug_function_calls(func):
    """Decorator to debug function calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        start_time = time.time()
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}", exc_info=True)
            raise
    
    return wrapper
```

#### Data Validation

```python
# src/utils/validation.py
def validate_tool_data(tool_data: Dict) -> List[str]:
    """Validate tool data structure."""
    errors = []
    
    required_fields = ['name', 'biotoolsID']
    for field in required_fields:
        if field not in tool_data:
            errors.append(f"Missing required field: {field}")
    
    # URL validation
    url_fields = ['homepage', 'repository']
    for field in url_fields:
        if field in tool_data:
            url = tool_data[field]
            if not url.startswith(('http://', 'https://')):
                errors.append(f"Invalid URL in {field}: {url}")
    
    return errors
```

### Common Issues and Solutions

#### Issue: API Rate Limiting
```python
# Solution: Implement exponential backoff
import time
import random

class RateLimitedClient:
    def __init__(self, max_retries=3, base_delay=1):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def make_request(self, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return self._make_request(*args, **kwargs)
            except RateLimitError:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                else:
                    raise
```

#### Issue: Memory Usage with Large Datasets
```python
# Solution: Stream processing
def stream_process_tools(api_client, query, limit=None):
    """Stream process tools to avoid loading all into memory."""
    offset = 0
    batch_size = 100
    processed = 0
    
    while limit is None or processed < limit:
        batch = api_client.get_tools(
            query=query, 
            limit=batch_size, 
            offset=offset
        )
        
        if not batch:
            break
            
        for tool in batch:
            yield process_tool(tool)
            processed += 1
            
            if limit and processed >= limit:
                break
        
        offset += batch_size
```

This development guide provides a comprehensive foundation for contributing to and extending the bio.tools annotation quality evaluation system while maintaining code quality and consistency.
