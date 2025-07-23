## bio.tools Annotation Quality Evaluation — Copilot Instructions

### Project Architecture & Workflow
- **Purpose:** Evaluate and improve metadata quality in the ELIXIR bio.tools registry using scoring, validation, and linter diagnostics.
- **Main pipeline:**
  - Data collection via `src/data_collection/api_client.py` (fetches tools by topic, collection, or query)
  - Parsing and normalization in `src/data_collection/data_parser.py`
  - Scoring and tier classification in `src/scoring/completeness_scorer.py` and `src/scoring/tier_classifier.py`
  - Statistical analysis in `src/analysis/statistics.py`
  - Visualization in `src/visualization/charts.py`
  - Orchestrated by scripts: `scripts/run_evaluation.py` and `scripts/run_evaluation_fixed.py`

### Key Conventions & Patterns
- **Tier-based scoring:** Tools are classified into 5 tiers based on metadata completeness. Scoring weights and rules are defined in `config/scoring_config.yaml` and implemented in `CompletenessScorer`.
- **Linter integration:** Linter results (errors/warnings) are merged with scoring for a composite quality assessment. See linter simulation and integration patterns in notebooks and scripts.
- **Schema validation:** Use JSON schema checks for compliance with biotoolsSchema. Validation helpers are in notebooks and scripts.
- **Config-driven:** Scoring and analysis are parameterized by YAML config files. Always respect config values for weights, required fields, etc.
- **Domain-specific analysis:** Support for collection/topic-based analysis (e.g., proteomics, genomics) is built-in. Use API client methods accordingly.

### Developer Workflows
- **Run full evaluation:**
  ```pwsh
  python scripts/run_evaluation_fixed.py --topic Proteomics --limit 100 --visualize
  ```
  - Use `--collection`, `--topic`, or `--query` to select tool sets.
  - Results and visualizations are saved in `data/processed/` and `data/visualizations/`.
- **Config updates:** Edit `config/scoring_config.yaml` to change scoring weights or required fields.
- **Debugging:** Use logging (set via `--log-level`) and inspect summary reports in output directory.
- **Notebook prototyping:** See `notebooks/bio_tools_quality_evaluation.ipynb` for stepwise analysis, validation, and visualization examples.

### Integration Points
- **External APIs:** All tool metadata is fetched from the [bio.tools API](https://bio.tools/api). API client supports retries and pagination.
- **Linter:** Integrate with [bio.tools linter](https://github.com/3top1a/biotools-linter) for diagnostics. Simulated in notebooks; real integration recommended for production.
- **Standards:** Scoring and validation are aligned with [Tool Information Standards](https://bio-tools.github.io/Tool-Information-Standards/use_cases.html) and [biotoolsSchema](https://github.com/bio-tools/biotoolsschema).

### Examples & Patterns
- **Scoring function:**
  ```python
  score = scorer.score_tool(tool_data)
  tier = classifier.classify_tool(score)
  ```
- **API usage:**
  ```python
  tools = api_client.get_tools_by_topic("Proteomics", limit=100)
  ```
- **Visualization:**
  ```python
  visualizer.create_tier_distribution_chart(scoring_results, save_path)
  ```

### Best Practices
- Always validate tool data before scoring.
- Merge linter results with scoring for final quality assessment.
- Use config files for all scoring and analysis parameters.
- Prefer batch operations for large-scale analysis.
- Document new analysis or scoring logic in notebooks and scripts.

---
For unclear or missing conventions, consult `README.md`, `notebooks/bio_tools_quality_evaluation.ipynb`, and config files. Ask for feedback if any section is incomplete or ambiguous.
