"""
Schema validation module for bio.tools entries.

This module validates bio.tools entries against the official biotoolsSchema
and provides detailed validation reports.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.request import urlopen

import jsonschema
from jsonschema import Draft4Validator, validators

logger = logging.getLogger(__name__)


class BiotoolsSchemaValidator:
    """
    Validator for bio.tools entries against biotoolsSchema.
    
    Downloads and caches the official biotoolsSchema and validates
    tool entries, providing detailed error reports.
    """
    
    SCHEMA_URL = "https://raw.githubusercontent.com/bio-tools/biotoolsSchema/main/jsonschema/biotoolsj.json"
    
    def __init__(self, schema_path: Optional[Union[str, Path]] = None):
        """
        Initialize the schema validator.
        
        Args:
            schema_path: Path to local schema file. If None, downloads from GitHub.
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema = None
        self.validator = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the biotoolsSchema from file or URL."""
        try:
            if self.schema_path and self.schema_path.exists():
                logger.info(f"Loading schema from local file: {self.schema_path}")
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
            else:
                logger.info(f"Downloading schema from: {self.SCHEMA_URL}")
                with urlopen(self.SCHEMA_URL) as response:
                    self.schema = json.loads(response.read().decode('utf-8'))
                
                # Cache the schema locally if path is provided
                if self.schema_path:
                    self.schema_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.schema_path, 'w', encoding='utf-8') as f:
                        json.dump(self.schema, f, indent=2)
                    logger.info(f"Schema cached to: {self.schema_path}")
            
            # Create validator instance
            self.validator = Draft4Validator(self.schema)
            
            logger.info("Schema loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise
    
    def validate_tool(self, tool_data: Dict) -> Dict:
        """
        Validate a single tool against the schema.
        
        Args:
            tool_data: Tool metadata to validate
            
        Returns:
            Validation result with errors and warnings
        """
        if not self.validator:
            raise RuntimeError("Schema not loaded. Cannot validate.")
        
        # Wrap single tool in array format if needed
        if isinstance(tool_data, dict):
            data_to_validate = [tool_data]
        else:
            data_to_validate = tool_data
        
        errors = []
        warnings = []
        
        try:
            # Validate against schema
            validation_errors = list(self.validator.iter_errors(data_to_validate))
            
            for error in validation_errors:
                error_info = {
                    "path": ".".join(str(p) for p in error.absolute_path),
                    "message": error.message,
                    "value": error.instance,
                    "validator": error.validator,
                    "schema_path": ".".join(str(p) for p in error.schema_path)
                }
                
                # Categorize as error or warning based on validator type
                if error.validator in ["required", "type", "format"]:
                    errors.append(error_info)
                else:
                    warnings.append(error_info)
            
            is_valid = len(errors) == 0
            
        except Exception as e:
            logger.error(f"Validation failed with exception: {e}")
            errors.append({
                "path": "root",
                "message": f"Validation exception: {str(e)}",
                "value": None,
                "validator": "exception",
                "schema_path": ""
            })
            is_valid = False
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "summary": self._generate_validation_summary(is_valid, errors, warnings)
        }
    
    def validate_tools_batch(self, tools_data: List[Dict]) -> Dict:
        """
        Validate multiple tools in batch.
        
        Args:
            tools_data: List of tool metadata to validate
            
        Returns:
            Batch validation results
        """
        results = {}
        summary = {
            "total_tools": len(tools_data),
            "valid_tools": 0,
            "invalid_tools": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "common_errors": {},
            "common_warnings": {}
        }
        
        for i, tool_data in enumerate(tools_data):
            tool_id = tool_data.get("biotoolsID", f"tool_{i}")
            result = self.validate_tool(tool_data)
            results[tool_id] = result
            
            if result["valid"]:
                summary["valid_tools"] += 1
            else:
                summary["invalid_tools"] += 1
            
            summary["total_errors"] += result["error_count"]
            summary["total_warnings"] += result["warning_count"]
            
            # Collect common error patterns
            for error in result["errors"]:
                error_key = f"{error['validator']}:{error['schema_path']}"
                summary["common_errors"][error_key] = summary["common_errors"].get(error_key, 0) + 1
            
            for warning in result["warnings"]:
                warning_key = f"{warning['validator']}:{warning['schema_path']}"
                summary["common_warnings"][warning_key] = summary["common_warnings"].get(warning_key, 0) + 1
        
        return {
            "results": results,
            "summary": summary
        }
    
    def _generate_validation_summary(self, is_valid: bool, errors: List[Dict], warnings: List[Dict]) -> str:
        """Generate a human-readable validation summary."""
        if is_valid:
            if warnings:
                return f"Valid with {len(warnings)} warning(s)"
            else:
                return "Valid"
        else:
            return f"Invalid: {len(errors)} error(s), {len(warnings)} warning(s)"
    
    def get_schema_info(self) -> Dict:
        """Get information about the loaded schema."""
        if not self.schema:
            return {"error": "Schema not loaded"}
        
        return {
            "title": self.schema.get("description", ""),
            "schema_version": self.schema.get("$schema", ""),
            "has_definitions": "definitions" in self.schema,
            "main_object": "tool" if "tool" in self.schema.get("definitions", {}) else None,
            "required_fields": self.schema.get("definitions", {}).get("tool", {}).get("required", [])
        }


class ExtendedSchemaValidator(BiotoolsSchemaValidator):
    """
    Extended validator with additional bio.tools specific checks.
    
    Performs additional validation beyond the basic schema checks,
    including URL validation, EDAM term checking, and consistency checks.
    """
    
    def __init__(self, schema_path: Optional[Union[str, Path]] = None):
        super().__init__(schema_path)
        self.additional_checks = True
    
    def validate_tool(self, tool_data: Dict) -> Dict:
        """
        Validate with extended checks.
        
        Performs schema validation plus additional bio.tools specific checks.
        """
        # Get basic schema validation results
        result = super().validate_tool(tool_data)
        
        if self.additional_checks:
            # Add custom validation checks
            custom_errors, custom_warnings = self._perform_custom_checks(tool_data)
            
            result["errors"].extend(custom_errors)
            result["warnings"].extend(custom_warnings)
            result["error_count"] = len(result["errors"])
            result["warning_count"] = len(result["warnings"])
            result["valid"] = len(result["errors"]) == 0
            result["summary"] = self._generate_validation_summary(
                result["valid"], result["errors"], result["warnings"]
            )
        
        return result
    
    def _perform_custom_checks(self, tool_data: Dict) -> tuple[List[Dict], List[Dict]]:
        """
        Perform custom validation checks specific to bio.tools.
        
        Returns:
            Tuple of (errors, warnings) lists
        """
        errors = []
        warnings = []
        
        # Check EDAM terms consistency
        edam_issues = self._check_edam_terms(tool_data)
        warnings.extend(edam_issues)
        
        # Check URL accessibility (basic format check)
        url_issues = self._check_urls(tool_data)
        warnings.extend(url_issues)
        
        # Check function input/output consistency
        function_issues = self._check_function_consistency(tool_data)
        warnings.extend(function_issues)
        
        # Check publication format
        pub_issues = self._check_publications(tool_data)
        warnings.extend(pub_issues)
        
        return errors, warnings
    
    def _check_edam_terms(self, tool_data: Dict) -> List[Dict]:
        """Check EDAM term format and consistency."""
        issues = []
        
        # Check topics
        topics = tool_data.get("topic", [])
        for i, topic in enumerate(topics):
            if isinstance(topic, dict):
                term = topic.get("term")
                uri = topic.get("uri")
                
                if uri and not uri.startswith("http://edamontology.org/topic_"):
                    issues.append({
                        "path": f"topic[{i}].uri",
                        "message": "EDAM topic URI should start with 'http://edamontology.org/topic_'",
                        "value": uri,
                        "validator": "custom_edam",
                        "schema_path": "topic.uri"
                    })
        
        # Check function operations
        functions = tool_data.get("function", [])
        for i, func in enumerate(functions):
            operations = func.get("operation", [])
            for j, operation in enumerate(operations):
                if isinstance(operation, dict):
                    uri = operation.get("uri")
                    if uri and not uri.startswith("http://edamontology.org/operation_"):
                        issues.append({
                            "path": f"function[{i}].operation[{j}].uri",
                            "message": "EDAM operation URI should start with 'http://edamontology.org/operation_'",
                            "value": uri,
                            "validator": "custom_edam",
                            "schema_path": "function.operation.uri"
                        })
        
        return issues
    
    def _check_urls(self, tool_data: Dict) -> List[Dict]:
        """Check URL format (basic validation)."""
        issues = []
        
        # Check homepage
        homepage = tool_data.get("homepage")
        if homepage and not (homepage.startswith("http://") or homepage.startswith("https://")):
            issues.append({
                "path": "homepage",
                "message": "Homepage URL should start with 'http://' or 'https://'",
                "value": homepage,
                "validator": "custom_url",
                "schema_path": "homepage"
            })
        
        # Check documentation URLs
        docs = tool_data.get("documentation", [])
        for i, doc in enumerate(docs):
            if isinstance(doc, dict):
                url = doc.get("url")
                if url and not (url.startswith("http://") or url.startswith("https://")):
                    issues.append({
                        "path": f"documentation[{i}].url",
                        "message": "Documentation URL should start with 'http://' or 'https://'",
                        "value": url,
                        "validator": "custom_url",
                        "schema_path": "documentation.url"
                    })
        
        return issues
    
    def _check_function_consistency(self, tool_data: Dict) -> List[Dict]:
        """Check function input/output consistency."""
        issues = []
        
        functions = tool_data.get("function", [])
        for i, func in enumerate(functions):
            operations = func.get("operation", [])
            inputs = func.get("input", [])
            outputs = func.get("output", [])
            
            # Warn if function has operations but no input/output
            if operations and not inputs and not outputs:
                issues.append({
                    "path": f"function[{i}]",
                    "message": "Function has operations but no input or output defined",
                    "value": None,
                    "validator": "custom_function",
                    "schema_path": "function"
                })
        
        return issues
    
    def _check_publications(self, tool_data: Dict) -> List[Dict]:
        """Check publication format."""
        issues = []
        
        pubs = tool_data.get("publication", [])
        for i, pub in enumerate(pubs):
            if isinstance(pub, dict):
                doi = pub.get("doi")
                pmid = pub.get("pmid")
                pmcid = pub.get("pmcid")
                
                # Check DOI format
                if doi and not doi.startswith("10."):
                    issues.append({
                        "path": f"publication[{i}].doi",
                        "message": "DOI should start with '10.'",
                        "value": doi,
                        "validator": "custom_publication",
                        "schema_path": "publication.doi"
                    })
                
                # Check PMCID format
                if pmcid and not pmcid.startswith("PMC"):
                    issues.append({
                        "path": f"publication[{i}].pmcid",
                        "message": "PMCID should start with 'PMC'",
                        "value": pmcid,
                        "validator": "custom_publication",
                        "schema_path": "publication.pmcid"
                    })
        
        return issues
