"""
Bio.tools API client for fetching tool metadata.

This module provides a client for interacting with the bio.tools API
to fetch tool information and metadata.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Iterator, Union
from urllib.parse import urljoin, urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logger = logging.getLogger(__name__)


class BioToolsAPIClient:
    """
    Client for interacting with the bio.tools API.
    
    Provides methods to fetch tool information with built-in rate limiting,
    caching, and error handling.
    """
    
    BASE_URL = "https://bio.tools/api/"
    TOOLS_ENDPOINT = "tool/"
    STATS_ENDPOINT = "stats"
    
    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        rate_limit_delay: float = 1.0,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the bio.tools API client.
        
        Args:
            cache_dir: Directory to store cached responses
            rate_limit_delay: Delay between API requests in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.last_request_time = 0
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Create cache directory if specified
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_path(self, endpoint: str, params: Dict) -> Optional[Path]:
        """Generate cache file path for given endpoint and parameters."""
        if not self.cache_dir:
            return None
        
        # Create a unique filename based on endpoint and params
        import hashlib
        
        # For single tools, use simple naming
        if endpoint.startswith(self.TOOLS_ENDPOINT) and "/" in endpoint:
            # Extract tool ID from endpoint like "tool/blast/" -> "blast"
            tool_id = endpoint.replace(self.TOOLS_ENDPOINT, "").rstrip("/")
            if tool_id and not "/" in tool_id:  # Simple tool ID, not a complex path
                cache_filename = f"tool_{tool_id}.json"
                return self.cache_dir / cache_filename
        
        # For searches and other endpoints, use hash-based naming
        param_str = urlencode(sorted(params.items())) if params else ""
        cache_key = f"{endpoint}_{param_str}"
        cache_hash = hashlib.md5(cache_key.encode()).hexdigest()
        cache_filename = f"search_{cache_hash}.json"
        
        return self.cache_dir / cache_filename
    
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load response from cache if it exists and is not too old."""
        if cache_path and cache_path.exists():
            try:
                # Check file age for search results (expire after 24 hours)
                # Individual tools are cached indefinitely unless manually cleared
                import time
                file_age = time.time() - cache_path.stat().st_mtime
                
                # If it's a search result, check age (24 hours = 86400 seconds)
                if cache_path.name.startswith("search_") and file_age > 86400:
                    logger.debug(f"Cache file {cache_path} is too old (search result), ignoring")
                    return None
                
                with open(cache_path, 'r', encoding='utf-8') as f:
                    logger.debug(f"Loading from cache: {cache_path}")
                    cached_data = json.load(f)
                    
                    # Add cache metadata
                    cached_data['_cache_info'] = {
                        'cached_at': cache_path.stat().st_mtime,
                        'cache_file': str(cache_path),
                        'age_hours': file_age / 3600
                    }
                    
                    return cached_data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache file {cache_path}: {e}")
        return None
    
    def _save_to_cache(self, cache_path: Path, data: Dict) -> None:
        """Save response to cache with metadata."""
        if cache_path:
            try:
                # Add cache metadata to the data before saving
                data_to_save = data.copy()
                data_to_save['_cache_info'] = {
                    'cached_at': time.time(),
                    'cache_file': str(cache_path),
                    'age_hours': 0
                }
                
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=2, ensure_ascii=False)
                logger.info(f"Saved to cache: {cache_path}")
            except IOError as e:
                logger.warning(f"Failed to save cache file {cache_path}: {e}")
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        use_cache: bool = True
    ) -> Dict:
        """
        Make a request to the bio.tools API.
        
        Args:
            endpoint: API endpoint (relative to base URL)
            params: Query parameters
            use_cache: Whether to use caching
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: If the request fails
        """
        params = params or {}
        cache_path = self._get_cache_path(endpoint, params) if use_cache else None
        
        # Try to load from cache first
        if cache_path:
            cached_data = self._load_from_cache(cache_path)
            if cached_data is not None:
                return cached_data
        
        # Make API request
        self._rate_limit()
        url = urljoin(self.BASE_URL, endpoint)
        
        logger.info(f"Making request to {url} with params: {params}")
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout,
                headers={'Accept': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Save to cache
            if cache_path:
                self._save_to_cache(cache_path, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise
    
    def get_tool(self, biotools_id: str, format: str = "json") -> Dict:
        """
        Get details for a specific tool.
        
        Args:
            biotools_id: The bio.tools ID of the tool
            format: Response format (json, xml, api)
            
        Returns:
            Tool data as dictionary
        """
        endpoint = f"{self.TOOLS_ENDPOINT}{biotools_id}/"
        params = {"format": format}
        return self._make_request(endpoint, params)
    
    def list_tools(
        self,
        page: int = 1,
        format: str = "json",
        query: Optional[str] = None,
        sort: str = "lastUpdate",
        order: str = "desc",
        **filters
    ) -> Dict:
        """
        List tools with optional filtering and pagination.
        
        Args:
            page: Page number for pagination
            format: Response format
            query: Search query
            sort: Sort field (lastUpdate, additionDate, name, affiliation, score)
            order: Sort order (desc, asc)
            **filters: Additional filter parameters
            
        Returns:
            Paginated list of tools
        """
        params = {
            "page": page,
            "format": format,
            "sort": sort,
            "ord": order
        }
        
        if query:
            params["q"] = query
        
        # Add filter parameters
        params.update(filters)
        
        return self._make_request(self.TOOLS_ENDPOINT, params)

    def search_by_collection(
        self,
        collection_id: str,
        page: int = 1,
        format: str = "json",
        sort: str = "lastUpdate",
        order: str = "desc",
        size: Optional[int] = None,
        **filters
    ) -> Dict:
        """
        Search tools by collection ID.
        
        Args:
            collection_id: The collection ID to search for
            page: Page number for pagination
            format: Response format
            sort: Sort field (lastUpdate, additionDate, name, affiliation, score)
            order: Sort order (desc, asc)
            size: Maximum number of tools to return (will fetch multiple pages if needed)
            **filters: Additional filter parameters
            
        Returns:
            Paginated list of tools in the collection
        """
        params = {
            "page": page,
            "format": format,
            "sort": sort,
            "ord": order,
            "collectionID": collection_id
        }
        
        # Add additional filter parameters
        params.update(filters)
        
        # If size is specified and > 25 (default page size), fetch multiple pages
        if size and size > 25:
            all_tools = []
            current_page = page
            tools_collected = 0
            last_response = None
            
            while tools_collected < size:
                params["page"] = current_page
                last_response = self._make_request(self.TOOLS_ENDPOINT, params)
                
                tools = last_response.get('list', [])
                if not tools:
                    break
                
                # Add tools up to the size limit
                remaining_needed = size - tools_collected
                tools_to_add = tools[:remaining_needed]
                all_tools.extend(tools_to_add)
                tools_collected += len(tools_to_add)
                
                # If we got fewer tools than page size, we've reached the end
                if len(tools) < 25:
                    break
                    
                current_page += 1
            
            # Return response with combined tools
            return {
                'count': last_response.get('count', len(all_tools)) if last_response else len(all_tools),
                'list': all_tools,
                'next': last_response.get('next') if last_response and tools_collected < last_response.get('count', 0) else None,
                'previous': last_response.get('previous') if last_response and page > 1 else None
            }
        else:
            return self._make_request(self.TOOLS_ENDPOINT, params)

    def clear_cache(self, tool_id: Optional[str] = None) -> bool:
        """
        Clear cached data.
        
        Args:
            tool_id: If provided, clear cache for specific tool. Otherwise clear all cache.
            
        Returns:
            True if cache was cleared successfully
        """
        if not self.cache_dir or not self.cache_dir.exists():
            return True
        
        try:
            if tool_id:
                # Clear specific tool cache
                cache_file = self.cache_dir / f"tool_{tool_id}.json"
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info(f"Cleared cache for tool: {tool_id}")
                return True
            else:
                # Clear all cache files
                import shutil
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info("Cleared all cache files")
                return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """
        Get statistics about cached data.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_dir or not self.cache_dir.exists():
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'tool_files': 0,
                'search_files': 0,
                'oldest_file': None,
                'newest_file': None
            }
        
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            
            total_size = sum(f.stat().st_size for f in cache_files)
            tool_files = len([f for f in cache_files if f.name.startswith("tool_")])
            search_files = len([f for f in cache_files if f.name.startswith("search_")])
            
            if cache_files:
                oldest_file = min(cache_files, key=lambda f: f.stat().st_mtime)
                newest_file = max(cache_files, key=lambda f: f.stat().st_mtime)
                oldest_time = oldest_file.stat().st_mtime
                newest_time = newest_file.stat().st_mtime
            else:
                oldest_file = newest_file = None
                oldest_time = newest_time = None
            
            return {
                'total_files': len(cache_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'tool_files': tool_files,
                'search_files': search_files,
                'oldest_file': oldest_file.name if oldest_file else None,
                'oldest_time': oldest_time,
                'newest_file': newest_file.name if newest_file else None,
                'newest_time': newest_time
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}
    
    def is_tool_cached(self, tool_id: str) -> bool:
        """
        Check if a tool is cached locally.
        
        Args:
            tool_id: The bio.tools ID of the tool
            
        Returns:
            True if tool is cached locally
        """
        if not self.cache_dir:
            return False
        
        cache_file = self.cache_dir / f"tool_{tool_id}.json"
        return cache_file.exists()

