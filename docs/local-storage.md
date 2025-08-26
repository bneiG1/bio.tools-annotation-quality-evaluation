# Local Data Storage System

The bio.tools evaluation system now includes comprehensive local data storage capabilities that allow you to:

1. **Download and save each biotool as individual JSON files**
2. **Run evaluations on either API data or locally stored data**
3. **Organize tools by collection, topic, or query**

## Features

### Individual Tool Storage
- Each biotool is saved as a separate JSON file
- Tools are organized in subdirectories by data source
- Files include metadata about when and how they were saved
- Automatic filename sanitization for compatibility

### Data Source Options
- **API Mode**: Fetch fresh data from bio.tools API
- **Local Mode**: Use previously downloaded data
- **Hybrid Mode**: Use local data when available, API as fallback
- **Legacy Mode**: Load from single JSON batch files

### Storage Organization
The local storage system organizes tools into subdirectories:
- `data/biotools/all/` - All tools (general storage)
- `data/biotools/collections/` - Tools from specific collections  
- `data/biotools/topics/` - Tools from specific topics
- `data/biotools/queries/` - Tools from search queries

## Usage

### Basic Evaluation with Local Storage

```bash
# Download and evaluate tools from a collection (saves locally by default)
python scripts/run_evaluation.py --collection proteomics --limit 50

# Use locally stored data instead of API
python scripts/run_evaluation.py --collection proteomics --use-local

# Disable local storage completely
python scripts/run_evaluation.py --collection proteomics --disable-local-storage

# Local storage management commands
python scripts/run_evaluation.py --storage-info
python scripts/run_evaluation.py --list-local-tools
python scripts/run_evaluation.py --clear-local-data all
```

### Local Data Management Tool

A dedicated command-line tool for managing local data:

```bash
# Show storage information
python scripts/manage_local_data.py info

# List stored tools
python scripts/manage_local_data.py list --subdirectory collections

# Download tools from API
python scripts/manage_local_data.py download --collection proteomics --limit 100

# Export tools to JSON file
python scripts/manage_local_data.py export --subdirectory all --output my_tools.json

# Clear stored tools
python scripts/manage_local_data.py clear --subdirectory collections --confirm
```

## Configuration Options

### API Client Configuration

```python
from data_collection.api_client import BioToolsAPIClient

# Enable local storage (default)
client = BioToolsAPIClient(
    enable_local_storage=True,
    local_data_dir="data/biotools"
)

# Disable local storage
client = BioToolsAPIClient(enable_local_storage=False)
```

### Method Parameters

All data collection methods now support local storage parameters:

```python
# Use local data if available, otherwise API
tools = client.get_tools_by_collection(
    "proteomics", 
    limit=100,
    use_local=True,
    save_locally=True
)

# Force API usage and save locally
tools = client.get_tools_by_collection(
    "proteomics", 
    limit=100,
    use_local=False,
    save_locally=True
)
```

## File Structure

Individual tool files follow this structure:

```json
{
  "biotoolsID": "tool_name",
  "name": "Tool Name",
  "description": "Tool description...",
  "function": [...],
  "topic": [...],
  // ... other tool data ...
  "_metadata": {
    "saved_at": "2025-08-26T10:30:00.123456",
    "saved_from": "collections",
    "file_version": "1.0"
  }
}
```

## Benefits

### Performance
- Faster evaluation runs when using local data
- Reduced API calls and network dependency
- Ability to work offline

### Data Management
- Individual files are easier to examine and debug
- Version control friendly (can track individual tool changes)
- Organized by data source for better management

### Flexibility
- Run evaluations on specific subsets of tools
- Compare different versions of tools over time
- Custom data processing workflows

## Migration from Existing Setup

The new system is backwards compatible:

1. **Existing scripts continue to work** with `--load-from-file`
2. **New local storage is opt-in** (enabled by default but can be disabled)  
3. **Legacy batch JSON files** are still supported
4. **Gradual migration** - start using local storage without changing existing workflows

## Best Practices

1. **Use local storage for repeated evaluations** to save API calls
2. **Organize by data source** using appropriate subdirectories
3. **Periodically update local data** to get latest tool information
4. **Use the management tool** for bulk operations
5. **Monitor storage usage** as individual files use more disk space

## Troubleshooting

### Storage Issues
- Check directory permissions
- Ensure sufficient disk space
- Verify file paths and names

### Data Sync Issues
- Use `--use-local=False` to force API updates
- Clear local data and re-download if needed
- Check API connectivity and rate limits

### Performance Issues
- Local mode should be faster than API mode
- Large numbers of files may impact filesystem performance
- Consider using export functionality for bulk processing
