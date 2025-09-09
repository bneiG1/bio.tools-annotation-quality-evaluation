# Bio.tools Linter Integration Summary

## Overview

Successfully integrated the [biotools-linter](https://github.com/3top1a/biotools-linter) into our bio.tools annotation quality evaluation pipeline. The linter provides rule-based checking for bio.tools tool metadata, detecting issues like obsolete EDAM terms, invalid URLs, and publication problems.

## Integration Architecture

### Components Added

1. **`src/analyzers/linter.py`** - Main integration module
   - `BiotoolsLinter` class for linter management
   - `LintIssue` dataclass for standardized issue representation
   - `IssueLevel` enum for severity classification
   - Convenience functions for single/batch linting

2. **Path Setup** - Automatic linter path detection
   - Detects `biotools-linter/linter` directory
   - Adds to Python path for imports
   - Graceful fallback when linter unavailable

3. **Async Integration** - Proper async handling
   - Wraps linter's async functionality
   - Batch processing with concurrency limits
   - Error handling for failed analyses

## Linter Capabilities

### Available Rules

The linter can detect 13+ types of issues:

| Rule Code | Description | Severity |
|-----------|-------------|----------|
| `EDAM_OBSOLETE` | Obsolete EDAM ontology terms | Error |
| `EDAM_NOT_RECOMMENDED` | Deprecated EDAM terms | Info |
| `EDAM_INVALID` | Invalid EDAM term URIs | Error |
| `URL_SSL_ERROR` | SSL certificate problems | Warning |
| `URL_INVALID` | Malformed URLs | Error |
| `URL_404` | Broken links (404 errors) | Warning |
| `URL_TIMEOUT` | Unreachable URLs | Warning |
| `URL_WITH_SPACES` | URLs containing spaces | Error |
| `SUSPICIOUS_DOMAIN` | Potentially problematic domains | Warning |
| `PUBLICATION_INVALID_DOI` | Invalid DOI format | Error |
| `PUBLICATION_INVALID_PMID` | Invalid PubMed ID | Error |
| `PUBLICATION_INVALID_PMCID` | Invalid PMC ID | Error |
| `MISSING_REQUIRED_FIELD` | Missing mandatory fields | Critical |

### Issue Severity Mapping

- **CRITICAL**: Security problems, severe structural issues
- **ERROR**: High priority problems requiring fixes
- **WARNING**: Medium priority issues affecting quality
- **INFO**: Low priority suggestions for improvement
- **INTERNAL**: Linter system messages (filtered out)

## Usage Examples

### Basic Tool Linting

```python
from analyzers.linter import lint_single_tool

# Analyze a single tool
tool_data = {...}  # bio.tools JSON
issues = lint_single_tool(tool_data)

for issue in issues:
    print(f"[{issue.level.value}] {issue.code}: {issue.message}")
    print(f"Location: {issue.location}")
```

### Batch Processing

```python
from analyzers.linter import lint_tools_batch

# Analyze multiple tools
tools_data = [...]  # List of bio.tools JSON
results = lint_tools_batch(tools_data)

for tool_id, issues in results.items():
    print(f"{tool_id}: {len(issues)} issues")
```

### Using the Linter Class

```python
from analyzers.linter import BiotoolsLinter

linter = BiotoolsLinter()

if linter.is_available():
    issues = linter.lint_tool(tool_data)
    summary = linter.get_issue_summary(issues)
    print(f"Total issues: {summary['total']}")
    print(f"By level: {summary['by_level']}")
```

## Installation and Setup

### Prerequisites

1. **Clone biotools-linter** (already done):
   ```bash
   git clone https://github.com/3top1a/biotools-linter.git
   ```

2. **Install dependencies**:
   ```bash
   pip install owlready2 cacheout aiohttp aiolimiter colorlog psycopg2-binary
   ```

3. **Copy EDAM files** (to avoid download issues):
   ```bash
   copy biotools-linter\EDAM.* biotools-linter\linter\
   ```

### Directory Structure

```
biotools-linter/
├── linter/              # Main linter code
│   ├── EDAM.csv        # Copied from parent
│   ├── EDAM.owl        # Copied from parent
│   ├── cli.py          # Command line interface
│   ├── lib.py          # Core linter functions
│   ├── message.py      # Issue reporting
│   └── rules/          # Linting rules
│       ├── edam.py     # EDAM ontology checks
│       ├── url.py      # URL validation
│       └── publications.py # Publication validation
```

## Integration with Quality Analysis

### Enhanced QualityAnalyzer

The existing `QualityAnalyzer` class in `src/analyzers/quality_analyzer.py` already includes linter integration:

```python
analyzer = QualityAnalyzer(enable_extended_validation=True)
report = analyzer.analyze_tool(tool_data)

# Linting results included in report
print(f"Lint issues: {report.metrics.lint_issues}")
print(f"Critical: {report.metrics.critical_issues}")
print(f"Errors: {report.metrics.error_issues}")
print(f"Warnings: {report.metrics.warning_issues}")
```

### Quality Metrics Impact

Linting results contribute to:

- **Overall Score**: Penalties for critical/error issues
- **Quality Grade**: Issues affect A-F grading
- **Recommendations**: Actionable fixes generated
- **Priority Fixes**: Critical issues highlighted

## Performance Considerations

### Optimization Features

1. **Concurrency Control**: Limited to 5 concurrent linting operations
2. **Graceful Degradation**: Falls back cleanly when linter unavailable
3. **Error Isolation**: Individual tool failures don't stop batch processing
4. **External API Tolerance**: Handles external service failures (PubMed, etc.)

### Known Limitations

1. **External Dependencies**: Requires PubMed API for publication validation
2. **Network Sensitivity**: URL checking depends on network connectivity
3. **EDAM File Size**: Large ontology files (~50MB) need local caching

## Example Analysis Results

From BLAST tool analysis:

```
Tool: BLAST (ID: blast)
🔍 Linting Analysis:
📊 Found 1 issues:
  ℹ️ INFO: 1
🔝 Top issues:
  • EDAM_NOT_RECOMMENDED: 1
📝 Issue details:
  [INFO] EDAM_NOT_RECOMMENDED
  📍 BLAST//function/0/output/0/format/6/uri
  💬 The term "Binary format" at BLAST//function/0/output/0/format/6/uri is no longer advised for use.
```

## Future Enhancements

### Potential Improvements

1. **Custom Rules**: Add domain-specific validation rules
2. **Issue Suggestions**: Generate fix recommendations
3. **Batch Optimization**: Improve large-scale processing performance
4. **Offline Mode**: Reduce external API dependencies
5. **Rule Configuration**: Allow enabling/disabling specific rules

### Integration Opportunities

1. **Real-time Validation**: Integrate with bio.tools submission process
2. **Quality Dashboards**: Visual reporting of linting trends
3. **Automated Fixes**: Generate corrected metadata suggestions
4. **CI/CD Integration**: Automated quality checks in workflows

## Status

✅ **Fully Integrated**: Linter is working and integrated into the quality analysis pipeline

✅ **Production Ready**: Handles errors gracefully and provides useful diagnostics

✅ **Well Documented**: Examples and usage patterns established

The biotools-linter integration significantly enhances our metadata quality evaluation capabilities by providing detailed, rule-based analysis of bio.tools entries. It complements our existing schema validation and standards scoring with practical, actionable quality insights.
