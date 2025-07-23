#!/usr/bin/env python3
"""
Updated test script to debug API issues with proper JSON format.
"""

import requests
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_collection.api_client import BioToolsAPIClient

def test_api_direct():
    """Test the bio.tools API directly with proper JSON format."""
    print("Testing bio.tools API with JSON format...")
    
    # Test 1: Basic API connection with format parameter
    url = "https://bio.tools/api/tool/?format=json"
    params = {'topic': 'Proteomics', 'page_size': 5, 'page': 1, 'format': 'json'}
    
    try:
        headers = {'Accept': 'application/json'}
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Response length: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ JSON parsing successful")
                if isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    if 'list' in data:
                        print(f"Number of tools: {len(data['list'])}")
                        if data['list']:
                            first_tool = data['list'][0]
                            print(f"First tool name: {first_tool.get('name', 'N/A')}")
                            print(f"First tool description: {first_tool.get('description', 'N/A')[:100]}...")
                    if 'count' in data:
                        print(f"Total count: {data['count']}")
                else:
                    print(f"Response type: {type(data)}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON parsing failed: {e}")
                print("Raw response content (first 500 chars):")
                print(response.text[:500])
        else:
            print(f"✗ HTTP error: {response.status_code}")
            print("Response content:")
            print(response.text[:500])
            
    except Exception as e:
        print(f"✗ Request failed: {e}")

def test_api_client():
    """Test using our API client."""
    print("\n" + "="*60)
    print("Testing with API client...")
    
    try:
        client = BioToolsAPIClient()
        
        # Test getting tools by topic
        print("Fetching tools by topic 'Proteomics'...")
        tools = client.get_tools_by_topic('Proteomics', limit=5)
        
        if tools:
            print(f"✓ Successfully retrieved {len(tools)} tools")
            for i, tool in enumerate(tools[:3]):
                print(f"  {i+1}. {tool.get('name', 'N/A')} - {tool.get('biotoolsID', 'N/A')}")
        else:
            print("✗ No tools retrieved")
            
        # Test getting a specific tool
        if tools:
            print(f"\nTesting individual tool retrieval...")
            first_tool_id = tools[0].get('biotoolsID')
            if first_tool_id:
                tool_detail = client.get_tool_by_id(first_tool_id)
                if tool_detail:
                    print(f"✓ Successfully retrieved details for {tool_detail.get('name', 'N/A')}")
                else:
                    print(f"✗ Failed to retrieve details for {first_tool_id}")
                    
    except Exception as e:
        print(f"✗ API client test failed: {e}")

if __name__ == "__main__":
    test_api_direct()
    test_api_client()
