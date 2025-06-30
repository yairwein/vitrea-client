"""Abstract socket implementation for Vitrea client communication."""

import asyncio
import socket
from abc import ABC, abstractmethod
from typing import Optional, Any, Callable, Dict, List
from ..core import LoggerProtocol
from ..config import SocketConfig
from ..exceptions import ConnectionExistsException, NoConnectionException
from .abstract_heartbeat_handler import AbstractHeartbeatHandler
from .writable_socket_protocol import WritableSocketProtocol
from .timeout import Timeout


class AbstractSocket(ABC, WritableSocketProtocol):
    """Abstract base class for socket communication with event handling."""
    
    def __init__(self, host: str, port: int, socket_config: SocketConfig):
        """Initialize abstract socket.
        
        Args:
            host: Target host address
            port: Target port number
            socket_config: Socket configuration settings
        """
        self.host = host
        self.port = port
        self.socket_config = socket_config
        self.log = socket_config.log
        
        self._socket: Optional[socket.socket] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._heartbeat: Optional[AbstractHeartbeatHandler] = None
        self._event_listeners: Dict[str, List[Callable]] = {}
        self._read_task: Optional[asyncio.Task] = None
    
    def _create_new_socket(self) -> socket.socket:
        """Create a new TCP socket with configured timeout.
        
        Returns:
            Configured socket instance
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.socket_config.request_timeout)
        return sock
    
    async def connect(self) -> None:
        """Establish connection to the target host and port.
        
        Raises:
            ConnectionExistsException: If connection already exists
            TimeoutException: If connection times out
        """
        self.log.debug("Attempting to make a connection")
        
        if self._socket is not None:
            error = ConnectionExistsException()
            self.log.error(str(error))
            raise error
        
        try:
            # Create connection with timeout
            connect_future = asyncio.open_connection(self.host, self.port)
            self._reader, self._writer = await asyncio.wait_for(
                connect_future, 
                timeout=self.socket_config.request_timeout
            )
            
            # Get the underlying socket
            self._socket = self._writer.get_extra_info('socket')
            
            # Start reading data in background
            self._read_task = asyncio.create_task(self._read_loop())
            
            await self._handle_connect()
            
        except asyncio.TimeoutError:
            from ..exceptions import TimeoutException
            raise TimeoutException(f"Connection timeout after {self.socket_config.request_timeout} seconds")
        except Exception as e:
            self.log.error(f"Connection failed: {e}")
            await self._cleanup_connection()
            raise
    
    def disconnect(self) -> None:
        """Disconnect from the target host."""
        if self._socket is not None:
            self.log.info("Forced a disconnection")
            if self._heartbeat is not None:
                self._heartbeat.pause()
            self.socket_config.should_reconnect = False
            asyncio.create_task(self._cleanup_connection())
    
    async def write(self, data: bytes) -> None:
        """Write data to the socket.
        
        Args:
            data: Bytes to write
            
        Raises:
            NoConnectionException: If no connection exists
        """
        if self._writer is None or self._writer.is_closing():
            raise NoConnectionException()
        
        try:
            self._writer.write(data)
            await self._writer.drain()
            self._restart_heartbeat()
        except Exception as e:
            self.log.error(f"Data written with an error - {e}")
            raise
    
    async def _cleanup_connection(self) -> None:
        """Clean up connection resources."""
        if self._read_task is not None:
            self._read_task.cancel()
            self._read_task = None
        
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
        
        self._reader = None
        self._socket = None
    
    async def _read_loop(self) -> None:
        """Background task to continuously read data from socket."""
        try:
            while self._reader is not None and not self._reader.at_eof():
                data = await self._reader.read(4096)
                if not data:
                    break
                await self._handle_data(data)
        except asyncio.CancelledError:
            # Read loop was cancelled, which is expected during disconnect
            pass
        except Exception as e:
            self.log.error(f"Error in read loop: {e}")
            await self._handle_error(e)
        finally:
            await self._handle_disconnect()
    
    async def _handle_disconnect(self) -> None:
        """Handle disconnection event."""
        self.log.debug("Connection closed")
        
        await self._cleanup_connection()
        
        if self.socket_config.should_reconnect:
            self.log.info("Automatically reconnecting", {"should_reconnect": self.socket_config.should_reconnect})
            try:
                await self.connect()
            except Exception as e:
                self.log.error(f"Reconnection failed: {e}")
        else:
            self.log.info("Not reconnecting", {"should_reconnect": self.socket_config.should_reconnect})
    
    async def _handle_error(self, error: Exception) -> None:
        """Handle socket error event.
        
        Args:
            error: The error that occurred
        """
        self.socket_config.should_reconnect = False
        self.log.error(f"An error occurred - {error}")
    
    async def _handle_connect(self) -> None:
        """Handle successful connection event."""
        self.log.debug("Connection established")
        self.socket_config.should_reconnect = True
        self._restart_heartbeat()
    
    def _restart_heartbeat(self) -> None:
        """Restart the heartbeat handler if it exists."""
        if self._heartbeat is not None:
            self._heartbeat.restart()
    
    def on(self, event_name: str, listener: Callable) -> None:
        """Add an event listener.
        
        Args:
            event_name: Name of the event to listen for
            listener: Callback function to call when event occurs
        """
        if event_name not in self._event_listeners:
            self._event_listeners[event_name] = []
        self._event_listeners[event_name].append(listener)
    
    def once(self, event_name: str, listener: Callable) -> None:
        """Add a one-time event listener.
        
        Args:
            event_name: Name of the event to listen for
            listener: Callback function to call when event occurs
        """
        def once_wrapper(*args, **kwargs):
            self.remove_listener(event_name, once_wrapper)
            listener(*args, **kwargs)
        
        self.on(event_name, once_wrapper)
    
    def remove_listener(self, event_name: str, listener: Callable) -> None:
        """Remove an event listener.
        
        Args:
            event_name: Name of the event
            listener: Callback function to remove
        """
        if event_name in self._event_listeners:
            try:
                self._event_listeners[event_name].remove(listener)
            except ValueError:
                pass
    
    def emit(self, event_name: str, *args, **kwargs) -> None:
        """Emit an event to all registered listeners.
        
        Args:
            event_name: Name of the event to emit
            *args: Positional arguments to pass to listeners
            **kwargs: Keyword arguments to pass to listeners
        """
        if event_name in self._event_listeners:
            for listener in self._event_listeners[event_name][:]:  # Copy to avoid modification during iteration
                try:
                    listener(*args, **kwargs)
                except Exception as e:
                    self.log.error(f"Error in event listener for {event_name}: {e}")
    
    @abstractmethod
    async def _handle_data(self, data: bytes) -> None:
        """Handle incoming data from socket.
        
        Args:
            data: Raw bytes received from socket
        """
        pass
    
    @abstractmethod
    async def _handle_unknown_data(self, data: bytes) -> None:
        """Handle unrecognized data from socket.
        
        Args:
            data: Raw bytes that couldn't be processed
        """
        pass 