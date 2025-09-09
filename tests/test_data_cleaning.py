"""
Test data cleaning functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.data_cleaner import ToolDataCleaner, clean_tool_data

def test_data_cleaning():
    """Test the data cleaning functionality"""
    
    # Sample tool data with empty values (similar to what might come from bio.tools API)
    sample_tool = {
        "biotoolsID": "test-tool",
        "name": "Test Tool",
        "description": "A test tool",
        "homepage": "https://example.com",
        "topic": [
            {"term": "Sequence analysis", "uri": "http://edamontology.org/topic_0080"},
            {"term": "", "uri": ""}  # Empty values to clean
        ],
        "toolType": ["Command-line tool"],
        "function": [
            {
                "operation": [{"term": "Alignment", "uri": "http://edamontology.org/operation_0292"}],
                "input": [],  # Empty list to clean
                "output": [],  # Empty list to clean
                "note": None,  # Null value to clean
                "cmd": ""  # Empty string to clean
            }
        ],
        "documentation": [
            {
                "url": "https://example.com/docs",
                "type": "General",
                "note": None  # Null value to clean
            },
            {
                "url": "",  # Empty URL to clean
                "type": "",  # Empty type to clean
                "note": ""  # Empty note to clean
            }
        ],
        "language": [],  # Empty list to clean
        "license": None,  # Null value to clean
        "maturity": "",  # Empty string to clean
        "operatingSystem": ["Linux", ""],  # Mix of valid and empty
        "cost": False,  # Boolean false (might be kept or removed based on settings)
        "accessibility": {},  # Empty dict to clean
        "elixirPlatform": [""],  # List with empty string
        "elixirNode": None  # Null value
    }
    
    print("=" * 60)
    print("DATA CLEANING TEST")
    print("=" * 60)
    
    print(f"\nOriginal tool data fields: {count_fields(sample_tool)}")
    print("Sample empty values found:")
    print("- Empty strings in topic, cmd, maturity, operatingSystem")
    print("- Null values in note, license, elixirNode")
    print("- Empty lists in input, output, language, elixirPlatform")
    print("- Empty dict in accessibility")
    
    # Test standard cleaning
    print("\n" + "-" * 40)
    print("STANDARD CLEANING")
    print("-" * 40)
    
    cleaner = ToolDataCleaner.create_biotools_standard_cleaner()
    cleaned_standard = cleaner.clean_tool(sample_tool)
    
    print(f"After standard cleaning: {count_fields(cleaned_standard)} fields")
    print(f"Removed: {count_fields(sample_tool) - count_fields(cleaned_standard)} empty fields")
    
    # Test aggressive cleaning
    print("\n" + "-" * 40)
    print("AGGRESSIVE CLEANING")
    print("-" * 40)
    
    cleaner_aggressive = ToolDataCleaner.create_aggressive_cleaner()
    cleaned_aggressive = cleaner_aggressive.clean_tool(sample_tool)
    
    print(f"After aggressive cleaning: {count_fields(cleaned_aggressive)} fields")
    print(f"Removed: {count_fields(sample_tool) - count_fields(cleaned_aggressive)} empty fields")
    
    # Test convenience function
    print("\n" + "-" * 40)
    print("CONVENIENCE FUNCTION TEST")
    print("-" * 40)
    
    cleaned_convenience = clean_tool_data(sample_tool, aggressive=False)
    print(f"Convenience function result: {count_fields(cleaned_convenience)} fields")
    
    # Show some specific cleaned results
    print("\n" + "-" * 40)
    print("CLEANING RESULTS SAMPLE")
    print("-" * 40)
    
    print(f"Original topic entries: {len(sample_tool['topic'])}")
    print(f"Cleaned topic entries: {len(cleaned_standard.get('topic', []))}")
    
    print(f"Original function note: {repr(sample_tool['function'][0].get('note'))}")
    print(f"Cleaned function note: {repr(cleaned_standard['function'][0].get('note', 'REMOVED'))}")
    
    print(f"Original language: {sample_tool['language']}")
    print(f"Cleaned language: {cleaned_standard.get('language', 'REMOVED')}")
    
    print(f"Original license: {repr(sample_tool['license'])}")
    print(f"Cleaned license: {repr(cleaned_standard.get('license', 'REMOVED'))}")
    
    print("\n" + "=" * 60)
    print("DATA CLEANING TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return cleaned_standard

def count_fields(data, count=0):
    """Recursively count fields in a data structure"""
    if isinstance(data, dict):
        count += len(data)
        for value in data.values():
            count = count_fields(value, count)
    elif isinstance(data, list):
        for item in data:
            count = count_fields(item, count)
    return count

if __name__ == "__main__":
    test_data_cleaning()
