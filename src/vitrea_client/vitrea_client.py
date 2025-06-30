"""Main Vitrea client implementation."""

import asyncio
from typing import TypeVar, Generic, Optional, Callable, Any, Dict, List
from .socket import AbstractSocket, VitreaHeartbeatHandler, SplitMultipleBuffers, Timeout
from .core import BaseRequest, BaseResponse
from .config import ConnectionConfig, SocketConfig
from .responses import ResponseFactory, Acknowledgement, GenericUnusedResponse, KeyStatus
from .requests import (
    Login, ToggleHeartbeat, RoomCount, NodeCount, NodeMetaData, RoomMetaData,
    KeyStatus as KeyStatusRequest, KeyParameters, NodeStatus, InternalUnitStatuses,
    ToggleKeyStatus, Heartbeat
)
from .responses import (
    RoomCount as RoomCountResponse, NodeCount as NodeCountResponse,
    NodeMetaData as NodeMetaDataResponse, RoomMetaData as RoomMetaDataResponse,
    KeyStatus as KeyStatusResponse, KeyParameters as KeyParametersResponse,
    InternalUnitStatuses as InternalUnitStatusesResponse
)
from .utilities import Events, KeyPowerStatus
from .exceptions import TimeoutException

T = TypeVar('T', bound=BaseRequest)
R = TypeVar('R', bound=BaseResponse)


class VitreaClient(AbstractSocket):
    """Main Vitrea client for communicating with Vitrea Smart Home systems."""
    
    def __init__(self, connection_config: ConnectionConfig, socket_config: SocketConfig):
        """Initialize Vitrea client.
        
        Args:
            connection_config: Connection configuration settings
            socket_config: Socket configuration settings
        """
        super().__init__(connection_config.host, connection_config.port, socket_config)
        self.connection_config = connection_config
        self._mutex = asyncio.Lock()
        self._pending_requests: Dict[str, asyncio.Future] = {}
        
        # Initialize heartbeat handler
        self._heartbeat = VitreaHeartbeatHandler(self)
    
    async def _acquire_mutex(self, event_name: str) -> Callable[[], None]:
        """Acquire mutex for request synchronization.
        
        Args:
            event_name: Name of the event for logging
            
        Returns:
            Release function to call when done
        """
        self.log.debug("Waiting for mutex", {"event_name": event_name})
        await self._mutex.acquire()
        self.log.debug("Acquired mutex", {"event_name": event_name})
        
        def release():
            self._mutex.release()
            self.log.debug("Released mutex", {"event_name": event_name})
        
        return release
    
    async def send(self, request: T) -> R:
        """Send a request and wait for the corresponding response.
        
        Args:
            request: The request to send
            
        Returns:
            The corresponding response
            
        Raises:
            TimeoutException: If request times out
        """
        event_name = request.event_name
        release = await self._acquire_mutex(event_name)
        
        try:
            return await self._send_with_timeout(request, release)
        except Exception:
            release()
            raise
    
    async def _send_with_timeout(self, request: T, release: Callable[[], None]) -> R:
        """Send request with timeout handling.
        
        Args:
            request: The request to send
            release: Mutex release function
            
        Returns:
            The corresponding response
        """
        self.log.info("Sending data", request.log_data)
        
        # Create future for this request
        future: asyncio.Future[R] = asyncio.Future()
        self._pending_requests[request.event_name] = future
        
        # Set up timeout
        timeout_task = None
        try:
            # Create timeout handler
            async def timeout_handler():
                await asyncio.sleep(self.socket_config.request_timeout)
                if not future.done():
                    error = TimeoutException("Sending timeout reached")
                    self.log.error(error.message, request.log_data)
                    if request.event_name in self._pending_requests:
                        del self._pending_requests[request.event_name]
                    future.set_exception(error)
            
            timeout_task = asyncio.create_task(timeout_handler())
            
            # Send the request
            await self.write(request.build())
            
            # Wait for response
            response = await future
            
            # Add request buffer delay before releasing
            if self.socket_config.request_buffer > 0:
                await asyncio.sleep(self.socket_config.request_buffer)
            
            return response
            
        finally:
            # Clean up
            if timeout_task and not timeout_task.done():
                timeout_task.cancel()
            if request.event_name in self._pending_requests:
                del self._pending_requests[request.event_name]
            release()
    
    def _should_log_response(self, response: BaseResponse) -> bool:
        """Check if response should be logged.
        
        Args:
            response: Response to check
            
        Returns:
            True if response should be logged
        """
        if self.socket_config.ignore_ack_logs:
            return not isinstance(response, (Acknowledgement, GenericUnusedResponse))
        return True
    
    async def _handle_connect(self) -> None:
        """Handle successful connection by toggling heartbeat and logging in."""
        await super()._handle_connect()
        
        # Toggle heartbeat and login
        try:
            await self.send(ToggleHeartbeat())
            await self.send(Login(self.connection_config.username, self.connection_config.password))
        except Exception as e:
            self.log.error(f"Failed to initialize connection: {e}")
            raise
    
    async def _handle_data(self, data: bytes) -> None:
        """Handle incoming data from socket.
        
        Args:
            data: Raw bytes received from socket
        """
        # Split multiple datagrams if present
        buffers = SplitMultipleBuffers.handle(data)
        
        for buffer in buffers:
            await self._process_single_buffer(buffer)
    
    async def _process_single_buffer(self, data: bytes) -> None:
        """Process a single datagram buffer.
        
        Args:
            data: Single datagram buffer
        """
        try:
            response = ResponseFactory.find(data, self.connection_config.version)
            
            if response is None:
                self.emit(Events.UNKNOWN_DATA, data)
                await self._handle_unknown_data(data)
                return
            
            if self._should_log_response(response):
                self.log.info("Data Received", response.log_data)
            
            # Handle pending request
            if response.event_name in self._pending_requests:
                future = self._pending_requests[response.event_name]
                if not future.done():
                    future.set_result(response)
            
            # Emit event for listeners
            self.emit(response.event_name, response)
            
        except Exception as e:
            self.log.error(f"Error processing buffer: {e}")
            await self._handle_unknown_data(data)
    
    async def _handle_unknown_data(self, data: bytes) -> None:
        """Handle unrecognized data from socket.
        
        Args:
            data: Raw bytes that couldn't be processed
        """
        self.log.warn("Ignoring unrecognized received data", {"raw": data.hex()})
    
    def on_key_status(self, listener: Callable[[KeyStatus], None]) -> None:
        """Register a listener for key status updates.
        
        Args:
            listener: Function to call when key status is received
        """
        self.on(Events.STATUS_UPDATE, listener)
    
    # Convenience methods for common operations
    
    async def get_room_count(self) -> int:
        """Get the number of rooms in the system.
        
        Returns:
            Number of rooms
        """
        response = await self.send(RoomCount())
        return response.room_count
    
    async def get_node_count(self) -> int:
        """Get the number of nodes in the system.
        
        Returns:
            Number of nodes
        """
        response = await self.send(NodeCount())
        return response.node_count
    
    async def get_room_metadata(self, room_id: int) -> RoomMetaDataResponse:
        """Get metadata for a specific room.
        
        Args:
            room_id: ID of the room
            
        Returns:
            Room metadata response
        """
        response = await self.send(RoomMetaData(room_id))
        return response
    
    async def get_node_metadata(self, node_id: int) -> NodeMetaDataResponse:
        """Get metadata for a specific node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Node metadata response
        """
        response = await self.send(NodeMetaData(node_id))
        return response
    
    async def get_key_status(self, node_id: int, key_id: int) -> KeyStatusResponse:
        """Get the status of a specific key.
        
        Args:
            node_id: ID of the node
            key_id: ID of the key
            
        Returns:
            Key status response
        """
        response = await self.send(KeyStatusRequest(node_id, key_id))
        return response
    
    async def get_key_parameters(self, node_id: int, key_id: int) -> KeyParametersResponse:
        """Get the parameters of a specific key.
        
        Args:
            node_id: ID of the node
            key_id: ID of the key
            
        Returns:
            Key parameters response
        """
        response = await self.send(KeyParameters(node_id, key_id))
        return response
    
    async def get_node_status(self, node_id: int) -> Acknowledgement:
        """Get the status of a specific node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Acknowledgement response (NodeStatus doesn't have a specific response class)
        """
        response = await self.send(NodeStatus(node_id))
        return response
    
    async def get_internal_unit_statuses(self) -> InternalUnitStatusesResponse:
        """Get internal unit statuses.
        
        Returns:
            Internal unit statuses response
        """
        response = await self.send(InternalUnitStatuses())
        return response
    
    async def toggle_key(
        self,
        node_id: int,
        key_id: int,
        power_status: KeyPowerStatus,
        timer: Optional[int] = None,
        dimmer_ratio: Optional[int] = None
    ) -> Acknowledgement:
        """Toggle a key with specified parameters.
        
        Args:
            node_id: ID of the node
            key_id: ID of the key
            power_status: Desired power status (ON, OFF, RELEASED)
            timer: Optional timer value in seconds
            dimmer_ratio: Optional dimmer ratio (0-100)
            
        Returns:
            Acknowledgement response
        """
        response = await self.send(ToggleKeyStatus(
            node_id, key_id, power_status, dimmer_ratio or 0, timer or 0
        ))
        return response
    
    async def turn_key_on(self, node_id: int, key_id: int, dimmer_ratio: Optional[int] = None) -> Acknowledgement:
        """Turn a key on.
        
        Args:
            node_id: ID of the node
            key_id: ID of the key
            dimmer_ratio: Optional dimmer ratio (0-100)
            
        Returns:
            Acknowledgement response
        """
        return await self.toggle_key(node_id, key_id, KeyPowerStatus.ON, dimmer_ratio=dimmer_ratio or 0)
    
    async def turn_key_off(self, node_id: int, key_id: int) -> Acknowledgement:
        """Turn a key off.
        
        Args:
            node_id: ID of the node
            key_id: ID of the key
            
        Returns:
            Acknowledgement response
        """
        return await self.toggle_key(node_id, key_id, KeyPowerStatus.OFF)
    
    async def release_key(self, node_id: int, key_id: int) -> Acknowledgement:
        """Release a key (momentary action).
        
        Args:
            node_id: ID of the node
            key_id: ID of the key
            
        Returns:
            Acknowledgement response
        """
        return await self.toggle_key(node_id, key_id, KeyPowerStatus.RELEASED)
    
    async def send_heartbeat(self) -> Acknowledgement:
        """Send a manual heartbeat.
        
        Returns:
            Acknowledgement response
        """
        response = await self.send(Heartbeat())
        return response
    
    @classmethod
    def create(
        cls,
        connection_config: Optional[Dict[str, Any]] = None,
        socket_config: Optional[Dict[str, Any]] = None
    ) -> "VitreaClient":
        """Create a VitreaClient instance with configuration.
        
        Args:
            connection_config: Optional connection configuration overrides
            socket_config: Optional socket configuration overrides
            
        Returns:
            Configured VitreaClient instance
        """
        from .config import ConnectionConfigParser, SocketConfigParser
        
        parsed_connection_config = ConnectionConfigParser.create(connection_config or {})
        parsed_socket_config = SocketConfigParser.create(socket_config or {})
        
        def redact(text: str) -> str:
            if len(text) <= 2:
                return "*" * len(text)
            return f"{text[0]}***{text[-1]}"
        
        instance = cls(parsed_connection_config, parsed_socket_config)
        
        instance.log.debug("VitreaClient instance created", {
            "connection": {
                "host": parsed_connection_config.host,
                "username": redact(parsed_connection_config.username),
                "password": redact(parsed_connection_config.password),
                "port": parsed_connection_config.port,
                "version": parsed_connection_config.version.value,
            },
            "socket": {
                "should_reconnect": parsed_socket_config.should_reconnect,
                "request_buffer": parsed_socket_config.request_buffer,
                "request_timeout": parsed_socket_config.request_timeout,
                "ignore_ack_logs": parsed_socket_config.ignore_ack_logs,
            },
        })
        
        return instance 