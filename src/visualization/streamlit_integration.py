#!/usr/bin/env python3
"""
Streamlit Dashboard Integration for Bio.tools Quality Analysis
Integrates existing quality analysis pipeline with Streamlit web interface.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

def run_streamlit_dashboard(results: List[Dict[str, Any]], 
                          statistics: Dict[str, Any], 
                          config: Dict[str, Any]) -> None:
    """
    Launch Streamlit dashboard with provided data.
    
    Args:
        results: List of tool analysis results
        statistics: Overall statistics dictionary
        config: Configuration dictionary
    """
    
    # Save data to temporary file for Streamlit app to load
    data_file = Path("data/temp_dashboard_data.json")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    dashboard_data = {
        "tools": results,
        "statistics": statistics,
        "config": config,
        "timestamp": str(Path(__file__).stat().st_mtime)
    }
    
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    logging.info(f"Dashboard data saved to {data_file}")
    
    # Launch Streamlit
    streamlit_script = Path(__file__).parent.parent / "streamlit_app.py"
    
    try:
        logging.info("Starting Streamlit dashboard...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_script), 
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start Streamlit: {e}")
        raise
    except FileNotFoundError:
        logging.error("Streamlit not found. Please install with: pip install streamlit")
        raise


def create_dashboard_launcher() -> str:
    """
    Create a simple launcher script for the Streamlit dashboard.
    
    Returns:
        Path to the launcher script
    """
    launcher_content = '''#!/usr/bin/env python3
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
        print("\\n👋 Dashboard stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found!")
        print("Please install with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    launcher_path = Path(__file__).parent.parent / "launch_dashboard.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # Make executable on Unix systems
    try:
        launcher_path.chmod(0o755)
    except:
        pass  # Windows doesn't support chmod
    
    return str(launcher_path)
