# Troubleshooting Guide

This comprehensive troubleshooting guide helps you resolve common issues with the Bio.tools Annotation Quality Evaluation Platform. Issues are organized by category with step-by-step solutions.

## Installation and Setup Issues

### Python and Environment Problems

#### Issue: Python Not Found or Wrong Version

**Symptoms**:
- `'python' is not recognized as an internal or external command`
- `Python version 3.7 or lower detected`
- `ModuleNotFoundError` during installation

**Solutions**:

1. **Verify Python Installation**:
   ```powershell
   python --version
   # Should show Python 3.8+ 
   ```

2. **Windows PATH Issues**:
   ```powershell
   # Add Python to PATH (run as Administrator)
   $pythonPath = (Get-Command python).Source
   $pathFolder = Split-Path $pythonPath
   [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$pathFolder", "Machine")
   ```

3. **Use Python3 Explicitly**:
   ```powershell
   python3 --version
   python3 -m pip install -r requirements.txt
   ```

4. **Fresh Python Installation**:
   - Download latest Python from [python.org](https://www.python.org/)
   - Ensure "Add Python to PATH" is checked during installation
   - Restart command prompt/PowerShell

#### Issue: Virtual Environment Problems

**Symptoms**:
- Virtual environment activation fails
- Packages installed globally instead of in venv
- Permission errors during venv creation

**Solutions**:

1. **PowerShell Execution Policy** (Windows):
   ```powershell
   # Check current policy
   Get-ExecutionPolicy
   
   # Allow script execution (run as Administrator)
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **Alternative Activation Methods**:
   ```powershell
   # If .ps1 fails, try .bat
   .venv\Scripts\activate.bat
   
   # Or use Python directly
   python -m venv .venv --prompt biotools-qa
   ```

3. **Clean Environment Recreation**:
   ```powershell
   # Remove existing environment
   Remove-Item -Recurse -Force .venv
   
   # Create fresh environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

#### Issue: Dependency Installation Failures

**Symptoms**:
- `pip install` fails with compilation errors
- Missing system dependencies
- Version conflicts

**Solutions**:

1. **Update pip and setuptools**:
   ```powershell
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install Dependencies Individually**:
   ```powershell
   # Core dependencies first
   pip install streamlit pandas plotly requests jsonschema
   
   # Additional dependencies
   pip install numpy pyyaml boltons
   
   # Development dependencies (optional)
   pip install pytest black flake8
   ```

3. **Use Conda Alternative**:
   ```powershell
   conda create -n biotools-qa python=3.9
   conda activate biotools-qa
   conda install streamlit pandas plotly requests jsonschema
   pip install boltons  # If not available in conda
   ```

4. **Platform-Specific Issues**:
   - **Windows**: Install Microsoft C++ Build Tools
   - **macOS**: Install Xcode command line tools: `xcode-select --install`
   - **Linux**: Install development packages: `sudo apt-get install python3-dev build-essential`

## Application Startup Issues

### Module Import Errors

#### Issue: Core Modules Not Found

**Symptoms**:
- `ModuleNotFoundError: No module named 'src'`
- `Some modules not available` warning
- Application starts but features are disabled

**Solutions**:

1. **Verify Project Structure**:
   ```powershell
   # Check if src directory exists
   Get-ChildItem -Path . -Directory -Name "src"
   
   # Verify module files
   Get-ChildItem -Path "src" -Recurse -Name "*.py"
   ```

2. **Set Python Path**:
   ```powershell
   # Add src to Python path
   $env:PYTHONPATH = "$PWD\src;$env:PYTHONPATH"
   python app.py
   ```

3. **Install in Development Mode**:
   ```powershell
   # Install package in editable mode
   pip install -e .
   ```

4. **Check Working Directory**:
   ```powershell
   # Ensure you're in the project root
   Get-Location
   # Should show: .../bio.tools-annotation-quality-evaluation
   
   # Verify app.py exists
   Test-Path app.py
   ```

#### Issue: Streamlit Import Problems

**Symptoms**:
- `ModuleNotFoundError: No module named 'streamlit'`
- Streamlit command not found
- Version compatibility issues

**Solutions**:

1. **Verify Streamlit Installation**:
   ```powershell
   pip show streamlit
   streamlit --version
   ```

2. **Reinstall Streamlit**:
   ```powershell
   pip uninstall streamlit
   pip install streamlit>=1.49.0
   ```

3. **Use Python Module Syntax**:
   ```powershell
   python -m streamlit run app.py
   ```

### Port and Network Issues

#### Issue: Port Already in Use

**Symptoms**:
- `OSError: [Errno 48] Address already in use`
- `Port 8501 is already in use`
- Application fails to start

**Solutions**:

1. **Use Different Port**:
   ```powershell
   streamlit run app.py --server.port 8502
   ```

2. **Find and Kill Process**:
   ```powershell
   # Windows: Find process using port 8501
   netstat -ano | findstr :8501
   
   # Kill process (replace PID with actual process ID)
   taskkill /PID <process_id> /F
   
   # macOS/Linux
   lsof -ti:8501 | xargs kill -9
   ```

3. **Configure Default Port**:
   Edit `.streamlit/config.toml`:
   ```toml
   [server]
   port = 8502
   ```

#### Issue: Network/Firewall Problems

**Symptoms**:
- Browser can't connect to localhost:8501
- "This site can't be reached" error
- Application starts but no browser access

**Solutions**:

1. **Check Firewall Settings**:
   - Windows: Allow Python/Streamlit through Windows Firewall
   - macOS: System Preferences > Security & Privacy > Firewall
   - Linux: Configure iptables or ufw

2. **Try Different Address**:
   ```powershell
   streamlit run app.py --server.address 127.0.0.1
   ```

3. **Manual Browser Navigation**:
   - Open browser manually
   - Navigate to `http://localhost:8501`
   - Try `http://127.0.0.1:8501`

## API and Data Issues

### Bio.tools API Connection Problems

#### Issue: API Timeouts and Connection Errors

**Symptoms**:
- `requests.exceptions.ConnectionError`
- `HTTPSConnectionPool: Max retries exceeded`
- Analysis fails with network errors

**Solutions**:

1. **Check Internet Connection**:
   ```powershell
   # Test basic connectivity
   Test-NetConnection bio.tools -Port 443
   
   # Test API endpoint
   Invoke-WebRequest -Uri "https://bio.tools/api/" -Method GET
   ```

2. **Configure Proxy Settings** (if behind corporate firewall):
   ```powershell
   # Set proxy environment variables
   $env:HTTP_PROXY = "http://proxy.company.com:8080"
   $env:HTTPS_PROXY = "http://proxy.company.com:8080"
   ```

3. **Verify bio.tools API Status**:
   - Check [bio.tools status page](https://bio.tools/)
   - Visit [API endpoint](https://bio.tools/api/) directly
   - Check [ELIXIR service status](https://www.elixir-europe.org/)

4. **Implement Retry Logic**:
   The application includes automatic retries, but you can adjust timeouts:
   ```python
   # In API client configuration
   TIMEOUT = 30  # Increase timeout
   MAX_RETRIES = 5  # Increase retry attempts
   ```

#### Issue: Rate Limiting

**Symptoms**:
- `429 Too Many Requests` errors
- Slow API responses
- Analysis failures after multiple requests

**Solutions**:

1. **Reduce Request Frequency**:
   ```powershell
   # Set rate limiting environment variable
   $env:BIOTOOLS_RATE_LIMIT = "50"  # Requests per hour
   ```

2. **Use Cached Data**:
   - Check `data/cache/` directory for existing data
   - The application automatically uses cached responses
   - Clear cache only when fresh data is needed

3. **Batch Processing Strategy**:
   - Analyze smaller tool sets (5-10 tools)
   - Wait between large analyses
   - Use random analysis sparingly

#### Issue: Invalid Tool IDs

**Symptoms**:
- `Tool not found` errors
- Empty analysis results
- 404 errors for specific tools

**Solutions**:

1. **Verify Tool ID Format**:
   - Use exact bio.tools ID (case-insensitive)
   - Examples: `blast`, `clustalw`, `galaxy`
   - Avoid spaces or special characters

2. **Search for Correct ID**:
   - Use bio.tools website search
   - Check tool homepage for bio.tools link
   - Use "Search & Analyze" mode to find tools

3. **Test with Known Tools**:
   ```
   Known working tool IDs:
   - blast
   - clustalw
   - muscle
   - emboss
   - galaxy
   ```

### Data Processing Issues

#### Issue: Analysis Failures

**Symptoms**:
- Analysis completes but shows errors
- Missing quality metrics
- Incomplete results

**Solutions**:

1. **Check Tool Data Quality**:
   - Some tools may have malformed metadata
   - Not all tools can be fully analyzed
   - Check source data at bio.tools website

2. **Review Analysis Logs**:
   ```powershell
   # Check log files
   Get-Content logs\biotools_quality_analysis.log | Select-Object -Last 50
   ```

3. **Retry Analysis**:
   - Clear cache for specific tool
   - Restart application
   - Try analysis with different tool

#### Issue: Schema Validation Errors

**Symptoms**:
- "Schema validation failed" messages
- Analysis completes but with warnings
- Unexpected validation results

**Solutions**:

1. **Update Schema Files**:
   - Ensure biotoolsSchema is current
   - Check for schema updates
   - Restart application after updates

2. **Understand Validation Context**:
   - Schema errors reflect actual tool metadata issues
   - Not all schema errors prevent analysis
   - Use results to guide tool improvement

## Performance Issues

### Slow Analysis Performance

#### Issue: Long Analysis Times

**Symptoms**:
- Individual tool analysis takes >30 seconds
- Bulk analysis times out
- Application becomes unresponsive

**Solutions**:

1. **Check System Resources**:
   ```powershell
   # Monitor memory and CPU usage
   Get-Process -Name python | Select-Object Name, CPU, WorkingSet
   ```

2. **Optimize Analysis Parameters**:
   - Reduce batch sizes for bulk analysis
   - Use cached data when possible
   - Analyze fewer tools simultaneously

3. **Improve Network Performance**:
   - Use wired connection instead of WiFi
   - Close bandwidth-intensive applications
   - Consider running during off-peak hours

4. **System Requirements Check**:
   - Minimum 4GB RAM (8GB recommended)
   - Stable internet connection
   - Updated Python and dependencies

#### Issue: Memory Problems

**Symptoms**:
- Out of memory errors
- Application crashes during large analyses
- System becomes slow

**Solutions**:

1. **Monitor Memory Usage**:
   ```powershell
   # Windows
   Get-Counter "\Memory\Available MBytes"
   
   # Check Python memory usage
   Get-Process python | Select-Object WorkingSet
   ```

2. **Optimize Memory Usage**:
   - Restart application between large analyses
   - Clear cache periodically
   - Close other applications

3. **Adjust Analysis Strategy**:
   - Process tools in smaller batches
   - Use streaming for large datasets
   - Export results frequently

## User Interface Issues

### Browser and Display Problems

#### Issue: Interface Not Loading

**Symptoms**:
- Blank page in browser
- "Unable to connect" errors
- Interface elements missing

**Solutions**:

1. **Browser Troubleshooting**:
   ```powershell
   # Try different browsers
   # Clear browser cache and cookies
   # Disable browser extensions
   # Try incognito/private mode
   ```

2. **Check Console Errors**:
   - Open browser developer tools (F12)
   - Check Console tab for JavaScript errors
   - Look for network connection issues

3. **Streamlit Configuration**:
   Edit `.streamlit/config.toml`:
   ```toml
   [server]
   enableCORS = false
   enableXsrfProtection = false
   
   [browser]
   gatherUsageStats = false
   ```

#### Issue: Slow Interface Response

**Symptoms**:
- Buttons take long time to respond
- Analysis seems stuck
- Page loading delays

**Solutions**:

1. **Check Application Status**:
   - Look for progress indicators
   - Check terminal/command prompt for activity
   - Wait for cache warming

2. **Browser Optimization**:
   - Close unnecessary browser tabs
   - Clear browser cache
   - Restart browser

3. **System Performance**:
   - Close other applications
   - Check available memory
   - Restart application if needed

### Visualization Problems

#### Issue: Charts Not Displaying

**Symptoms**:
- Empty chart areas
- "Unable to render" messages
- Missing visualizations

**Solutions**:

1. **JavaScript and Library Issues**:
   - Ensure browser JavaScript is enabled
   - Check for ad blockers affecting Plotly
   - Try refreshing the page

2. **Data Availability**:
   - Verify analysis completed successfully
   - Check for analysis errors
   - Retry analysis if needed

3. **Browser Compatibility**:
   - Use modern browser (Chrome, Firefox, Safari, Edge)
   - Update browser to latest version
   - Try different browser

## Getting Additional Help

### Diagnostic Information Collection

When reporting issues, collect the following information:

1. **System Information**:
   ```powershell
   # Operating system
   Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion
   
   # Python version
   python --version
   
   # Package versions
   pip freeze | findstr -i "streamlit plotly pandas"
   ```

2. **Application Logs**:
   ```powershell
   # Recent log entries
   Get-Content logs\biotools_quality_analysis.log | Select-Object -Last 100
   ```

3. **Error Messages**:
   - Full error text from terminal/command prompt
   - Browser console errors (F12 → Console)
   - Screenshots of interface issues

### Support Channels

1. **GitHub Issues**:
   - [Report bugs](https://github.com/bneiG1/bio.tools-annotation-quality-evaluation/issues)
   - Search existing issues first
   - Provide diagnostic information

2. **Community Discussions**:
   - [GitHub Discussions](https://github.com/bneiG1/bio.tools-annotation-quality-evaluation/discussions)
   - Community support and questions
   - Feature requests and suggestions

3. **Documentation**:
   - Check other documentation sections
   - Review examples and tutorials
   - Consult API documentation

### Emergency Workarounds

If you need to continue working while resolving issues:

1. **Use Alternative Analysis Methods**:
   - Try bio.tools website directly
   - Use biotools-linter command line tool
   - Manual quality assessment

2. **Reduce Analysis Scope**:
   - Analyze single tools instead of collections
   - Use cached data when possible
   - Focus on most critical tools

3. **Alternative Environments**:
   - Try different computer/operating system
   - Use cloud-based Python environment
   - Run in Docker container (if available)

## Preventing Common Issues

### Best Practices

1. **Regular Updates**:
   ```powershell
   # Update dependencies periodically
   pip install --upgrade -r requirements.txt
   
   # Check for application updates
   git pull origin main
   ```

2. **Environment Management**:
   - Use virtual environments consistently
   - Document your configuration
   - Keep backup of working setup

3. **Data Management**:
   - Monitor cache size and clean periodically
   - Export important results
   - Document analysis parameters

4. **Resource Monitoring**:
   - Monitor system performance during analysis
   - Plan analyses during low-usage periods
   - Ensure adequate disk space

### Configuration Backup

Save working configuration for easy restoration:

```powershell
# Backup environment
pip freeze > requirements_working.txt

# Backup configuration
Copy-Item .streamlit\config.toml .streamlit\config_backup.toml

# Document working setup
@"
Working Configuration - $(Get-Date)
OS: $(Get-ComputerInfo | Select-Object -ExpandProperty WindowsProductName)
Python: $(python --version)
Working Directory: $(Get-Location)
"@ | Out-File -FilePath "working_config.txt"
```

Remember: Most issues have solutions, and the community is here to help. Don't hesitate to ask for assistance when needed!
