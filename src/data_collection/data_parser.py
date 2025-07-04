"""
Data parser for bio.tools JSON data and schema validation.
"""

import json
import jsonschema
from typing import Dict, List, Optional, Any, Set
import logging
from pathlib import Path

class BioToolsDataParser:
    """Parser for bio.tools JSON data with schema validation."""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the data parser.
        
        Args:
            schema_path: Path to biotoolsSchema JSON file
        """
        self.logger = logging.getLogger(__name__)
        self.schema = None
        
        if schema_path and Path(schema_path).exists():
            self.load_schema(schema_path)
    
    def load_schema(self, schema_path: str):
        """
        Load the biotoolsSchema for validation.
        
        Args:
            schema_path: Path to the schema file
        """
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            self.logger.info(f"Loaded schema from {schema_path}")
        except Exception as e:
            self.logger.error(f"Failed to load schema: {e}")
    
    def validate_tool(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Validate a tool against the biotoolsSchema.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing validation results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not self.schema:
            result['warnings'].append("No schema loaded for validation")
            return result
        
        try:
            jsonschema.validate(tool_data, self.schema)
        except jsonschema.ValidationError as e:
            result['is_valid'] = False
            result['errors'].append({
                'message': e.message,
                'path': list(e.path),
                'schema_path': list(e.schema_path)
            })
        except jsonschema.SchemaError as e:
            result['errors'].append(f"Schema error: {e.message}")
        
        return result
    
    def extract_basic_info(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Extract basic information from tool data.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing basic tool information
        """
        return {
            'biotoolsID': tool_data.get('biotoolsID'),
            'biotoolsCURIE': tool_data.get('biotoolsCURIE'),
            'name': tool_data.get('name'),
            'description': tool_data.get('description'),
            'homepage': tool_data.get('homepage'),
            'version': tool_data.get('version', []),
            'toolType': tool_data.get('toolType', []),
            'topic': tool_data.get('topic', []),
            'operatingSystem': tool_data.get('operatingSystem', []),
            'language': tool_data.get('language', []),
            'license': tool_data.get('license'),
            'collectionID': tool_data.get('collectionID', []),
            'maturity': tool_data.get('maturity'),
            'cost': tool_data.get('cost'),
            'accessibility': tool_data.get('accessibility', [])
        }
    
    def extract_function_info(self, tool_data: Dict) -> List[Dict[str, Any]]:
        """
        Extract function information from tool data.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            List of function dictionaries
        """
        functions = tool_data.get('function', [])
        extracted_functions = []
        
        for func in functions:
            extracted_functions.append({
                'operation': func.get('operation', []),
                'input': func.get('input', []),
                'output': func.get('output', []),
                'note': func.get('note'),
                'cmd': func.get('cmd')
            })
        
        return extracted_functions
    
    def extract_documentation_info(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Extract documentation and publication information.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing documentation information
        """
        return {
            'documentation': tool_data.get('documentation', []),
            'publication': tool_data.get('publication', []),
            'publicationsPrimaryID': tool_data.get('publicationsPrimaryID'),
            'publicationsOtherID': tool_data.get('publicationsOtherID', [])
        }
    
    def extract_links_info(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Extract links and download information.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing links information
        """
        return {
            'download': tool_data.get('download', []),
            'link': tool_data.get('link', []),
            'repository': tool_data.get('repository', [])
        }
    
    def extract_community_info(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Extract community and contact information.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing community information
        """
        return {
            'credit': tool_data.get('credit', []),
            'contact': tool_data.get('contact', []),
            'owner': tool_data.get('owner'),
            'additionDate': tool_data.get('additionDate'),
            'lastUpdate': tool_data.get('lastUpdate')
        }
    
    def get_all_fields(self, tool_data: Dict) -> Set[str]:
        """
        Get all field names present in tool data.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Set of field names
        """
        fields = set()
        
        def extract_fields(data, prefix=''):
            if isinstance(data, dict):
                for key, value in data.items():
                    field_name = f"{prefix}.{key}" if prefix else key
                    fields.add(field_name)
                    if isinstance(value, (dict, list)):
                        extract_fields(value, field_name)
            elif isinstance(data, list) and data:
                for i, item in enumerate(data[:1]):  # Check first item only
                    extract_fields(item, prefix)
        
        extract_fields(tool_data)
        return fields
    
    def check_field_completeness(self, tool_data: Dict, required_fields: List[str]) -> Dict[str, Any]:
        """
        Check completeness of required fields in tool data.
        
        Args:
            tool_data: Tool data dictionary
            required_fields: List of required field names
            
        Returns:
            Dictionary containing completeness information
        """
        present_fields = []
        missing_fields = []
        empty_fields = []
        
        for field in required_fields:
            if '.' in field:
                # Handle nested fields
                parts = field.split('.')
                current = tool_data
                field_exists = True
                
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        field_exists = False
                        break
                
                if field_exists:
                    if self._is_field_empty(current):
                        empty_fields.append(field)
                    else:
                        present_fields.append(field)
                else:
                    missing_fields.append(field)
            else:
                # Handle top-level fields
                if field in tool_data:
                    if self._is_field_empty(tool_data[field]):
                        empty_fields.append(field)
                    else:
                        present_fields.append(field)
                else:
                    missing_fields.append(field)
        
        return {
            'present_fields': present_fields,
            'missing_fields': missing_fields,
            'empty_fields': empty_fields,
            'completeness_ratio': len(present_fields) / len(required_fields) if required_fields else 0
        }
    
    def _is_field_empty(self, value: Any) -> bool:
        """
        Check if a field value is considered empty.
        
        Args:
            value: Field value to check
            
        Returns:
            True if field is empty, False otherwise
        """
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (list, dict)) and not value:
            return True
        return False
    
    def extract_tool_summary(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Extract a comprehensive summary of tool data.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dictionary containing tool summary
        """
        return {
            'basic_info': self.extract_basic_info(tool_data),
            'functions': self.extract_function_info(tool_data),
            'documentation': self.extract_documentation_info(tool_data),
            'links': self.extract_links_info(tool_data),
            'community': self.extract_community_info(tool_data),
            'all_fields': list(self.get_all_fields(tool_data)),
            'field_count': len(self.get_all_fields(tool_data))
        }
    
    def batch_parse_tools(self, tools_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        Parse multiple tools in batch.
        
        Args:
            tools_data: List of tool data dictionaries
            
        Returns:
            List of parsed tool summaries
        """
        parsed_tools = []
        
        for i, tool_data in enumerate(tools_data):
            try:
                summary = self.extract_tool_summary(tool_data)
                summary['parse_index'] = i
                parsed_tools.append(summary)
            except Exception as e:
                self.logger.error(f"Failed to parse tool {i}: {e}")
                parsed_tools.append({
                    'parse_index': i,
                    'error': str(e),
                    'biotoolsID': tool_data.get('biotoolsID', 'unknown')
                })
        
        return parsed_tools
