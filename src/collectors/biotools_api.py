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
        param_str = urlencode(sorted(params.items())) if params else ""
        cache_filename = f"{endpoint.replace('/', '_')}_{hash(param_str)}.json"
        return self.cache_dir / cache_filename
    
    def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load response from cache if it exists."""
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    logger.debug(f"Loading from cache: {cache_path}")
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load cache file {cache_path}: {e}")
        return None
    
    def _save_to_cache(self, cache_path: Path, data: Dict) -> None:
        """Save response to cache."""
        if cache_path:
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.debug(f"Saved to cache: {cache_path}")
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
    
    def get_all_tools(
        self,
        batch_size: int = 25,
        max_tools: Optional[int] = None,
        **filters
    ) -> Iterator[Dict]:
        """
        Generator to fetch all tools from bio.tools.
        
        Args:
            batch_size: Number of tools per page
            max_tools: Maximum number of tools to fetch (None for all)
            **filters: Filter parameters
            
        Yields:
            Individual tool dictionaries
        """
        page = 1
        total_fetched = 0
        
        while True:
            try:
                response = self.list_tools(page=page, **filters)
                tools = response.get("list", [])
                
                if not tools:
                    logger.info("No more tools to fetch")
                    break
                
                for tool in tools:
                    if max_tools and total_fetched >= max_tools:
                        return
                    
                    yield tool
                    total_fetched += 1
                
                # Check if we have more pages
                if "next" not in response or not response["next"]:
                    logger.info(f"Reached last page. Total tools fetched: {total_fetched}")
                    break
                
                page += 1
                logger.info(f"Fetched {total_fetched} tools, moving to page {page}")
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
    
    def get_stats(self) -> Dict:
        """
        Get bio.tools registry statistics.
        
        Returns:
            Statistics data
        """
        return self._make_request(self.STATS_ENDPOINT)
    
    def search_tools(
        self,
        query: str,
        max_results: Optional[int] = None,
        **filters
    ) -> List[Dict]:
        """
        Search for tools matching a query.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            **filters: Additional filter parameters
            
        Returns:
            List of matching tools
        """
        tools = []
        
        for tool in self.get_all_tools(query=query, max_tools=max_results, **filters):
            tools.append(tool)
        
        return tools
    
    def get_tools_by_collection(self, collection_id: str) -> List[Dict]:
        """
        Get all tools in a specific collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            List of tools in the collection
        """
        return self.search_tools(query="", collectionID=f'"{collection_id}"')
