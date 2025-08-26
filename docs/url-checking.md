# URL Accessibility Checking

This document describes the URL accessibility checking feature added to the bio.tools annotation quality evaluation system.

## Overview

The URL accessibility checker validates whether homepage URLs and other links in bio.tools entries are still functional. This helps identify broken links and improves the overall quality assessment by penalizing tools with inaccessible homepages.

## Features

- **Homepage Validation**: Checks if the primary homepage URL is accessible
- **Link Validation**: Validates all URLs found in link, documentation, and download arrays
- **Batch Processing**: Efficiently checks multiple URLs concurrently
- **Caching**: Caches results to avoid duplicate checks during evaluation
- **Rate Limiting**: Respects servers by introducing delays between requests
- **Retry Logic**: Automatically retries failed requests with exponential backoff

## Impact on Scoring

When URL checking is enabled, the accessibility scoring is enhanced:

- **Homepage Bonus**: +3 points for accessible homepage
- **Homepage Penalty**: -1 point for broken homepage  
- **Overall URL Quality**: Up to +2 points based on percentage of accessible URLs
  - 80%+ accessible: +2 points
  - 60-79% accessible: +1 point
  - <50% accessible: -1 point
- **Maximum Impact**: ±10% of the accessibility category weight

## Usage

### Command Line

Enable URL checking by adding the `--check-urls` flag:

```bash
# Basic usage with URL checking
python scripts/run_evaluation.py --topic "Proteomics" --limit 50 --check-urls

# With additional options
python scripts/run_evaluation.py \
  --collection "Galaxy" \
  --limit 100 \
  --check-urls \
  --output-dir results/galaxy_with_urls \
  --visualize
```

### Programmatic Usage

```python
from src.scoring.completeness_scorer import CompletenessScorer

# Enable URL checking in the scorer
scorer = CompletenessScorer(
    config_path='config/scoring_config.yaml',
    enable_url_checking=True
)

# Score a tool with URL checking
result = scorer.score_tool(tool_data)

# Check URL accessibility details
if 'accessibility' in result['details']:
    url_info = result['details']['accessibility']['url_accessibility']
    if url_info:
        print(f"URLs found: {url_info['summary']['total_urls']}")
        print(f"Accessible: {url_info['summary']['accessible_urls']}")
        print(f"Homepage OK: {url_info['summary']['homepage_accessible']}")
```

## Configuration

The URL checker can be customized by modifying the URLChecker initialization in the CompletenessScorer:

```python
# Default settings
self.url_checker = URLChecker(
    timeout=5,              # 5 second timeout per URL
    max_workers=3,          # 3 concurrent workers  
    delay_between_requests=0.3  # 300ms delay between requests
)
```

## Output Details

When URL checking is enabled, the results include additional information:

### In scoring results:
```json
{
  "details": {
    "accessibility": {
      "url_checking_enabled": true,
      "url_accessibility": {
        "homepage_result": {
          "is_accessible": true,
          "status_code": 200,
          "response_time": 0.45,
          "final_url": "https://example.com"
        },
        "all_urls_results": {...},
        "summary": {
          "total_urls": 4,
          "accessible_urls": 3,
          "inaccessible_urls": 1,
          "accessibility_rate": 0.75,
          "homepage_accessible": true
        }
      },
      "url_accessibility_score": 4,
      "url_bonus": 1.6
    }
  }
}
```

### In summary reports:
```
URL Accessibility Checking: Enabled
```

## Error Handling

The system gracefully handles common issues:

- **Import errors**: If URLChecker is unavailable, URL checking is disabled with a warning
- **Network timeouts**: URLs that timeout are marked as inaccessible
- **Connection errors**: DNS failures and connection refused errors are caught
- **Invalid URLs**: Malformed URLs are marked as inaccessible
- **Rate limiting**: Built-in delays prevent overwhelming target servers

## Performance Considerations

- **Concurrent processing**: Multiple URLs are checked simultaneously
- **Caching**: Results are cached for 1 hour to avoid duplicate checks
- **Rate limiting**: Configurable delays between requests (default: 300ms)
- **Timeouts**: Short timeout (5s) to prevent hanging on slow sites
- **Stream downloads**: Only headers are downloaded, not full content

## Monitoring

The system provides detailed logging:

```
INFO - URL accessibility checking enabled
INFO - Checking accessibility of 10 unique URLs  
DEBUG - ✓ https://github.com/example (HTTP 200)
DEBUG - ✗ https://broken-site.com (Connection error: ...)
```

## Best Practices

1. **Use for comprehensive evaluations**: Enable URL checking for complete quality assessments
2. **Consider performance**: URL checking adds 2-10 seconds per tool depending on link count
3. **Monitor logs**: Check logs for patterns in broken links
4. **Batch processing**: Use reasonable limits (50-100 tools) to balance thoroughness and speed
5. **Network considerations**: Run during stable network conditions

## Example Results

Here's what you might see with URL checking enabled:

```bash
$ python scripts/run_evaluation.py --topic "Sequence analysis" --limit 5 --check-urls

2025-08-26 13:12:06 - INFO - URL accessibility checking enabled
2025-08-26 13:12:07 - INFO - Checking accessibility of 10 unique URLs
2025-08-26 13:12:11 - INFO - Checking accessibility of 7 unique URLs
...

Tools analyzed: 5
Average quality score: 59.92/100 (includes URL accessibility bonus/penalty)
```

The URL checking feature provides valuable insights into the real-world accessibility of bio.tools entries, helping maintain the quality and usability of the registry.
