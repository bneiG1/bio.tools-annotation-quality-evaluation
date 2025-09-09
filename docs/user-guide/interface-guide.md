# User Interface Guide

This guide provides a comprehensive overview of the Bio.tools Annotation Quality Evaluation Platform's user interface, helping you navigate and use all features effectively.

## Overview

The application features a clean, modern web interface built with Streamlit. The design follows bio.tools styling conventions to provide a familiar experience for users of the ELIXIR ecosystem.

## Main Interface Layout

### Header Section

The header displays:

- **Application title**: "Bio.tools Live Quality Analyzer"
- **System status indicators**: Module availability and health checks
- **Navigation elements**: Quick access to different analysis modes

### Stats Dashboard

The main landing page shows:

- **Registry statistics**: Total tools available (~30,538)
- **Quality insights**: Average quality metrics across the registry
- **Recent analysis**: Quick access to previously analyzed tools

### Analysis Interface Cards

The interface is organized into distinct analysis mode cards:

1. **Single Tool Analysis Card**
2. **Search & Analyze Tools Card**
3. **Random Tools Analysis Card**
4. **Collection Analysis Card**

## Analysis Modes

### 1. Single Tool Analysis

**Purpose**: Deep-dive analysis of a specific bio.tools entry

**Interface Elements**:

- **Tool ID Input**: Text field for entering bio.tools identifier
- **Cache Indicator**: Shows if tool data is cached locally
- **Analyze Button**: Triggers the analysis process
- **Progress Indicator**: Real-time analysis status

**Usage**:

1. Enter a valid bio.tools ID (e.g., "blast", "clustalw", "galaxy")
2. Click "🔍 Analyze Tool"
3. Wait for analysis to complete
4. Review detailed results

### 2. Search & Analyze Tools

**Purpose**: Search bio.tools registry and analyze multiple results

**Interface Elements**:

- **Search Query Field**: Free-text search input
- **Search Scope Checkboxes**: Control what fields to search
  - Name (always enabled)
  - Description
  - Topics
  - Operations
  - Data Types
  - Formats
  - Publications
  - Collections
- **Result Limit Slider**: Control number of results (1-50)
- **Sort Options**: Order results by relevance, date, or score
- **Search Button**: Execute search and analysis

**Usage**:

1. Enter search terms related to tools you're interested in
2. Select which fields to include in the search
3. Adjust result limit and sorting preferences
4. Click "🔍 Search & Analyze"
5. Review results for multiple tools

### 3. Random Tools Analysis

**Purpose**: Discover and analyze random tools from the registry

**Interface Elements**:

- **Number Input**: Specify how many random tools to analyze (1-20)
- **Random Analyze Button**: Trigger random selection and analysis

**Usage**:

1. Choose the number of tools to analyze
2. Click "🎲 Analyze Random Tools"
3. Explore diverse tools and their quality metrics

### 4. Collection Analysis

**Purpose**: Analyze tools from specific domains or collections

**Interface Elements**:

- **Collection Dropdown**: Select predefined collections
  - COVID-19 Tools
  - Recent Tools
  - Popular Tools
  - Custom Collection
- **Custom Tool IDs**: Text area for custom tool lists (when Custom Collection is selected)
- **Analyze Collection Button**: Start collection analysis

**Usage**:

1. Select a collection type from the dropdown
2. For custom collections, enter tool IDs (one per line)
3. Click "📊 Analyze Collection"
4. Review aggregated results and individual tool metrics

## Results Display

### Single Tool Results

When analyzing a single tool, results are displayed in several sections:

#### Quality Overview Cards

Four prominent cards show key metrics:

- **Quality Grade**: A-F grade with color coding
- **Standards Tier**: ELIXIR compliance level (1-5)
- **Schema Validation**: Pass/fail status
- **Completeness Score**: Percentage of fields completed

#### Detailed Metrics Section

Comprehensive breakdown including:

- **Overall Score**: Numerical score out of 100
- **Schema Errors/Warnings**: Count of validation issues
- **Lint Issues**: Breakdown by severity level
- **Field Completeness**: Detailed field coverage analysis

#### Radar Chart Visualization

Interactive Plotly radar chart showing:

- Multiple quality dimensions
- Comparative visualization
- Hover tooltips with detailed information
- Download options for the chart

#### Recommendations Panel

Structured improvement suggestions:

- **Critical Issues**: Must-fix problems
- **Warnings**: Recommended improvements
- **Tier Advancement**: Steps to reach higher standards tiers
- **Best Practices**: General quality improvement tips

#### Raw Data Export

Options to download:

- **JSON**: Complete analysis results with metadata
- **CSV**: Tabular summary for spreadsheet analysis

### Bulk Analysis Results

When analyzing multiple tools (search, random, or collection):

#### Summary Statistics

Overview cards showing:

- **Total Tools Analyzed**: Count of processed tools
- **Average Quality Score**: Mean score across all tools
- **High Quality Tools**: Count of A/B grade tools
- **Schema Compliance**: Percentage of valid tools

#### Distribution Visualizations

- **Quality Grade Distribution**: Bar chart of grade frequencies
- **Score Histogram**: Distribution of numerical scores
- **Tier Compliance**: Standards tier breakdown

#### Detailed Results Table

Sortable, filterable table with:

- **Tool Information**: ID, name, description
- **Quality Metrics**: Grade, score, tier, completeness
- **Issues Summary**: Count of errors and warnings
- **Quick Actions**: Links to detailed analysis

### Analysis History

The interface maintains a history of recent analyses:

- **Recent Tools**: Quick access to previously analyzed tools
- **Click to Reload**: Instantly view cached results
- **Visual Indicators**: Shows analysis timestamp and quality grade

## Interactive Features

### Real-time Analysis

- **Progress Indicators**: Live updates during analysis
- **Streaming Results**: Results appear as analysis completes
- **Error Handling**: Graceful handling of API failures

### Data Caching

- **Intelligent Caching**: Stores API responses locally
- **Cache Indicators**: Shows when cached data is available
- **Fresh Data Options**: Force refresh for latest information

### Export and Sharing

- **Multiple Formats**: JSON and CSV export options
- **Complete Data**: Full analysis results including metadata
- **Reproducible**: Include analysis parameters and timestamps

## Navigation Tips

### Efficient Workflow

1. **Start with Single Tool Analysis** for familiar tools
2. **Use Search** to discover relevant tools in your domain
3. **Try Random Analysis** to explore the registry diversity
4. **Use Collections** for systematic domain analysis

### Best Practices

- **Check Cache Status**: Avoid unnecessary API calls
- **Use Appropriate Batch Sizes**: Start small for testing
- **Export Important Results**: Save analysis data for later reference
- **Monitor Rate Limits**: Be aware of API usage constraints

### Keyboard Shortcuts

- **Enter**: Submit forms and trigger analysis
- **Escape**: Close modals and cancel operations
- **Tab**: Navigate between interface elements

## Responsive Design

The interface adapts to different screen sizes:

- **Desktop**: Full-width layout with multi-column displays
- **Tablet**: Responsive column layouts
- **Mobile**: Single-column stack with touch-friendly controls

## Accessibility Features

- **Semantic HTML**: Proper heading structure and labels
- **Color Contrast**: High contrast for readability
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and descriptions

## Customization Options

### Streamlit Configuration

Customize appearance through `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Environment Variables

Control behavior with environment variables:

- `BIOTOOLS_CACHE_DIR`: Custom cache location
- `BIOTOOLS_RATE_LIMIT`: API rate limiting
- `BIOTOOLS_DEBUG`: Enable debug mode

## Troubleshooting Interface Issues

### Common Problems

**Slow Loading**:

- Check internet connection
- Verify bio.tools API status
- Clear browser cache

**Missing Features**:

- Ensure all Python modules are installed
- Check console for import errors
- Restart the application

**Display Issues**:

- Refresh the browser page
- Try a different browser
- Check browser console for JavaScript errors

**Export Problems**:

- Verify browser download settings
- Check available disk space
- Try different export formats

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).

## Next Steps

- **[Analysis Types](analysis-types.md)**: Learn about different analysis modes in detail
- **[Quality Metrics](quality-metrics.md)**: Understand the scoring system
- **[Export & Reports](export-reports.md)**: Work with analysis results
