"""
Processing Pipeline for Parallel Data Flow

Orchestrates the complete data processing pipeline with concurrent fetching,
analysis, and result aggregation using producer-consumer patterns.
"""

import asyncio
import threading
import time
import logging
from queue import Queue, Empty
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

from ..collectors.async_biotools_api import AsyncBioToolsAPIClient, create_async_client
from ..analyzers.parallel_processor import ParallelQualityProcessor, ProcessingResult
from ..analyzers.quality_analyzer import QualityReport
from ..utils.parallel_config import ParallelProcessingConfig

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """Statistics for pipeline execution."""
    total_tools: int = 0
    fetched_tools: int = 0
    processed_tools: int = 0
    successful_analyses: int = 0
    fetch_time: float = 0.0
    processing_time: float = 0.0
    total_time: float = 0.0
    throughput: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class PipelineProgress:
    """Progress tracking for pipeline execution."""
    phase: str = "starting"  # starting, fetching, processing, finishing
    fetched: int = 0
    processed: int = 0
    total: int = 0
    current_operation: str = ""
    estimated_time_remaining: float = 0.0


class ProcessingPipeline:
    """
    Main processing pipeline that orchestrates concurrent fetching and analysis.
    
    Implements a producer-consumer pattern where:
    - Producer: Fetches tools from API concurrently
    - Buffer: Queue of fetched tools waiting for analysis  
    - Consumer: Analyzes tools in parallel
    - Aggregator: Collects and manages results
    """
    
    def __init__(
        self,
        config: Optional[ParallelProcessingConfig] = None,
        cache_dir: Optional[Path] = None,
        analyzer_kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the processing pipeline.
        
        Args:
            config: Parallel processing configuration
            cache_dir: Directory for caching API responses
            analyzer_kwargs: Arguments for quality analyzer initialization
        """
        self.config = config or ParallelProcessingConfig.create_default()
        self.cache_dir = cache_dir
        self.analyzer_kwargs = analyzer_kwargs or {}
        
        # Pipeline components
        self.api_client: Optional[AsyncBioToolsAPIClient] = None
        self.processor: Optional[ParallelQualityProcessor] = None
        
        # Pipeline state
        self.stats = PipelineStats()
        self.progress = PipelineProgress()
        self._stop_event = threading.Event()
        self._progress_callbacks: List[Callable[[PipelineProgress], None]] = []
        self._error_callbacks: List[Callable[[str], None]] = []
    
    def add_progress_callback(self, callback: Callable[[PipelineProgress], None]) -> None:
        """Add a progress callback function."""
        self._progress_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable[[str], None]) -> None:
        """Add an error callback function."""
        self._error_callbacks.append(callback)
    
    def _notify_progress(self) -> None:
        """Notify all progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(self.progress)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def _notify_error(self, error_msg: str) -> None:
        """Notify all error callbacks."""
        self.stats.errors.append(error_msg)
        for callback in self._error_callbacks:
            try:
                callback(error_msg)
            except Exception as e:
                logger.warning(f"Error callback error: {e}")
    
    async def process_tool_ids(
        self,
        tool_ids: List[str],
        enable_pipeline: bool = True
    ) -> List[QualityReport]:
        """
        Process a list of tool IDs with concurrent fetching and analysis.
        
        Args:
            tool_ids: List of bio.tools tool identifiers
            enable_pipeline: Whether to use pipeline mode (overlapped fetch/process)
            
        Returns:
            List of quality reports for successfully processed tools
        """
        logger.info(f"Starting pipeline processing of {len(tool_ids)} tools")
        start_time = time.time()
        
        self.stats = PipelineStats(total_tools=len(tool_ids))
        self.progress = PipelineProgress(total=len(tool_ids))
        
        try:
            # Initialize components
            self.api_client = create_async_client(self.config, self.cache_dir)
            self.processor = ParallelQualityProcessor(self.config, self.analyzer_kwargs)
            
            # Verify components are initialized
            assert self.api_client is not None, "API client initialization failed"
            assert self.processor is not None, "Processor initialization failed"
            
            async with self.api_client:
                if enable_pipeline and self.config.enable_pipeline_mode:
                    reports = await self._process_with_pipeline(tool_ids)
                else:
                    reports = await self._process_sequential_batches(tool_ids)
            
            self.stats.total_time = time.time() - start_time
            self.stats.throughput = self.stats.processed_tools / self.stats.total_time if self.stats.total_time > 0 else 0
            
            logger.info(f"Pipeline complete: {self.stats.successful_analyses}/{len(tool_ids)} successful "
                       f"in {self.stats.total_time:.2f}s ({self.stats.throughput:.1f} tools/sec)")
            
            return reports
            
        except Exception as e:
            error_msg = f"Pipeline processing failed: {e}"
            logger.error(error_msg)
            self._notify_error(error_msg)
            return []
        finally:
            if self.processor:
                self.processor.cleanup()
    
    async def _process_with_pipeline(self, tool_ids: List[str]) -> List[QualityReport]:
        """Process tools using overlapped fetch and analysis pipeline."""
        self.progress.phase = "pipeline"
        self._notify_progress()
        
        reports = []
        
        # Create queues for pipeline stages
        fetch_queue = asyncio.Queue(maxsize=self.config.pipeline_buffer_size)
        process_queue = asyncio.Queue(maxsize=self.config.pipeline_buffer_size)
        
        # Start producer task (fetcher)
        fetch_task = asyncio.create_task(
            self._fetch_producer(tool_ids, fetch_queue)
        )
        
        # Start processor task  
        process_task = asyncio.create_task(
            self._process_consumer(fetch_queue, process_queue)
        )
        
        # Start result collector
        collect_task = asyncio.create_task(
            self._result_collector(process_queue, reports)
        )
        
        # Wait for all tasks to complete
        await asyncio.gather(fetch_task, process_task, collect_task)
        
        return reports
    
    async def _process_sequential_batches(self, tool_ids: List[str]) -> List[QualityReport]:
        """Process tools in sequential batches (fetch all, then process all)."""
        if not self.api_client or not self.processor:
            raise RuntimeError("Components not initialized")
            
        self.progress.phase = "fetching"
        self._notify_progress()
        
        # Fetch all tools first
        fetch_results = await self.api_client.fetch_tools_batch(
            tool_ids,
            progress_callback=self._update_fetch_progress
        )
        
        self.stats.fetch_time = time.time() - time.time()  # Will be updated by callback
        self.stats.fetched_tools = sum(1 for r in fetch_results if r.success)
        
        # Extract successful tool data
        tools_data = [r.data for r in fetch_results if r.success and r.data]
        
        if not tools_data:
            logger.warning("No tools successfully fetched")
            return []
        
        self.progress.phase = "processing"
        self._notify_progress()
        
        # Process all tools
        process_results = await self.processor.process_tools_batch(
            tools_data,
            progress_callback=self._update_process_progress
        )
        
        self.stats.processed_tools = len(process_results)
        self.stats.successful_analyses = sum(1 for r in process_results if r.success)
        
        # Extract reports
        reports = [r.report for r in process_results if r.success and r.report]
        return reports
    
    async def _fetch_producer(self, tool_ids: List[str], output_queue: asyncio.Queue) -> None:
        """Producer task that fetches tools and puts them in queue."""
        if not self.api_client:
            raise RuntimeError("API client not initialized")
            
        try:
            fetch_start = time.time()
            
            async for result in self.api_client.fetch_tools_stream(tool_ids):
                if self._stop_event.is_set():
                    break
                
                self.stats.fetched_tools += 1
                self.progress.fetched = self.stats.fetched_tools
                self._notify_progress()
                
                if result.success and result.data:
                    await output_queue.put(result.data)
                else:
                    logger.warning(f"Failed to fetch tool {result.tool_id}: {result.error}")
            
            self.stats.fetch_time = time.time() - fetch_start
            
        except Exception as e:
            self._notify_error(f"Fetch producer error: {e}")
        finally:
            # Signal end of fetching
            await output_queue.put(None)
    
    async def _process_consumer(
        self, 
        input_queue: asyncio.Queue, 
        output_queue: asyncio.Queue
    ) -> None:
        """Consumer task that processes tools from input queue."""
        try:
            process_start = time.time()
            batch = []
            
            while True:
                try:
                    # Get tool data from queue
                    tool_data = await asyncio.wait_for(input_queue.get(), timeout=1.0)
                    
                    if tool_data is None:  # End of data signal
                        break
                    
                    batch.append(tool_data)
                    
                    # Process when batch is full
                    if len(batch) >= self.config.analysis_batch_size:
                        await self._process_batch(batch, output_queue)
                        batch = []
                
                except asyncio.TimeoutError:
                    # Process partial batch if we have data and timeout occurred
                    if batch:
                        await self._process_batch(batch, output_queue)
                        batch = []
                
                if self._stop_event.is_set():
                    break
            
            # Process remaining batch
            if batch:
                await self._process_batch(batch, output_queue)
            
            self.stats.processing_time = time.time() - process_start
            
        except Exception as e:
            self._notify_error(f"Process consumer error: {e}")
        finally:
            # Signal end of processing
            await output_queue.put(None)
    
    async def _process_batch(self, batch: List[Dict], output_queue: asyncio.Queue) -> None:
        """Process a batch of tools and put results in output queue."""
        if not self.processor:
            raise RuntimeError("Processor not initialized")
            
        results = await self.processor.process_tools_batch(batch)
        
        for result in results:
            self.stats.processed_tools += 1
            if result.success:
                self.stats.successful_analyses += 1
            
            self.progress.processed = self.stats.processed_tools
            self._notify_progress()
            
            await output_queue.put(result)
    
    async def _result_collector(
        self, 
        input_queue: asyncio.Queue, 
        reports: List[QualityReport]
    ) -> None:
        """Collector task that aggregates results."""
        try:
            while True:
                try:
                    result = await asyncio.wait_for(input_queue.get(), timeout=1.0)
                    
                    if result is None:  # End of data signal
                        break
                    
                    if result.success and result.report:
                        reports.append(result.report)
                    elif not result.success:
                        logger.warning(f"Analysis failed for {result.tool_id}: {result.error}")
                
                except asyncio.TimeoutError:
                    continue
                
                if self._stop_event.is_set():
                    break
                    
        except Exception as e:
            self._notify_error(f"Result collector error: {e}")
    
    def _update_fetch_progress(self, current: int, total: int) -> None:
        """Update fetch progress."""
        self.progress.fetched = current
        self._notify_progress()
    
    def _update_process_progress(self, current: int, total: int) -> None:
        """Update processing progress."""
        self.progress.processed = current
        self._notify_progress()
    
    def stop(self) -> None:
        """Stop the pipeline processing."""
        self._stop_event.set()
    
    def get_stats(self) -> PipelineStats:
        """Get current pipeline statistics."""
        return self.stats
    
    def get_progress(self) -> PipelineProgress:
        """Get current pipeline progress."""
        return self.progress
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        if self.processor:
            self.processor.cleanup()


def create_pipeline(
    config: Optional[ParallelProcessingConfig] = None,
    cache_dir: Optional[Path] = None,
    **analyzer_kwargs
) -> ProcessingPipeline:
    """
    Factory function to create a processing pipeline.
    
    Args:
        config: Parallel processing configuration
        cache_dir: Directory for caching API responses
        **analyzer_kwargs: Arguments for quality analyzer
        
    Returns:
        Configured ProcessingPipeline
    """
    return ProcessingPipeline(
        config=config,
        cache_dir=cache_dir,
        analyzer_kwargs=analyzer_kwargs
    )
