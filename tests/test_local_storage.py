#!/usr/bin/env python3
"""
Test script for local data storage functionality.
"""

import sys
import tempfile
import shutil
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_collection.local_data_manager import LocalDataManager

def test_local_data_manager():
    """Test the LocalDataManager functionality."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing with temporary directory: {temp_dir}")
        
        # Initialize the manager
        manager = LocalDataManager(temp_dir, create_dirs=True)
        
        # Test data
        test_tool = {
            "biotoolsID": "test_tool",
            "name": "Test Tool",
            "description": "A test tool for validation",
            "function": [{"operation": [{"term": "Data handling"}]}],
            "topic": [{"term": "Data management"}]
        }
        
        test_tool2 = {
            "biotoolsID": "test_tool_2",
            "name": "Another Test Tool", 
            "description": "Second test tool",
            "function": [{"operation": [{"term": "Analysis"}]}],
            "topic": [{"term": "Bioinformatics"}]
        }
        
        print("\n1. Testing tool saving...")
        
        # Test saving a single tool
        result = manager.save_tool(test_tool, "all")
        assert result, "Failed to save tool"
        print("✓ Single tool saved successfully")
        
        # Test saving multiple tools
        tools = [test_tool, test_tool2]
        result = manager.save_tools(tools, "collections")
        assert result['saved'] == 2, f"Expected 2 saved, got {result['saved']}"
        print("✓ Multiple tools saved successfully")
        
        print("\n2. Testing tool loading...")
        
        # Test loading a single tool
        loaded_tool = manager.load_tool("test_tool", "all")
        assert loaded_tool is not None, "Failed to load tool"
        assert loaded_tool['name'] == "Test Tool", "Tool data corrupted"
        print("✓ Single tool loaded successfully")
        
        # Test loading multiple tools
        loaded_tools = manager.load_tools(["test_tool", "test_tool_2"], "collections")
        assert len(loaded_tools) == 2, f"Expected 2 tools, got {len(loaded_tools)}"
        print("✓ Multiple tools loaded successfully")
        
        # Test loading all tools from a subdirectory
        all_tools = manager.load_all_tools("collections")
        assert len(all_tools) == 2, f"Expected 2 tools in collections, got {len(all_tools)}"
        print("✓ All tools loaded from subdirectory")
        
        print("\n3. Testing utility functions...")
        
        # Test listing available tools
        tool_list = manager.list_available_tools("all")
        assert "test_tool" in tool_list, "Tool not in list"
        print("✓ Tool listing works")
        
        # Test tool existence check
        exists = manager.tool_exists("test_tool", "all")
        assert exists, "Tool should exist"
        
        not_exists = manager.tool_exists("nonexistent_tool", "all")
        assert not not_exists, "Non-existent tool should not exist"
        print("✓ Tool existence checks work")
        
        # Test storage info
        info = manager.get_storage_info()
        assert info['subdirectories']['all']['tool_count'] == 1, "Wrong tool count in 'all'"
        assert info['subdirectories']['collections']['tool_count'] == 2, "Wrong tool count in 'collections'"
        print("✓ Storage info works")
        
        print("\n4. Testing data cleanup...")
        
        # Test clearing tools
        deleted_count = manager.clear_tools("collections")
        assert deleted_count == 2, f"Expected to delete 2 tools, deleted {deleted_count}"
        
        # Verify tools are gone
        remaining_tools = manager.list_available_tools("collections")
        assert len(remaining_tools) == 0, f"Expected 0 remaining tools, found {len(remaining_tools)}"
        print("✓ Tool clearing works")
        
        print("\n✅ All tests passed!")
        
        return True

def test_filename_sanitization():
    """Test filename sanitization."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = LocalDataManager(temp_dir)
        
        # Test problematic tool IDs
        problematic_ids = [
            "tool/with/slashes",
            "tool:with:colons",
            "tool<with>brackets",
            'tool"with"quotes',
            "tool|with|pipes"
        ]
        
        for tool_id in problematic_ids:
            test_tool = {
                "biotoolsID": tool_id,
                "name": "Test Tool",
                "description": "Test"
            }
            
            # This should not raise an exception
            result = manager.save_tool(test_tool, "all")
            assert result, f"Failed to save tool with ID: {tool_id}"
            
            # Should be able to load it back
            loaded = manager.load_tool(tool_id, "all") 
            assert loaded is not None, f"Failed to load tool with ID: {tool_id}"
            assert loaded['biotoolsID'] == tool_id, "Tool ID corrupted"
        
        print("✅ Filename sanitization tests passed!")
        
        return True

if __name__ == '__main__':
    try:
        print("Testing Local Data Manager...")
        test_local_data_manager()
        test_filename_sanitization()
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
