#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scoring.group_based_scorer import GroupBasedScorer
import yaml

def test_downloads_type_checking():
    """Test Downloads field group type checking with synthetic data"""
    
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    downloads_config = scorer.config['field_groups']['downloads_group']
    
    print("=== Testing Downloads Field Group Type Checking ===\n")
    
    # Test case 1: Tool with Binaries download
    tool_with_binaries = {
        "name": "Test Tool with Binaries",
        "download": [
            {"type": "Binaries", "url": "https://example.com/tool.zip"},
            {"type": "Source code", "url": "https://example.com/source.tar.gz"}
        ]
    }
    
    is_satisfied1, details1 = scorer.evaluate_field_group(tool_with_binaries, "downloads_group", downloads_config)
    print(f"Tool with Binaries download:")
    print(f"  Satisfied: {is_satisfied1}")
    print(f"  Details: {details1}")
    print()
    
    # Test case 2: Tool with Container file
    tool_with_container = {
        "name": "Test Tool with Container",
        "download": [
            {"type": "Container file", "url": "https://example.com/container.tar"},
            {"type": "Documentation", "url": "https://example.com/docs.pdf"}
        ]
    }
    
    is_satisfied2, details2 = scorer.evaluate_field_group(tool_with_container, "downloads_group", downloads_config)
    print(f"Tool with Container file:")
    print(f"  Satisfied: {is_satisfied2}")
    print(f"  Details: {details2}")
    print()
    
    # Test case 3: Tool with multiple supported downloads
    tool_with_multiple = {
        "name": "Test Tool with Multiple Downloads",
        "download": [
            {"type": "Binaries", "url": "https://example.com/tool.zip"},
            {"type": "CWL file", "url": "https://example.com/workflow.cwl"},
            {"type": "Tool wrapper (galaxy)", "url": "https://example.com/galaxy-wrapper.xml"},
            {"type": "VM image", "url": "https://example.com/vm.ova"}
        ]
    }
    
    is_satisfied3, details3 = scorer.evaluate_field_group(tool_with_multiple, "downloads_group", downloads_config)
    print(f"Tool with multiple supported downloads:")
    print(f"  Satisfied: {is_satisfied3}")
    print(f"  Details: {details3}")
    print()
    
    # Test case 4: Tool with no supported download types
    tool_with_unsupported = {
        "name": "Test Tool with Unsupported Downloads",
        "download": [
            {"type": "Source code", "url": "https://example.com/source.tar.gz"},
            {"type": "Test data", "url": "https://example.com/test-data.zip"}
        ]
    }
    
    is_satisfied4, details4 = scorer.evaluate_field_group(tool_with_unsupported, "downloads_group", downloads_config)
    print(f"Tool with unsupported download types:")
    print(f"  Satisfied: {is_satisfied4}")
    print(f"  Details: {details4}")
    print()
    
    # Test case 5: Tool with no downloads
    tool_no_downloads = {
        "name": "Test Tool with No Downloads",
        "download": []
    }
    
    is_satisfied5, details5 = scorer.evaluate_field_group(tool_no_downloads, "downloads_group", downloads_config)
    print(f"Tool with no downloads:")
    print(f"  Satisfied: {is_satisfied5}")
    print(f"  Details: {details5}")
    print()

def test_with_real_biotools_data():
    """Test with real bio.tools data from the attached JSON"""
    print("=== Testing with Real bio.tools Data ===\n")
    
    scorer = GroupBasedScorer('config/scoring_config.yaml')
    downloads_config = scorer.config['field_groups']['downloads_group']
    
    # Test tools from the JSON data
    tools_to_test = [
        {
            "name": "GENEX workflow", 
            "download": [],
            "link": [{"url": "https://github.com/NikolayOskolkov/MCWorkflow", "type": ["Repository"], "note": None}]
        },
        {
            "name": "FREEPII",
            "download": [],
            "link": []
        },
        {
            "name": "hictkpy",
            "download": [],
            "link": []
        }
    ]
    
    for tool in tools_to_test:
        is_satisfied, details = scorer.evaluate_field_group(tool, "downloads_group", downloads_config)
        print(f"Tool: {tool['name']}")
        print(f"  Satisfied: {is_satisfied}")
        print(f"  Details: {details}")
        print()

if __name__ == "__main__":
    test_downloads_type_checking()
    test_with_real_biotools_data()
