# Utils package initialization

# Add biotools-linter constants to avoid import conflicts
REPORT = 25  # Report log level from biotools-linter

def flatten_json_to_single_dict(json_data, parent_key="", separator="/"):
    """Placeholder function for biotools-linter compatibility"""
    return {}

def array_without_value(arr, value):
    """Placeholder function for biotools-linter compatibility"""
    return [item for item in arr if item != value]

def sanity_check_json(json_data):
    """Placeholder function for biotools-linter compatibility"""
    return isinstance(json_data, dict)
