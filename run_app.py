#!/usr/bin/env python3
"""
Simple launcher for Bio.tools Live Quality Analyzer
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit application."""
    
    # Get the directory where this script is located
    app_dir = Path(__file__).parent
    app_file = app_dir / "app.py"
    
    if not app_file.exists():
        print(f"Error: {app_file} not found!")
        sys.exit(1)
    
    # Launch Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_file)]
    
    print("🚀 Starting Bio.tools Live Quality Analyzer...")
    print(f"Command: {' '.join(cmd)}")
    print("The application will open in your web browser.")
    print("Press Ctrl+C to stop the server.")
    
    try:
        # Use shell=True and redirect output to NUL on Windows
        if sys.platform == "win32":
            subprocess.run(" ".join(cmd) + " > NUL", shell=True, check=True)
        else:
            subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
