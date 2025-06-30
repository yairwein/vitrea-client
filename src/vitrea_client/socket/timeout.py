"""Timeout handling for socket operations."""

import asyncio
from typing import Optional, Callable, Any
from ..exceptions import TimeoutException


class Timeout:
    """Handles timeout operations for socket requests."""
    
    def __init__(
        self,
        interval: float,
        message: str,
        on_timeout: Optional[Callable[[TimeoutException], None]] = None
    ):
        """Initialize timeout handler.
        
        Args:
            interval: Timeout interval in seconds
            message: Error message for timeout exception
            on_timeout: Optional callback function when timeout occurs
        """
        self.interval = interval
        self.message = message
        self.on_timeout = on_timeout or (lambda _: None)
        self._task: Optional[asyncio.Task] = None
    
    def start(self) -> None:
        """Start the timeout timer."""
        if self._task is not None:
            self.stop()
        
        try:
            self._task = asyncio.create_task(self._timeout_handler())
        except RuntimeError:
            # No event loop running, which is fine for tests
            pass
    
    def stop(self) -> None:
        """Stop the timeout timer."""
        if self._task is not None:
            self._task.cancel()
            self._task = None
    
    async def _timeout_handler(self) -> None:
        """Internal timeout handler that waits and raises exception."""
        try:
            await asyncio.sleep(self.interval)
            error = TimeoutException(self.message)
            self.on_timeout(error)
            raise error
        except asyncio.CancelledError:
            # Timeout was cancelled, which is expected
            pass
    
    @classmethod
    def create(
        cls,
        interval: float,
        message: Optional[str] = None,
        on_timeout: Optional[Callable[[TimeoutException], None]] = None
    ) -> "Timeout":
        """Create and start a timeout instance.
        
        Args:
            interval: Timeout interval in seconds
            message: Optional custom error message
            on_timeout: Optional callback function when timeout occurs
            
        Returns:
            Started Timeout instance
        """
        if message is None:
            message = f"Timeout reached after {interval} seconds"
        
        instance = cls(interval, message, on_timeout)
        instance.start()
        return instance 