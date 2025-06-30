"""Protocol definition for writable socket interface."""

from typing import Protocol


class WritableSocketProtocol(Protocol):
    """Protocol for objects that can write data to a socket."""
    
    async def write(self, data: bytes) -> None:
        """Write data to the socket.
        
        Args:
            data: Bytes to write to the socket
            
        Raises:
            NoConnectionException: If no connection exists
        """
        ... 