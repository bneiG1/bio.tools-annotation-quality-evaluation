#!/usr/bin/env python3
"""
Deployment startup script for Bio.tools Live Quality Analyzer
Handles deployment-specific configuration and error handling
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_deployment_environment():
    """Setup environment for deployment."""
    print("🚀 Setting up deployment environment...")
    
    # Set deployment-specific environment variables
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Use PORT environment variable if available (common in many deployment platforms)
    port = os.environ.get('PORT', '8501')
    os.environ['STREAMLIT_SERVER_PORT'] = port
    
    # Bind to all interfaces in deployment
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    
    print(f"✓ Configured for port {port}")
    print(f"✓ Headless mode enabled")
    print(f"✓ CORS/XSRF disabled for deployment")

def check_deployment_readiness():
    """Check if the app is ready for deployment."""
    print("🔍 Checking deployment readiness...")
    
    app_dir = Path(__file__).parent
    app_file = app_dir / "app.py"
    
    if not app_file.exists():
        print(f"❌ {app_file} not found!")
        return False
    
    # Run health check
    health_check_file = app_dir / "health_check.py" 
    if health_check_file.exists():
        print("Running health check...")
        try:
            result = subprocess.run([sys.executable, str(health_check_file)], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"❌ Health check failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            else:
                print("✅ Health check passed")
        except subprocess.TimeoutExpired:
            print("⚠️ Health check timed out, continuing anyway...")
    
    return True

def start_streamlit():
    """Start the Streamlit application."""
    app_file = Path(__file__).parent / "app.py"
    
    # Build command
    cmd = [
        sys.executable, 
        "-m", 
        "streamlit", 
        "run", 
        str(app_file),
        "--server.headless=true",
        "--server.enableCORS=false", 
        "--server.enableXsrfProtection=false",
        "--browser.gatherUsageStats=false"
    ]
    
    # Add port if specified
    port = os.environ.get('PORT', '8501')
    cmd.extend(["--server.port", port])
    cmd.extend(["--server.address", "0.0.0.0"])
    
    print(f"🚀 Starting Streamlit on port {port}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Start the process
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Streamlit failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user.")
        sys.exit(0)

def main():
    """Main deployment entry point."""
    print("🔬 Bio.tools Live Quality Analyzer - Deployment Startup")
    print("=" * 60)
    
    try:
        # Setup deployment environment
        setup_deployment_environment()
        
        # Check readiness
        if not check_deployment_readiness():
            print("❌ Deployment readiness check failed")
            sys.exit(1)
        
        # Start the application
        start_streamlit()
        
    except Exception as e:
        print(f"❌ Deployment startup failed: {e}")
        import traceback
        print(f"📋 Traceback:\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
