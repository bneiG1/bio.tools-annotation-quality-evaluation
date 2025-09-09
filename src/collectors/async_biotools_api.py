"""
Unified Bio.tools API Client

Enhanced API client with support for both synchronous and asynchronous operations,
concurrent fetching, batch operations, and efficient pipeline processing.
"""

import asyncio
import aiohttp
import time
import json
import logging
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Union, AsyncIterator, Callable, Any, TYPE_CHECKING
from urllib.parse import urljoin, urlencode
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..utils.parallel_config import ParallelProcessingConfig
else:
    try:
        from ..utils.parallel_config import ParallelProcessingConfig
    except ImportError:
        # Fallback if parallel config is not available
        class ParallelProcessingConfig:
            def __init__(self):
                self.max_concurrent_api_requests = 5
                self.api_rate_limit_delay = 0.1
                self.api_timeout = 30
                self.analysis_batch_size = 10
                self.pipeline_buffer_size = 100
                self.enable_pipeline_mode = True
            
            @classmethod
            def create_default(cls):
                return cls()

logger = logging.getLogger(__name__)


@dataclass
class FetchResult:
    """Result of a tool fetch operation."""
    tool_id: str
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    fetch_time: float = 0.0


class AsyncBioToolsAPIClient:
    """
    Async bio.tools API client for concurrent operations.
    
    Provides efficient batch fetching, rate limiting, and caching
    while respecting API constraints.
    """
    
    BASE_URL = "https://bio.tools/api/"
    TOOLS_ENDPOINT = "tool/"
    
    def __init__(
        self,
        config: Optional[ParallelProcessingConfig] = None,
        cache_dir: Optional[Union[str, Path]] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the async API client.
        
        Args:
            config: Parallel processing configuration
            cache_dir: Directory for caching responses
            session: Existing aiohttp session (optional)
        """
        self.config = config or ParallelProcessingConfig.create_default()
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._session = session
        self._session_owned = session is None
        self._rate_limiter = asyncio.Semaphore(self.config.max_concurrent_api_requests)
        self._last_request_time = 0.0
        
        # Create cache directory if specified
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def __aenter__(self):
        """Async context manager entry."""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.api_timeout)
            connector = aiohttp.TCPConnector(limit=self.config.max_concurrent_api_requests * 2)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={'User-Agent': 'bio.tools-quality-analyzer/1.0'}
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session_owned and self._session:
            await self._session.close()
    
    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.config.api_rate_limit_delay:
            sleep_time = self.config.api_rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _get_cache_path(self, tool_id: str) -> Optional[Path]:
        """Get cache file path for a tool."""
        if not self.cache_dir:
            return None
        
        # Sanitize tool ID for filename
        safe_id = tool_id.replace('/', '_').replace('\\', '_')
        return self.cache_dir / f"tool_{safe_id}.json"
    
    async def _load_from_cache(self, cache_path: Path) -> Optional[Dict]:
        """Load data from cache file."""
        try:
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.debug(f"Loaded from cache: {cache_path}")
                return data
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_path}: {e}")
        return None
    
    async def _save_to_cache(self, cache_path: Path, data: Dict) -> None:
        """Save data to cache file."""
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved to cache: {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_path}: {e}")
    
    async def fetch_tool(self, tool_id: str) -> FetchResult:
        """
        Fetch a single tool with rate limiting and caching.
        
        Args:
            tool_id: Bio.tools tool identifier
            
        Returns:
            FetchResult with tool data or error information
        """
        start_time = time.time()
        
        # Check cache first
        cache_path = self._get_cache_path(tool_id)
        if cache_path:
            cached_data = await self._load_from_cache(cache_path)
            if cached_data:
                return FetchResult(
                    tool_id=tool_id,
                    success=True,
                    data=cached_data,
                    fetch_time=time.time() - start_time
                )
        
        # Fetch from API with rate limiting
        async with self._rate_limiter:
            await self._rate_limit()
            
            if not self._session:
                raise RuntimeError("Client not initialized. Use 'async with' context manager.")
            
            url = urljoin(self.BASE_URL, f"{self.TOOLS_ENDPOINT}{tool_id}/")
            
            try:
                async with self._session.get(url, params={'format': 'json'}) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Save to cache
                        if cache_path:
                            await self._save_to_cache(cache_path, data)
                        
                        return FetchResult(
                            tool_id=tool_id,
                            success=True,
                            data=data,
                            fetch_time=time.time() - start_time
                        )
                    else:
                        error_msg = f"HTTP {response.status}: {response.reason}"
                        return FetchResult(
                            tool_id=tool_id,
                            success=False,
                            error=error_msg,
                            fetch_time=time.time() - start_time
                        )
                        
            except asyncio.TimeoutError:
                return FetchResult(
                    tool_id=tool_id,
                    success=False,
                    error="Request timeout",
                    fetch_time=time.time() - start_time
                )
            except Exception as e:
                return FetchResult(
                    tool_id=tool_id,
                    success=False,
                    error=str(e),
                    fetch_time=time.time() - start_time
                )
    
    async def fetch_tools_batch(
        self, 
        tool_ids: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[FetchResult]:
        """
        Fetch multiple tools concurrently.
        
        Args:
            tool_ids: List of tool identifiers to fetch
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of FetchResult objects
        """
        logger.info(f"Fetching {len(tool_ids)} tools concurrently")
        
        async def fetch_with_progress(tool_id: str, index: int) -> FetchResult:
            result = await self.fetch_tool(tool_id)
            if progress_callback:
                progress_callback(index + 1, len(tool_ids))
            return result
        
        # Create tasks for all tools
        tasks = [
            fetch_with_progress(tool_id, i) 
            for i, tool_id in enumerate(tool_ids)
        ]
        
        # Execute with limited concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        fetch_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                fetch_results.append(FetchResult(
                    tool_id=tool_ids[i],
                    success=False,
                    error=str(result)
                ))
            else:
                fetch_results.append(result)
        
        successful = sum(1 for r in fetch_results if r.success)
        logger.info(f"Successfully fetched {successful}/{len(tool_ids)} tools")
        
        return fetch_results
    
    async def fetch_tools_stream(
        self,
        tool_ids: List[str],
        batch_size: Optional[int] = None
    ) -> AsyncIterator[FetchResult]:
        """
        Fetch tools as a stream, yielding results as they complete.
        
        Args:
            tool_ids: List of tool identifiers to fetch
            batch_size: Size of batches to process (defaults to config batch size)
            
        Yields:
            FetchResult objects as they complete
        """
        batch_size = batch_size or self.config.analysis_batch_size
        
        for i in range(0, len(tool_ids), batch_size):
            batch = tool_ids[i:i + batch_size]
            batch_results = await self.fetch_tools_batch(batch)
            
            for result in batch_results:
                yield result
    
    async def search_tools(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        format_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for tools using bio.tools API.
        
        Args:
            query: Search query string
            domain: Scientific domain filter
            format_filter: Data format filter
            limit: Maximum number of results
            
        Returns:
            List of tool metadata dictionaries
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        # Build search parameters
        params = {'format': 'json'}
        if query:
            params['q'] = query
        if domain:
            params['domain'] = domain
        if format_filter:
            params['format'] = format_filter
        
        url = urljoin(self.BASE_URL, self.TOOLS_ENDPOINT)
        
        try:
            async with self._session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tools = data.get('list', [])
                    
                    # Apply limit if specified
                    if limit and len(tools) > limit:
                        tools = tools[:limit]
                    
                    logger.info(f"Found {len(tools)} tools matching search criteria")
                    return tools
                else:
                    logger.error(f"Search failed: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def get_stats(self) -> Optional[Dict]:
        """Get bio.tools registry statistics."""
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        url = urljoin(self.BASE_URL, "stats")
        
        try:
            async with self._session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Stats request failed: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Stats request error: {e}")
            return None
    
    async def fetch_all_tools(self, batch_size: int = 1000) -> List[Dict]:
        """
        Fetch all tools from bio.tools using pagination.
        
        Args:
            batch_size: Number of tools to fetch per page
            
        Returns:
            List of all tool metadata dictionaries
        """
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        logger.info("Starting to fetch all bio.tools entries...")
        all_tools = []
        page = 1
        
        while True:
            # Check cache for this page
            cache_key = f"all_tools_page_{page}_{batch_size}"
            cache_path = self._get_cache_path_for_key(cache_key) if self.cache_dir else None
            
            if cache_path and cache_path.exists():
                try:
                    with open(cache_path, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    # Check if cache is recent (within 24 hours)
                    cache_time = cached_data.get('cached_at', 0)
                    if time.time() - cache_time <= 24 * 3600:  # 24 hours
                        page_tools = cached_data.get('data', {}).get('list', [])
                        logger.info(f"Loaded page {page} from cache ({len(page_tools)} tools)")
                        
                        if page_tools:
                            all_tools.extend(page_tools)
                            if len(page_tools) < batch_size:
                                logger.info(f"Reached last page from cache (page {page})")
                                break
                            page += 1
                            continue
                except Exception as e:
                    logger.warning(f"Failed to load cache for page {page}: {e}")
            
            # Fetch page from API with rate limiting
            await self._rate_limit()
            url = urljoin(self.BASE_URL, self.TOOLS_ENDPOINT)
            params = {
                'format': 'json',
                'page': page,
                'page_size': batch_size
            }
            
            try:
                timeout = aiohttp.ClientTimeout(total=60)
                async with self._session.get(url, params=params, timeout=timeout) as response:
                    if response.status == 200:
                        page_data = await response.json()
                        page_tools = page_data.get('list', [])
                        
                        # Save to cache
                        if cache_path:
                            try:
                                cached_data = {
                                    'cached_at': time.time(),
                                    'data': page_data
                                }
                                with open(cache_path, 'w', encoding='utf-8') as f:
                                    json.dump(cached_data, f, indent=2, ensure_ascii=False)
                            except Exception as e:
                                logger.warning(f"Failed to save cache for page {page}: {e}")
                        
                        logger.info(f"Fetched page {page} from API ({len(page_tools)} tools)")
                        
                        if page_tools:
                            all_tools.extend(page_tools)
                            
                            # Check if we got fewer tools than requested (last page)
                            if len(page_tools) < batch_size:
                                logger.info(f"Reached last page (page {page})")
                                break
                                
                            page += 1
                        else:
                            logger.info(f"No more tools found (page {page})")
                            break
                    else:
                        logger.error(f"Failed to fetch page {page}: HTTP {response.status}")
                        break
                        
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        logger.info(f"Successfully fetched {len(all_tools)} total tools from bio.tools")
        return all_tools
    
    def _get_cache_path_for_key(self, cache_key: str) -> Optional[Path]:
        """Get cache file path for a given key."""
        if not self.cache_dir:
            return None
        # Clean the cache key for filename
        safe_key = "".join(c for c in cache_key if c.isalnum() or c in ('_', '-', '.'))
        return self.cache_dir / f"{safe_key}.json"


class UnifiedBioToolsAPIClient:
    """
    Synchronous wrapper around the async bio.tools API client.
    
    Provides a synchronous interface for tools that need simple blocking operations.
    """
    
    def __init__(self, cache_dir: Optional[Union[str, Path]] = None, rate_limit_delay: float = 0.1):
        """
        Initialize the synchronous API client.
        
        Args:
            cache_dir: Directory for caching responses
            rate_limit_delay: Delay between requests in seconds
        """
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.rate_limit_delay = rate_limit_delay
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'bio.tools-quality-analyzer/1.0'})
        self._last_request_time = 0.0
        
        # Create cache directory if specified
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._session.close()
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _get_cache_path(self, cache_key: str) -> Optional[Path]:
        """Get cache file path for a given key."""
        if not self.cache_dir:
            return None
        safe_key = "".join(c for c in cache_key if c.isalnum() or c in ('_', '-', '.'))
        return self.cache_dir / f"{safe_key}.json"
    
    def _create_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Create a cache key for an API request."""
        cache_data = {
            'endpoint': endpoint,
            'params': params or {}
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load data from cache if available and recent."""
        cache_path = self._get_cache_path(cache_key)
        if not cache_path or not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is recent (within 24 hours)
            cache_time = cached_data.get('cached_at', 0)
            if time.time() - cache_time > 24 * 3600:  # 24 hours
                logger.debug(f"Cache expired for key: {cache_key}")
                return None
            
            logger.debug(f"Cache hit for key: {cache_key}")
            return cached_data.get('data')
            
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_key}: {e}")
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save data to cache."""
        cache_path = self._get_cache_path(cache_key)
        if not cache_path:
            return
        
        try:
            cached_data = {
                'cached_at': time.time(),
                'data': data
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_key}: {e}")
    
    def fetch_tool(self, tool_id: str) -> Optional[Dict]:
        """
        Fetch a single tool by ID.
        
        Args:
            tool_id: The bio.tools ID of the tool
            
        Returns:
            Tool metadata dictionary or None if not found
        """
        # Check cache first
        cache_key = self._create_cache_key(f"tool/{tool_id}")
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Make API request
        self._rate_limit()
        url = urljoin(AsyncBioToolsAPIClient.BASE_URL, f"{AsyncBioToolsAPIClient.TOOLS_ENDPOINT}{tool_id}/")
        
        try:
            response = self._session.get(url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self._save_to_cache(cache_key, data)
                logger.debug(f"Fetched tool: {tool_id}")
                return data
            elif response.status_code == 404:
                logger.warning(f"Tool not found: {tool_id}")
                return None
            else:
                logger.error(f"Failed to fetch tool {tool_id}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching tool {tool_id}: {e}")
            return None
    
    def search_tools(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        format_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Search for tools using bio.tools API with pagination support for large requests.
        
        Args:
            query: Search query string
            domain: Scientific domain filter
            format_filter: Data format filter
            limit: Maximum number of results
            
        Returns:
            List of tool metadata dictionaries
        """
        # If requesting many tools or no limit, use pagination
        # Note: bio.tools API has a fixed page size of 50, so use pagination for requests > 50
        if limit is None or limit > 50:
            return self._search_with_pagination(query, domain, format_filter, limit)
        
        # For small requests, use single page search
        return self._search_single_page(query, domain, format_filter, limit)
    
    def _search_single_page(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        format_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Search tools using a single API request (original implementation)."""
        # Build search parameters
        params = {'format': 'json'}
        if query:
            params['q'] = query
        if domain:
            params['domain'] = domain
        if format_filter:
            params['format'] = format_filter
        
        # Check cache first
        cache_key = self._create_cache_key("search", params)
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            tools = cached_data.get('list', [])
            if limit and len(tools) > limit:
                tools = tools[:limit]
            logger.info(f"Found {len(tools)} tools from cache")
            return tools
        
        # Make API request
        self._rate_limit()
        url = urljoin(AsyncBioToolsAPIClient.BASE_URL, AsyncBioToolsAPIClient.TOOLS_ENDPOINT)
        
        try:
            response = self._session.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self._save_to_cache(cache_key, data)
                
                tools = data.get('list', [])
                
                # Apply limit if specified
                if limit and len(tools) > limit:
                    tools = tools[:limit]
                
                logger.info(f"Found {len(tools)} tools matching search criteria")
                return tools
            else:
                logger.error(f"Search failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in search: {e}")
            return []
    
    def _search_with_pagination(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        format_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Search tools using pagination for large requests."""
        logger.info(f"Using paginated search for large request (limit: {limit})")
        
        all_tools = []
        page = 1
        # Note: bio.tools API has a fixed page size of 50, doesn't respect page_size parameter
        page_size = 50  
        
        # Build base search parameters
        base_params = {'format': 'json'}
        if query:
            base_params['q'] = query
        if domain:
            base_params['domain'] = domain
        if format_filter:
            base_params['format'] = format_filter
        
        while True:
            # Add pagination parameters
            params = base_params.copy()
            params['page'] = str(page)
            # Note: bio.tools ignores page_size, but we'll include it anyway
            
            # Check cache for this page
            cache_key = self._create_cache_key("search_paginated", params)
            cached_data = self._load_from_cache(cache_key)
            
            if cached_data:
                page_tools = cached_data.get('list', [])
                has_next = bool(cached_data.get('next'))
                logger.info(f"Loaded search page {page} from cache ({len(page_tools)} tools)")
            else:
                # Fetch page from API
                self._rate_limit()
                url = urljoin(AsyncBioToolsAPIClient.BASE_URL, AsyncBioToolsAPIClient.TOOLS_ENDPOINT)
                
                try:
                    response = self._session.get(url, params=params, timeout=30)
                    if response.status_code == 200:
                        page_data = response.json()
                        page_tools = page_data.get('list', [])
                        has_next = bool(page_data.get('next'))  # Check if there's a next page
                        
                        # Save to cache
                        self._save_to_cache(cache_key, page_data)
                        
                        logger.info(f"Fetched search page {page} from API ({len(page_tools)} tools, has_next: {has_next})")
                    else:
                        logger.error(f"Failed to fetch search page {page}: HTTP {response.status_code}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching search page {page}: {e}")
                    break
            
            # Add tools to collection
            if page_tools:
                all_tools.extend(page_tools)
                
                # Check if we've reached the requested limit
                if limit and len(all_tools) >= limit:
                    all_tools = all_tools[:limit]
                    logger.info(f"Reached requested limit of {limit} tools")
                    break
                
                # Check if there's a next page (use API response, not page size)
                if not has_next:
                    logger.info(f"No more pages available (last page: {page})")
                    break
                    
                page += 1
            else:
                logger.info(f"No tools found on page {page}")
                break
        
        logger.info(f"Successfully found {len(all_tools)} tools matching search criteria")
        return all_tools
    
    def fetch_all_tools(self, batch_size: int = 1000) -> List[Dict]:
        """
        Fetch all tools from bio.tools using pagination.
        
        Args:
            batch_size: Number of tools to fetch per page
            
        Returns:
            List of all tool metadata dictionaries
        """
        logger.info("Starting to fetch all bio.tools entries...")
        all_tools = []
        page = 1
        
        while True:
            # Check cache for this page
            cache_key = self._create_cache_key("all_tools", {"page": page, "page_size": batch_size})
            cached_data = self._load_from_cache(cache_key)
            
            if cached_data:
                page_tools = cached_data.get('list', [])
                logger.info(f"Loaded page {page} from cache ({len(page_tools)} tools)")
            else:
                # Fetch page from API
                self._rate_limit()
                url = urljoin(AsyncBioToolsAPIClient.BASE_URL, AsyncBioToolsAPIClient.TOOLS_ENDPOINT)
                params = {
                    'format': 'json',
                    'page': page,
                    'page_size': batch_size
                }
                
                try:
                    response = self._session.get(url, params=params, timeout=60)
                    if response.status_code == 200:
                        page_data = response.json()
                        page_tools = page_data.get('list', [])
                        
                        # Save to cache
                        self._save_to_cache(cache_key, page_data)
                        
                        logger.info(f"Fetched page {page} from API ({len(page_tools)} tools)")
                    else:
                        logger.error(f"Failed to fetch page {page}: HTTP {response.status_code}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error fetching page {page}: {e}")
                    break
            
            # Add tools to collection
            if page_tools:
                all_tools.extend(page_tools)
                
                # Check if we got fewer tools than the API's page size (50) - indicates last page
                # Note: bio.tools API has a fixed page size of 50, don't use batch_size for this check
                if len(page_tools) < 50:
                    logger.info(f"Reached last page (page {page})")
                    break
                
                # Check if we have enough tools for the requested batch_size
                if len(all_tools) >= batch_size:
                    logger.info(f"Reached requested batch size of {batch_size} tools")
                    all_tools = all_tools[:batch_size]  # Trim to exact size
                    break
                    
                page += 1
            else:
                logger.info(f"No more tools found (page {page})")
                break
        
        logger.info(f"Successfully fetched {len(all_tools)} total tools from bio.tools")
        return all_tools

    def save_individual_raw_tools(self, tools_data: List[Dict], output_dir: Path, timestamp: Optional[str] = None) -> Path:
        """
        Save individual raw tool data with tool names as filenames.
        
        Args:
            tools_data: List of tool data dictionaries
            output_dir: Directory to save individual files
            timestamp: Optional timestamp string for directory naming (unused now)
            
        Returns:
            Path to the directory containing individual files
        """
        individual_dir = output_dir / "individual_tools"
        individual_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving {len(tools_data)} individual raw tool files to: {individual_dir}")
        
        for i, tool_data in enumerate(tools_data, 1):
            tool_id = tool_data.get('biotoolsID', f'unknown_{i}')
            tool_name = tool_data.get('name', tool_id)
            
            # Create filename from tool name or tool_id
            display_name = tool_name if tool_name and tool_name != tool_id else tool_id
            
            # Clean name for filename - more aggressive cleaning for tool names
            safe_name = "".join(c for c in display_name if c.isalnum() or c in ('_', '-', '.', ' ')).strip()
            safe_name = safe_name.replace(' ', '_')  # Replace spaces with underscores
            
            # Fallback to tool_id if name cleaning results in empty string
            if not safe_name:
                safe_name = "".join(c for c in tool_id if c.isalnum() or c in ('_', '-', '.')).rstrip()
                
            tool_filename = f"{safe_name}.json"
            tool_filepath = individual_dir / tool_filename
            
            # Save individual tool data
            with open(tool_filepath, 'w', encoding='utf-8') as f:
                json.dump(tool_data, f, indent=2, ensure_ascii=False)
            
            if i % 100 == 0:
                logger.info(f"Saved {i}/{len(tools_data)} individual raw tool files")
        
        logger.info(f"All individual raw tool files saved to: {individual_dir}")
        return individual_dir


def create_async_client(
    config: Optional[ParallelProcessingConfig] = None,
    cache_dir: Optional[Union[str, Path]] = None
) -> AsyncBioToolsAPIClient:
    """
    Factory function to create an async bio.tools API client.
    
    Args:
        config: Parallel processing configuration
        cache_dir: Directory for caching responses
        
    Returns:
        Configured AsyncBioToolsAPIClient
    """
    return AsyncBioToolsAPIClient(config=config, cache_dir=cache_dir)


# Export the classes and functions that the CLI expects
__all__ = [
    'AsyncBioToolsAPIClient',
    'UnifiedBioToolsAPIClient', 
    'FetchResult',
    'create_async_client'
]
