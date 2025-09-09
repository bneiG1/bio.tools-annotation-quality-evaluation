# Analysis Types

The Bio.tools Annotation Quality Evaluation Platform offers four distinct analysis modes, each designed for different use cases and research objectives. This guide explains when and how to use each analysis type effectively.

## Overview of Analysis Types

| Analysis Type | Purpose | Input | Output | Best For |
|---------------|---------|-------|--------|----------|
| Single Tool | Deep quality assessment | Tool ID | Detailed report | Quality improvement, specific tool evaluation |
| Search & Analyze | Domain exploration | Search query | Multiple tool comparison | Topic research, domain analysis |
| Random Tools | Registry sampling | Number of tools | Quality distribution | Registry overview, baseline assessment |
| Collection Analysis | Batch evaluation | Tool collection | Aggregated metrics | Community analysis, systematic evaluation |

## 1. Single Tool Analysis

### Purpose and Use Cases

Single tool analysis provides the most comprehensive quality assessment for individual bio.tools entries. This mode is ideal for:

- **Tool developers** wanting to improve their tool's metadata quality
- **Registry curators** performing detailed quality assessments
- **Researchers** evaluating specific tools for their work
- **Students** learning about tool annotation standards

### Input Requirements

- **Tool ID**: Valid bio.tools identifier (e.g., "blast", "clustalw", "galaxy")
- **Case sensitivity**: Tool IDs are case-insensitive
- **Validation**: The system validates the tool ID before analysis

### Analysis Process

1. **Data Retrieval**: Fetches tool metadata from bio.tools API
2. **Schema Validation**: Validates against biotoolsSchema
3. **Standards Assessment**: Evaluates ELIXIR Tool Information Standards compliance
4. **Completeness Scoring**: Analyzes field coverage and quality
5. **Linting**: Runs biotools-linter for additional quality checks
6. **Report Generation**: Compiles comprehensive quality report

### Output Components

#### Quality Metrics
- **Overall Grade** (A-F): Composite quality score
- **Standards Tier** (1-5): ELIXIR compliance level
- **Completeness Score** (%): Field coverage percentage
- **Schema Validation**: Structural validity status

#### Detailed Analysis
- **Field-by-field assessment**: Individual field quality scores
- **Missing elements**: Required and recommended fields not present
- **Content quality**: URL validation, EDAM term verification
- **Lint issues**: Categorized by severity (critical, error, warning, info)

#### Recommendations
- **Improvement suggestions**: Specific actions to enhance quality
- **Tier advancement paths**: Steps to reach higher standards tiers
- **Best practices**: General quality improvement guidance

### Example Workflow

```
1. Enter "blast" as tool ID
2. Click "Analyze Tool"
3. Review overall grade (likely A or B)
4. Examine specific recommendations
5. Export results for reference
```

## 2. Search & Analyze Tools

### Purpose and Use Cases

Search analysis allows you to discover and evaluate multiple tools related to specific topics, techniques, or domains. Perfect for:

- **Comparative analysis** of tools in a specific domain
- **Literature reviews** requiring tool quality assessment
- **Technology surveys** across bioinformatics domains
- **Educational research** on tool availability and quality

### Search Configuration

#### Search Fields
- **Name** (always included): Tool name and title
- **Description**: Tool descriptions and summaries
- **Topics**: EDAM topic annotations
- **Operations**: Functional categories and operations
- **Data Types**: Input/output data type specifications
- **Formats**: Supported file formats
- **Publications**: Associated research papers
- **Collections**: Tool collections and communities

#### Search Parameters
- **Query**: Free-text search terms
- **Result Limit**: 1-50 tools (adjustable based on analysis needs)
- **Sort Order**: 
  - Relevance (default)
  - Last Update (newest first)
  - Score (most popular)

### Analysis Process

1. **Query Execution**: Searches bio.tools registry using specified criteria
2. **Result Filtering**: Applies relevance and limit filters
3. **Batch Analysis**: Analyzes each tool using the same quality metrics as single tool analysis
4. **Aggregation**: Compiles comparative statistics and visualizations
5. **Ranking**: Orders results by quality scores and relevance

### Output Components

#### Summary Statistics
- **Total tools found**: Number of tools matching search criteria
- **Average quality score**: Mean quality across all results
- **Quality distribution**: Breakdown of grades (A, B, C, D, F)
- **Standards compliance**: Tier distribution analysis

#### Comparative Visualizations
- **Quality comparison chart**: Side-by-side quality metrics
- **Distribution histograms**: Score and grade distributions
- **Trend analysis**: Quality patterns across results

#### Detailed Results Table
- **Sortable columns**: Quality metrics, tool information
- **Quick preview**: Summary of each tool's quality
- **Drill-down links**: Access to detailed individual analysis

### Search Strategy Tips

#### Effective Query Construction
- **Use specific terms**: "protein structure prediction" vs "protein"
- **Combine concepts**: "machine learning AND genomics"
- **Use synonyms**: Include alternative terminology
- **Domain-specific terms**: Leverage EDAM ontology terms

#### Result Optimization
- **Start broad, narrow down**: Begin with general terms, refine based on results
- **Adjust field selection**: Focus search on most relevant metadata fields
- **Experiment with limits**: Balance comprehensiveness with analysis time

### Example Workflows

#### Workflow 1: Domain Survey
```
Query: "phylogenetic analysis"
Fields: Name, Description, Topics, Operations
Limit: 20 tools
Goal: Compare phylogenetic software quality
```

#### Workflow 2: Method Comparison
```
Query: "machine learning AND protein"
Fields: Name, Description, Operations
Limit: 15 tools
Goal: Evaluate ML tools for protein analysis
```

## 3. Random Tools Analysis

### Purpose and Use Cases

Random analysis provides unbiased sampling of the bio.tools registry for:

- **Registry quality assessment**: Understanding overall metadata quality
- **Baseline establishment**: Setting quality benchmarks
- **Tool discovery**: Finding unexpected or interesting tools
- **Statistical analysis**: Representative sampling for research

### Configuration Options

#### Sample Size
- **Range**: 1-20 tools
- **Recommendations**:
  - 5 tools: Quick overview
  - 10 tools: Balanced sample
  - 15-20 tools: Comprehensive assessment

#### Sampling Method
- **True random**: Unbiased selection across entire registry
- **Stratified sampling**: Representative across tool categories
- **Quality-blind**: No bias toward high or low quality tools

### Analysis Benefits

#### Unbiased Assessment
- **No selection bias**: Avoids cherry-picking high-quality tools
- **Representative sampling**: Reflects actual registry state
- **Discovery potential**: May reveal hidden gems or quality issues

#### Baseline Metrics
- **Quality benchmarks**: Establishes expected quality levels
- **Trend analysis**: Track registry improvement over time
- **Comparative context**: Provides context for domain-specific analyses

### Output Interpretation

#### Statistical Insights
- **Quality distribution**: Actual grade distribution in registry
- **Common issues**: Frequently occurring metadata problems
- **Best practices**: Examples of high-quality annotations

#### Quality Patterns
- **Field completion rates**: Which fields are commonly filled
- **Standards compliance**: Typical tier achievement
- **Content quality**: URL validity, description quality

### Example Use Cases

#### Registry Assessment
```
Sample Size: 15 tools
Purpose: Evaluate overall registry quality
Analysis: Focus on completion rates and common issues
```

#### Baseline Study
```
Sample Size: 20 tools
Purpose: Establish quality benchmarks
Analysis: Statistical distribution of quality metrics
```

## 4. Collection Analysis

### Purpose and Use Cases

Collection analysis enables systematic evaluation of tool groups for:

- **Community assessment**: Evaluating specific bioinformatics communities
- **Domain analysis**: Comprehensive quality review of research domains
- **Curation support**: Supporting registry curation efforts
- **Comparative studies**: Cross-community quality comparisons

### Collection Types

#### Predefined Collections
- **COVID-19 Tools**: Pandemic-related bioinformatics tools
- **Recent Tools**: Recently added or updated tools
- **Popular Tools**: Highly accessed and cited tools

#### Custom Collections
- **User-defined lists**: Specific tool sets defined by user
- **Research-focused**: Tools relevant to specific research projects
- **Institution-based**: Tools from specific organizations

### Collection Configuration

#### Predefined Collection Setup
1. Select collection type from dropdown
2. System automatically identifies relevant tools
3. Applies appropriate filtering and limits

#### Custom Collection Setup
1. Select "Custom Collection" option
2. Enter tool IDs in text area (one per line)
3. System validates each tool ID
4. Processes valid tools for analysis

### Analysis Scope

#### Comprehensive Evaluation
- **Individual tool analysis**: Each tool receives full quality assessment
- **Aggregate statistics**: Collection-wide quality metrics
- **Comparative ranking**: Tools ranked within collection context
- **Trend identification**: Quality patterns across the collection

#### Community Insights
- **Quality leadership**: Identify highest quality tools in domain
- **Common gaps**: Recurring quality issues across domain
- **Best practices**: Examples of exemplary annotation
- **Improvement opportunities**: Systematic enhancement recommendations

### Output Components

#### Collection Overview
- **Tools analyzed**: Total number and success rate
- **Quality summary**: Average scores and grade distribution
- **Standards compliance**: Tier achievement across collection
- **Issue prevalence**: Common problems and their frequency

#### Comparative Analysis
- **Quality ranking**: Tools ordered by quality metrics
- **Outlier identification**: Exceptionally high or low quality tools
- **Pattern analysis**: Trends in metadata quality
- **Benchmark comparison**: How collection compares to registry average

#### Detailed Reports
- **Individual tool cards**: Summary of each tool's quality
- **Drill-down capability**: Access full analysis for any tool
- **Export options**: Collection data in multiple formats
- **Visualization**: Charts and graphs of collection metrics

### Strategic Applications

#### Curation Workflows
1. **Identify focus areas**: Use collection analysis to find domains needing attention
2. **Prioritize improvements**: Focus on tools with highest impact potential
3. **Track progress**: Regular collection analysis to measure improvement
4. **Community engagement**: Share results with relevant communities

#### Research Applications
1. **Quality assessment**: Evaluate tools before research use
2. **Method comparison**: Compare tools within specific domains
3. **Gap analysis**: Identify areas lacking high-quality tools
4. **Trend monitoring**: Track quality evolution in research domains

### Example Collection Analyses

#### COVID-19 Research Tools
```
Collection: COVID-19 Tools
Size: ~50 tools
Focus: Pandemic response tool quality
Insights: Rapid development vs. quality trade-offs
```

#### Structural Biology Tools
```
Collection: Custom (protein structure tools)
Size: 25 tools
Focus: Community-specific quality assessment
Insights: Domain expertise reflected in annotation quality
```

## Choosing the Right Analysis Type

### Decision Framework

| Goal | Recommended Analysis | Rationale |
|------|---------------------|-----------|
| Improve specific tool | Single Tool | Detailed, actionable recommendations |
| Explore research domain | Search & Analyze | Comprehensive domain coverage |
| Assess registry quality | Random Tools | Unbiased, representative sampling |
| Evaluate community | Collection Analysis | Systematic community assessment |

### Combining Analysis Types

#### Sequential Analysis Strategy
1. **Start with Random**: Establish baseline understanding
2. **Focus with Search**: Explore relevant domains
3. **Deep-dive with Single**: Analyze specific tools of interest
4. **Aggregate with Collections**: Systematic evaluation

#### Comparative Analysis Strategy
1. **Multiple searches**: Compare different domains
2. **Collection comparison**: Evaluate different communities
3. **Temporal analysis**: Track quality changes over time

## Best Practices

### Planning Your Analysis

1. **Define objectives clearly**: What do you want to learn?
2. **Choose appropriate scope**: Match analysis type to goals
3. **Consider resource constraints**: Analysis time and API limits
4. **Plan for follow-up**: How will you use the results?

### Interpreting Results

1. **Context matters**: Consider domain-specific factors
2. **Look for patterns**: Identify systematic issues
3. **Consider improvement potential**: Focus on actionable insights
4. **Share findings**: Contribute to community knowledge

### Documentation and Sharing

1. **Export important results**: Save data for future reference
2. **Document methodology**: Record analysis parameters
3. **Share insights**: Contribute to community improvement efforts
4. **Track changes**: Monitor quality improvements over time

## Next Steps

- **[Quality Metrics](quality-metrics.md)**: Understand the scoring system in detail
- **[Export & Reports](export-reports.md)**: Learn to work with analysis results
- **[Examples](../examples/basic-usage.md)**: See practical analysis examples
