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
    
    # Clean up any existing processes first
    cleanup_existing_processes()
    
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

def cleanup_existing_processes():
    """Clean up any existing Streamlit processes."""
    print("🧹 Cleaning up existing processes...")
    
    try:
        # Import and run cleanup
        cleanup_script = Path(__file__).parent / "cleanup.py"
        if cleanup_script.exists():
            subprocess.run([sys.executable, str(cleanup_script)], 
                         timeout=10, capture_output=True)
            print("✓ Cleanup completed")
        else:
            print("⚠️ Cleanup script not found, skipping...")
    except subprocess.TimeoutExpired:
        print("⚠️ Cleanup timed out, continuing...")
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}, continuing...")

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
    
    # Get port from environment, with fallback logic for port conflicts
    port = os.environ.get('PORT', '8501')
    
    # Try alternative ports if the default is in use
    alternative_ports = [port, '8502', '8503', '8504', '8505']
    
    for attempt_port in alternative_ports:
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
            "--browser.gatherUsageStats=false",
            "--server.port", attempt_port,
            "--server.address", "0.0.0.0"
        ]
        
        print(f"🚀 Attempting to start Streamlit on port {attempt_port}...")
        print(f"Command: {' '.join(cmd)}")
        
        try:
            # Start the process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a moment to see if it starts successfully
            import time
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ Streamlit started successfully on port {attempt_port}")
                # Update PORT environment variable for any other processes
                os.environ['PORT'] = attempt_port
                
                # Wait for the process to complete
                try:
                    stdout, stderr = process.communicate()
                    if stdout:
                        print("STDOUT:", stdout)
                    if stderr:
                        print("STDERR:", stderr)
                except KeyboardInterrupt:
                    print("\n👋 Application stopped by user.")
                    process.terminate()
                    sys.exit(0)
                
                return
            else:
                # Process ended, check output
                stdout, stderr = process.communicate()
                if "Port" in stderr and "already in use" in stderr:
                    print(f"⚠️ Port {attempt_port} is in use, trying next port...")
                    continue
                else:
                    print(f"❌ Failed to start on port {attempt_port}")
                    if stdout:
                        print("STDOUT:", stdout)
                    if stderr:
                        print("STDERR:", stderr)
                    
        except Exception as e:
            print(f"❌ Error starting on port {attempt_port}: {e}")
            continue
    
    print("❌ Failed to start Streamlit on any available port")
    sys.exit(1)

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
