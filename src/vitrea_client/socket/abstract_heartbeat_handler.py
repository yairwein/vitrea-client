"""Abstract base class for heartbeat handlers."""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from .writable_socket_protocol import WritableSocketProtocol


class AbstractHeartbeatHandler(ABC):
    """Abstract base class for handling heartbeat functionality."""
    
    def __init__(self, interval: float, socket: WritableSocketProtocol):
        """Initialize heartbeat handler.
        
        Args:
            interval: Heartbeat interval in seconds
            socket: Socket to write heartbeat data to
        """
        self.interval = interval
        self.socket = socket
        self._task: Optional[asyncio.Task] = None
    
    @property
    def is_paused(self) -> bool:
        """Check if heartbeat is currently paused.
        
        Returns:
            True if heartbeat is paused, False otherwise
        """
        return self._task is None or self._task.done()
    
    def pause(self) -> None:
        """Pause the heartbeat timer."""
        if not self.is_paused and self._task is not None:
            self._task.cancel()
            self._task = None
    
    def restart(self) -> None:
        """Restart the heartbeat timer."""
        self.pause()
        self._task = asyncio.create_task(self._heartbeat_loop())
    
    async def _heartbeat_loop(self) -> None:
        """Internal heartbeat loop that runs continuously."""
        try:
            while True:
                await asyncio.sleep(self.interval)
                await self._handle_heartbeat()
        except asyncio.CancelledError:
            # Heartbeat was cancelled, which is expected
            pass
    
    async def _handle_heartbeat(self) -> None:
        """Handle a single heartbeat by sending data and restarting timer."""
        try:
            heartbeat_data = self.get_heartbeat_datagram()
            await self.socket.write(heartbeat_data)
        except Exception:
            # If heartbeat fails, we should pause to avoid continuous errors
            self.pause()
            raise
    
    @abstractmethod
    def get_heartbeat_datagram(self) -> bytes:
        """Get the heartbeat datagram to send.
        
        Returns:
            Bytes representing the heartbeat datagram
        """
        pass 