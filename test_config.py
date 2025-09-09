#!/usr/bin/env python3
"""
Test script to verify Streamlit configuration is valid.
"""

import streamlit as st
import sys
from pathlib import Path

def test_config():
    """Test that Streamlit configuration loads without errors."""
    print("Testing Streamlit configuration...")
    
    try:
        # This will load and parse the config.toml file
        import streamlit.config as config
        print("✅ Config loaded successfully")
        
        # Check some key settings
        print(f"✅ Headless mode: {config.get_option('server.headless')}")
        print(f"✅ CORS enabled: {config.get_option('server.enableCORS')}")
        print(f"✅ Server address: {config.get_option('server.address')}")
        print(f"✅ Server port: {config.get_option('server.port')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
