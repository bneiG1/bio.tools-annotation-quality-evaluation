# bio.tools Annotation Quality — Evaluation & Enhancement

A semi-automated pipeline to assess and improve the metadata quality of tools registered in the ELIXIR bio.tools registry.

## Overview

Metadata quality in the bio.tools registry directly affects discoverability and reuse. This project builds a repeatable workflow that:

- scores tool metadata completeness against the Tool Information Standards and the biotoolsSchema
- integrates linter diagnostics to detect structural and syntactic issues
- summarizes missing or malformed attributes across collections/domains
- produces visual reports (radar charts, heatmaps) and recommendations for standard improvements

The pipeline is designed to be modular so it can be split into two sub-projects: (1) completeness scoring and (2) linter analysis.

## Key objectives

1. Implement a tier-based scoring pipeline that assigns each tool a completeness score and a tier (1–5).
2. Analyze completeness patterns across domains/collections and identify commonly missing attributes.
3. Integrate bio.tools linter output to enrich diagnostics.
4. Produce visual and tabular reports and draft proposed revisions to the Tool Information Standards.

## Methodology

1. Data collection
	- Retrieve tool entries using the bio.tools API or curated subsets (for example: proteomics).
	- Store raw JSON records for reproducibility.

2. JSON schema validation
	- Validate metadata against the biotoolsSchema to detect structural issues.

3. Tier-based scoring
	- Map the Tool Information Standards to a set of scored attributes.
	- Compute an overall completeness score and assign a tier (1–5).

4. Linter integration
	- Run the bio.tools linter on selected entries.
	- Parse errors/warnings and merge diagnostics with completeness scores.

5. Reporting
	- Aggregate statistics on missing or malformed fields by tier and domain.
	- Generate visual summaries (radar charts, heatmaps) and CSV/JSON summary tables.

## Expected outcomes

- A reusable scoring and analysis pipeline for bio.tools metadata.
- An integrated dataset combining raw metadata, schema validation results, linter diagnostics, and completeness scores.
- Visual and tabular reports of metadata quality per tier and domain.
- A short proposal for revisions to the Tool Information Standards based on empirical findings.

## Prerequisites

- Python 3.8+ and basic familiarity with virtual environments
- Experience with JSON handling and data visualization (matplotlib, seaborn, plotly, etc.)

## Getting started (suggested)

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if a requirements file is added):

```powershell
pip install -r requirements.txt
```

3. Run the main pipeline (TBD — implement script entrypoints):

```powershell
python -m src.main --help
```

Note: This repository currently contains planning and scope material. Implementation files (scripts, modules, requirements) should be added to follow the project structure.

## Contribution & project structure

Recommended structure when implementing:

- src/ — Python package for pipeline code
- data/ — raw and processed JSON/CSV outputs
- notebooks/ — exploratory analysis and figures
- tests/ — unit and integration tests
- docs/ — additional documentation and the proposed revision drafts

If you'd like help scaffolding the codebase (project layout, starter scripts, tests, and a minimal working pipeline), open an issue or request a scaffold in this repository and I'll create it.

## Resources

- Tool Information Standards: https://bio-tools.github.io/Tool-Information-Standards/use_cases.html
- biotoolsSchema: https://github.com/bio-tools/biotoolsschema
- bio.tools linter: https://github.com/3top1a/biotools-linter/tree/main

## License

See the `LICENSE` file for licensing details.

---

Maintainers: bneiG1
