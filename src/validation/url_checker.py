"""
URL accessibility checker for bio.tools homepage validation.

This module provides functionality to check if homepage URLs and other links
in bio.tools entries are still accessible and functional.
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple, Set, Any
from urllib.parse import urlparse, urljoin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class URLChecker:
    """URL accessibility checker with retry logic and rate limiting."""
    
    def __init__(self, 
                 timeout: int = 10,
                 max_workers: int = 5,
                 delay_between_requests: float = 0.5,
                 max_retries: int = 2,
                 user_agent: str = "bio.tools-quality-evaluator/1.0"):
        """
        Initialize the URL checker.
        
        Args:
            timeout: Request timeout in seconds
            max_workers: Maximum number of concurrent workers for URL checking
            delay_between_requests: Delay between requests to avoid overwhelming servers
            max_retries: Maximum number of retry attempts for failed requests
            user_agent: User agent string to identify the checker
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.delay = delay_between_requests
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.logger = logging.getLogger(__name__)
        
        # Session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({'User-Agent': self.user_agent})
        
        # Cache for recently checked URLs to avoid duplicate checks
        self._url_cache = {}
        self.cache_ttl = 3600  # Cache results for 1 hour
        
    def check_url(self, url: str, use_head: bool = True) -> Dict[str, Any]:
        """
        Check if a single URL is accessible.
        
        Args:
            url: URL to check
            use_head: Whether to use HEAD request first (faster)
            
        Returns:
            Dict containing check results:
            - is_accessible: bool
            - status_code: int or None
            - response_time: float or None
            - error_message: str or None
            - final_url: str (after redirects)
            - redirect_count: int
        """
        if not url or not isinstance(url, str):
            return {
                'is_accessible': False,
                'status_code': None,
                'response_time': None,
                'error_message': 'Invalid URL',
                'final_url': url,
                'redirect_count': 0
            }
        
        # Clean and validate URL
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check cache first
        cache_key = url
        current_time = time.time()
        if cache_key in self._url_cache:
            cached_result, cache_time = self._url_cache[cache_key]
            if current_time - cache_time < self.cache_ttl:
                self.logger.debug(f"Using cached result for {url}")
                return cached_result
        
        result = {
            'is_accessible': False,
            'status_code': None,
            'response_time': None,
            'error_message': None,
            'final_url': url,
            'redirect_count': 0
        }
        
        start_time = time.time()
        
        try:
            # Parse URL to check if it's valid
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
            
            # Try HEAD request first if enabled (faster)
            response = None
            if use_head:
                try:
                    response = self.session.head(
                        url, 
                        timeout=self.timeout, 
                        allow_redirects=True
                    )
                except requests.exceptions.RequestException:
                    # If HEAD fails, fall back to GET
                    pass
            
            # If HEAD didn't work or wasn't used, try GET
            if response is None:
                response = self.session.get(
                    url, 
                    timeout=self.timeout, 
                    allow_redirects=True,
                    stream=True  # Don't download the full content
                )
                # Close the stream to free up the connection
                response.close()
            
            result['status_code'] = response.status_code
            result['response_time'] = time.time() - start_time
            result['final_url'] = response.url
            result['redirect_count'] = len(response.history)
            
            # Consider 2xx and 3xx status codes as accessible
            result['is_accessible'] = 200 <= response.status_code < 400
            
            if not result['is_accessible']:
                result['error_message'] = f"HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            result['error_message'] = 'Request timeout'
            result['response_time'] = self.timeout
        except requests.exceptions.ConnectionError as e:
            result['error_message'] = f'Connection error: {str(e)}'
            result['response_time'] = time.time() - start_time
        except requests.exceptions.RequestException as e:
            result['error_message'] = f'Request error: {str(e)}'
            result['response_time'] = time.time() - start_time
        except ValueError as e:
            result['error_message'] = str(e)
            result['response_time'] = time.time() - start_time
        except Exception as e:
            result['error_message'] = f'Unexpected error: {str(e)}'
            result['response_time'] = time.time() - start_time
        
        # Cache the result
        self._url_cache[cache_key] = (result, current_time)
        
        return result
    
    def check_urls_batch(self, urls: List[str]) -> Dict[str, Dict]:
        """
        Check multiple URLs concurrently.
        
        Args:
            urls: List of URLs to check
            
        Returns:
            Dict mapping URLs to their check results
        """
        if not urls:
            return {}
        
        results = {}
        unique_urls = list(set(urls))  # Remove duplicates
        
        self.logger.info(f"Checking accessibility of {len(unique_urls)} unique URLs")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all URL checks
            future_to_url = {
                executor.submit(self.check_url, url): url 
                for url in unique_urls
            }
            
            # Process completed checks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results[url] = result
                    
                    if result['is_accessible']:
                        self.logger.debug(f"✓ {url} (HTTP {result['status_code']})")
                    else:
                        self.logger.debug(f"✗ {url} ({result['error_message']})")
                        
                except Exception as e:
                    self.logger.error(f"Error checking {url}: {e}")
                    results[url] = {
                        'is_accessible': False,
                        'status_code': None,
                        'response_time': None,
                        'error_message': f'Check failed: {str(e)}',
                        'final_url': url,
                        'redirect_count': 0
                    }
                
                # Rate limiting
                time.sleep(self.delay)
        
        return results
    
    def extract_urls_from_tool(self, tool_data: Dict) -> List[str]:
        """
        Extract all URLs from a bio.tools entry.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            List of URLs found in the tool data
        """
        urls = []
        
        # Homepage
        if 'homepage' in tool_data and tool_data['homepage']:
            urls.append(tool_data['homepage'])
        
        # Links
        if 'link' in tool_data and tool_data['link']:
            for link in tool_data['link']:
                if isinstance(link, dict) and 'url' in link:
                    urls.append(link['url'])
                elif isinstance(link, str):
                    urls.append(link)
        
        # Downloads
        if 'download' in tool_data and tool_data['download']:
            for download in tool_data['download']:
                if isinstance(download, dict) and 'url' in download:
                    urls.append(download['url'])
                elif isinstance(download, str):
                    urls.append(download)
        
        # Documentation
        if 'documentation' in tool_data and tool_data['documentation']:
            for doc in tool_data['documentation']:
                if isinstance(doc, dict) and 'url' in doc:
                    urls.append(doc['url'])
                elif isinstance(doc, str):
                    urls.append(doc)
        
        # Repository (from link array with type="Repository")
        if 'link' in tool_data and tool_data['link']:
            for link in tool_data['link']:
                if isinstance(link, dict) and link.get('type') == 'Repository' and 'url' in link:
                    urls.append(link['url'])
        
        # Remove None values and empty strings
        urls = [url for url in urls if url and isinstance(url, str) and url.strip()]
        
        return urls
    
    def check_tool_urls(self, tool_data: Dict) -> Dict[str, Any]:
        """
        Check all URLs associated with a bio.tools entry.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Dict containing comprehensive URL check results:
            - homepage_result: Homepage check result
            - all_urls_results: Results for all URLs found
            - summary: Summary statistics
        """
        urls = self.extract_urls_from_tool(tool_data)
        
        if not urls:
            return {
                'homepage_result': None,
                'all_urls_results': {},
                'summary': {
                    'total_urls': 0,
                    'accessible_urls': 0,
                    'inaccessible_urls': 0,
                    'accessibility_rate': 0.0,
                    'homepage_accessible': False,
                    'avg_response_time': None
                }
            }
        
        # Check all URLs
        results = self.check_urls_batch(urls)
        
        # Extract homepage result
        homepage_result = None
        homepage = tool_data.get('homepage')
        if homepage and homepage in results:
            homepage_result = results[homepage]
        
        # Calculate summary statistics
        accessible_count = sum(1 for r in results.values() if r['is_accessible'])
        total_count = len(results)
        response_times = [r['response_time'] for r in results.values() if r['response_time'] is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        summary = {
            'total_urls': total_count,
            'accessible_urls': accessible_count,
            'inaccessible_urls': total_count - accessible_count,
            'accessibility_rate': accessible_count / total_count if total_count > 0 else 0.0,
            'homepage_accessible': homepage_result['is_accessible'] if homepage_result else False,
            'avg_response_time': avg_response_time
        }
        
        return {
            'homepage_result': homepage_result,
            'all_urls_results': results,
            'summary': summary
        }
    
    def clear_cache(self):
        """Clear the URL check cache."""
        self._url_cache.clear()
        self.logger.info("URL check cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'cached_urls': len(self._url_cache),
            'cache_ttl': self.cache_ttl
        }
