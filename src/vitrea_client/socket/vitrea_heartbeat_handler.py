"""Vitrea-specific heartbeat handler implementation."""

from .abstract_heartbeat_handler import AbstractHeartbeatHandler
from .writable_socket_protocol import WritableSocketProtocol
from ..requests import Heartbeat


class VitreaHeartbeatHandler(AbstractHeartbeatHandler):
    """Vitrea-specific heartbeat handler that sends heartbeat requests."""
    
    def __init__(self, socket: WritableSocketProtocol):
        """Initialize Vitrea heartbeat handler with 3-second interval.
        
        Args:
            socket: Socket to write heartbeat data to
        """
        super().__init__(3.0, socket)  # 3 second interval
    
    def get_heartbeat_datagram(self) -> bytes:
        """Get the Vitrea heartbeat datagram.
        
        Returns:
            Bytes representing the heartbeat request datagram
        """
        return Heartbeat().build()
    
    @classmethod
    def create(cls, socket: WritableSocketProtocol) -> "VitreaHeartbeatHandler":
        """Create and start a Vitrea heartbeat handler.
        
        Args:
            socket: Socket to write heartbeat data to
            
        Returns:
            Started VitreaHeartbeatHandler instance
        """
        instance = cls(socket)
        instance.restart()
        return instance 