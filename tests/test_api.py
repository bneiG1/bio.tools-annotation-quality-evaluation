#!/usr/bin/env python3
"""
Test script to debug API issues.
"""

import requests
import json

def test_api():
    """Test the bio.tools API directly."""
    print("Testing bio.tools API...")
    
    # Test 1: Basic API connection
    url = "https://bio.tools/api/tool/?format=json"
    params = {'topic': 'Proteomics', 'page_size': 5, 'page': 1}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Response length: {len(response.text)}")
        print(f"First 200 chars: {repr(response.text[:200])}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ JSON parsing successful")
                if isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    if 'list' in data:
                        print(f"Number of tools: {len(data['list'])}")
                    if 'count' in data:
                        print(f"Total count: {data['count']}")
                else:
                    print(f"Response type: {type(data)}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON parsing failed: {e}")
                print("Raw response content:")
                print(response.text)
        else:
            print(f"✗ HTTP error: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Request failed: {e}")

    # Test 2: Try a simpler request
    print("\n" + "="*50)
    print("Testing simpler API request...")
    
    try:
        simple_url = "https://bio.tools/api/tool/?format=json"
        response = requests.get(simple_url, timeout=30)
        print(f"Status code: {response.status_code}")
        print(f"First 100 chars: {repr(response.text[:100])}")
    except Exception as e:
        print(f"✗ Simple request failed: {e}")

if __name__ == "__main__":
    test_api()
