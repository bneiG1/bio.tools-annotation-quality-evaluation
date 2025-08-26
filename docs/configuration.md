# Configuration Guide

This guide explains how to configure the bio.tools Annotation Quality Evaluation system to meet your specific requirements.

## Table of Contents
1. [Configuration Overview](#configuration-overview)
2. [Scoring Configuration](#scoring-configuration)
3. [System Configuration](#system-configuration)
4. [Custom Profiles](#custom-profiles)
5. [Advanced Configuration](#advanced-configuration)
6. [Validation and Testing](#validation-and-testing)

## Configuration Overview

The system uses YAML-based configuration files to control scoring behavior, thresholds, and system parameters. The main configuration file is `config/scoring_config.yaml`, which contains all scoring-related settings.

### Configuration Hierarchy

1. **Default Configuration**: Built-in defaults in the code
2. **System Configuration**: `config/scoring_config.yaml`
3. **User Configuration**: Custom YAML files specified via CLI
4. **Runtime Overrides**: Programmatic configuration changes

### Basic Configuration Structure

```yaml
scoring:
  weights:          # Category weights (must sum to 100)
  tiers:           # Tier classification thresholds
  field_weights:   # Individual field scoring weights
  requirements:    # Required fields and validation rules
  
system:
  api:             # API client settings
  output:          # Output format and location settings
  logging:         # Logging configuration
```

## Scoring Configuration

### Category Weights

The `weights` section defines how much each scoring category contributes to the final score. All weights must sum to 100.

```yaml
scoring:
  weights:
    basic_info: 15           # Name, description, homepage, IDs
    core_metadata: 25        # Tool type, topics, publications
    technical_info: 20       # Operations, documentation, platform info
    accessibility: 20        # I/O formats, downloads, code availability
    advanced_features: 15    # Benchmarks, monitoring, community features
    community: 5             # Credits, contact information
```

#### Customizing Category Weights

For different use cases, you might want to adjust these weights:

**Research-Focused Profile**:
```yaml
scoring:
  weights:
    basic_info: 10
    core_metadata: 35        # Emphasize publications and scientific context
    technical_info: 25       # Important for reproducibility
    accessibility: 25        # Critical for research replication
    advanced_features: 5     # Less critical
    community: 0             # Not essential for research
```

**Developer-Focused Profile**:
```yaml
scoring:
  weights:
    basic_info: 15
    core_metadata: 15        # Basic scientific context
    technical_info: 30       # Critical for implementation
    accessibility: 30        # Essential for usage
    advanced_features: 10    # Nice to have
    community: 0             # Less relevant
```

### Tier Thresholds

The `tiers` section defines score ranges for tier classification:

```yaml
scoring:
  tiers:
    tier_1: [0, 15]      # SPARSE - minimal viable entry
    tier_2: [16, 40]     # BASIC DETAILS - essential metadata
    tier_3: [41, 65]     # DETAILED - comprehensive core information
    tier_4: [66, 85]     # HIGHLY DETAILED - rich metadata
    tier_5: [86, 100]    # COMPREHENSIVE - complete tool profile
```

#### Adjusting Tier Standards

You can modify these thresholds to be more or less stringent:

**Strict Standards**:
```yaml
scoring:
  tiers:
    tier_1: [0, 10]      # Very minimal
    tier_2: [11, 30]     # Basic but more complete
    tier_3: [31, 55]     # Well-documented
    tier_4: [56, 80]     # Comprehensive
    tier_5: [81, 100]    # Exceptional
```

**Lenient Standards**:
```yaml
scoring:
  tiers:
    tier_1: [0, 20]      # Allow more basic entries
    tier_2: [21, 45]     # Lower bar for basic details
    tier_3: [46, 70]     # Easier to reach detailed
    tier_4: [71, 88]     # More accessible high tier
    tier_5: [89, 100]    # Only truly complete tools
```

### Field Weights

Individual field weights determine how much each metadata field contributes within its category:

```yaml
scoring:
  field_weights:
    # Basic Information (15% total)
    name: 4                  # Essential identifier
    description: 6           # Critical for understanding
    homepage: 3              # Important for access
    biotoolsID: 2           # Technical identifier
    
    # Core Metadata (25% total)
    toolType: 6             # Essential classification
    topic: 8                # Primary scientific area
    publication: 10          # Scientific credibility
    
    # Technical Information (20% total)
    function: 7             # What the tool does
    operation: 6            # Specific operations
    language: 3             # Implementation language
    operatingSystem: 3      # Platform compatibility
    license: 4              # Legal/usage terms
    
    # Accessibility (20% total)
    version: 4              # Current version info
    maturity: 3             # Development status
    download: 6             # How to obtain
    documentation: 8         # Usage instructions
    
    # Advanced Features (15% total)
    cost: 3                 # Pricing information  
    accessibility: 6        # Accessibility features
    repository: 5           # Source code access
    
    # Community (5% total)
    contact: 3              # Support contact
    credit: 2               # Attribution info
```

#### Field Weight Customization

Adjust field weights based on your priorities:

```yaml
# Emphasize documentation and reproducibility
scoring:
  field_weights:
    documentation: 12       # Higher weight for docs
    repository: 8          # Important for reproducibility
    license: 6             # Legal clarity important
    version: 6             # Version tracking critical
    publication: 15        # Strong emphasis on citations
```

## System Configuration

### API Client Settings

Configure API behavior and rate limiting:

```yaml
system:
  api:
    base_url: "https://bio.tools/api"
    timeout: 30                    # Request timeout in seconds
    max_retries: 3                # Maximum retry attempts
    retry_delay: 1                # Initial retry delay
    retry_backoff: 2              # Backoff multiplier
    rate_limit_delay: 0.1         # Delay between requests
    batch_size: 100               # Tools per API request
    cache_responses: true         # Enable response caching
    cache_duration: 3600          # Cache duration in seconds
```

### Output Configuration

Control output formats and locations:

```yaml
system:
  output:
    base_dir: "data/processed"
    create_subdirs: true          # Create date-based subdirectories
    formats:
      json: true                  # Save JSON results
      csv: true                   # Save CSV exports
      html: true                  # Generate HTML reports
    visualization:
      create_charts: true         # Generate visualization charts
      chart_format: "png"        # Chart format (png, svg, pdf)
      chart_dpi: 300             # Chart resolution
      interactive: false         # Create interactive charts
```

### Logging Configuration

Configure logging behavior:

```yaml
system:
  logging:
    level: "INFO"                 # DEBUG, INFO, WARNING, ERROR
    file_logging: true           # Log to file
    console_logging: true        # Log to console
    log_file: "evaluation.log"   # Log file name
    max_log_size: 10485760      # 10MB max log file size
    backup_count: 5             # Number of backup log files
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Custom Profiles

### Creating Custom Profiles

Create specialized configuration profiles for different scenarios:

#### Domain-Specific Profile

**config/proteomics_profile.yaml**:
```yaml
scoring:
  weights:
    basic_info: 15
    core_metadata: 30           # Emphasize scientific context
    technical_info: 20          
    accessibility: 25           # Important for wet-lab researchers
    advanced_features: 10
    community: 0
    
  field_weights:
    # Proteomics-specific emphasis
    topic: 12                   # Scientific area critical
    publication: 15             # Publications very important
    function: 10                # What analysis is performed
    documentation: 12           # Usage instructions critical
    operatingSystem: 2          # Less important for web tools
    
  # Custom requirements for proteomics tools
  requirements:
    required_fields:
      - name
      - description
      - function
      - topic
    required_topics:
      - "Proteomics"
    min_publication_count: 1
```

#### Quality Assurance Profile

**config/qa_profile.yaml**:
```yaml
scoring:
  # Strict quality requirements
  tiers:
    tier_1: [0, 5]              # Very strict minimum
    tier_2: [6, 25]
    tier_3: [26, 50]
    tier_4: [51, 80]
    tier_5: [81, 100]
    
  weights:
    basic_info: 20              # Higher weight on basics
    core_metadata: 25
    technical_info: 25          # Technical accuracy important
    accessibility: 20
    advanced_features: 5
    community: 5
    
  # Stricter field requirements
  field_weights:
    license: 8                  # Legal clarity essential
    version: 6                  # Version control important
    documentation: 15           # Documentation critical
    repository: 8               # Source access important
```

### Using Custom Profiles

```bash
# Use custom profile
python scripts/run_evaluation.py --config config/proteomics_profile.yaml --topic Proteomics

# Chain multiple configs (later configs override earlier ones)
python scripts/run_evaluation.py --config config/base_config.yaml --config config/overrides.yaml
```

## Advanced Configuration

### Conditional Scoring

Configure different scoring rules based on tool characteristics:

```yaml
scoring:
  conditional_rules:
    # Different standards for different tool types
    by_tool_type:
      "Web application":
        required_fields:
          - homepage
          - documentation
        field_weights:
          operatingSystem: 0    # Not relevant for web apps
          
      "Command-line tool":
        required_fields:
          - operatingSystem
          - language
        field_weights:
          operatingSystem: 6    # Very important for CLI tools
          
    # Different standards by maturity
    by_maturity:
      "Mature":
        min_score: 50           # Higher expectations
        required_fields:
          - license
          - documentation
          - version
          
      "Emerging":
        min_score: 20           # Lower initial bar
        bonus_points: 5         # Bonus for being new/innovative
```

### Group-Based Requirements

Define requirements that apply to groups of related fields:

```yaml
scoring:
  group_requirements:
    # At least one contact method required
    contact_group:
      fields: ["contact", "homepage", "repository"]
      min_required: 1
      bonus_all: 2            # Bonus if all present
      
    # At least one download method
    download_group:  
      fields: ["download", "repository", "homepage"]
      min_required: 1
      weight_multiplier: 1.2  # Multiply scores if requirement met
      
    # Publication requirements
    publication_group:
      fields: ["publication", "doi"]
      min_required: 1
      penalty_none: -5        # Penalty if none present
```

### Dynamic Scoring

Configure scoring that adapts based on other fields:

```yaml
scoring:
  dynamic_rules:
    # Commercial tools have different license expectations
    - condition:
        field: "cost"
        operator: "not_equals"
        value: "Free"
      modifications:
        field_weights:
          license: 8          # License more important for paid tools
          
    # Web applications don't need OS specification  
    - condition:
        field: "toolType"
        operator: "contains"
        value: "Web"
      modifications:
        field_weights:
          operatingSystem: 0  # Not relevant for web tools
```

### Validation Rules

Configure custom validation for metadata fields:

```yaml
scoring:
  validation:
    # URL validation
    url_fields:
      - homepage
      - repository
      - documentation
    validation_rules:
      homepage:
        required: true
        format: "url"
        reachable: false      # Don't check if URL is reachable
        
      version:
        required: false
        format: "semver"      # Semantic versioning format
        
      publication:
        required: false
        validation: "doi_or_pmid"  # Custom validation function
```

## Validation and Testing

### Configuration Validation

Validate your configuration before use:

```python
# Built-in validation
from src.scoring.completeness_scorer import CompletenessScorer

try:
    scorer = CompletenessScorer("config/my_config.yaml")
    print("Configuration valid!")
except Exception as e:
    print(f"Configuration error: {e}")
```

### Testing Configuration Changes

Test configuration changes with a small dataset:

```bash
# Test new configuration
python scripts/run_evaluation.py \
  --config config/test_config.yaml \
  --topic Proteomics \
  --limit 10 \
  --log-level DEBUG
```

### Configuration Linting

Create a configuration validation script:

```python
#!/usr/bin/env python3
"""Validate scoring configuration file."""

import yaml
import sys

def validate_config(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    errors = []
    
    # Check weights sum to 100
    if 'scoring' in config and 'weights' in config['scoring']:
        weights = config['scoring']['weights']
        total = sum(weights.values())
        if abs(total - 100) > 0.1:
            errors.append(f"Weights sum to {total}, not 100")
    
    # Check tier thresholds are non-overlapping
    if 'scoring' in config and 'tiers' in config['scoring']:
        tiers = config['scoring']['tiers']
        for tier, (min_val, max_val) in tiers.items():
            if min_val >= max_val:
                errors.append(f"Invalid tier range for {tier}: [{min_val}, {max_val}]")
    
    return errors

if __name__ == "__main__":
    errors = validate_config(sys.argv[1])
    if errors:
        print("Configuration errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("Configuration is valid!")
```

### Profile Comparison

Compare different configuration profiles:

```bash
# Compare profiles on same dataset
python scripts/run_evaluation.py --config config/strict_profile.yaml --topic Test --limit 50 --output-dir strict_results
python scripts/run_evaluation.py --config config/lenient_profile.yaml --topic Test --limit 50 --output-dir lenient_results

# Generate comparison report
python scripts/compare_profiles.py strict_results lenient_results
```

## Environment-Specific Configuration

### Development Configuration

**config/development.yaml**:
```yaml
system:
  api:
    max_retries: 1            # Fail fast during development
    cache_responses: true     # Use caching
  logging:
    level: "DEBUG"            # Verbose logging
    console_logging: true
  output:
    create_subdirs: false     # Simpler output structure
```

### Production Configuration

**config/production.yaml**:
```yaml
system:
  api:
    max_retries: 5            # More robust in production
    rate_limit_delay: 0.5     # Respectful API usage
  logging:
    level: "INFO"             # Less verbose
    file_logging: true
    console_logging: false    # Log to file only
  output:
    create_subdirs: true      # Organized output
    backup_results: true      # Keep result backups
```

### Configuration Best Practices

1. **Version Control**: Keep configuration files in version control
2. **Documentation**: Comment your custom configurations
3. **Validation**: Always validate configurations before deployment
4. **Testing**: Test configuration changes on small datasets first
5. **Backups**: Keep backup copies of working configurations
6. **Environment Separation**: Use different configs for dev/staging/production
7. **Security**: Don't include sensitive data in configuration files

This comprehensive configuration guide should help you customize the system to meet your specific evaluation needs while maintaining reliability and consistency.
