# Standards Mapping

This document explains how the bio.tools Annotation Quality Evaluation system aligns with community standards and specifications.

## Table of Contents
1. [Tool Information Standards Alignment](#tool-information-standards-alignment)
2. [biotoolsSchema Mapping](#biotoolsschema-mapping)
3. [EDAM Ontology Integration](#edam-ontology-integration)
4. [Quality Framework Alignment](#quality-framework-alignment)
5. [Community Standards Support](#community-standards-support)

## Tool Information Standards Alignment

The evaluation system directly implements the [ELIXIR Tool Information Standards](https://bio-tools.github.io/Tool-Information-Standards/), providing a concrete framework for the five-tier quality model.

### Tier Mapping

| Standard Tier | Score Range | Description | Key Requirements |
|---------------|-------------|-------------|------------------|
| **SPARSE** | 0-15 | Minimal viable entry | Basic identification and access |
| **BASIC DETAILS** | 16-40 | Essential discoverability | Scientific classification |
| **DETAILED** | 41-65 | Comprehensive metadata | Technical specifications |
| **HIGHLY DETAILED** | 66-85 | Rich tool description | Enhanced discoverability |
| **COMPREHENSIVE** | 86-100 | Complete tool profile | Community integration |

### Standards Implementation

#### SPARSE Tier Requirements
**Standard Requirements:**
- Tool name and description
- Basic access information (homepage or repository)
- Unique identifier

**System Implementation:**
```python
def meets_sparse_requirements(tool_data):
    required = ['name', 'description', 'biotoolsID']
    access_methods = ['homepage', 'repository', 'link']
    
    has_basic = all(field in tool_data for field in required)
    has_access = any(field in tool_data for field in access_methods)
    
    return has_basic and has_access
```

**Scoring Weights:**
- Name: 4 points
- Description: 6 points  
- Homepage: 3 points
- biotoolsID: 2 points
- **Total: 15 points (matches tier threshold)**

#### BASIC DETAILS Tier Requirements
**Standard Requirements (beyond SPARSE):**
- Tool type classification
- Scientific topic annotation
- Basic functional description

**System Implementation:**
```python
def meets_basic_details_requirements(tool_data):
    core_fields = ['toolType', 'topic', 'function']
    return all(field in tool_data for field in core_fields)
```

**Additional Scoring:**
- toolType: 6 points
- topic: 8 points
- function/operation: 6 points
- **Additional: 20 points (total: 35 points)**

#### DETAILED Tier Requirements
**Standard Requirements (beyond BASIC DETAILS):**
- Platform compatibility information
- Programming language (if applicable)  
- License information
- Scientific publication
- Documentation

**System Implementation:**
```python
def meets_detailed_requirements(tool_data):
    technical_fields = ['operatingSystem', 'language', 'license']
    scientific_fields = ['publication']
    access_fields = ['documentation']
    
    return (any(field in tool_data for field in technical_fields) and
            any(field in tool_data for field in scientific_fields) and
            any(field in tool_data for field in access_fields))
```

#### HIGHLY DETAILED Tier Requirements
**Standard Requirements (beyond DETAILED):**
- Version information
- Maturity/development status
- Input/output format specifications
- Download/access instructions
- Contact information

#### COMPREHENSIVE Tier Requirements
**Standard Requirements (beyond HIGHLY DETAILED):**
- Multiple validation sources
- Community integration markers
- Complete accessibility information
- Comprehensive attribution

### Gap Analysis

The system identifies where current bio.tools entries fall short of standards:

```python
def analyze_tier_gaps(tool_data, current_tier, target_tier):
    """Identify specific improvements needed to reach target tier."""
    gaps = []
    
    if target_tier >= 2 and current_tier < 2:
        if 'toolType' not in tool_data:
            gaps.append("Add tool type classification")
        if 'topic' not in tool_data:
            gaps.append("Add scientific topic annotation")
    
    if target_tier >= 3 and current_tier < 3:
        if 'publication' not in tool_data:
            gaps.append("Add primary publication")
        if 'license' not in tool_data:
            gaps.append("Specify software license")
    
    return gaps
```

## biotoolsSchema Mapping

The system validates and scores fields according to the [biotoolsSchema](https://github.com/bio-tools/biotoolsschema) specification.

### Schema Structure Alignment

#### Core Fields Mapping
```yaml
# biotoolsSchema -> Scoring System
name: basic_info.name (4 points)
description: basic_info.description (6 points)  
homepage: basic_info.homepage (3 points)
biotoolsID: basic_info.biotoolsID (2 points)
biotoolsCURIE: basic_info.biotoolsCURIE (1 point)
```

#### Function Structure
```json
{
  "function": [
    {
      "operation": [...],  // technical_info.operation (6 points)
      "input": [...],      // accessibility.input (scored as part of formats)
      "output": [...],     // accessibility.output (scored as part of formats)
      "note": "..."        // technical_info.function (7 points)
    }
  ]
}
```

#### Publication Structure
```json
{
  "publication": [
    {
      "doi": "...",        // core_metadata.publication (10 points)
      "pmid": "...",       // Alternative identifier
      "pmcid": "...",      // Alternative identifier
      "type": "Primary"    // Weighted by type (Primary > Method > Other)
    }
  ]
}
```

### Schema Validation Integration

```python
class BiotoolsSchemaValidator:
    """Validates tool data against biotoolsSchema."""
    
    def __init__(self, schema_path):
        with open(schema_path) as f:
            self.schema = json.load(f)
    
    def validate_tool(self, tool_data):
        """Validate tool against schema."""
        try:
            jsonschema.validate(tool_data, self.schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
    
    def get_field_requirements(self, field_path):
        """Get requirements for a specific field."""
        # Navigate schema structure to get field requirements
        pass
```

### Schema Extension Points

The system can accommodate biotoolsSchema extensions:

```python
def handle_schema_extension(tool_data, extension_fields):
    """Handle additional fields not in core schema."""
    extended_score = 0
    
    for field, weight in extension_fields.items():
        if field in tool_data:
            extended_score += weight
    
    return extended_score
```

## EDAM Ontology Integration

The system recognizes and scores [EDAM](http://edamontology.org/) (EMBRACE Data and Methods) ontology terms.

### EDAM Term Recognition

#### Topic Terms (EDAM:topic)
```python
def score_edam_topics(topics):
    """Score EDAM topic annotations."""
    score = 0
    
    for topic in topics:
        if 'term' in topic:
            score += 2  # Base score for any topic
            
            # Bonus for specific EDAM URI
            if 'uri' in topic and 'edamontology.org' in topic['uri']:
                score += 1
    
    return min(score, 8)  # Cap at maximum topic score
```

#### Operation Terms (EDAM:operation)
```python  
def score_edam_operations(operations):
    """Score EDAM operation annotations."""
    score = 0
    
    for operation in operations:
        if 'term' in operation:
            score += 1.5  # Base score for operation
            
            # Bonus for EDAM URI
            if 'uri' in operation and 'edamontology.org' in operation['uri']:
                score += 0.5
    
    return min(score, 6)  # Cap at maximum operation score
```

#### Data Format Terms (EDAM:format)
```python
def score_edam_formats(formats):
    """Score EDAM format annotations."""
    score = 0
    
    for format_item in formats:
        if 'term' in format_item:
            score += 1  # Base score for format
            
            # Bonus for EDAM URI
            if 'uri' in format_item and 'edamontology.org' in format_item['uri']:
                score += 0.5
    
    return score  # No cap - more formats = better
```

### EDAM Quality Indicators

```python
def assess_edam_quality(tool_data):
    """Assess quality of EDAM term usage."""
    quality_indicators = {
        'has_topic_uris': False,
        'has_operation_uris': False,
        'has_format_uris': False,
        'topic_specificity': 0,
        'operation_coverage': 0
    }
    
    # Check for EDAM URIs
    topics = tool_data.get('topic', [])
    for topic in topics:
        if 'uri' in topic and 'edamontology.org' in topic['uri']:
            quality_indicators['has_topic_uris'] = True
            
            # Assess specificity (deeper in hierarchy = more specific)
            if 'topic_' in topic['uri']:
                depth = topic['uri'].split('_')[-1]
                if depth.isdigit():
                    quality_indicators['topic_specificity'] = max(
                        quality_indicators['topic_specificity'], 
                        int(depth)
                    )
    
    return quality_indicators
```

## Quality Framework Alignment

### FAIR Data Principles

The scoring system promotes FAIR (Findable, Accessible, Interoperable, Reusable) principles:

#### Findability
- **Rich metadata**: Core metadata category (25% weight)
- **Unique identifiers**: biotoolsID requirements
- **Searchable content**: Description quality assessment

#### Accessibility  
- **Access protocols**: Homepage and download links
- **Authentication clarity**: Access restrictions documentation
- **Metadata persistence**: Version and maintenance information

#### Interoperability
- **Standard vocabularies**: EDAM ontology integration
- **Format specifications**: Input/output format documentation
- **Technical standards**: Schema compliance validation

#### Reusability
- **Usage licenses**: License information requirements
- **Detailed provenance**: Publication and attribution
- **Documentation**: Usage instructions and examples

### Research Software Quality

Alignment with research software quality frameworks:

#### Technical Quality
- **Version control**: Repository information (5 points)
- **Testing information**: Where available in metadata
- **Documentation**: User guides and API documentation (8 points)

#### Scientific Quality  
- **Peer review**: Publication requirements (10 points)
- **Benchmarking**: Performance information where available
- **Validation**: Testing and verification information

#### Community Quality
- **Maintenance**: Contact information (3 points)
- **Support**: Community and support channels
- **Contribution**: Developer credits and attribution (2 points)

### Metadata Quality Standards

#### Dublin Core Alignment
```python
DUBLIN_CORE_MAPPING = {
    'dc:title': 'name',
    'dc:description': 'description', 
    'dc:creator': 'credit',
    'dc:publisher': 'contact',
    'dc:identifier': 'biotoolsID',
    'dc:subject': 'topic',
    'dc:type': 'toolType',
    'dc:rights': 'license'
}
```

#### Schema.org Integration
The system supports schema.org software application markup:

```python
def generate_schema_org(tool_data, score_data):
    """Generate Schema.org structured data."""
    return {
        "@context": "https://schema.org/",
        "@type": "SoftwareApplication",
        "name": tool_data.get('name'),
        "description": tool_data.get('description'),
        "url": tool_data.get('homepage'),
        "applicationCategory": tool_data.get('toolType'),
        "operatingSystem": tool_data.get('operatingSystem'),
        "softwareVersion": tool_data.get('version'),
        "license": tool_data.get('license'),
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": score_data['total_score'],
            "bestRating": 100
        }
    }
```

## Community Standards Support

### ELIXIR Integration

#### Platform Services
```python
def assess_elixir_integration(tool_data):
    """Assess integration with ELIXIR infrastructure."""
    integration_score = 0
    
    if 'elixirPlatform' in tool_data:
        platforms = tool_data['elixirPlatform']
        integration_score += len(platforms) * 2  # 2 points per platform
    
    if 'elixirNode' in tool_data:
        nodes = tool_data['elixirNode']
        integration_score += len(nodes) * 2  # 2 points per node
    
    if 'elixirCommunity' in tool_data:
        communities = tool_data['elixirCommunity']
        integration_score += len(communities) * 2  # 2 points per community
    
    return min(integration_score, 6)  # Cap at 6 points
```

#### Galaxy Integration
```python
def assess_galaxy_integration(tool_data):
    """Assess Galaxy tool shed integration."""
    if 'collection' in tool_data:
        collections = tool_data.get('collection', [])
        for collection in collections:
            if 'galaxy' in collection.lower():
                return 3  # Bonus for Galaxy integration
    return 0
```

### Workflow Standards

#### Common Workflow Language (CWL)
```python
def assess_workflow_compatibility(tool_data):
    """Assess workflow system compatibility."""
    workflow_score = 0
    
    # Check for workflow descriptions
    if 'link' in tool_data:
        links = tool_data['link']
        for link in links:
            if any(wf in link.get('type', '').lower() 
                   for wf in ['cwl', 'nextflow', 'snakemake', 'workflow']):
                workflow_score += 2
    
    return min(workflow_score, 4)
```

### Container Standards

#### Docker/Singularity Support
```python
def assess_containerization(tool_data):
    """Assess container availability."""
    container_score = 0
    
    if 'download' in tool_data:
        downloads = tool_data['download']
        for download in downloads:
            download_type = download.get('type', '').lower()
            if 'container' in download_type or 'docker' in download_type:
                container_score += 3
    
    return min(container_score, 6)
```

### Quality Assurance Standards

#### Continuous Integration
```python
def assess_qa_practices(tool_data):
    """Assess quality assurance indicators."""
    qa_score = 0
    
    # Repository-based QA indicators
    if 'repository' in tool_data:
        repos = tool_data['repository']
        for repo in repos:
            if 'github.com' in repo.get('url', ''):
                qa_score += 2  # GitHub integration potential
    
    # Testing information
    if 'documentation' in tool_data:
        docs = tool_data['documentation']
        for doc in docs:
            if 'test' in doc.get('type', '').lower():
                qa_score += 3
    
    return min(qa_score, 8)
```

This standards mapping ensures that the evaluation system not only assesses current quality but also promotes alignment with established community standards and best practices.
