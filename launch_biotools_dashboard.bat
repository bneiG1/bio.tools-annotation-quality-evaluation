@echo off
echo 🧬 Bio.tools Real Data Dashboard Launcher
echo =====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Streamlit not found. Installing...
    pip install streamlit plotly pandas numpy
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check data availability
if not exist "data\cache\tool*.json" (
    echo ❌ No bio.tools cache data found in data\cache\
    echo Please ensure bio.tools data is cached first
    pause
    exit /b 1
)

echo ✅ All requirements met
echo 🚀 Launching dashboard...
echo.

REM Launch the dashboard
python launch_biotools_dashboard.py

echo.
echo 👋 Dashboard session ended
pause
