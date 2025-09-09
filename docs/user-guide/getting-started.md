# Getting Started

Welcome to the Bio.tools Annotation Quality Evaluation Platform! This guide will help you get the application up and running on your system.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: Version 3.8 or higher (3.9-3.11 recommended)
- **Memory**: 4GB RAM minimum (8GB recommended for large analyses)
- **Storage**: 2GB free space for application and cache
- **Network**: Internet connection for bio.tools API access

### Required Software

#### Python Installation

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and ensure "Add Python to PATH" is checked
3. Verify installation:
   ```powershell
   python --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### Git (Optional but Recommended)

**Windows:** Download from [git-scm.com](https://git-scm.com/)
**macOS:** `brew install git`
**Linux:** `sudo apt install git`

## Installation

### Method 1: Quick Installation (Recommended)

1. **Download the Application**
   ```powershell
   # Clone the repository
   git clone https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
   cd bio.tools-annotation-quality-evaluation
   ```

   *If you don't have Git, download the ZIP file from GitHub and extract it.*

2. **Create Virtual Environment**
   ```powershell
   # Create virtual environment
   python -m venv .venv
   
   # Activate it (Windows PowerShell)
   .\.venv\Scripts\Activate.ps1
   
   # Activate it (Windows Command Prompt)
   .venv\Scripts\activate.bat
   
   # Activate it (macOS/Linux)
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Launch the Application**
   ```powershell
   python app.py
   ```

### Method 2: Development Installation

For developers or users who want to contribute:

1. **Clone with Submodules**
   ```powershell
   git clone --recursive https://github.com/bneiG1/bio.tools-annotation-quality-evaluation.git
   cd bio.tools-annotation-quality-evaluation
   ```

2. **Setup Development Environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   
   # Install development dependencies (if available)
   pip install pytest black flake8 mypy
   ```

3. **Run Tests**
   ```powershell
   # Test API connectivity
   python test_api.py
   
   # Run unit tests (if available)
   pytest tests/
   ```

## First Launch

### Starting the Application

After installation, you can start the application using any of these methods:

#### Method 1: Direct Python Execution
```powershell
python app.py
```

#### Method 2: Streamlit Command
```powershell
streamlit run app.py
```

#### Method 3: Convenience Scripts
- **Windows**: Double-click `launch.bat` (if available)
- **PowerShell**: `.\launch.ps1` (if available)
- **Cross-platform**: `python run_app.py` (if available)

### Accessing the Interface

Once started, the application will:

1. **Display startup information** in the terminal
2. **Automatically open** your default web browser
3. **Navigate to** `http://localhost:8501`

If the browser doesn't open automatically, manually navigate to `http://localhost:8501`.

### Initial Setup Verification

1. **Check the Welcome Screen**: You should see the bio.tools quality analyzer interface
2. **Verify API Connectivity**: Try analyzing a simple tool like "blast"
3. **Check Features**: Ensure all analysis modes are accessible

## Configuration

### Optional Configuration

#### Environment Variables

You can customize the application behavior with environment variables:

```powershell
# Custom cache directory
$env:BIOTOOLS_CACHE_DIR = "C:\custom\cache\path"

# API rate limiting (requests per hour)
$env:BIOTOOLS_RATE_LIMIT = "100"

# Debug mode
$env:BIOTOOLS_DEBUG = "true"

# Custom port
$env:STREAMLIT_SERVER_PORT = "8502"
```

#### Streamlit Configuration

Create or edit `.streamlit/config.toml`:

```toml
[server]
port = 8501
enableCORS = false
maxUploadSize = 200

[browser]
serverAddress = "localhost"
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## Troubleshooting Installation

### Common Issues

#### Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Ensure Python is installed
2. Add Python to your system PATH
3. Try using `python3` instead of `python`

#### Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python path: `which python` (macOS/Linux) or `where python` (Windows)

#### Permission Errors (Windows)
**Error**: Execution policy errors in PowerShell

**Solution**:
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use alternative activation method
.venv\Scripts\activate.bat
```

#### Port Already in Use
**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
1. Change port: `streamlit run app.py --server.port 8502`
2. Find and stop conflicting process
3. Use different port in environment variable

#### Network/API Issues
**Error**: Connection timeouts or API errors

**Solution**:
1. Check internet connectivity
2. Verify bio.tools API status: <https://bio.tools/api/>
3. Check firewall/proxy settings
4. Try again later (rate limiting)

### Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Look in the `logs/` directory for error details
2. **Test API**: Run `python test_api.py` to verify connectivity
3. **GitHub Issues**: Search for similar issues or create a new one
4. **Documentation**: Check other sections of this documentation

## Next Steps

Now that you have the application running:

1. **[Interface Guide](interface-guide.md)**: Learn about the user interface
2. **[Analysis Types](analysis-types.md)**: Understand different analysis modes
3. **[Quality Metrics](quality-metrics.md)**: Learn about quality scoring
4. **[Examples](../examples/basic-usage.md)**: Try some example analyses

## Quick Test

To verify everything is working:

1. **Open the application** in your browser
2. **Go to Single Tool Analysis**
3. **Enter "blast"** as the tool ID
4. **Click "Analyze Tool"**
5. **Wait for results** to appear

If this works, your installation is successful!
