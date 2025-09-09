#!/usr/bin/env python3
"""
Launch Bio.tools Real Data Dashboard
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit dashboard with real bio.tools data."""
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    dashboard_script = script_dir / "biotools_dashboard.py"
    
    if not dashboard_script.exists():
        print(f"❌ Dashboard script not found: {dashboard_script}")
        return 1
    
    # Check data directory
    data_dir = script_dir / "data" / "cache"
    if not data_dir.exists():
        print(f"❌ Data cache directory not found: {data_dir}")
        return 1
    
    # Count available data files
    tool_files = list(data_dir.glob("tool*.json"))
    print(f"🔍 Found {len(tool_files)} tool files in cache")
    
    if len(tool_files) == 0:
        print("⚠️  No tool data files found in cache")
        return 1
    
    print("🚀 Launching Bio.tools Dashboard with real data...")
    print(f"📁 Data source: {data_dir}")
    print(f"📊 Tools available: {len(tool_files)}")
    print("\n" + "="*50)
    
    # Launch Streamlit
    try:
        cmd = [
            sys.executable, 
            "-m", "streamlit", 
            "run", 
            str(dashboard_script),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd, cwd=script_dir)
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
