# Examples and Use Cases

This document provides practical examples and common use cases for the bio.tools Annotation Quality Evaluation system.

## Table of Contents
1. [Basic Usage Examples](#basic-usage-examples)
2. [Advanced Workflows](#advanced-workflows)
3. [Domain-Specific Analysis](#domain-specific-analysis)
4. [Quality Improvement Workflows](#quality-improvement-workflows)
5. [Comparative Analysis](#comparative-analysis)
6. [Programmatic Usage](#programmatic-usage)
7. [Custom Configurations](#custom-configurations)

## Basic Usage Examples

### Quick Quality Assessment

Perform a quick assessment of tools in a specific domain:

```bash
# Evaluate 50 proteomics tools with visualizations
python scripts/run_evaluation.py --topic Proteomics --limit 50 --visualize

# Check results
ls data/processed/  # JSON results and summary reports
ls data/visualizations/  # Charts and plots
```

**Expected Output:**
- `evaluation_results_YYYYMMDD_HHMMSS.json`: Detailed scoring data
- `summary_report_YYYYMMDD_HHMMSS.txt`: Human-readable summary
- Visualization charts in PNG format

### Collection-Based Evaluation

Evaluate tools from a specific collection:

```bash
# Evaluate Galaxy tools
python scripts/run_evaluation.py --collection Galaxy --limit 100 --log-level INFO

# Generate dashboard for results
python scripts/generate_dashboard.py --data-dir data/processed
```

### Custom Search Query

Use free-text search to find and evaluate tools:

```bash
# Search for machine learning tools
python scripts/run_evaluation.py \
  --query "machine learning bioinformatics" \
  --limit 200 \
  --output-dir results/ml_tools \
  --visualize
```

## Advanced Workflows

### Multi-Topic Comparative Analysis

Compare quality across multiple scientific domains:

```bash
#!/bin/bash
# batch_evaluation.sh

# Define topics to analyze
topics=("Proteomics" "Genomics" "Transcriptomics" "Metabolomics")

# Evaluate each topic
for topic in "${topics[@]}"; do
    echo "Evaluating $topic tools..."
    python scripts/run_evaluation.py \
        --topic "$topic" \
        --limit 200 \
        --output-dir "results/$topic" \
        --visualize \
        --log-level INFO
done

# Generate comparative dashboard
python scripts/generate_dashboard.py \
    --data-dir results \
    --output-dir comparative_dashboard \
    --compare-mode
```

### Temporal Quality Analysis

Track quality improvements over time:

```bash
# Create baseline assessment
python scripts/run_evaluation.py \
    --topic Proteomics \
    --limit 500 \
    --output-dir baseline_2025_01 \
    --tag "baseline"

# Later assessment (after improvements)
python scripts/run_evaluation.py \
    --topic Proteomics \
    --limit 500 \
    --output-dir followup_2025_06 \
    --tag "followup"

# Compare results
python scripts/compare_assessments.py \
    baseline_2025_01 \
    followup_2025_06 \
    --output comparison_report
```

### Large-Scale Registry Analysis

Analyze entire registry or large subsets:

```bash
# Comprehensive analysis with progress tracking
python scripts/run_evaluation.py \
    --query "*" \
    --limit 0 \
    --output-dir registry_analysis \
    --batch-size 500 \
    --progress-bar \
    --resume-on-error
```

## Domain-Specific Analysis

### Proteomics Tools Analysis

Focused analysis for proteomics research community:

```bash
# Use proteomics-specific configuration
python scripts/run_evaluation.py \
    --config config/proteomics_profile.yaml \
    --topic Proteomics \
    --limit 1000 \
    --output-dir proteomics_analysis \
    --visualize \
    --detailed-reports
```

**Proteomics Configuration (config/proteomics_profile.yaml):**
```yaml
scoring:
  weights:
    basic_info: 10
    core_metadata: 35      # Emphasize publications and scientific context
    technical_info: 20     # Important for reproducibility  
    accessibility: 25      # Critical for wet-lab researchers
    advanced_features: 10
    community: 0
    
  field_weights:
    publication: 20        # Publications very important in proteomics
    function: 12          # Analytical functionality critical
    documentation: 15     # Usage instructions essential
    operatingSystem: 1    # Less important for web-based tools
    
  requirements:
    min_publications: 1   # Require at least one publication
    required_topics:
      - "Proteomics"
```

### Genomics Tools Analysis

Analysis tailored for genomics community:

```bash
python scripts/run_evaluation.py \
    --config config/genomics_profile.yaml \
    --collection "Genomics tools" \
    --limit 0 \
    --output-dir genomics_comprehensive
```

**Key differences in genomics profile:**
- Higher weight on data format compatibility
- Emphasis on scalability information
- Required genome assembly version compatibility

### Clinical Bioinformatics Analysis

Analysis for clinical applications:

```bash
python scripts/run_evaluation.py \
    --config config/clinical_profile.yaml \
    --query "clinical genomics diagnostic" \
    --limit 100 \
    --output-dir clinical_analysis
```

**Clinical Configuration Features:**
- Strong emphasis on licensing and regulatory compliance
- Required accessibility and privacy information
- Higher weight on validation and benchmarking data

## Quality Improvement Workflows

### Identify Improvement Targets

Find tools most in need of quality improvements:

```python
#!/usr/bin/env python3
"""Find tools with highest improvement potential."""

import json
import pandas as pd
from pathlib import Path

def analyze_improvement_potential(results_file):
    """Analyze which tools need most improvement."""
    with open(results_file) as f:
        results = json.load(f)
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(results)
    
    # Identify improvement targets
    tier_1_tools = df[df['tier'] == 1]  # Lowest tier
    high_potential = df[
        (df['total_score'] > 30) & 
        (df['tier'] < 4)
    ]  # Good content, poor presentation
    
    missing_pubs = df[
        df['missing_fields'].apply(lambda x: 'publication' in x)
    ]
    
    print(f"Tier 1 tools needing basic improvements: {len(tier_1_tools)}")
    print(f"Tools with high improvement potential: {len(high_potential)}")
    print(f"Tools missing publications: {len(missing_pubs)}")
    
    return {
        'tier_1': tier_1_tools,
        'high_potential': high_potential,
        'missing_publications': missing_pubs
    }

# Usage
results = analyze_improvement_potential('data/processed/evaluation_results_latest.json')
```

### Track Improvement Progress

Monitor improvements in specific tools:

```python
#!/usr/bin/env python3
"""Track improvement progress for specific tools."""

import json
from datetime import datetime

def track_tool_improvements(tool_ids, baseline_file, current_file):
    """Track improvements for specific tools."""
    # Load baseline and current results
    with open(baseline_file) as f:
        baseline = {r['biotoolsID']: r for r in json.load(f)}
    
    with open(current_file) as f:
        current = {r['biotoolsID']: r for r in json.load(f)}
    
    # Analyze improvements
    improvements = []
    for tool_id in tool_ids:
        if tool_id in baseline and tool_id in current:
            base_score = baseline[tool_id]['total_score']
            curr_score = current[tool_id]['total_score']
            improvement = curr_score - base_score
            
            improvements.append({
                'tool_id': tool_id,
                'baseline_score': base_score,
                'current_score': curr_score,
                'improvement': improvement,
                'tier_change': current[tool_id]['tier'] - baseline[tool_id]['tier']
            })
    
    # Sort by improvement
    improvements.sort(key=lambda x: x['improvement'], reverse=True)
    
    print("Tool Improvement Summary")
    print("=" * 50)
    for item in improvements[:10]:  # Top 10 improvements
        print(f"{item['tool_id']}: {item['improvement']:+.1f} points "
              f"(Tier {baseline[item['tool_id']]['tier']} → {current[item['tool_id']]['tier']})")
    
    return improvements

# Usage
target_tools = ['tool1', 'tool2', 'tool3']  # Replace with actual tool IDs
improvements = track_tool_improvements(
    target_tools,
    'baseline/evaluation_results.json',
    'current/evaluation_results.json'
)
```

### Generate Improvement Recommendations

Create actionable improvement recommendations:

```python
#!/usr/bin/env python3
"""Generate improvement recommendations for tools."""

def generate_recommendations(tool_data, score_details):
    """Generate specific recommendations for a tool."""
    recommendations = []
    missing_fields = score_details.get('missing_fields', [])
    
    # Basic information improvements
    if 'description' in missing_fields:
        recommendations.append({
            'priority': 'High',
            'category': 'Basic Information',
            'action': 'Add a clear, informative description (minimum 50 characters)',
            'impact': '6 points'
        })
    
    # Publication improvements
    if 'publication' in missing_fields:
        recommendations.append({
            'priority': 'High', 
            'category': 'Core Metadata',
            'action': 'Add primary publication or preprint',
            'impact': '10 points'
        })
    
    # Technical improvements
    if 'license' in missing_fields:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Technical Information',
            'action': 'Specify software license (e.g., MIT, GPL-3.0)',
            'impact': '4 points'
        })
    
    # Documentation improvements  
    if 'documentation' in missing_fields:
        recommendations.append({
            'priority': 'High',
            'category': 'Accessibility',
            'action': 'Add user manual or tutorial links',
            'impact': '8 points'
        })
    
    return recommendations

# Generate recommendations report
def create_recommendations_report(results_file, output_file):
    """Create comprehensive recommendations report."""
    with open(results_file) as f:
        results = json.load(f)
    
    all_recommendations = {}
    for tool in results:
        if tool['tier'] < 4:  # Focus on tools that can be improved
            recs = generate_recommendations(tool, tool)
            all_recommendations[tool['biotoolsID']] = {
                'tool_name': tool.get('name', 'Unknown'),
                'current_score': tool['total_score'],
                'current_tier': tool['tier'],
                'recommendations': recs,
                'potential_score': tool['total_score'] + sum(
                    int(r['impact'].split()[0]) for r in recs
                )
            }
    
    # Save recommendations
    with open(output_file, 'w') as f:
        json.dump(all_recommendations, f, indent=2)
    
    print(f"Recommendations saved to {output_file}")
    return all_recommendations
```

## Comparative Analysis

### Cross-Collection Comparison

Compare quality across different tool collections:

```python
#!/usr/bin/env python3
"""Compare quality across collections."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def compare_collections(collection_results):
    """Compare quality metrics across collections."""
    comparison_data = []
    
    for collection, results in collection_results.items():
        scores = [r['total_score'] for r in results]
        tiers = [r['tier'] for r in results]
        
        comparison_data.append({
            'collection': collection,
            'mean_score': np.mean(scores),
            'median_score': np.median(scores),
            'tier_4_5_percentage': len([t for t in tiers if t >= 4]) / len(tiers) * 100,
            'total_tools': len(results)
        })
    
    df = pd.DataFrame(comparison_data)
    
    # Create comparison visualizations
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Mean scores
    df.plot(x='collection', y='mean_score', kind='bar', ax=ax1)
    ax1.set_title('Mean Quality Score by Collection')
    ax1.set_ylabel('Mean Score')
    
    # High-quality tool percentage
    df.plot(x='collection', y='tier_4_5_percentage', kind='bar', ax=ax2)
    ax2.set_title('Percentage of High-Quality Tools (Tier 4-5)')
    ax2.set_ylabel('Percentage (%)')
    
    # Tool count
    df.plot(x='collection', y='total_tools', kind='bar', ax=ax3)
    ax3.set_title('Total Tools by Collection')
    ax3.set_ylabel('Number of Tools')
    
    # Score distribution comparison
    for collection, results in collection_results.items():
        scores = [r['total_score'] for r in results]
        ax4.hist(scores, alpha=0.6, label=collection, bins=20)
    ax4.set_title('Score Distribution by Collection')
    ax4.set_xlabel('Quality Score')
    ax4.set_ylabel('Number of Tools')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('collection_comparison.png', dpi=300)
    plt.show()
    
    return df

# Usage example
collection_data = {
    'Galaxy': json.load(open('galaxy_results.json')),
    'BioConda': json.load(open('bioconda_results.json')),
    'ELIXIR Tools': json.load(open('elixir_results.json'))
}

comparison_df = compare_collections(collection_data)
```

### Before/After Analysis

Analyze improvements after quality enhancement initiatives:

```bash
# Before improvement initiative
python scripts/run_evaluation.py \
    --topic Proteomics \
    --limit 1000 \
    --output-dir before_improvements \
    --tag "before"

# After improvement initiative (6 months later)
python scripts/run_evaluation.py \
    --topic Proteomics \
    --limit 1000 \
    --output-dir after_improvements \
    --tag "after"

# Generate comparison report
python scripts/improvement_analysis.py \
    --before before_improvements/evaluation_results.json \
    --after after_improvements/evaluation_results.json \
    --output improvement_report.html
```

## Programmatic Usage

### Custom Analysis Pipeline

Build custom analysis using the API:

```python
#!/usr/bin/env python3
"""Custom analysis pipeline example."""

import json
from pathlib import Path
from src.data_collection.api_client import BioToolsAPIClient
from src.scoring.completeness_scorer import CompletenessScorer
from src.analysis.statistics import QualityStatistics
from src.visualization.charts import QualityVisualizer

class CustomAnalysisPipeline:
    """Custom analysis pipeline for specific research questions."""
    
    def __init__(self, config_path=None):
        self.api_client = BioToolsAPIClient()
        self.scorer = CompletenessScorer(config_path)
        self.stats = QualityStatistics()
        self.visualizer = QualityVisualizer()
        
    def analyze_tool_evolution(self, tool_ids, output_dir):
        """Analyze how specific tools have evolved over time."""
        results = {}
        
        for tool_id in tool_ids:
            try:
                # Get current tool data
                tool_data = self.api_client.get_tool_details(tool_id)
                
                # Score the tool
                score = self.scorer.score_tool(tool_data)
                detailed = self.scorer.get_detailed_score(tool_data)
                
                results[tool_id] = {
                    'name': tool_data.get('name', 'Unknown'),
                    'current_score': score,
                    'detailed_scores': detailed,
                    'last_updated': tool_data.get('lastUpdate')
                }
                
            except Exception as e:
                print(f"Error analyzing {tool_id}: {e}")
                continue
        
        # Save results
        output_path = Path(output_dir) / 'tool_evolution_analysis.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def compare_scientific_domains(self, domains, sample_size=100):
        """Compare quality across scientific domains."""
        domain_results = {}
        
        for domain in domains:
            print(f"Analyzing {domain}...")
            
            # Fetch tools
            tools = self.api_client.get_tools_by_topic(domain, limit=sample_size)
            
            # Score tools
            results = []
            for tool in tools:
                try:
                    score = self.scorer.score_tool(tool)
                    detailed = self.scorer.get_detailed_score(tool)
                    
                    results.append({
                        'biotoolsID': tool.get('biotoolsID'),
                        'name': tool.get('name'),
                        'total_score': score,
                        'category_scores': detailed['category_scores'],
                        'tier': self.scorer.classify_tier(score)
                    })
                except:
                    continue
            
            domain_results[domain] = results
        
        # Generate comparative analysis
        comparison = self.stats.compare_collections(domain_results)
        
        # Create visualizations
        self.visualizer.create_comparison_chart(
            comparison, 
            save_path='domain_comparison.png'
        )
        
        return domain_results, comparison

# Usage
pipeline = CustomAnalysisPipeline('config/research_config.yaml')

# Analyze specific tools
target_tools = ['blast', 'clustalw', 'muscle']  # Example tool IDs
evolution_results = pipeline.analyze_tool_evolution(
    target_tools, 
    'analysis_output'
)

# Compare domains
domains = ['Proteomics', 'Genomics', 'Transcriptomics']
domain_results, comparison = pipeline.compare_scientific_domains(domains)
```

### Automated Quality Monitoring

Set up automated monitoring for quality changes:

```python
#!/usr/bin/env python3
"""Automated quality monitoring system."""

import schedule
import time
from datetime import datetime
from pathlib import Path

class QualityMonitor:
    """Monitor quality changes over time."""
    
    def __init__(self, monitored_collections):
        self.collections = monitored_collections
        self.api_client = BioToolsAPIClient()
        self.scorer = CompletenessScorer()
        
    def daily_quality_check(self):
        """Perform daily quality assessment."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for collection in self.collections:
            print(f"Monitoring {collection}...")
            
            # Sample tools from collection
            tools = self.api_client.get_tools_by_collection(
                collection, 
                limit=50
            )
            
            # Score tools
            scores = []
            for tool in tools:
                try:
                    score = self.scorer.score_tool(tool)
                    scores.append(score)
                except:
                    continue
            
            # Save monitoring data
            monitoring_data = {
                'timestamp': timestamp,
                'collection': collection,
                'sample_size': len(scores),
                'mean_score': sum(scores) / len(scores) if scores else 0,
                'scores': scores
            }
            
            output_file = f"monitoring/{collection}_{timestamp}.json"
            Path(output_file).parent.mkdir(exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(monitoring_data, f, indent=2)
            
            print(f"Saved monitoring data to {output_file}")
    
    def start_monitoring(self):
        """Start automated monitoring."""
        # Schedule daily checks
        schedule.every().day.at("09:00").do(self.daily_quality_check)
        
        print("Starting quality monitoring...")
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour

# Usage
monitor = QualityMonitor(['Galaxy', 'BioConda', 'ELIXIR Tools'])
monitor.start_monitoring()
```

## Custom Configurations

### Research-Focused Configuration

Configuration optimized for research evaluation:

```yaml
# config/research_config.yaml
scoring:
  weights:
    basic_info: 10
    core_metadata: 40        # Strong emphasis on scientific content
    technical_info: 25       # Reproducibility important
    accessibility: 20        # Access to methods important
    advanced_features: 5
    community: 0            # Less relevant for research
  
  field_weights:
    # Scientific credibility
    publication: 25         # Publications critical
    function: 15           # Scientific function important
    topic: 12              # Scientific classification
    
    # Technical reproducibility
    version: 8             # Version tracking important
    license: 6             # Open licensing preferred
    repository: 10         # Source access valuable
    documentation: 12      # Methods documentation crucial
    
    # Less important for research
    cost: 1               # Usually not primary concern
    maturity: 2           # Early tools can be valuable
    
  tiers:
    # More stringent requirements for research
    tier_1: [0, 10]       # Very basic
    tier_2: [11, 30]      # Minimal research standard
    tier_3: [31, 55]      # Acceptable research tool
    tier_4: [56, 80]      # Good research tool
    tier_5: [81, 100]     # Excellent research tool
```

### Production Deployment Configuration

Configuration for production quality assessment:

```yaml
# config/production_config.yaml
scoring:
  weights:
    basic_info: 15
    core_metadata: 20
    technical_info: 25       # Technical stability important
    accessibility: 25        # User experience critical
    advanced_features: 10
    community: 5
  
  field_weights:
    # Production readiness
    maturity: 8             # Stability important
    version: 6              # Version tracking required
    license: 8              # Legal clarity essential
    documentation: 15       # User guidance critical
    operatingSystem: 5      # Platform support important
    
    # Support and maintenance
    contact: 6              # Support availability
    homepage: 4             # Professional presence
    
    # Less critical for production
    publication: 5          # Nice to have, not essential

system:
  api:
    max_retries: 5          # More robust for production
    rate_limit_delay: 0.5   # Respectful API usage
    cache_responses: true   # Improve performance
    
  logging:
    level: "INFO"           # Production logging level
    file_logging: true
    console_logging: false  # File only in production
    
  output:
    create_subdirs: true    # Organized output
    backup_results: true    # Keep result history
```

### Educational Configuration

Configuration for educational/training purposes:

```yaml
# config/educational_config.yaml
scoring:
  weights:
    basic_info: 20          # Clear identification important
    core_metadata: 20       # Scientific context
    technical_info: 20      # Learning technical details
    accessibility: 30       # Easy access for students
    advanced_features: 5
    community: 5
  
  field_weights:
    # Educational value
    description: 10         # Clear explanations
    documentation: 20       # Learning materials
    homepage: 6             # Easy access
    function: 12            # Understanding what it does
    
    # Learning accessibility
    cost: 8                # Free tools preferred
    operatingSystem: 4      # Multi-platform access
    
  # Lenient tiers for educational context
  tiers:
    tier_1: [0, 20]        # Basic educational tool
    tier_2: [21, 45]       # Useful for learning
    tier_3: [46, 70]       # Good educational resource
    tier_4: [71, 90]       # Excellent teaching tool
    tier_5: [91, 100]      # Outstanding educational resource
```

These examples demonstrate the flexibility and power of the bio.tools annotation quality evaluation system across various use cases and requirements.
