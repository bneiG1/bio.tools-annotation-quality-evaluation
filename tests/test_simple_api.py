#!/usr/bin/env python3
"""
Simple API test with timeout.
"""

import requests
import json
import sys

def test_simple():
    """Test API with shorter timeout."""
    print("Testing bio.tools API with short timeout...")
    
    try:
        # Try to get the API documentation or basic info
        url = "https://bio.tools/api/tool/?format=json"
        print(f"Requesting: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content (first 500 chars): {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("JSON parse successful")
                print(f"Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
            except:
                print("JSON parse failed - not valid JSON")
        
    except requests.Timeout:
        print("Request timed out")
    except requests.ConnectionError:
        print("Connection error")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple()
