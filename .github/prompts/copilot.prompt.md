```prompt
---
mode: ask
---

# bio.tools Quality Evaluation Task Definition

## Primary Objectives

When working on this project, focus on these key deliverables:

### 1. Data Pipeline Implementation
- **Requirement**: Build modular pipeline (collect → validate → score → report)
- **Constraint**: Must handle ~27,000 bio.tools entries efficiently
- **Success Criteria**: Process proteomics domain (500+ tools) in <5 minutes

### 2. Scoring Algorithm Development
- **Requirement**: Map Tool Information Standards to tier-based scoring (1-5)
- **Constraint**: Preserve original bio.tools JSON structure throughout pipeline
- **Success Criteria**: Reproducible tier assignments with clear rationale

### 3. Schema Integration
- **Requirement**: Validate against biotoolsSchema and integrate linter diagnostics
- **Constraint**: Handle external tool dependency (3top1a/biotools-linter)
- **Success Criteria**: Detect structural issues and merge with completeness scores

### 4. Visualization & Reporting
- **Requirement**: Generate radar charts, heatmaps, and CSV summaries
- **Constraint**: Reports must scale to full bio.tools registry
- **Success Criteria**: Clear visual patterns showing quality gaps by domain

## Implementation Priorities

1. **Start with data collection**: Implement `BioToolsAPIClient` with caching
2. **Build scoring foundation**: Create tier assignment logic for Tool Information Standards
3. **Add validation layer**: Integrate biotoolsSchema validation
4. **Develop reporting**: Begin with CSV outputs, then add visualizations

## Quality Gates

- All API interactions must handle rate limiting gracefully
- Test with real bio.tools entries from multiple domains
- Ensure pipeline can resume from cached data if API fails
- Document biotoolsSchema field mappings in scoring logic

## Domain Context Requirements

- Understand ELIXIR bio.tools registry structure and metadata standards
- Recognize bioinformatics tool categorization (proteomics, genomics, etc.)
- Handle JSON-heavy data processing with pandas for aggregation
- Design for reproducible research workflows with cached intermediate results
```