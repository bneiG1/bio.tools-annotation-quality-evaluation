#!/usr/bin/env python3
"""
Analyze validation results and create a summary report.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

def analyze_validation_results(results_file):
    """Analyze validation results and create summary."""
    
    print("Loading validation results...")
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # The data structure has bio.tools filenames as keys
    total_files = len(data)
    valid_files = 0
    files_with_errors = 0
    files_with_warnings = 0
    
    # Error analysis
    error_types = Counter()
    warning_types = Counter()
    error_messages = []
    common_errors = defaultdict(int)
    
    # Sample files for detailed analysis
    sample_errors = []
    sample_warnings = []
    
    for filename, result in data.items():
        has_errors = len(result.get('errors', [])) > 0
        has_warnings = len(result.get('warnings', [])) > 0
        
        if not has_errors and not has_warnings:
            valid_files += 1
        
        if has_errors:
            files_with_errors += 1
            
            for error in result['errors']:
                error_types[error.get('type', 'Unknown')] += 1
                if len(sample_errors) < 5:
                    sample_errors.append({
                        'file': filename,
                        'error': error.get('message', 'No message')[:200]
                    })
                
                # Extract common error patterns
                msg = error.get('message', '')
                if 'is not of type' in msg:
                    common_errors['Type mismatch'] += 1
                elif 'is a required property' in msg:
                    common_errors['Missing required field'] += 1
                elif 'does not match pattern' in msg:
                    common_errors['Pattern validation failed'] += 1
                elif 'is not valid under any of the given schemas' in msg:
                    common_errors['Schema validation failed'] += 1
                else:
                    common_errors['Other'] += 1
        
        if has_warnings:
            files_with_warnings += 1
            
            for warning in result['warnings']:
                warning_types[warning] += 1
                if len(sample_warnings) < 5:
                    sample_warnings.append({
                        'file': filename,
                        'warning': warning[:200]
                    })
    
    # Create summary report
    report = f"""
=== BIO.TOOLS SCHEMA VALIDATION ANALYSIS ===

OVERVIEW:
- Total files processed: {total_files:,}
- Valid files (no errors/warnings): {valid_files:,} ({valid_files/total_files*100:.1f}%)
- Files with schema errors: {files_with_errors:,} ({files_with_errors/total_files*100:.1f}%)
- Files with warnings: {files_with_warnings:,} ({files_with_warnings/total_files*100:.1f}%)

MAIN FINDINGS:
The bio.tools dataset appears to have a fundamental schema mismatch. The provided JSON schema expects an ARRAY of tools, but the bio.tools files contain individual TOOL OBJECTS.

ERROR ANALYSIS:
"""
    
    for error_type, count in error_types.most_common(10):
        report += f"- {error_type}: {count:,} files\n"
    
    report += f"\nCOMMON ERROR PATTERNS:\n"
    for pattern, count in sorted(common_errors.items(), key=lambda x: x[1], reverse=True):
        report += f"- {pattern}: {count:,} occurrences\n"
    
    if warning_types:
        report += f"\nWARNING ANALYSIS:\n"
        for warning_type, count in warning_types.most_common(10):
            report += f"- {warning_type}: {count:,} files\n"
    
    report += f"\nSAMPLE VALIDATION ERRORS:\n"
    for i, error in enumerate(sample_errors[:5], 1):
        report += f"{i}. File: {error['file']}\n"
        report += f"   Error: {error['error']}\n\n"
    
    if sample_warnings:
        report += f"\nSAMPLE WARNINGS:\n"
        for i, warning in enumerate(sample_warnings[:5], 1):
            report += f"{i}. File: {warning['file']}\n"
            report += f"   Warning: {warning['warning']}\n\n"
    
    report += f"""
SCHEMA COMPATIBILITY ASSESSMENT:
The provided JSON Schema defines a bio.tools tool as an ARRAY containing tool objects, but the actual bio.tools files contain individual tool objects directly. This suggests:

1. Schema Format Mismatch: The schema expects: [{{tool1}}, {{tool2}}, ...]
   But bio.tools files contain: {{tool}}

2. Validation Approach: To properly validate, we need to either:
   - Modify the schema to validate individual tool objects
   - Wrap each bio.tools file content in an array before validation

RECOMMENDATIONS:
1. The schema should be adapted to validate individual bio.tools entries
2. Many files have missing optional fields that could improve completeness
3. URL validation and EDAM concept validation should be improved
"""
    
    return report

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_validation_results.py <validation_results.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    if not Path(results_file).exists():
        print(f"Error: Results file {results_file} not found")
        sys.exit(1)
    
    try:
        report = analyze_validation_results(results_file)
        print(report)
        
        # Save summary to file
        summary_file = "validation_summary_report.txt"
        with open(summary_file, 'w') as f:
            f.write(report)
        print(f"\nDetailed summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"Error analyzing results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
