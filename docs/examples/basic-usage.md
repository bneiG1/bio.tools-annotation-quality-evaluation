# Basic Usage Examples

This guide provides practical examples of using the Bio.tools Annotation Quality Evaluation Platform for common analysis scenarios.

## Getting Started Examples

### Example 1: Your First Tool Analysis

Let's start with a simple analysis of a well-known bioinformatics tool:

**Steps**:

1. **Launch the Application**
   ```powershell
   python app.py
   ```

2. **Navigate to Single Tool Analysis**
   - The interface opens in your browser
   - You'll see four analysis mode cards
   - Click on "Single Tool Analysis"

3. **Enter Tool ID**
   - In the text field, type: `blast`
   - Click "🔍 Analyze Tool"

4. **Review Results**
   - Wait for analysis to complete (usually 10-30 seconds)
   - Review the quality grade and metrics
   - Explore recommendations for improvement

**Expected Results**:
- BLAST typically receives a Grade B (80-89%)
- High standards tier (Tier 3-4)
- Good schema validation
- Some recommendations for documentation enhancement

### Example 2: Search and Compare Tools

Find and analyze multiple phylogenetic analysis tools:

**Steps**:

1. **Go to Search & Analyze Tools**
2. **Configure Search**:
   - Query: `phylogenetic analysis`
   - Fields: Enable Name, Description, Topics, Operations
   - Result Limit: 10 tools
   - Sort: By relevance

3. **Execute Search**
   - Click "🔍 Search & Analyze"
   - Wait for bulk analysis to complete

4. **Explore Results**
   - Review summary statistics
   - Examine quality distribution chart
   - Use the detailed results table to compare tools
   - Click on individual tools for detailed analysis

**Expected Results**:
- 10+ phylogenetic tools found
- Quality grades typically range from C to A
- Clear visualization of quality distribution
- Comparative table for easy tool selection

## Domain-Specific Analysis Examples

### Example 3: Protein Structure Analysis Tools

**Objective**: Evaluate the quality of protein structure prediction and analysis tools

**Search Configuration**:
- **Query**: `protein structure prediction`
- **Fields**: Name, Description, Topics, Operations
- **Filters**: Focus on computational tools
- **Limit**: 15 tools

**Analysis Steps**:

1. **Execute Search**:
   ```
   Search Query: "protein structure prediction"
   Expected Tools: ChimeraX, PyMOL, SWISS-MODEL, etc.
   ```

2. **Review Domain Patterns**:
   - Structure tools often have good documentation
   - Visualization tools may have lower completeness scores
   - Academic tools vs. commercial tools show quality differences

3. **Detailed Tool Analysis**:
   - Select highest-rated tool for detailed review
   - Compare against lowest-rated tool
   - Identify common improvement areas

**Typical Findings**:
- **High-quality tools**: Comprehensive documentation, proper EDAM terms
- **Common issues**: Missing download links, incomplete version information
- **Domain characteristics**: Strong publication links, visualization focus

### Example 4: Machine Learning in Bioinformatics

**Objective**: Assess quality of ML tools in bioinformatics

**Search Configuration**:
- **Query**: `machine learning genomics`
- **Additional Search**: `deep learning bioinformatics`
- **Combined Analysis**: Merge results for comprehensive view

**Step-by-Step Analysis**:

1. **First Search - ML Genomics**:
   ```
   Query: "machine learning genomics"
   Expected Results: 8-12 tools
   Quality Range: Typically C to B grades
   ```

2. **Second Search - Deep Learning**:
   ```
   Query: "deep learning bioinformatics"
   Expected Results: 6-10 tools
   Quality Range: Variable, often newer tools with less documentation
   ```

3. **Quality Pattern Analysis**:
   - Newer ML tools often have lower completeness scores
   - Code repositories well-linked but documentation sparse
   - Publication links strong but user guides weak

**Key Insights**:
- **Rapid development impact**: New tools may lack comprehensive metadata
- **Documentation gaps**: Technical papers vs. user documentation
- **Community tools**: Often high-quality code but minimal bio.tools annotation

## Bulk Analysis Examples

### Example 5: COVID-19 Tools Collection Analysis

**Objective**: Evaluate pandemic-related bioinformatics tools

**Analysis Steps**:

1. **Select Collection Analysis**
2. **Choose "COVID-19 Tools"** from dropdown
3. **Execute Collection Analysis**

**Detailed Examination**:

1. **Collection Overview**:
   ```
   Typical Results:
   - 30-50 tools analyzed
   - Average quality: 70-75%
   - Grade distribution: Mostly B and C grades
   ```

2. **Quality Patterns**:
   - **Rapid development**: Tools created quickly during pandemic
   - **Variable quality**: Some excellent, others minimal annotation
   - **Strong publication links**: Academic focus evident

3. **Improvement Opportunities**:
   - Standardize documentation approaches
   - Enhance EDAM term coverage
   - Improve long-term maintenance indicators

### Example 6: Custom Collection - Your Research Tools

**Objective**: Analyze tools specific to your research domain

**Custom Tool List**:
```
blast
clustalw
muscle
mafft
phylip
mega
iqtree
fasttree
raxml
```

**Analysis Process**:

1. **Setup Custom Collection**:
   - Select "Custom Collection" from dropdown
   - Enter tool IDs (one per line) in text area
   - Click "📊 Analyze Collection"

2. **Review Batch Results**:
   - Summary statistics for your tool set
   - Quality distribution specific to your domain
   - Comparative ranking of your tools

3. **Strategic Analysis**:
   - Identify highest quality tools for priority use
   - Note tools needing improvement for community contribution
   - Document quality baseline for future tracking

## Quality Improvement Examples

### Example 7: Before and After Tool Improvement

**Scenario**: You're a tool developer wanting to improve your tool's bio.tools entry

**Initial Analysis**:

1. **Analyze Current State**:
   ```
   Tool ID: your-tool-name
   Initial Grade: D (65%)
   Key Issues:
   - Missing documentation links
   - Incomplete EDAM terms
   - No download information
   ```

2. **Review Detailed Recommendations**:
   - Critical: Add homepage URL
   - Important: Include publication DOI
   - Recommended: Add installation instructions

**Improvement Process**:

1. **Update bio.tools Entry**:
   - Add missing required fields
   - Enhance description with keywords
   - Include proper EDAM topic and operation terms
   - Add documentation and download links

2. **Re-analyze Tool**:
   ```powershell
   # Clear cache to ensure fresh data
   Remove-Item data/cache/tool_your-tool-name.json
   
   # Re-run analysis
   # Navigate to Single Tool Analysis
   # Enter your tool ID
   # Review improved results
   ```

3. **Compare Results**:
   ```
   Before: Grade D (65%)
   After:  Grade B (82%)
   
   Improvements:
   - Standards tier: 2 → 3
   - Completeness: 45% → 78%
   - Schema validation: Pass
   - Lint issues: 15 → 3
   ```

### Example 8: Community Quality Initiative

**Objective**: Lead a community effort to improve tool quality in your domain

**Planning Phase**:

1. **Baseline Assessment**:
   ```
   Domain: Proteomics
   Search: "proteomics mass spectrometry"
   Initial Results:
   - 25 tools found
   - Average grade: C+ (74%)
   - 40% need significant improvement
   ```

2. **Prioritization Strategy**:
   - Focus on most-used tools first
   - Identify easy wins (missing URLs, simple fixes)
   - Coordinate with tool developers

**Implementation Example**:

1. **Monthly Progress Tracking**:
   ```
   Month 1: Baseline analysis
   Month 2: Contact tool developers
   Month 3: First improvements implemented
   Month 4: Re-analysis and progress assessment
   ```

2. **Community Engagement**:
   - Share analysis results with community
   - Create improvement guidelines
   - Recognize contributors and improvements

## Advanced Analysis Examples

### Example 9: Temporal Quality Analysis

**Objective**: Track quality changes over time

**Methodology**:

1. **Regular Analysis Schedule**:
   ```powershell
   # Monthly analysis script
   $date = Get-Date -Format "yyyy-MM-dd"
   
   # Analyze core tools
   # Export results with timestamp
   # Store in dated directory
   ```

2. **Trend Analysis**:
   - Compare monthly results
   - Identify improving and declining tools
   - Correlate with bio.tools updates

**Example Results Tracking**:
```
Tool: galaxy
January:  Grade A (91%)
February: Grade A (92%) - Documentation improved
March:    Grade A (94%) - New features documented
April:    Grade A (93%) - Minor URL updates
```

### Example 10: Cross-Domain Quality Comparison

**Objective**: Compare quality patterns across different bioinformatics domains

**Domains to Compare**:

1. **Sequence Analysis**:
   ```
   Search: "sequence alignment"
   Typical Quality: High (mature domain)
   Common Strengths: Documentation, publications
   ```

2. **Structural Biology**:
   ```
   Search: "protein structure"
   Typical Quality: High (established tools)
   Common Strengths: Visualization, academic links
   ```

3. **Machine Learning**:
   ```
   Search: "machine learning bioinformatics"
   Typical Quality: Variable (emerging domain)
   Common Issues: Documentation gaps, rapid development
   ```

4. **Workflow Management**:
   ```
   Search: "workflow management"
   Typical Quality: High (community focus)
   Common Strengths: Documentation, examples
   ```

**Comparative Analysis Process**:

1. **Standardized Analysis**:
   - Use same search parameters
   - Consistent result limits
   - Export results for comparison

2. **Pattern Identification**:
   - Quality averages by domain
   - Common issues and strengths
   - Domain-specific recommendations

## Export and Sharing Examples

### Example 11: Creating Analysis Reports

**Research Report Generation**:

1. **Comprehensive Domain Analysis**:
   ```
   Domain: Phylogenetics
   Analysis Date: 2025-01-09
   Tools Analyzed: 15
   
   Export Formats:
   - JSON: Complete data for further analysis
   - CSV: Summary table for publication
   - Charts: Quality distribution visualization
   ```

2. **Report Structure**:
   ```
   1. Executive Summary
      - Key findings
      - Quality overview
      - Recommendations

   2. Detailed Analysis
      - Tool-by-tool assessment
      - Quality metrics breakdown
      - Improvement priorities

   3. Appendices
      - Raw data (CSV)
      - Methodology notes
      - Analysis parameters
   ```

### Example 12: Collaborative Quality Assessment

**Multi-Institution Collaboration**:

1. **Standardized Protocol**:
   ```
   Analysis Parameters:
   - Search scope: Agreed domain terms
   - Result limits: Consistent across sites
   - Export format: JSON for data sharing
   - Analysis frequency: Monthly
   ```

2. **Data Sharing Workflow**:
   ```powershell
   # Export analysis
   # Share via Git repository
   git add monthly_analysis_2025-01.json
   git commit -m "Add January 2025 analysis results"
   git push origin main
   
   # Collaborative analysis
   # Merge results from multiple sites
   # Generate combined reports
   ```

## Performance Optimization Examples

### Example 13: Large-Scale Analysis

**Analyzing 100+ Tools Efficiently**:

1. **Batch Strategy**:
   ```
   Approach: Process in chunks of 10-15 tools
   Timing: Allow 2-3 minutes per chunk
   Caching: Leverage cached results when possible
   ```

2. **Resource Management**:
   ```
   Memory: Monitor during large analyses
   Network: Respect API rate limits
   Storage: Plan for result storage needs
   ```

3. **Error Handling**:
   ```
   Strategy: Continue analysis despite individual failures
   Logging: Track failed analyses for retry
   Recovery: Manual retry for critical tools
   ```

## Next Steps

After working through these examples:

1. **Explore Advanced Features**: Try different visualization options and export formats
2. **Contribute Improvements**: Use insights to improve tools in your domain
3. **Share Results**: Contribute to community knowledge about tool quality
4. **Automate Workflows**: Create scripts for regular quality monitoring

For more advanced usage patterns, see:
- **[Advanced Analysis Guide](advanced-analysis.md)**: Complex analysis scenarios
- **[API Integration](api-integration.md)**: Programmatic usage examples
- **[Quality Metrics Deep Dive](../user-guide/quality-metrics.md)**: Understanding the scoring system
