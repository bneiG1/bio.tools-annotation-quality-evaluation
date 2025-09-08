import requests
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from logger import get_logger, log_api_response


def save_tool_individual(tool: Dict[str, Any], output_dir: Path) -> str:
    """
    Save a single tool to an individual JSON file.
    
    Args:
        tool: Tool data dictionary
        output_dir: Directory to save the file
    
    Returns:
        str: Path to the saved file
    """
    biotoolsID = tool.get('biotoolsID', 'unknown_tool')
    # Sanitize filename
    safe_id = "".join(c for c in biotoolsID if c.isalnum() or c in ('-', '_', '.')).rstrip()
    
    filename = f"{safe_id}.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tool, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def save_batch(tools: List[Dict[str, Any]], batch_num: int, output_dir: Path) -> str:
    """
    Save a batch of tools to a single file.
    
    Args:
        tools: List of tool dictionaries
        batch_num: Batch number for filename
        output_dir: Directory to save the file
    
    Returns:
        str: Path to the saved file
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"biotools_batch_{batch_num:04d}_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def get_request(url: str, 
                headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, Any]] = None,
                timeout: int = 30,
                max_retries: int = 3,
                retry_delay: float = 1.0) -> requests.Response:
    """
    Make a GET request to a URL with robust error handling and retry logic.
    
    This function is designed for bio.tools API integration and other bioinformatics
    data sources that may have rate limiting or temporary availability issues.
    
    Args:
        url (str): The URL to make the GET request to
        headers (dict, optional): HTTP headers to include in the request
        params (dict, optional): URL parameters to include in the request
        timeout (int): Request timeout in seconds (default: 30)
        max_retries (int): Maximum number of retry attempts (default: 3)
        retry_delay (float): Delay between retries in seconds (default: 1.0)
    
    Returns:
        requests.Response: The response object from the successful request
        
    Raises:
        requests.exceptions.RequestException: If all retry attempts fail
        
    Example:
        >>> response = get_request("https://bio.tools/api/tool/")
        >>> if response.status_code == 200:
        ...     data = response.json()
    """
    logger = get_logger("utils")
    
    if headers is None:
        headers = {
            'User-Agent': 'bio.tools-quality-evaluator/1.0',
            'Accept': 'application/json'
        }
    
    logger.debug(f"Making GET request to {url} with params: {params}")
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(
                url=url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            # Raise an exception for bad status codes
            response.raise_for_status()
            
            logger.info(f"Successful request to {url} - Status: {response.status_code}")
            logger.debug(f"Response size: {len(response.content)} bytes")
            
            return response
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            
            if attempt < max_retries:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                # Exponential backoff for retries
                retry_delay *= 2
            else:
                logger.error(f"All retry attempts failed. Last error: {e}")
    
    # If we get here, all retries failed
    if last_exception is not None:
        # Re-raise the last encountered exception to preserve original traceback
        raise last_exception
    else:
        # Safety fallback: raise a generic RequestException if somehow no exception was captured
        raise requests.exceptions.RequestException("Request failed after all retry attempts without capturing an exception")

def fetch_all_biotools(
    base_url: str = "https://bio.tools/api/tool/",
    output_file: Optional[Union[str, Path]] = None,
    page_size: int = 25,
    max_tools: Optional[int] = None,
    start_page: int = 1,
    delay: float = 0.5,
    stats_only: bool = False,
    save_mode: str = "single",
    batch_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Fetch all tools from the bio.tools API with pagination handling.
    
    Args:
        base_url (str): Base API URL for bio.tools
        output_file (str, optional): Path to save all collected tools as JSON
        page_size (int): Number of tools per page (default: 25, max: 100)
        max_tools (int, optional): Maximum number of tools to fetch (for testing)
        start_page (int): Page number to start from (default: 1)
        delay (float): Delay between API requests in seconds (default: 0.5)
        stats_only (bool): Only collect statistics, don't save full data (default: False)
        save_mode (str): How to save tools - 'single', 'individual', or 'batch' (default: 'single')
        batch_size (int): Number of tools per batch file when save_mode='batch' (default: 1000)
    
    Returns:
        List[Dict]: List of all tool entries from bio.tools
    """
    logger = get_logger("biotools_collector")
    logger.info(f"Starting collection of all bio.tools entries")
    logger.info(f"Page size: {page_size}, Start page: {start_page}, Delay: {delay}s")
    logger.info(f"Save mode: {save_mode}")
    
    if stats_only:
        logger.info("STATS ONLY MODE - Collecting basic statistics only")
    
    all_tools = []
    current_page = start_page
    tools_collected = 0
    total_tools = None
    batch_count = 0
    current_batch = []
    
    # Create data directory structure based on save mode
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize directories for different save modes
    individual_dir = data_dir / "individual_tools"
    batch_dir = data_dir / "batches"
    
    if save_mode == "individual":
        individual_dir.mkdir(exist_ok=True)
        logger.info(f"Individual JSON files will be saved to: {individual_dir}")
    elif save_mode == "batch":
        batch_dir.mkdir(exist_ok=True)
        logger.info(f"Batch JSON files will be saved to: {batch_dir} (size: {batch_size})")
    
    while True:
        try:
            logger.info(f"Fetching page {current_page}")
            
            # Make API request
            params = {
                "page": current_page,
                "format": "json",
                "page_size": page_size
            }
            
            response = get_request(base_url, params=params)
            log_api_response(logger, response, base_url, params)
            
            data = response.json()
            
            # Get total count on first page
            if total_tools is None and 'count' in data:
                total_tools = data['count']
                logger.info(f"Total tools available in bio.tools: {total_tools:,}")
            
            # Extract tools from current page
            page_tools = data.get('list', [])
            
            if not page_tools:
                logger.info("No more tools found, collection complete")
                break
            
            # Trim page_tools if we're approaching the max_tools limit
            if max_tools and tools_collected + len(page_tools) > max_tools:
                tools_needed = max_tools - tools_collected
                page_tools = page_tools[:tools_needed]
                logger.info(f"Trimming page to {len(page_tools)} tools to respect max_tools limit")
            
            # In stats_only mode, only collect basic info, not full tool data
            if stats_only:
                # Just collect basic statistics without storing full tool objects
                tools_collected += len(page_tools)
                logger.info(f"Page {current_page}: {len(page_tools)} tools")
                # For stats mode, we just track counts without storing data
                all_tools = []  # Keep empty to save memory in stats mode
            else:
                # Process tools based on save mode
                if save_mode == "individual":
                    # Save each tool individually as JSON
                    for tool in page_tools:
                        try:
                            saved_path = save_tool_individual(tool, individual_dir)
                            logger.debug(f"Saved individual tool: {saved_path}")
                        except Exception as e:
                            logger.error(f"Failed to save individual tool {tool.get('biotoolsID', 'unknown')}: {e}")
                    
                    # Don't store in memory for individual mode to save RAM
                    tools_collected += len(page_tools)
                    logger.info(f"Saved {len(page_tools)} individual tools from page {current_page}")
                
                elif save_mode == "batch":
                    # Add tools to current batch
                    current_batch.extend(page_tools)
                    tools_collected += len(page_tools)
                    
                    # Save batch when it reaches the specified size
                    while len(current_batch) >= batch_size:
                        batch_to_save = current_batch[:batch_size]
                        current_batch = current_batch[batch_size:]
                        batch_count += 1
                        
                        try:
                            saved_path = save_batch(batch_to_save, batch_count, batch_dir)
                            logger.info(f"Saved batch {batch_count} ({len(batch_to_save)} tools): {saved_path}")
                        except Exception as e:
                            logger.error(f"Failed to save batch {batch_count}: {e}")
                    
                    logger.info(f"Collected {len(page_tools)} tools from page {current_page} (batch mode)")
                
                else:  # save_mode == "single"
                    # Standard single file mode
                    all_tools.extend(page_tools)
                    tools_collected += len(page_tools)
                    
                    logger.info(f"Collected {len(page_tools)} tools from page {current_page}")
                    
                    # Save intermediate results every 10 pages (only in single file mode)
                    if current_page % 10 == 0:
                        intermediate_file = data_dir / f"biotools_partial_{current_page}pages.json"
                        with open(intermediate_file, 'w', encoding='utf-8') as f:
                            json.dump(all_tools, f, indent=2, ensure_ascii=False)
                        logger.info(f"Saved intermediate results to {intermediate_file}")
            
            logger.info(f"Total collected so far: {tools_collected:,}")
            
            # Check if we've reached the maximum tools limit
            if max_tools and tools_collected >= max_tools:
                logger.info(f"Reached maximum tools limit ({max_tools}), stopping collection")
                break
            
            # Check if there's a next page
            if not data.get('next'):
                logger.info("Reached last page, collection complete")
                break
            
            current_page += 1
            
            # Add a configurable delay to be respectful to the API
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {current_page}: {e}")
            logger.warning("Retrying in 5 seconds...")
            time.sleep(5)
            continue
        
        except Exception as e:
            logger.error(f"Unexpected error on page {current_page}: {e}")
            break
    
    # Handle any remaining batch at the end
    if save_mode == "batch" and current_batch and not stats_only:
        batch_count += 1
        try:
            saved_path = save_batch(current_batch, batch_count, batch_dir)
            logger.info(f"Saved final batch {batch_count} ({len(current_batch)} tools): {saved_path}")
        except Exception as e:
            logger.error(f"Failed to save final batch {batch_count}: {e}")
    
    if stats_only:
        logger.info(f"Statistics collection completed. Total tools counted: {tools_collected:,}")
        # Return empty list for stats mode, but log the count
        return []
    elif save_mode == "individual":
        logger.info(f"Individual file collection completed. Total tools saved: {tools_collected:,}")
        # Return empty list for individual mode to save memory
        return []
    elif save_mode == "batch":
        logger.info(f"Batch collection completed. Total tools saved: {tools_collected:,} in {batch_count} batches")
        # Return empty list for batch mode to save memory
        return []
    else:
        logger.info(f"Collection completed. Total tools collected: {tools_collected:,}")
    
    # Save final results (only for single file mode)
    if save_mode == "single" and not stats_only:
        if output_file is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = data_dir / f"biotools_complete_{timestamp}.json"
        else:
            output_file = Path(output_file)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_tools, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved all {len(all_tools):,} tools to {output_file}")
            
            # Also save a summary
            summary = {
                "collection_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tools": len(all_tools),
                "api_total_count": total_tools,
                "pages_fetched": current_page - start_page + 1,
                "data_file": str(output_file)
            }
            
            summary_file = output_file.parent / f"collection_summary_{time.strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Saved collection summary to {summary_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    return all_tools
