"""
Parallel Quality Processor

Enhanced quality analysis with concurrent processing, batch operations,
and efficient resource management.
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Optional, Callable, Any, Union, Iterator
from dataclasses import dataclass
from queue import Queue, Empty
import threading

from ..analyzers.quality_analyzer import QualityAnalyzer, QualityReport
from ..utils.parallel_config import ParallelProcessingConfig

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of a tool processing operation."""
    tool_id: str
    success: bool
    report: Optional[QualityReport] = None
    error: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class BatchProcessingStats:
    """Statistics for batch processing operations."""
    total_tools: int
    successful: int
    failed: int
    total_time: float
    avg_time_per_tool: float
    throughput: float  # tools per second


class ParallelQualityProcessor:
    """
    Parallel quality analyzer with configurable concurrency and batch processing.
    
    Supports both thread-based and process-based parallelism depending on the
    workload characteristics.
    """
    
    def __init__(
        self,
        config: Optional[ParallelProcessingConfig] = None,
        analyzer_kwargs: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the parallel processor.
        
        Args:
            config: Parallel processing configuration
            analyzer_kwargs: Keyword arguments for QualityAnalyzer initialization
        """
        self.config = config or ParallelProcessingConfig.create_default()
        self.analyzer_kwargs = analyzer_kwargs or {}
        
        # Thread-local storage for analyzers (avoid thread safety issues)
        self._local = threading.local()
        
        # Executors (will be created when needed)
        self._thread_executor: Optional[ThreadPoolExecutor] = None
        self._process_executor: Optional[ProcessPoolExecutor] = None
    
    def _get_analyzer(self) -> QualityAnalyzer:
        """Get thread-local quality analyzer instance."""
        if not hasattr(self._local, 'analyzer'):
            self._local.analyzer = QualityAnalyzer(**self.analyzer_kwargs)
        return self._local.analyzer
    
    def _get_thread_executor(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor."""
        if self._thread_executor is None:
            self._thread_executor = ThreadPoolExecutor(
                max_workers=self.config.max_concurrent_analyses,
                thread_name_prefix="quality_analyzer"
            )
        return self._thread_executor
    
    def _get_process_executor(self) -> ProcessPoolExecutor:
        """Get or create process pool executor."""
        if self._process_executor is None:
            self._process_executor = ProcessPoolExecutor(
                max_workers=self.config.max_concurrent_analyses
            )
        return self._process_executor
    
    def _analyze_tool_sync(self, tool_data: Dict) -> ProcessingResult:
        """
        Synchronous analysis of a single tool (for use in thread pool).
        
        Args:
            tool_data: Tool metadata dictionary
            
        Returns:
            ProcessingResult with analysis outcome
        """
        start_time = time.time()
        tool_id = tool_data.get('biotoolsID', 'unknown')
        
        try:
            analyzer = self._get_analyzer()
            report = analyzer.analyze_tool(tool_data)
            
            return ProcessingResult(
                tool_id=tool_id,
                success=True,
                report=report,
                processing_time=time.time() - start_time
            )
        except Exception as e:
            logger.error(f"Error analyzing tool {tool_id}: {e}")
            return ProcessingResult(
                tool_id=tool_id,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    async def process_tool(self, tool_data: Dict) -> ProcessingResult:
        """
        Process a single tool asynchronously.
        
        Args:
            tool_data: Tool metadata dictionary
            
        Returns:
            ProcessingResult with analysis outcome
        """
        loop = asyncio.get_event_loop()
        executor = self._get_thread_executor()
        
        return await loop.run_in_executor(
            executor, 
            self._analyze_tool_sync, 
            tool_data
        )
    
    async def process_tools_batch(
        self,
        tools_data: List[Dict],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ProcessingResult]:
        """
        Process multiple tools concurrently.
        
        Args:
            tools_data: List of tool metadata dictionaries
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ProcessingResult objects
        """
        logger.info(f"Processing {len(tools_data)} tools in parallel")
        
        start_time = time.time()
        
        async def process_with_progress(tool_data: Dict, index: int) -> ProcessingResult:
            result = await self.process_tool(tool_data)
            if progress_callback:
                progress_callback(index + 1, len(tools_data))
            return result
        
        # Create tasks for all tools
        tasks = [
            process_with_progress(tool_data, i)
            for i, tool_data in enumerate(tools_data)
        ]
        
        # Execute with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processing_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                tool_id = tools_data[i].get('biotoolsID', f'tool_{i}')
                processing_results.append(ProcessingResult(
                    tool_id=tool_id,
                    success=False,
                    error=str(result),
                    processing_time=0.0
                ))
            else:
                processing_results.append(result)
        
        # Calculate statistics
        total_time = time.time() - start_time
        successful = sum(1 for r in processing_results if r.success)
        
        logger.info(f"Batch processing complete: {successful}/{len(tools_data)} successful "
                   f"in {total_time:.2f}s ({len(tools_data)/total_time:.1f} tools/sec)")
        
        return processing_results
    
    async def process_tools_stream(
        self,
        tools_data: List[Dict],
        batch_size: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ):
        """
        Process tools in streaming fashion, yielding results as they complete.
        
        Args:
            tools_data: List of tool metadata dictionaries
            batch_size: Size of processing batches
            progress_callback: Optional callback for progress updates
            
        Yields:
            ProcessingResult objects as they complete
        """
        batch_size = batch_size or self.config.analysis_batch_size
        total_processed = 0
        
        for i in range(0, len(tools_data), batch_size):
            batch = tools_data[i:i + batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1} "
                        f"({len(batch)} tools)")
            
            # Process batch
            batch_results = await self.process_tools_batch(batch)
            
            # Yield results and update progress
            for result in batch_results:
                total_processed += 1
                if progress_callback:
                    progress_callback(total_processed, len(tools_data))
                yield result
    
    def process_tools_pipeline(
        self,
        tools_iterator: Iterator[Dict],
        output_queue: Queue,
        stop_event: threading.Event
    ) -> None:
        """
        Process tools in a pipeline fashion with producer-consumer pattern.
        
        Args:
            tools_iterator: Iterator yielding tool data
            output_queue: Queue to put processing results
            stop_event: Event to signal stopping
        """
        async def async_pipeline():
            batch = []
            
            try:
                for tool_data in tools_iterator:
                    if stop_event.is_set():
                        break
                    
                    batch.append(tool_data)
                    
                    # Process when batch is full
                    if len(batch) >= self.config.analysis_batch_size:
                        results = await self.process_tools_batch(batch)
                        for result in results:
                            output_queue.put(result)
                        batch = []
                
                # Process remaining tools
                if batch and not stop_event.is_set():
                    results = await self.process_tools_batch(batch)
                    for result in results:
                        output_queue.put(result)
                        
            except Exception as e:
                logger.error(f"Error in processing pipeline: {e}")
                output_queue.put(ProcessingResult(
                    tool_id="pipeline_error",
                    success=False,
                    error=str(e)
                ))
            finally:
                # Signal completion
                output_queue.put(None)
        
        # Run the async pipeline in a new event loop
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(async_pipeline())
        finally:
            if loop:
                loop.close()
    
    def get_processing_stats(self, results: List[ProcessingResult]) -> BatchProcessingStats:
        """
        Calculate statistics for a batch of processing results.
        
        Args:
            results: List of ProcessingResult objects
            
        Returns:
            BatchProcessingStats with performance metrics
        """
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        total_time = sum(r.processing_time for r in results)
        
        return BatchProcessingStats(
            total_tools=len(results),
            successful=successful,
            failed=failed,
            total_time=total_time,
            avg_time_per_tool=total_time / len(results) if results else 0.0,
            throughput=len(results) / total_time if total_time > 0 else 0.0
        )
    
    def cleanup(self) -> None:
        """Clean up executor resources."""
        if self._thread_executor:
            self._thread_executor.shutdown(wait=True)
            self._thread_executor = None
        
        if self._process_executor:
            self._process_executor.shutdown(wait=True)
            self._process_executor = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def create_parallel_processor(
    config: Optional[ParallelProcessingConfig] = None,
    **analyzer_kwargs
) -> ParallelQualityProcessor:
    """
    Factory function to create a parallel quality processor.
    
    Args:
        config: Parallel processing configuration
        **analyzer_kwargs: Keyword arguments for QualityAnalyzer
        
    Returns:
        Configured ParallelQualityProcessor
    """
    return ParallelQualityProcessor(config=config, analyzer_kwargs=analyzer_kwargs)
