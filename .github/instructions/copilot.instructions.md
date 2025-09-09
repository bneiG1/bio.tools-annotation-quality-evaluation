```instructions
---
applyTo: '**'
---

# Coding Guidelines for bio.tools Quality Evaluation Pipeline

## Code Organization Rules

### Module Structure
- Use `src/` package structure with clear domain separation
- `collectors/` for API clients, `validators/` for scoring, `analyzers/` for linter integration
- Keep bio.tools domain logic separate from generic data processing utilities
- Each module should handle one aspect of the pipeline (collect → validate → score → report)

### Naming Conventions
- Use bioinformatics terminology: `tool_entry`, `biotool_id`, `completeness_score`
- API classes: `BioToolsAPIClient`, `SchemaValidator`, `TierScorer`
- Data files: `{domain}_{timestamp}.json` for raw data, `{collection}_scores.csv` for results

### Data Handling Patterns
```python
# Always preserve original bio.tools JSON structure
def process_tool_entry(tool_data: dict) -> dict:
    """Process while keeping original biotoolsID and metadata."""
    return {
        'original': tool_data,
        'scores': calculate_completeness(tool_data),
        'validation': validate_schema(tool_data)
    }
```

### Error Handling for External Dependencies
```python
# Bio.tools API resilience
try:
    response = biotools_client.fetch_tools(domain="proteomics")
except (requests.RequestException, RateLimitError) as e:
    logger.warning(f"API fetch failed: {e}, using cached data")
    response = load_cached_tools(domain)
```

## Testing Requirements

### Use Real bio.tools Data
- Test fixtures should use actual tool entries from different domains
- Mock API responses with realistic bio.tools JSON structure
- Test scoring against known high/low quality tools

### Domain-Specific Test Cases
```python
def test_tier_scoring_proteomics_tools():
    """Test scoring algorithm on proteomics domain tools."""
    high_quality_tool = load_fixture('maxquant_entry.json')
    assert calculate_tier(high_quality_tool) >= 4
```

## Performance Guidelines

### Batch Processing
- Process tools in chunks of 100-500 for memory efficiency
- Use pandas for aggregating scores across large collections
- Cache API responses locally in `data/raw/` with timestamps

### Rate Limiting
- Respect bio.tools API limits (implement exponential backoff)
- Use `time.sleep()` between requests, check response headers for rate info

## Documentation Standards
- Document biotoolsSchema field mappings in docstrings
- Include Tool Information Standards references for scoring logic
- Add examples of expected JSON structures from bio.tools API
```