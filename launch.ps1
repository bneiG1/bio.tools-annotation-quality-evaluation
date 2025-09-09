# Bio.tools Live Quality Analyzer Launcher
# PowerShell script to launch the Streamlit application

Write-Host "🚀 Starting Bio.tools Live Quality Analyzer..." -ForegroundColor Green
Write-Host ""
Write-Host "The application will open in your web browser." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

try {
    python run_app.py
}
catch {
    Write-Host "Error starting application: $_" -ForegroundColor Red
    Write-Host "Make sure Python and required dependencies are installed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
