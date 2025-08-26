# Scoring Methodology

This document provides a comprehensive explanation of the tier-based scoring system used to evaluate bio.tools annotation quality, aligned with the Tool Information Standards.

## Table of Contents
1. [Overview](#overview)
2. [Tier Classification System](#tier-classification-system)
3. [Scoring Categories](#scoring-categories)
4. [Field-Level Scoring](#field-level-scoring)
5. [Calculation Methods](#calculation-methods)
6. [Quality Metrics](#quality-metrics)
7. [Standards Alignment](#standards-alignment)

## Overview

The bio.tools annotation quality evaluation system uses a **tier-based scoring methodology** that assesses metadata completeness across multiple dimensions. This approach provides both granular insights into specific metadata categories and an overall quality classification that aligns with the [Tool Information Standards](https://bio-tools.github.io/Tool-Information-Standards/use_cases.html).

### Core Principles

1. **Standards Alignment**: Directly maps to Tool Information Standards tiers
2. **Weighted Scoring**: Different metadata categories have different importance  
3. **Completeness Focus**: Emphasizes presence and quality of metadata
4. **Configurability**: Weights and thresholds can be customized
5. **Transparency**: Clear scoring rules and calculations
6. **Actionability**: Identifies specific areas for improvement

### Scoring Range

All scores are normalized to a **0-100 scale**, where:
- **0-15**: Minimal viable metadata (SPARSE)
- **16-40**: Basic discoverable information (BASIC DETAILS)
- **41-65**: Comprehensive core metadata (DETAILED)
- **66-85**: Rich, well-documented tools (HIGHLY DETAILED)
- **86-100**: Complete, exemplary tool profiles (COMPREHENSIVE)

## Tier Classification System

The tier system directly corresponds to the Tool Information Standards, providing a clear progression path for metadata quality improvement.

### Tier 1: SPARSE (0-15 points)
**Definition**: Minimal viable entry with just enough information for basic tool identification.

**Requirements**:
- Tool name and basic description
- At least one access method (homepage or repository)
- Unique identifier (biotoolsID)

**Typical Profile**:
```json
{
  "name": "ExampleTool",
  "description": "Brief tool description",
  "homepage": "https://example.com",
  "biotoolsID": "exampletool"
}
```

**Quality Indicators**:
- ✅ Tool can be identified and located
- ❌ Limited scientific context
- ❌ Minimal technical information
- ❌ No usage guidance

### Tier 2: BASIC DETAILS (16-40 points)
**Definition**: Essential metadata for basic discoverability and scientific classification.

**Additional Requirements** (beyond Tier 1):
- Tool type classification
- At least one scientific topic
- Basic functional description

**Typical Profile**:
```json
{
  "toolType": ["Web application"],
  "topic": [{"term": "Proteomics"}],
  "function": [{
    "operation": [{"term": "Protein identification"}],
    "note": "Identifies proteins from mass spectrometry data"
  }]
}
```

**Quality Indicators**:
- ✅ Scientific domain clearly identified
- ✅ Tool type known
- ✅ Basic functionality described
- ⚠️ Limited technical details
- ❌ Minimal accessibility information

### Tier 3: DETAILED (41-65 points)  
**Definition**: Comprehensive core information enabling informed tool selection and usage.

**Additional Requirements** (beyond Tier 2):
- Operating system compatibility
- Programming language (if applicable)
- License information
- At least one publication
- Documentation or usage instructions

**Typical Profile**:
```json
{
  "operatingSystem": ["Linux", "Mac"],
  "language": ["Python"],
  "license": "MIT",
  "publication": [{
    "type": "Primary",
    "title": "ExampleTool: Advanced protein analysis"
  }],
  "documentation": [{
    "type": "User manual",
    "url": "https://example.com/docs"
  }]
}
```

**Quality Indicators**:
- ✅ Platform compatibility clear
- ✅ Legal usage terms defined
- ✅ Scientific credibility established
- ✅ Basic usage guidance available
- ⚠️ Limited accessibility features

### Tier 4: HIGHLY DETAILED (66-85 points)
**Definition**: Rich metadata supporting comprehensive tool evaluation and comparison.

**Additional Requirements** (beyond Tier 3):
- Version information
- Maturity level
- Input/output format specifications
- Download information
- Contact details

**Typical Profile**:
```json
{
  "version": "2.1.0",
  "maturity": "Mature",
  "function": [{
    "input": [{"format": [{"term": "FASTA"}]}],
    "output": [{"format": [{"term": "TSV"}]}]
  }],
  "download": [{
    "type": "Source code",
    "url": "https://github.com/example/tool"
  }],
  "contact": [{
    "email": "support@example.com",
    "name": "Support Team"
  }]
}
```

**Quality Indicators**:
- ✅ Version tracking available
- ✅ Data format compatibility clear
- ✅ Acquisition method specified
- ✅ Support contact available
- ✅ Development status known

### Tier 5: COMPREHENSIVE (86-100 points)
**Definition**: Complete, exemplary tool profile with advanced metadata and community features.

**Additional Requirements** (beyond Tier 4):
- Multiple publications (if applicable)
- ELIXIR platform/node association (if applicable)
- Comprehensive accessibility information
- Cost/pricing details
- Credit and attribution information
- Multiple contact methods

**Typical Profile**:
```json
{
  "publication": [
    {"type": "Primary"},
    {"type": "Method"}
  ],
  "elixirPlatform": ["Tools"],
  "accessibility": ["Open access", "Free of charge"],
  "cost": "Free",
  "credit": [{
    "name": "Jane Doe",
    "type": "Developer"
  }],
  "repository": [{
    "type": "Git",
    "url": "https://github.com/example/tool"
  }]
}
```

**Quality Indicators**:
- ✅ Multiple validation sources
- ✅ Community integration
- ✅ Full accessibility information
- ✅ Complete attribution
- ✅ Comprehensive technical details

## Scoring Categories

The scoring system evaluates six main categories, each contributing a weighted percentage to the final score.

### 1. Basic Information (15% weight)
**Purpose**: Establishes tool identity and basic accessibility.

**Fields Evaluated**:
- `name` (4 points): Tool name and identification
- `description` (6 points): Clear, informative description
- `homepage` (3 points): Primary website or landing page
- `biotoolsID` (2 points): Unique identifier in bio.tools

**Scoring Logic**:
```python
def score_basic_info(tool_data):
    score = 0
    if tool_data.get('name'): 
        score += 4
    if tool_data.get('description') and len(tool_data['description']) > 10:
        score += 6
    if tool_data.get('homepage') and is_valid_url(tool_data['homepage']):
        score += 3
    if tool_data.get('biotoolsID'):
        score += 2
    return score
```

### 2. Core Metadata (25% weight)
**Purpose**: Provides scientific context and classification.

**Fields Evaluated**:
- `toolType` (6 points): Tool category classification
- `topic` (8 points): Scientific domain/field
- `publication` (10 points): Scientific publications
- `function.operation` (6 points): Computational operations

**Quality Factors**:
- **Topic Specificity**: More specific topics score higher
- **Publication Quality**: Primary publications score higher than general references
- **Operation Detail**: Specific EDAM operations preferred

### 3. Technical Information (20% weight)  
**Purpose**: Enables technical evaluation and implementation planning.

**Fields Evaluated**:
- `function` (7 points): Detailed functional description
- `language` (3 points): Programming/implementation language  
- `operatingSystem` (3 points): Platform compatibility
- `license` (4 points): Legal and usage terms
- `maturity` (3 points): Development status

**Quality Factors**:
- **Function Completeness**: Input/output specifications increase score
- **License Clarity**: Recognized licenses (MIT, GPL, etc.) score higher
- **OS Coverage**: Multi-platform support increases score

### 4. Accessibility (20% weight)
**Purpose**: Assesses how easily users can access and use the tool.

**Fields Evaluated**:
- `version` (4 points): Version information and tracking
- `download` (6 points): Download and acquisition methods
- `documentation` (8 points): User guides and documentation
- `accessibility` (6 points): Accessibility features and barriers

**Quality Factors**:
- **Documentation Types**: Multiple documentation types increase score
- **Download Methods**: Multiple acquisition options preferred
- **Version Currency**: Recent versions indicate active maintenance

### 5. Advanced Features (15% weight)
**Purpose**: Evaluates enhanced functionality and community integration.

**Fields Evaluated**:
- `cost` (3 points): Pricing and cost information
- `elixirPlatform` (2 points): ELIXIR infrastructure integration
- `elixirNode` (2 points): ELIXIR node association
- `repository` (5 points): Source code repository access
- `link` (3 points): Additional relevant links

**Quality Factors**:
- **ELIXIR Integration**: Platform/node association indicates community involvement
- **Repository Access**: Source code availability enhances transparency
- **Cost Transparency**: Clear pricing information benefits users

### 6. Community (5% weight)
**Purpose**: Assesses community support and attribution.

**Fields Evaluated**:
- `contact` (3 points): Support contact information
- `credit` (2 points): Developer and contributor attribution

**Quality Factors**:
- **Contact Methods**: Multiple contact options preferred
- **Attribution Completeness**: Comprehensive credit information

## Field-Level Scoring

### Presence Scoring
Most fields use binary presence scoring:
```python
def score_field_presence(field_value, max_points):
    return max_points if field_value else 0
```

### Quality-Based Scoring
Some fields incorporate quality assessment:

#### URL Validation
```python
def score_url_field(url_value, max_points):
    if not url_value:
        return 0
    if is_valid_url_format(url_value):
        return max_points
    return max_points * 0.5  # Partial credit for format issues
```

#### Description Quality
```python
def score_description(description, max_points):
    if not description:
        return 0
    
    score = max_points
    if len(description) < 20:
        score *= 0.5  # Short descriptions get partial credit
    if len(description) > 500:
        score *= 1.1  # Bonus for comprehensive descriptions
    
    return min(score, max_points)
```

#### List Field Scoring
```python  
def score_list_field(field_list, max_points):
    if not field_list:
        return 0
        
    base_score = max_points * 0.6  # Base score for presence
    bonus_score = max_points * 0.4 * min(len(field_list) / 3, 1)  # Bonus for multiple items
    
    return base_score + bonus_score
```

## Calculation Methods

### Category Score Calculation
Each category score is calculated as a weighted sum of its field scores:

```python
def calculate_category_score(field_scores, field_weights, category_weight):
    # Calculate raw category score
    raw_score = sum(field_scores[field] * field_weights[field] 
                   for field in field_scores)
    
    # Normalize to category weight
    max_possible = sum(field_weights.values())
    normalized_score = (raw_score / max_possible) * category_weight
    
    return normalized_score
```

### Final Score Calculation
The final score combines all category scores:

```python
def calculate_final_score(category_scores):
    return sum(category_scores.values())
```

### Tier Assignment
Tier assignment uses configured thresholds:

```python
def assign_tier(final_score, tier_thresholds):
    for tier in sorted(tier_thresholds.keys(), reverse=True):
        min_score, max_score = tier_thresholds[tier]
        if min_score <= final_score <= max_score:
            return tier
    return 1  # Default to lowest tier
```

## Quality Metrics

### Completeness Metrics

#### Field Completeness Rate
```python
def calculate_field_completeness(tools_data, field_name):
    total_tools = len(tools_data)
    tools_with_field = sum(1 for tool in tools_data if tool.get(field_name))
    return tools_with_field / total_tools
```

#### Category Completeness
```python
def calculate_category_completeness(tools_data, category_fields):
    completeness_scores = []
    for tool in tools_data:
        present_fields = sum(1 for field in category_fields if tool.get(field))
        completeness = present_fields / len(category_fields)
        completeness_scores.append(completeness)
    return statistics.mean(completeness_scores)
```

### Quality Distribution Metrics

#### Score Distribution Analysis
```python
def analyze_score_distribution(scores):
    return {
        'mean': statistics.mean(scores),
        'median': statistics.median(scores),
        'std_dev': statistics.stdev(scores),
        'quartiles': numpy.percentile(scores, [25, 50, 75]),
        'range': (min(scores), max(scores))
    }
```

#### Tier Distribution
```python
def calculate_tier_distribution(tier_assignments):
    tier_counts = Counter(tier_assignments)
    total = len(tier_assignments)
    return {tier: count/total for tier, count in tier_counts.items()}
```

## Standards Alignment

### Tool Information Standards Mapping

The scoring system directly aligns with the Tool Information Standards progression:

| Standard Tier | Score Range | Key Requirements |
|---------------|-------------|------------------|
| SPARSE | 0-15 | Basic identification |
| BASIC DETAILS | 16-40 | Scientific classification |
| DETAILED | 41-65 | Technical specifications |
| HIGHLY DETAILED | 66-85 | Rich metadata |
| COMPREHENSIVE | 86-100 | Complete profile |

### EDAM Ontology Integration

The system recognizes and scores EDAM (EMBRACE Data and Methods) ontology terms:

- **Topic Terms**: Scientific domains from EDAM Topic
- **Operation Terms**: Computational operations from EDAM Operation
- **Data Format Terms**: Input/output formats from EDAM Format

### biotoolsSchema Compliance

All scoring aligns with the biotoolsSchema structure:
- Field names match schema definitions
- Data type expectations align with schema
- Required vs. optional field distinctions respected

## Validation and Verification

### Score Validation
```python
def validate_score(score_data):
    """Validate that scores are within expected ranges and sum correctly."""
    final_score = score_data['total_score']
    category_sum = sum(score_data['category_scores'].values())
    
    assert 0 <= final_score <= 100, f"Final score {final_score} out of range"
    assert abs(final_score - category_sum) < 0.01, "Category scores don't sum to final"
    
    for category, score in score_data['category_scores'].items():
        max_category_score = CATEGORY_WEIGHTS[category]
        assert 0 <= score <= max_category_score, f"{category} score out of range"
```

### Methodology Testing
The scoring methodology includes comprehensive tests:
- Unit tests for individual scoring functions
- Integration tests for complete scoring pipeline  
- Regression tests with known tool examples
- Edge case testing with incomplete/malformed data

This scoring methodology provides a robust, transparent, and configurable framework for evaluating bio.tools annotation quality while maintaining alignment with established community standards.
