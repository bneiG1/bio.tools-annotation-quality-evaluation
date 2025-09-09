@echo off
echo Bio.tools Quality Dashboard
echo ===========================
echo.
echo Starting Streamlit web interface...
echo.

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" > nul 2>&1
if errorlevel 1 (
    echo Error: Streamlit is not installed
    echo Installing Streamlit...
    pip install streamlit streamlit-aggrid plotly
    if errorlevel 1 (
        echo Failed to install Streamlit
        pause
        exit /b 1
    )
)

REM Launch the dashboard
echo Opening dashboard in your default browser...
python -m streamlit run streamlit_app.py --server.port 8501 --browser.gatherUsageStats false

pause
