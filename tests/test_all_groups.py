#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scoring.group_based_scorer import GroupBasedScorer

def test_all_field_groups_comprehensive():
    """Test all field groups including Downloads with real-world examples"""
    
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    
    print("=== Comprehensive Field Group Testing ===\n")
    
    # Test tool with all field group types
    comprehensive_tool = {
        "name": "Comprehensive Tool",
        "description": "A tool demonstrating all field groups",
        "homepage": "https://example.com/tool",
        "biotoolsID": "comprehensive-tool",
        "toolType": ["Command-line tool"],
        "topic": [{"uri": "http://edamontology.org/topic_0091", "term": "Bioinformatics"}],
        
        # Documentation group - API documentation type
        "documentation": [
            {"type": "API documentation", "url": "https://example.com/api-docs"}
        ],
        
        # Code availability group - Repository
        "link": [
            {"type": "Repository", "url": "https://github.com/example/tool"}
        ],
        
        # Downloads group - Binaries and CWL file
        "download": [
            {"type": "Binaries", "url": "https://example.com/tool.zip"},
            {"type": "CWL file", "url": "https://example.com/workflow.cwl"}
        ],
        
        # Accessibility group - Cost information
        "cost": "Free of charge",
        
        # Support group - Primary contact
        "credit": [
            {"typeRole": "Primary contact", "name": "John Doe", "email": "john@example.com"}
        ]
    }
    
    field_groups = ['documentation_group', 'code_availability_group', 'downloads_group', 'accessibility_group', 'support_group']
    
    for group_name in field_groups:
        group_config = scorer.config['field_groups'][group_name]
        is_satisfied, details = scorer.evaluate_field_group(comprehensive_tool, group_name, group_config)
        
        print(f"Field Group: {group_name}")
        print(f"  Satisfied: {is_satisfied}")
        print(f"  Type matches: {details.get('type_matches', [])}")
        print(f"  Description: {details['description']}")
        print()

    print("=== Testing Downloads Field Group with Various Types ===\n")
    
    # Test different download types
    download_tests = [
        {
            "name": "Tool with Biological data",
            "download": [{"type": "Biological data", "url": "https://example.com/data.zip"}]
        },
        {
            "name": "Tool with Binary package", 
            "download": [{"type": "Binary package", "url": "https://example.com/package.deb"}]
        },
        {
            "name": "Tool with Ontology",
            "download": [{"type": "Ontology", "url": "https://example.com/ontology.owl"}]
        },
        {
            "name": "Tool with VM image",
            "download": [{"type": "VM image", "url": "https://example.com/vm.ova"}]
        },
        {
            "name": "Tool with Tool wrapper (taverna)",
            "download": [{"type": "Tool wrapper (taverna)", "url": "https://example.com/taverna-wrapper.xml"}]
        },
        {
            "name": "Tool with Tool wrapper (other)",
            "download": [{"type": "Tool wrapper (other)", "url": "https://example.com/custom-wrapper.json"}]
        }
    ]
    
    downloads_config = scorer.config['field_groups']['downloads_group']
    
    for test_tool in download_tests:
        is_satisfied, details = scorer.evaluate_field_group(test_tool, "downloads_group", downloads_config)
        print(f"{test_tool['name']}: {'✅ Satisfied' if is_satisfied else '❌ Not satisfied'}")
        if is_satisfied:
            print(f"  Found types: {details['type_matches']}")
        print()

if __name__ == "__main__":
    test_all_field_groups_comprehensive()
