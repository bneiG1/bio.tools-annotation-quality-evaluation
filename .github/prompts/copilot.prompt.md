---
mode: ask
---
## bio.tools Annotation Quality Evaluation — Copilot Prompt Guidance

When defining a task for AI agents in this project, include:

- **Clear objective:** State the metadata quality evaluation or improvement goal (e.g., "Score all proteomics tools and visualize tier distribution").
- **Scope:** Specify the collection, topic, or query (e.g., `--topic Proteomics`, `--collection Genomics`).
- **Constraints:** Reference config files, standards, or required fields (e.g., "Use weights from config/scoring_config.yaml", "Validate against biotoolsSchema").
- **Success criteria:** Describe expected outputs (e.g., "Save results to data/processed/", "Generate radar chart in data/visualizations/").
- **Integration:** Note if linter diagnostics or external API data should be included.
- **Preferred workflow:** Indicate if batch processing, notebook prototyping, or script orchestration is required.

### Example Prompt
"Score all tools in the Proteomics topic using the latest scoring config, merge linter results, and generate tier distribution and completeness heatmap visualizations. Save outputs in the processed and visualizations folders."

---
For more details, see `.github/copilot-instructions.md`, `README.md`, and `notebooks/bio_tools_quality_evaluation.ipynb`.