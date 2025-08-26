#!/usr/bin/env python3
"""
Command-line tool for managing local bio.tools data storage.
"""

import argparse
import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from data_collection.local_data_manager import LocalDataManager
from data_collection.api_client import BioToolsAPIClient

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Manage local bio.tools data storage'
    )
    
    parser.add_argument('--data-dir', type=str, default='data/biotools',
                       help='Local data directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show storage information')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List stored tools')
    list_parser.add_argument('--subdirectory', type=str, default='all',
                           choices=['all', 'collections', 'topics', 'queries'],
                           help='Subdirectory to list')
    list_parser.add_argument('--limit', type=int, help='Limit number of tools to show')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear stored tools')
    clear_parser.add_argument('--subdirectory', type=str, default='all',
                            choices=['all', 'collections', 'topics', 'queries'],
                            help='Subdirectory to clear')
    clear_parser.add_argument('--confirm', action='store_true',
                            help='Confirm deletion without prompt')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download tools from API')
    download_parser.add_argument('--collection', type=str, help='Collection to download')
    download_parser.add_argument('--topic', type=str, help='Topic to download')
    download_parser.add_argument('--query', type=str, help='Query to download')
    download_parser.add_argument('--limit', type=int, default=100, help='Limit number of tools')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export tools to JSON file')
    export_parser.add_argument('--subdirectory', type=str, default='all',
                             choices=['all', 'collections', 'topics', 'queries'],
                             help='Subdirectory to export')
    export_parser.add_argument('--output', type=str, required=True,
                             help='Output JSON file')
    export_parser.add_argument('--limit', type=int, help='Limit number of tools to export')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Initialize local data manager
        local_manager = LocalDataManager(args.data_dir)
        
        if args.command == 'info':
            info = local_manager.get_storage_info()
            print(f"\nLocal Storage Information:")
            print(f"Data Directory: {info['data_directory']}")
            print(f"\nSubdirectories:")
            total_tools = 0
            for subdir, details in info['subdirectories'].items():
                status = "exists" if details['exists'] else "missing"
                print(f"  {subdir:12} {details['tool_count']:6} tools  ({status})")
                total_tools += details['tool_count']
            print(f"\nTotal: {total_tools} tools stored locally")
            
        elif args.command == 'list':
            tools = local_manager.list_available_tools(args.subdirectory)
            if args.limit:
                tools = tools[:args.limit]
            
            print(f"\nTools in '{args.subdirectory}' subdirectory ({len(tools)} total):")
            print("-" * 50)
            for tool_id in tools:
                print(f"  {tool_id}")
            
            if not tools:
                print("  No tools found")
        
        elif args.command == 'clear':
            tools_count = len(local_manager.list_available_tools(args.subdirectory))
            
            if tools_count == 0:
                print(f"No tools found in '{args.subdirectory}' subdirectory")
                return 0
            
            if not args.confirm:
                response = input(f"Delete {tools_count} tools from '{args.subdirectory}'? (y/N): ")
                if response.lower() != 'y':
                    print("Cancelled")
                    return 0
            
            deleted_count = local_manager.clear_tools(args.subdirectory)
            print(f"Deleted {deleted_count} tools from '{args.subdirectory}' subdirectory")
        
        elif args.command == 'download':
            # Initialize API client
            api_client = BioToolsAPIClient(enable_local_storage=True, local_data_dir=args.data_dir)
            
            print("Downloading tools from bio.tools API...")
            
            if args.collection:
                print(f"Collection: {args.collection}")
                tools = api_client.get_tools_by_collection(args.collection, args.limit, save_locally=True)
                subdirectory = "collections"
            elif args.topic:
                print(f"Topic: {args.topic}")
                tools = api_client.get_tools_by_topic(args.topic, args.limit, save_locally=True)
                subdirectory = "topics"
            elif args.query:
                print(f"Query: {args.query}")
                tools = api_client.search_tools(args.query, args.limit, save_locally=True)
                subdirectory = "queries"
            else:
                print(f"All tools (limit: {args.limit})")
                tools = api_client.get_all_tools(args.limit, save_locally=True)
                subdirectory = "all"
            
            print(f"Downloaded and saved {len(tools)} tools to '{subdirectory}' subdirectory")
        
        elif args.command == 'export':
            tools = local_manager.load_all_tools(args.subdirectory, limit=args.limit)
            
            if not tools:
                print(f"No tools found in '{args.subdirectory}' subdirectory")
                return 0
            
            # Remove metadata for cleaner export
            clean_tools = []
            for tool in tools:
                clean_tool = {k: v for k, v in tool.items() if not k.startswith('_')}
                clean_tools.append(clean_tool)
            
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(clean_tools, f, indent=2, ensure_ascii=False)
            
            print(f"Exported {len(clean_tools)} tools to {output_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
