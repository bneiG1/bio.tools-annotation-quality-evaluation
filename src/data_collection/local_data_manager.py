"""
Local data manager for bio.tools data storage and retrieval.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
import re
from datetime import datetime


class LocalDataManager:
    """Manager for local bio.tools data storage and retrieval."""
    
    def __init__(self, data_dir: str = "data/biotools", create_dirs: bool = True):
        """
        Initialize the local data manager.
        
        Args:
            data_dir: Directory to store individual tool JSON files
            create_dirs: Whether to create directories if they don't exist
        """
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
        if create_dirs:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
        # Create subdirectories for organization
        self.collections_dir = self.data_dir / "collections"
        self.topics_dir = self.data_dir / "topics" 
        self.queries_dir = self.data_dir / "queries"
        self.all_tools_dir = self.data_dir / "all"
        
        if create_dirs:
            for dir_path in [self.collections_dir, self.topics_dir, self.queries_dir, self.all_tools_dir]:
                dir_path.mkdir(exist_ok=True)
    
    def _sanitize_filename(self, tool_id: str) -> str:
        """
        Sanitize biotoolsID for use as filename.
        
        Args:
            tool_id: The biotoolsID
            
        Returns:
            Sanitized filename
        """
        # Replace invalid filename characters with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', tool_id)
        # Remove any trailing/leading spaces and dots
        sanitized = sanitized.strip('. ')
        return sanitized
    
    def _get_tool_path(self, tool_id: str, subdirectory: str = "all") -> Path:
        """
        Get the file path for a specific tool.
        
        Args:
            tool_id: The biotoolsID
            subdirectory: Subdirectory to store the file in
            
        Returns:
            Path to the tool JSON file
        """
        sanitized_id = self._sanitize_filename(tool_id)
        filename = f"{sanitized_id}.json"
        
        if subdirectory == "collections":
            return self.collections_dir / filename
        elif subdirectory == "topics":
            return self.topics_dir / filename
        elif subdirectory == "queries":
            return self.queries_dir / filename
        else:
            return self.all_tools_dir / filename
    
    def save_tool(self, tool_data: Dict, subdirectory: str = "all") -> bool:
        """
        Save a single tool to a JSON file.
        
        Args:
            tool_data: Tool data dictionary
            subdirectory: Subdirectory to save the file in
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract biotoolsID
            tool_id = tool_data.get('biotoolsID')
            if not tool_id:
                self.logger.error("Tool data missing biotoolsID")
                return False
            
            # Add metadata
            enhanced_tool_data = tool_data.copy()
            enhanced_tool_data['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'saved_from': subdirectory,
                'file_version': '1.0'
            }
            
            # Get file path
            file_path = self._get_tool_path(tool_id, subdirectory)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_tool_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved tool {tool_id} to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save tool: {e}")
            return False
    
    def save_tools(self, tools: List[Dict], subdirectory: str = "all") -> Dict[str, int]:
        """
        Save multiple tools to individual JSON files.
        
        Args:
            tools: List of tool data dictionaries
            subdirectory: Subdirectory to save the files in
            
        Returns:
            Dictionary with counts of saved and failed tools
        """
        saved_count = 0
        failed_count = 0
        
        for tool in tools:
            if self.save_tool(tool, subdirectory):
                saved_count += 1
            else:
                failed_count += 1
        
        self.logger.info(f"Saved {saved_count} tools, failed to save {failed_count} tools to {subdirectory}")
        return {'saved': saved_count, 'failed': failed_count}
    
    def load_tool(self, tool_id: str, subdirectory: str = "all") -> Optional[Dict]:
        """
        Load a single tool from a JSON file.
        
        Args:
            tool_id: The biotoolsID
            subdirectory: Subdirectory to load from
            
        Returns:
            Tool data dictionary or None if not found
        """
        try:
            file_path = self._get_tool_path(tool_id, subdirectory)
            
            if not file_path.exists():
                self.logger.debug(f"Tool file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                tool_data = json.load(f)
            
            self.logger.debug(f"Loaded tool {tool_id} from {file_path}")
            return tool_data
            
        except Exception as e:
            self.logger.error(f"Failed to load tool {tool_id}: {e}")
            return None
    
    def load_tools(self, tool_ids: List[str], subdirectory: str = "all") -> List[Dict]:
        """
        Load multiple tools from JSON files.
        
        Args:
            tool_ids: List of biotoolsIDs
            subdirectory: Subdirectory to load from
            
        Returns:
            List of tool data dictionaries
        """
        tools = []
        
        for tool_id in tool_ids:
            tool_data = self.load_tool(tool_id, subdirectory)
            if tool_data:
                tools.append(tool_data)
        
        self.logger.info(f"Loaded {len(tools)} out of {len(tool_ids)} requested tools from {subdirectory}")
        return tools
    
    def load_all_tools(self, subdirectory: str = "all", limit: Optional[int] = None) -> List[Dict]:
        """
        Load all tools from a subdirectory.
        
        Args:
            subdirectory: Subdirectory to load from
            limit: Maximum number of tools to load
            
        Returns:
            List of tool data dictionaries
        """
        try:
            if subdirectory == "collections":
                target_dir = self.collections_dir
            elif subdirectory == "topics":
                target_dir = self.topics_dir
            elif subdirectory == "queries":
                target_dir = self.queries_dir
            else:
                target_dir = self.all_tools_dir
            
            if not target_dir.exists():
                self.logger.warning(f"Directory does not exist: {target_dir}")
                return []
            
            # Get all JSON files
            json_files = list(target_dir.glob("*.json"))
            
            if limit:
                json_files = json_files[:limit]
            
            tools = []
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        tool_data = json.load(f)
                    tools.append(tool_data)
                except Exception as e:
                    self.logger.error(f"Failed to load {json_file}: {e}")
            
            self.logger.info(f"Loaded {len(tools)} tools from {target_dir}")
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to load tools from {subdirectory}: {e}")
            return []
    
    def list_available_tools(self, subdirectory: str = "all") -> List[str]:
        """
        List all available tool IDs in a subdirectory.
        
        Args:
            subdirectory: Subdirectory to check
            
        Returns:
            List of biotoolsIDs
        """
        try:
            if subdirectory == "collections":
                target_dir = self.collections_dir
            elif subdirectory == "topics":
                target_dir = self.topics_dir
            elif subdirectory == "queries":
                target_dir = self.queries_dir
            else:
                target_dir = self.all_tools_dir
            
            if not target_dir.exists():
                return []
            
            # Get all JSON files and extract tool IDs from filenames
            tool_ids = []
            for json_file in target_dir.glob("*.json"):
                # Remove .json extension to get tool ID
                tool_id = json_file.stem
                tool_ids.append(tool_id)
            
            return sorted(tool_ids)
            
        except Exception as e:
            self.logger.error(f"Failed to list tools from {subdirectory}: {e}")
            return []
    
    def tool_exists(self, tool_id: str, subdirectory: str = "all") -> bool:
        """
        Check if a tool exists locally.
        
        Args:
            tool_id: The biotoolsID
            subdirectory: Subdirectory to check
            
        Returns:
            True if tool exists, False otherwise
        """
        file_path = self._get_tool_path(tool_id, subdirectory)
        return file_path.exists()
    
    def get_storage_info(self) -> Dict:
        """
        Get information about local storage.
        
        Returns:
            Dictionary with storage statistics
        """
        info = {
            'data_directory': str(self.data_dir),
            'subdirectories': {}
        }
        
        for subdir_name, subdir_path in [
            ('all', self.all_tools_dir),
            ('collections', self.collections_dir),
            ('topics', self.topics_dir),
            ('queries', self.queries_dir)
        ]:
            if subdir_path.exists():
                json_files = list(subdir_path.glob("*.json"))
                info['subdirectories'][subdir_name] = {
                    'path': str(subdir_path),
                    'tool_count': len(json_files),
                    'exists': True
                }
            else:
                info['subdirectories'][subdir_name] = {
                    'path': str(subdir_path),
                    'tool_count': 0,
                    'exists': False
                }
        
        return info
    
    def clear_tools(self, subdirectory: str = "all") -> int:
        """
        Clear all tools from a subdirectory.
        
        Args:
            subdirectory: Subdirectory to clear
            
        Returns:
            Number of files deleted
        """
        try:
            if subdirectory == "collections":
                target_dir = self.collections_dir
            elif subdirectory == "topics":
                target_dir = self.topics_dir
            elif subdirectory == "queries":
                target_dir = self.queries_dir
            else:
                target_dir = self.all_tools_dir
            
            if not target_dir.exists():
                return 0
            
            json_files = list(target_dir.glob("*.json"))
            deleted_count = 0
            
            for json_file in json_files:
                try:
                    json_file.unlink()
                    deleted_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to delete {json_file}: {e}")
            
            self.logger.info(f"Deleted {deleted_count} tools from {target_dir}")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to clear tools from {subdirectory}: {e}")
            return 0
