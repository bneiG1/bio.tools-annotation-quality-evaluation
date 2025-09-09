# HTML Template System for Bio.tools Quality Reports

## Overview

The bio.tools quality analysis system now uses a template-based approach for generating HTML reports, separating presentation (HTML/CSS) from logic (Python code).

## Architecture

### Template File Location
```
src/reporters/templates/tool_report_template.html
```

### Python Integration
The template is loaded and processed by the `QualityReporter` class in `src/reporters/visualizer.py`.

## Template System Features

### 1. **Separation of Concerns**
- **HTML/CSS**: Stored in separate template file for easy editing
- **Data Processing**: Handled in Python code
- **Template Variables**: Dynamic content injected via string formatting

### 2. **Template Variables**
The template uses Python string formatting with named placeholders:

```html
<h1>{tool_name}</h1>
<div>Score: {overall_score}/100</div>
<span class="grade-badge">{quality_grade}</span>
```

### 3. **CSS Escaping**
CSS curly braces are escaped by doubling them to avoid conflicts with template variables:

```css
.header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}}
```

## Template Variables Reference

### Basic Information
- `{tool_name}` - Tool display name
- `{tool_id}` - Bio.tools ID
- `{analysis_date}` - When the analysis was performed

### Quality Metrics
- `{overall_score}` - Overall quality score (0-100)
- `{quality_grade}` - Quality grade (A, B, C, D, F)
- `{grade_color}` - CSS color code for the grade badge
- `{standards_tier}` - Standards compliance tier
- `{completeness_score}` - Completeness score

### Field Completeness
- `{field_completeness_percent}` - Overall completeness percentage (e.g., "70%")
- `{field_completeness_width}` - Width for progress bar (e.g., 70)
- `{recommended_fields_percent}` - Recommended fields percentage
- `{recommended_fields_width}` - Width for recommended fields progress bar

### Content Quality Status
- `{functions_status}` - "✅ Present" or "❌ Missing"
- `{functions_status_class}` - CSS class: "status-yes" or "status-no"
- `{documentation_status}` - Documentation availability
- `{documentation_status_class}` - CSS class for documentation
- `{publications_status}` - Publications availability
- `{publications_status_class}` - CSS class for publications
- `{contacts_status}` - Contacts availability
- `{contacts_status_class}` - CSS class for contacts

### Quality Scores
- `{publication_quality}` - Publication quality percentage
- `{url_health}` - URL health percentage
- `{edam_consistency}` - EDAM consistency percentage

### Schema Validation
- `{schema_status}` - "✅ Valid" or "❌ Invalid"
- `{schema_status_class}` - CSS class for schema status
- `{schema_errors}` - Number of schema errors
- `{schema_warnings}` - Number of schema warnings

### Issues and Recommendations
- `{lint_issues_count}` - Total number of lint issues
- `{lint_issues_content}` - HTML content for lint issues list
- `{recommendations_content}` - HTML content for recommendations section

### Summary
- `{summary}` - Executive summary text

## Template Processing Flow

### 1. **Template Loading**
```python
template_path = Path(__file__).parent / "templates" / "tool_report_template.html"
with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()
```

### 2. **Variable Preparation**
```python
template_vars = {
    'tool_name': report.tool_name,
    'tool_id': report.tool_id,
    'overall_score': report.metrics.overall_score,
    # ... all other variables
}
```

### 3. **Template Rendering**
```python
html_content = template_content.format(**template_vars)
```

### 4. **Fallback Handling**
If the template file is not found, the system falls back to a simple inline HTML generator.

## Customization Guide

### Modifying the Template

1. **Edit the HTML structure** in `tool_report_template.html`
2. **Modify CSS styles** by editing the `<style>` section
3. **Add new template variables** by updating both:
   - The template file (add `{new_variable}`)
   - The Python code (add to `template_vars` dictionary)

### Adding New Sections

1. **Add HTML structure** for the new section:
```html
<div class="section">
    <h2>New Section</h2>
    <div>{new_section_content}</div>
</div>
```

2. **Update Python code** to provide the content:
```python
template_vars['new_section_content'] = generate_new_section_content(report)
```

### Styling Guidelines

- **Responsive design**: Uses CSS Grid for metrics cards
- **Color scheme**: Consistent with Bootstrap-like color palette
- **Grade colors**: Different colors for quality grades (A=green, F=gray)
- **Status indicators**: Green for positive, red for negative status

## Helper Methods

### `_generate_lint_issues_html(lint_issues)`
Converts lint issues list to HTML with appropriate CSS classes:
- `issue-critical` - Critical issues (red)
- `issue-error` - Error issues (red)
- `issue-warning` - Warning issues (orange)
- `issue-info` - Info issues (blue)

### `_generate_recommendations_html(report)`
Generates HTML for recommendations with:
- Priority fixes (high importance)
- General recommendations (medium importance)

### `_generate_fallback_html_report(report)`
Simple HTML generator used when template file is unavailable.

## File Structure

```
src/reporters/
├── visualizer.py                    # Main reporter class
└── templates/
    └── tool_report_template.html    # HTML template
```

## Benefits of Template System

### 1. **Maintainability**
- Easy to modify presentation without touching Python code
- Clear separation between logic and presentation
- Template changes don't require Python knowledge

### 2. **Consistency**
- All HTML reports use the same template
- Consistent styling and structure across all tools
- Centralized style management

### 3. **Flexibility**
- Easy to create different templates for different report types
- Support for multiple themes or layouts
- Template variables can be extended without breaking existing reports

### 4. **Development Efficiency**
- Frontend developers can work on templates independently
- Faster iteration on visual design
- Better collaboration between backend and frontend developers

## Testing Template Changes

After modifying the template, test with:

```bash
# Generate a single tool report
python main.py per-tool-analysis -t blast --format html

# Check the output file
# Location: data/reports/per_tool_analysis/blast_TIMESTAMP.html
```

## Future Enhancements

### Potential Improvements
1. **Template Engine**: Consider using Jinja2 for more advanced templating features
2. **Multiple Templates**: Support for different report layouts (detailed, summary, etc.)
3. **Dynamic Theming**: CSS variables for easy color scheme changes
4. **Internationalization**: Support for multiple languages in templates
5. **Component System**: Reusable template components for different sections

### Template Variables to Add
- Tool categories and topics
- Version information
- License details
- Operating system compatibility
- Language support
- Integration details

This template system provides a solid foundation for generating professional, maintainable HTML reports while keeping the codebase clean and organized.
