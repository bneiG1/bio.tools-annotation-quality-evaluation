"""
API client for retrieving tool data from bio.tools registry.
"""

import requests
import time
import logging
from typing import Dict, List, Optional, Union
from urllib.parse import urljoin, urlencode
import json

class BioToolsAPIClient:
    """Client for interacting with the bio.tools API."""
    
    def __init__(self, base_url: str = "https://bio.tools/api/tool/?format=json",
                 timeout: int = 30, retry_attempts: int = 3,
                 delay_between_requests: float = 1.0):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the bio.tools API
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            delay_between_requests: Delay between requests in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.delay = delay_between_requests
        self.session = requests.Session()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'bio.tools-quality-evaluation/1.0',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the bio.tools API with retry logic.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.RequestException: If request fails after all retries
        """
        url = urljoin(self.base_url, endpoint)
        
        # Ensure we get JSON format
        if params is None:
            params = {}
        params['format'] = 'json'
        
        for attempt in range(self.retry_attempts):
            try:
                self.logger.debug(f"Making request to {url} (attempt {attempt + 1})")
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                # Add delay between requests to be respectful
                time.sleep(self.delay)
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.retry_attempts - 1:
                    # Re-raise the exception on final attempt
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # This should never be reached due to the raise above, but satisfy type checker
        raise requests.exceptions.RequestException("All retry attempts failed")
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict]:
        """
        Retrieve a single tool by its biotoolsID.
        
        Args:
            tool_id: The biotoolsID of the tool
            
        Returns:
            Tool data as dictionary or None if not found
        """
        try:
            return self._make_request(f"{tool_id}/")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve tool {tool_id}: {e}")
            return None
    
    def get_tools_by_collection(self, collection: str, limit: int = 100,
                               page: int = 1) -> List[Dict]:
        """
        Retrieve tools from a specific collection.
        
        Args:
            collection: Collection name (e.g., 'proteomics')
            limit: Maximum number of tools to retrieve
            page: Page number for pagination
            
        Returns:
            List of tool dictionaries
        """
        # Use bio.tools API page size (50 per page)
        page_size = 50
        params = {
            'collection': collection,
            'page_size': page_size
        }
        
        tools = []
        current_page = page
        
        while len(tools) < limit:
            params['page'] = current_page
            try:
                response = self._make_request("", params)
                
                if 'list' not in response:
                    self.logger.warning(f"No 'list' key in response: {response}")
                    break
                
                page_tools = response['list']
                if not page_tools:
                    self.logger.info(f"No more tools available for collection '{collection}', stopping at page {current_page}")
                    break
                
                tools.extend(page_tools)
                self.logger.info(f"Retrieved {len(tools)} tools so far for collection '{collection}'... (page {current_page}, got {len(page_tools)} tools this page)")
                
                # Check if we have more pages available
                total_count = response.get('count', 0)
                if total_count > 0:
                    self.logger.info(f"Total tools available for collection '{collection}': {total_count}")
                
                # Continue to next page if we haven't hit our limit and there might be more data
                if len(tools) >= total_count:
                    self.logger.info(f"Retrieved all available tools for collection '{collection}' ({len(tools)})")
                    break
                
                current_page += 1
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to retrieve tools from collection {collection}: {e}")
                break
        
        final_tools = tools[:limit]
        self.logger.info(f"Returning {len(final_tools)} tools for collection '{collection}' (requested limit: {limit})")
        return final_tools
    
    def get_tools_by_topic(self, topic: str, limit: int = 100) -> List[Dict]:
        """
        Retrieve tools by topic.
        
        Args:
            topic: Topic name (e.g., 'Proteomics')
            limit: Maximum number of tools to retrieve
            
        Returns:
            List of tool dictionaries
        """
        # Use bio.tools API page size (50 per page)
        page_size = 50
        params = {
            'topic': topic,
            'page_size': page_size
        }
        
        tools = []
        page = 1
        
        while len(tools) < limit:
            params['page'] = page
            try:
                response = self._make_request("", params)
                
                if 'list' not in response:
                    self.logger.warning(f"No 'list' key in response: {response}")
                    break
                
                page_tools = response['list']
                if not page_tools:
                    self.logger.info(f"No more tools available for topic '{topic}', stopping at page {page}")
                    break
                
                tools.extend(page_tools)
                self.logger.info(f"Retrieved {len(tools)} tools so far for topic '{topic}'... (page {page}, got {len(page_tools)} tools this page)")
                
                # Check if we have more pages available
                total_count = response.get('count', 0)
                if total_count > 0:
                    self.logger.info(f"Total tools available for topic '{topic}': {total_count}")
                
                # Continue to next page if we haven't hit our limit and there might be more data
                if len(tools) >= total_count:
                    self.logger.info(f"Retrieved all available tools for topic '{topic}' ({len(tools)})")
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to retrieve tools by topic {topic}: {e}")
                break
        
        final_tools = tools[:limit]
        self.logger.info(f"Returning {len(final_tools)} tools for topic '{topic}' (requested limit: {limit})")
        return final_tools
    
    def search_tools(self, query: str, limit: int = 100) -> List[Dict]:
        """
        Search for tools using a query string.
        
        Args:
            query: Search query
            limit: Maximum number of tools to retrieve
            
        Returns:
            List of tool dictionaries
        """
        # Use bio.tools API page size (50 per page)
        page_size = 50
        params = {
            'q': query,
            'page_size': page_size
        }
        
        tools = []
        page = 1
        
        while len(tools) < limit:
            params['page'] = page
            try:
                response = self._make_request("", params)
                
                if 'list' not in response:
                    self.logger.warning(f"No 'list' key in response: {response}")
                    break
                
                page_tools = response['list']
                if not page_tools:
                    self.logger.info(f"No more tools available for query '{query}', stopping at page {page}")
                    break
                
                tools.extend(page_tools)
                self.logger.info(f"Retrieved {len(tools)} tools so far for query '{query}'... (page {page}, got {len(page_tools)} tools this page)")
                
                # Check if we have more pages available
                total_count = response.get('count', 0)
                if total_count > 0:
                    self.logger.info(f"Total tools available for query '{query}': {total_count}")
                
                # Continue to next page if we haven't hit our limit and there might be more data
                if len(tools) >= total_count:
                    self.logger.info(f"Retrieved all available tools for query '{query}' ({len(tools)})")
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to search tools with query '{query}': {e}")
                break
        
        final_tools = tools[:limit]
        self.logger.info(f"Returning {len(final_tools)} tools for query '{query}' (requested limit: {limit})")
        return final_tools
    
    def get_all_tools(self, limit: int = 1000) -> List[Dict]:
        """
        Retrieve all tools from the registry.
        
        Args:
            limit: Maximum number of tools to retrieve
            
        Returns:
            List of tool dictionaries
        """
        # Start with API's maximum page size - bio.tools API returns 50 per page
        page_size = 50
        params = {'page_size': page_size}
        
        tools = []
        page = 1
        
        while len(tools) < limit:
            params['page'] = page
            try:
                response = self._make_request("", params)
                
                if 'list' not in response:
                    self.logger.warning(f"No 'list' key in response: {response}")
                    break
                
                page_tools = response['list']
                if not page_tools:
                    self.logger.info(f"No more tools available, stopping at page {page}")
                    break
                
                tools.extend(page_tools)
                self.logger.info(f"Retrieved {len(tools)} tools so far... (page {page}, got {len(page_tools)} tools this page)")
                
                # Check if we have more pages available
                total_count = response.get('count', 0)
                if total_count > 0:
                    self.logger.info(f"Total tools available in registry: {total_count}")
                
                # Continue to next page if we haven't hit our limit and there might be more data
                if len(tools) >= total_count:
                    self.logger.info(f"Retrieved all available tools ({len(tools)})")
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Failed to retrieve all tools: {e}")
                break
        
        final_tools = tools[:limit]
        self.logger.info(f"Returning {len(final_tools)} tools (requested limit: {limit})")
        return final_tools
    
    def get_tool_statistics(self) -> Dict:
        """
        Get basic statistics about the bio.tools registry.
        
        Returns:
            Dictionary containing registry statistics
        """
        try:
            response = self._make_request("stats/")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve tool statistics: {e}")
            return {}
    
    def save_tools_to_file(self, tools: List[Dict], filename: str):
        """
        Save tools data to a JSON file.
        
        Args:
            tools: List of tool dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(tools, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(tools)} tools to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save tools to file: {e}")
    
    def load_tools_from_file(self, filename: str) -> List[Dict]:
        """
        Load tools data from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            List of tool dictionaries
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                tools = json.load(f)
            self.logger.info(f"Loaded {len(tools)} tools from {filename}")
            return tools
        except Exception as e:
            self.logger.error(f"Failed to load tools from file: {e}")
            return []
