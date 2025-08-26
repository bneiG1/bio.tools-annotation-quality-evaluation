#!/usr/bin/env python3
"""
Comprehensive Bio.tools Schema Validation Script
This script validates all bio.tools JSON files against the provided JSON schema.
"""

import json
import jsonschema
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
from collections import defaultdict, Counter
import logging

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def load_schema(schema_path: str) -> Optional[Dict[str, Any]]:
    """Load the JSON schema from file or attachment"""
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        return schema
    except FileNotFoundError:
        print(f"Schema file not found at {schema_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in schema file: {e}")
        return None

def load_biotool_file(file_path: str) -> Dict[str, Any]:
    """Load a single biotool JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        return {"error": f"JSON decode error: {e}"}
    except Exception as e:
        return {"error": f"File read error: {e}"}

def validate_biotool(biotool_data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single biotool against the schema"""
    validation_result = {
        "valid": False,
        "errors": [],
        "warnings": []
    }
    
    if "error" in biotool_data:
        validation_result["errors"].append(biotool_data["error"])
        return validation_result
    
    try:
        # Validate against schema
        jsonschema.validate(instance=biotool_data, schema=schema)
        validation_result["valid"] = True
    except jsonschema.ValidationError as e:
        validation_result["errors"].append({
            "type": "ValidationError",
            "message": e.message,
            "path": list(e.path) if e.path else [],
            "schema_path": list(e.schema_path) if e.schema_path else []
        })
    except jsonschema.SchemaError as e:
        validation_result["errors"].append({
            "type": "SchemaError", 
            "message": e.message
        })
    except Exception as e:
        validation_result["errors"].append({
            "type": "UnexpectedError",
            "message": str(e)
        })
    
    # Additional custom validations
    custom_validations = perform_custom_validations(biotool_data)
    validation_result["warnings"].extend(custom_validations["warnings"])
    validation_result["errors"].extend(custom_validations["errors"])
    
    return validation_result

def perform_custom_validations(biotool_data: Dict[str, Any]) -> Dict[str, List]:
    """Perform additional custom validations beyond schema"""
    result = {"warnings": [], "errors": []}
    
    # Check required fields that might be missing
    required_fields = ["name", "description", "homepage"]
    for field in required_fields:
        if field not in biotool_data or not biotool_data.get(field):
            result["errors"].append(f"Required field '{field}' is missing or empty")
    
    # Validate EDAM terms format
    if "topic" in biotool_data:
        for topic in biotool_data["topic"]:
            if "uri" in topic:
                if not topic["uri"].startswith("http://edamontology.org/topic_"):
                    result["warnings"].append(f"Invalid EDAM topic URI format: {topic['uri']}")
    
    # Check function operations
    if "function" in biotool_data:
        for func in biotool_data["function"]:
            if "operation" in func:
                for op in func["operation"]:
                    if "uri" in op:
                        if not op["uri"].startswith("http://edamontology.org/operation_"):
                            result["warnings"].append(f"Invalid EDAM operation URI format: {op['uri']}")
    
    # Validate publication DOIs
    if "publication" in biotool_data:
        for pub in biotool_data["publication"]:
            if "doi" in pub:
                doi = pub["doi"]
                if doi is not None and not doi.startswith("10."):
                    result["warnings"].append(f"Invalid DOI format: {doi}")
    
    # Check for empty arrays that should have content
    important_arrays = ["toolType", "topic", "function"]
    for field in important_arrays:
        if field in biotool_data and isinstance(biotool_data[field], list) and len(biotool_data[field]) == 0:
            result["warnings"].append(f"Important field '{field}' is empty")
    
    # Validate URLs
    url_fields = ["homepage"]
    for field in url_fields:
        if field in biotool_data:
            url = biotool_data[field]
            if url and not (url.startswith("http://") or url.startswith("https://")):
                result["warnings"].append(f"URL in '{field}' should use http:// or https://: {url}")
    
    return result

def generate_statistics(validation_results: Dict[str, Dict]) -> Dict[str, Any]:
    """Generate comprehensive statistics from validation results"""
    stats = {
        "total_files": len(validation_results),
        "valid_files": 0,
        "invalid_files": 0,
        "files_with_warnings": 0,
        "error_types": Counter(),
        "warning_types": Counter(),
        "common_missing_fields": Counter(),
        "validation_details": []
    }
    
    for filename, result in validation_results.items():
        if result["valid"] and not result["errors"]:
            stats["valid_files"] += 1
        else:
            stats["invalid_files"] += 1
        
        if result["warnings"]:
            stats["files_with_warnings"] += 1
        
        # Count error types
        for error in result["errors"]:
            if isinstance(error, dict):
                stats["error_types"][error.get("type", "Unknown")] += 1
                if "Required field" in error.get("message", ""):
                    field_name = error["message"].split("'")[1]
                    stats["common_missing_fields"][field_name] += 1
            else:
                stats["error_types"]["String Error"] += 1
        
        # Count warning types  
        for warning in result["warnings"]:
            if "Invalid EDAM" in warning:
                stats["warning_types"]["Invalid EDAM URI"] += 1
            elif "empty" in warning:
                stats["warning_types"]["Empty Important Field"] += 1
            elif "URL" in warning:
                stats["warning_types"]["URL Format"] += 1
            else:
                stats["warning_types"]["Other"] += 1
        
        # Store detailed results for problematic files
        if result["errors"] or result["warnings"]:
            stats["validation_details"].append({
                "filename": filename,
                "errors": result["errors"],
                "warnings": result["warnings"]
            })
    
    return stats

def save_detailed_report(validation_results: Dict[str, Dict], output_file: str):
    """Save detailed validation report to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)

def print_summary_report(stats: Dict[str, Any]):
    """Print a summary report to console"""
    print("\n" + "="*60)
    print("BIO.TOOLS SCHEMA VALIDATION SUMMARY REPORT")
    print("="*60)
    
    print(f"\nOVERALL STATISTICS:")
    print(f"  Total files processed: {stats['total_files']}")
    print(f"  Valid files: {stats['valid_files']} ({stats['valid_files']/stats['total_files']*100:.1f}%)")
    print(f"  Invalid files: {stats['invalid_files']} ({stats['invalid_files']/stats['total_files']*100:.1f}%)")
    print(f"  Files with warnings: {stats['files_with_warnings']} ({stats['files_with_warnings']/stats['total_files']*100:.1f}%)")
    
    print(f"\nERROR BREAKDOWN:")
    if stats['error_types']:
        for error_type, count in stats['error_types'].most_common():
            print(f"  {error_type}: {count}")
    else:
        print("  No errors found!")
    
    print(f"\nWARNING BREAKDOWN:")
    if stats['warning_types']:
        for warning_type, count in stats['warning_types'].most_common():
            print(f"  {warning_type}: {count}")
    else:
        print("  No warnings found!")
    
    print(f"\nCOMMON MISSING FIELDS:")
    if stats['common_missing_fields']:
        for field, count in stats['common_missing_fields'].most_common(10):
            print(f"  {field}: {count} files")
    else:
        print("  No commonly missing required fields!")
    
    print(f"\nMOST PROBLEMATIC FILES:")
    problematic_files = sorted(stats['validation_details'], 
                             key=lambda x: len(x['errors']) + len(x['warnings']), 
                             reverse=True)[:10]
    
    for i, file_info in enumerate(problematic_files, 1):
        error_count = len(file_info['errors'])
        warning_count = len(file_info['warnings'])
        print(f"  {i}. {file_info['filename']}: {error_count} errors, {warning_count} warnings")

def main():
    parser = argparse.ArgumentParser(description="Validate bio.tools JSON files against schema")
    parser.add_argument("--biotools-dir", required=True, help="Directory containing bio.tools JSON files")
    parser.add_argument("--schema-file", required=True, help="Path to the JSON schema file")
    parser.add_argument("--output", help="Output file for detailed results (JSON)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--limit", type=int, help="Limit number of files to process (for testing)")
    
    args = parser.parse_args()
    
    logger = setup_logging(args.log_level)
    logger.info("Starting bio.tools schema validation")
    
    # Load schema
    logger.info(f"Loading schema from {args.schema_file}")
    schema = load_schema(args.schema_file)
    if not schema:
        logger.error("Failed to load schema")
        sys.exit(1)
    
    # Find all JSON files
    biotools_dir = Path(args.biotools_dir)
    if not biotools_dir.exists():
        logger.error(f"Bio.tools directory does not exist: {biotools_dir}")
        sys.exit(1)
    
    json_files = list(biotools_dir.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files")
    
    if args.limit:
        json_files = json_files[:args.limit]
        logger.info(f"Limited to {len(json_files)} files for testing")
    
    # Validate each file
    validation_results = {}
    
    for i, json_file in enumerate(json_files, 1):
        if i % 100 == 0:
            logger.info(f"Processed {i}/{len(json_files)} files")
        
        logger.debug(f"Validating {json_file.name}")
        biotool_data = load_biotool_file(str(json_file))
        validation_result = validate_biotool(biotool_data, schema)
        validation_results[json_file.name] = validation_result
    
    logger.info(f"Validation complete. Processed {len(json_files)} files")
    
    # Generate statistics
    stats = generate_statistics(validation_results)
    
    # Save detailed report if requested
    if args.output:
        logger.info(f"Saving detailed report to {args.output}")
        save_detailed_report(validation_results, args.output)
    
    # Print summary
    print_summary_report(stats)
    
    # Return appropriate exit code
    if stats["invalid_files"] > 0:
        logger.warning(f"Validation completed with {stats['invalid_files']} invalid files")
        sys.exit(1)
    else:
        logger.info("All files passed validation!")
        sys.exit(0)

if __name__ == "__main__":
    main()
