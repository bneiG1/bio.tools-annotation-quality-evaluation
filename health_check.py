#!/usr/bin/env python3
"""
Health check script for Bio.tools Live Quality Analyzer
"""

import sys
import os
import logging
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    print(f"✓ Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    return True

def check_modules():
    """Check if required modules are available."""
    print("\n📦 Checking modules...")
    
    # Check standard library modules
    standard_modules = ['json', 'sys', 'logging', 'time', 'pathlib', 'datetime', 'asyncio']
    for module in standard_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    # Check third-party modules
    third_party_modules = ['streamlit', 'pandas', 'plotly', 'requests']
    for module in third_party_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    # Check custom modules
    print("\n🔧 Checking custom modules...")
    sys.path.append(str(Path(__file__).parent / 'src'))
    
    custom_modules = [
        'src.collectors.biotools_api',
        'src.analyzers.quality_analyzer', 
        'src.utils.logger'
    ]
    
    for module in custom_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"⚠️ {module}: {e}")
    
    return True

def check_files():
    """Check if required files exist."""
    print("\n📁 Checking files...")
    
    app_dir = Path(__file__).parent
    required_files = [
        'app.py',
        'requirements.txt',
        'src/__init__.py',
        'src/collectors/__init__.py',
        'src/analyzers/__init__.py',
        'src/utils/__init__.py'
    ]
    
    for file_path in required_files:
        full_path = app_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            return False
    
    return True

def check_environment():
    """Check environment variables and settings."""
    print("\n🌍 Environment info...")
    print(f"✓ Current directory: {os.getcwd()}")
    print(f"✓ Script directory: {Path(__file__).parent}")
    print(f"✓ Python path: {sys.executable}")
    
    # Check if running in deployment environment
    deployment_indicators = [
        'STREAMLIT_SERVER_PORT',
        'PORT', 
        'DYNO',
        'RENDER',
        'RAILWAY_ENVIRONMENT'
    ]
    
    deployment_env = None
    for indicator in deployment_indicators:
        if indicator in os.environ:
            deployment_env = indicator
            print(f"✓ Deployment environment detected: {indicator}")
            break
    
    if not deployment_env:
        print("✓ Local environment detected")
    
    return True

def main():
    """Run all health checks."""
    print("🔬 Bio.tools Live Quality Analyzer - Health Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Modules", check_modules),
        ("Files", check_files),
        ("Environment", check_environment)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All health checks passed!")
        print("The app should be ready to run.")
    else:
        print("❌ Some health checks failed.")
        print("Please fix the issues above before deploying.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
