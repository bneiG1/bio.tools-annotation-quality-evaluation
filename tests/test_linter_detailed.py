import sys
import json
from pathlib import Path
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/analyzers')

from linter import BiotoolsLinter

# Load a sample tool
sample_file = Path('data/cache/tool_BLAST__-1179062606671494878.json')
with open(sample_file, 'r', encoding='utf-8') as f:
    tool_data = json.load(f)

# Test linting
linter = BiotoolsLinter()
print(f'Linter available: {linter.is_available()}')

if linter.is_available():
    issues = linter.lint_tool(tool_data)
    tool_id = tool_data.get('biotoolsID', 'unknown')
    print(f'Found {len(issues)} linting issues for {tool_id}')
    
    # Show summary
    summary = linter.get_issue_summary(issues)
    print(f'Issue summary by level:')
    for level, count in summary['by_level'].items():
        if count > 0:
            print(f'  {level}: {count}')
    
    print(f'Top issue types:')
    for code, count in summary['top_issues']:
        print(f'  {code}: {count}')
    
    # Show first 5 issues
    print('\nIssues found:')
    for i, issue in enumerate(issues[:5]):
        print(f'{i+1}. [{issue.level.value}] {issue.code}: {issue.message}')
        if issue.location:
            print(f'   Location: {issue.location}')
    
    if len(issues) > 5:
        print(f'... and {len(issues) - 5} more issues')
