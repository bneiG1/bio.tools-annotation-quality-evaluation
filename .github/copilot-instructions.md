# bio.tools Annotation Quality Evaluation

## Project Overview
This is a **bioinformatics data analysis pipeline** for evaluating metadata quality in the ELIXIR bio.tools registry. The project focuses on scoring tool completeness, integrating linter diagnostics, and generating visual reports for improving metadata standards.

## Architecture & Key Concepts

### Core Pipeline Components
1. **Data Collection**: Fetch tool entries via bio.tools API (JSON format)
2. **Schema Validation**: Validate against biotoolsSchema for structural issues
3. **Tier-based Scoring**: Map Tool Information Standards to scored attributes (tiers 1-5)
4. **Linter Integration**: Parse bio.tools linter diagnostics
5. **Reporting**: Generate radar charts, heatmaps, and CSV/JSON summaries

### Domain-Specific Knowledge
- **bio.tools**: ELIXIR's registry of biological software tools and databases
- **biotoolsSchema**: JSON schema defining tool metadata structure
- **Tool Information Standards**: ELIXIR guidelines for tool annotation completeness
- **Linter**: External tool (3top1a/biotools-linter) for detecting metadata issues

## Development Workflow

### Environment Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Planned Project Structure
```
src/                    # Main Python package
├── collectors/         # API clients and data fetching
├── validators/         # Schema validation and scoring
├── analyzers/          # Linter integration and analysis
├── reporters/          # Visualization and report generation
└── main.py            # Pipeline entrypoint
data/                  # Raw and processed datasets
├── raw/               # JSON from bio.tools API
├── processed/         # Scored and validated data
└── reports/           # Generated visualizations
notebooks/             # Exploratory analysis (Jupyter)
tests/                 # Unit and integration tests
```

## Coding Patterns & Conventions

### Data Processing Approach
- **JSON-centric**: All bio.tools data is JSON; preserve original structure
- **Modular pipeline**: Each stage (collect → validate → score → report) is independent
- **Reproducible**: Store raw data and intermediate results for repeatability
- **Domain-driven**: Group code by bioinformatics concepts, not generic patterns

### Key Libraries Expected
- `requests` for bio.tools API calls
- `jsonschema` for biotoolsSchema validation
- `pandas` for data manipulation and aggregation
- `matplotlib/seaborn/plotly` for visualization (radar charts, heatmaps)
- `pytest` for testing

### API Integration Patterns
- Bio.tools API endpoint: `https://bio.tools/api/tool/`
- Handle pagination and rate limiting
- Cache responses locally in `data/raw/`
- Support filtered queries by domain/collection

### Scoring Algorithm
- Map Tool Information Standards attributes to numeric weights
- Calculate completeness percentage per tool
- Assign tiers (1=minimal, 5=comprehensive) based on thresholds
- Track missing/malformed fields by category

### Error Handling
- Graceful API failure handling (network issues, rate limits)
- Schema validation error aggregation (don't stop on first error)
- Linter integration robustness (external tool may change)

## Testing Strategy
- **Unit tests**: Individual scoring functions, validators
- **Integration tests**: Full pipeline with sample data
- **Fixtures**: Use real bio.tools entries as test cases
- **Mock API**: Don't hit live API in tests

## External Dependencies
- **bio.tools API**: Live registry data (rate limited)
- **biotoolsSchema**: JSON schema from bio-tools/biotoolsschema repo
- **bio.tools linter**: Command-line tool from 3top1a/biotools-linter

## Implementation Priority
1. **Data collector**: Fetch and cache bio.tools entries
2. **Basic scoring**: Implement tier assignment logic
3. **Schema validation**: Integrate biotoolsSchema validation
4. **Report generation**: Start with simple CSV summaries
5. **Linter integration**: Add external tool parsing
6. **Visualization**: Radar charts and heatmaps

## Performance Considerations
- Bio.tools has ~27,000 tools; design for batch processing
- Cache API responses to avoid repeated requests
- Use pandas for efficient data aggregation across large datasets
- Generate reports incrementally for large collections