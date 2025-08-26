#!/usr/bin/env python3
"""
Generate comprehensive HTML dashboard for bio.tools annotation quality evaluation.
"""

import os
import sys
import argparse
import logging
import yaml
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from visualization.charts import QualityVisualizer


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def generate_sample_data(limit: int = 50) -> tuple:
    """
    Generate sample data for dashboard testing.
    
    Args:
        limit: Number of tools to analyze
        
    Returns:
        Tuple of (results, statistics, scoring_config)
    """
    print(f"🧪 Generating {limit} sample tools for testing...")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'scoring_config.yaml')
    config = load_config(config_path)
    
    # Generate sample results with realistic data
    results = []
    tool_names = [
        'blast', 'clustalw', 'muscle', 'hmmer', 'emboss', 'samtools', 'bowtie2', 'bwa',
        'fastqc', 'trimmomatic', 'gatk', 'picard', 'bedtools', 'vcftools', 'r-project',
        'bioconductor', 'galaxy', 'cytoscape', 'pymol', 'chimera', 'interpro', 'pfam',
        'uniprot', 'pdb', 'ensembl', 'ncbi', 'ebi', 'embl', 'genbank', 'refseq',
        'go', 'kegg', 'reactome', 'string', 'mint', 'biogrid', 'dip', 'intact',
        'pride', 'peptideatlas', 'human-protein-atlas', 'expressionatlas', 'arrayexpress',
        'geo', 'sra', 'ena', 'dbgap', 'tcga', 'cosmic', 'clinvar'
    ]
    
    collections = ['proteomics', 'genomics', 'structural_biology', 'bioinformatics', 'systems_biology']
    
    for i in range(limit):
        # Assign tier with some distribution (more tools in middle tiers)
        tier_weights = [0.1, 0.2, 0.4, 0.2, 0.1]  # Distribution across tiers
        tier = 1
        rand_val = (i / limit)
        cumulative = 0
        for t, weight in enumerate(tier_weights, 1):
            cumulative += weight
            if rand_val <= cumulative:
                tier = t
                break
        
        # Calculate score based on tier with some variation
        base_score = {1: 12, 2: 30, 3: 55, 4: 75, 5: 90}[tier]
        score = base_score + ((i * 7) % 15) - 7  # Add some variation
        score = max(0, min(100, score))  # Clamp to 0-100
        
        # Determine missing fields based on tier
        all_fields = ['publication', 'license', 'documentation', 'version', 'maturity', 
                     'operatingSystem', 'language', 'download', 'accessibility', 'cost']
        missing_count = max(0, 8 - tier - (i % 3))
        missing_fields = all_fields[:missing_count]
        
        # Select tool name
        tool_name = tool_names[i % len(tool_names)]
        if i >= len(tool_names):
            tool_name += f"_{(i // len(tool_names)) + 1}"
        
        result = {
            'biotoolsID': tool_name,
            'score': score,
            'tier': tier,
            'component_scores': {
                'basic_info': min(100, score * (0.9 + (i % 5) * 0.02)),
                'core_metadata': min(100, score * (0.8 + (i % 7) * 0.03)),
                'technical_info': min(100, score * (0.85 + (i % 6) * 0.02)),
                'accessibility': min(100, score * (0.7 + (i % 8) * 0.04)),
                'advanced_features': min(100, score * (0.6 + (i % 9) * 0.05)),
                'community': min(100, score * (0.8 + (i % 4) * 0.05))
            },
            'missing_fields': missing_fields,
            'raw_data': {
                'biotoolsID': tool_name,
                'name': tool_name.replace('_', ' ').title(),
                'description': f"Bioinformatics tool for {collections[i % len(collections)]} analysis"
            },
            'collection': collections[i % len(collections)]
        }
        results.append(result)
    
    # Generate statistics
    print("📊 Calculating statistics...")
    scores = [r['score'] for r in results]
    tiers = [r['tier'] for r in results]
    
    statistics = {
        'total_tools': len(results),
        'average_score': sum(scores) / len(scores) if scores else 0,
        'median_score': sorted(scores)[len(scores)//2] if scores else 0,
        'tier_distribution': {tier: tiers.count(tier) for tier in range(1, 6)},
        'tier_percentages': {tier: tiers.count(tier)/len(tiers)*100 for tier in range(1, 6)},
        'score_statistics': {
            'mean': sum(scores) / len(scores) if scores else 0,
            'median': sorted(scores)[len(scores)//2] if scores else 0,
            'std': (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5 if scores else 0,
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
            'quartiles': {
                'q1': sorted(scores)[len(scores)//4] if scores else 0,
                'q2': sorted(scores)[len(scores)//2] if scores else 0,
                'q3': sorted(scores)[3*len(scores)//4] if scores else 0
            }
        }
    }
    
    return results, statistics, config


def main():
    """Main function to generate the dashboard."""
    parser = argparse.ArgumentParser(description='Generate bio.tools quality dashboard')
    parser.add_argument('--limit', type=int, default=50, help='Number of tools to analyze')
    parser.add_argument('--output-dir', default='dashboard', help='Output directory for dashboard')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Generate sample data
        results, statistics, config = generate_sample_data(args.limit)
        
        print(f"✅ Generated {len(results)} sample tools successfully!")
        
        # Create visualizer and generate dashboard
        print("🎨 Generating HTML dashboard...")
        visualizer = QualityVisualizer()
        
        # Create output directory
        output_path = os.path.join(os.path.dirname(__file__), '..', args.output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # Generate complete dashboard
        visualizer.generate_complete_dashboard(
            results=results,
            statistics=statistics,
            scoring_config=config,
            output_dir=output_path
        )
        
        print("🎉 Dashboard generation complete!")
        print(f"📂 Dashboard saved to: {os.path.abspath(output_path)}")
        print(f"🌐 Open {os.path.join(output_path, 'index.html')} in your browser")
        
        # Print summary
        print("\n📋 Dashboard Summary:")
        print(f"   • Total tools analyzed: {len(results)}")
        print(f"   • Average quality score: {statistics.get('average_score', 0):.1f}")
        print(f"   • Tier distribution: {statistics.get('tier_distribution', {})}")
        print(f"   • Pages generated: Home, Tools Overview, Field Analysis, Statistics, Linter Reports")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        logging.error(f"Dashboard generation failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
