#!/usr/bin/env python3
"""
Simple launcher for Bio.tools Quality Dashboard
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit dashboard."""
    print("🔬 Bio.tools Quality Dashboard")
    print("================================")
    print("Starting Streamlit web interface...")
    
    streamlit_app = Path(__file__).parent / "streamlit_app.py"
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(streamlit_app),
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found!")
        print("Please install with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
