# Bio.tools Quality Dashboard Launcher
# PowerShell script for launching the Streamlit dashboard

Write-Host "🔬 Bio.tools Quality Dashboard" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Blue
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Streamlit is installed
try {
    python -c "import streamlit" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Streamlit is available" -ForegroundColor Green
    } else {
        throw "Streamlit not found"
    }
} catch {
    Write-Host "❌ Streamlit is not installed" -ForegroundColor Red
    Write-Host "Installing Streamlit and dependencies..." -ForegroundColor Yellow
    
    pip install streamlit streamlit-aggrid plotly pandas matplotlib seaborn
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
}

# Check for data directory
if (!(Test-Path "data")) {
    Write-Host "📁 Creating data directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
}

# Show menu
Write-Host ""
Write-Host "🚀 Launch Options:" -ForegroundColor Cyan
Write-Host "1. Demo with sample data (recommended for first time)"
Write-Host "2. Load from existing file"
Write-Host "3. Generate custom sample data"
Write-Host "4. Launch empty dashboard"
Write-Host ""

$choice = Read-Host "Choose an option (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🔄 Launching demo with 100 sample tools..." -ForegroundColor Yellow
        python dashboard.py --demo
    }
    "2" {
        $filePath = Read-Host "Enter path to JSON file"
        if (Test-Path $filePath) {
            Write-Host "📂 Loading data from file..." -ForegroundColor Yellow
            python dashboard.py --file $filePath
        } else {
            Write-Host "❌ File not found: $filePath" -ForegroundColor Red
        }
    }
    "3" {
        $count = Read-Host "Enter number of sample tools (default: 100)"
        if ($count -eq "") { $count = "100" }
        Write-Host "🔄 Generating $count sample tools..." -ForegroundColor Yellow
        python dashboard.py --sample --count $count
    }
    "4" {
        Write-Host "🌐 Launching empty dashboard..." -ForegroundColor Yellow
        streamlit run streamlit_app.py --server.port 8501 --browser.gatherUsageStats false
    }
    default {
        Write-Host "❌ Invalid choice. Launching demo..." -ForegroundColor Red
        python dashboard.py --demo
    }
}

Write-Host ""
Write-Host "👋 Dashboard session ended" -ForegroundColor Blue
