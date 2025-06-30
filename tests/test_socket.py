"""Tests for socket communication components."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from vitrea_client.socket import (
    Timeout, SplitMultipleBuffers, AbstractHeartbeatHandler, 
    VitreaHeartbeatHandler, AbstractSocket, WritableSocketProtocol
)
from vitrea_client.vitrea_client import VitreaClient
from vitrea_client.exceptions import TimeoutException, ConnectionExistsException, NoConnectionException
from vitrea_client.config import ConnectionConfig, SocketConfig, ProtocolVersion
from vitrea_client.core import NullLogger
from vitrea_client.requests import Heartbeat, RoomCount
from vitrea_client.responses import RoomCount as RoomCountResponse


class TestTimeout:
    """Test cases for Timeout class."""
    
    @pytest.mark.asyncio
    async def test_timeout_creation_and_start(self):
        """Test timeout creation and automatic start."""
        callback = Mock()
        timeout = Timeout.create(0.1, "Test timeout", callback)
        
        assert timeout.interval == 0.1
        assert timeout.message == "Test timeout"
        assert timeout.on_timeout == callback
        assert timeout._task is not None
        
        timeout.stop()
    
    @pytest.mark.asyncio
    async def test_timeout_triggers_callback_and_exception(self):
        """Test that timeout triggers callback and raises exception."""
        callback = Mock()
        timeout = Timeout(0.1, "Test timeout", callback)
        
        # Start the timeout and wait for it to trigger
        timeout.start()
        
        # Wait longer than the timeout period
        await asyncio.sleep(0.2)
        
        # The callback should have been called
        callback.assert_called_once()
        
        # The task should be done due to the exception
        assert timeout._task is not None
        assert timeout._task.done()
    
    @pytest.mark.asyncio
    async def test_timeout_stop_prevents_exception(self):
        """Test that stopping timeout prevents exception."""
        callback = Mock()
        timeout = Timeout(0.1, "Test timeout", callback)
        timeout.start()
        
        # Stop before timeout
        await asyncio.sleep(0.05)
        timeout.stop()
        
        # Wait past timeout period
        await asyncio.sleep(0.1)
        
        # Should not have been called
        callback.assert_not_called()
    
    def test_timeout_default_message(self):
        """Test timeout with default message."""
        timeout = Timeout.create(1.0)
        assert timeout.message == "Timeout reached after 1.0 seconds"


class TestSplitMultipleBuffers:
    """Test cases for SplitMultipleBuffers utility."""
    
    def test_single_buffer(self):
        """Test handling of single buffer."""
        buffer = bytes([0x56, 0x54, 0x55, 0x3C, 0x01, 0x02, 0x03])
        result = SplitMultipleBuffers.handle(buffer)
        
        assert len(result) == 1
        assert result[0] == buffer
    
    def test_multiple_buffers(self):
        """Test splitting multiple buffers."""
        # Two buffers concatenated
        buffer1 = bytes([0x56, 0x54, 0x55, 0x3C, 0x01, 0x02, 0x03])
        buffer2 = bytes([0x56, 0x54, 0x55, 0x3C, 0x04, 0x05, 0x06])
        combined = buffer1 + buffer2
        
        result = SplitMultipleBuffers.handle(combined)
        
        assert len(result) == 2
        assert result[0] == buffer1
        assert result[1] == buffer2
    
    def test_three_buffers(self):
        """Test splitting three buffers."""
        buffer1 = bytes([0x56, 0x54, 0x55, 0x3C, 0x01])
        buffer2 = bytes([0x56, 0x54, 0x55, 0x3C, 0x02])
        buffer3 = bytes([0x56, 0x54, 0x55, 0x3C, 0x03])
        combined = buffer1 + buffer2 + buffer3
        
        result = SplitMultipleBuffers.handle(combined)
        
        assert len(result) == 3
        assert result[0] == buffer1
        assert result[1] == buffer2
        assert result[2] == buffer3
    
    def test_empty_buffer(self):
        """Test handling of empty buffer."""
        result = SplitMultipleBuffers.handle(b'')
        assert result == []
    
    def test_buffer_without_prefix(self):
        """Test buffer that doesn't contain the prefix."""
        buffer = bytes([0x01, 0x02, 0x03, 0x04])
        result = SplitMultipleBuffers.handle(buffer)
        
        # Should return empty list as no valid prefix found
        assert result == []


class MockWritableSocket:
    """Mock writable socket for testing."""
    
    def __init__(self):
        self.written_data = []
        self.should_fail = False
    
    async def write(self, data: bytes) -> None:
        if self.should_fail:
            raise Exception("Mock write failure")
        self.written_data.append(data)


class TestAbstractHeartbeatHandler:
    """Test cases for AbstractHeartbeatHandler."""
    
    class ConcreteHeartbeatHandler(AbstractHeartbeatHandler):
        def get_heartbeat_datagram(self) -> bytes:
            return b"heartbeat"
    
    @pytest.mark.asyncio
    async def test_heartbeat_initialization(self):
        """Test heartbeat handler initialization."""
        socket = MockWritableSocket()
        handler = self.ConcreteHeartbeatHandler(1.0, socket)
        
        assert handler.interval == 1.0
        assert handler.socket == socket
        assert handler.is_paused
    
    @pytest.mark.asyncio
    async def test_heartbeat_restart_and_pause(self):
        """Test heartbeat restart and pause functionality."""
        socket = MockWritableSocket()
        handler = self.ConcreteHeartbeatHandler(0.1, socket)
        
        # Start heartbeat
        handler.restart()
        assert not handler.is_paused
        
        # Wait for at least one heartbeat
        await asyncio.sleep(0.15)
        assert len(socket.written_data) >= 1
        assert socket.written_data[0] == b"heartbeat"
        
        # Pause heartbeat
        handler.pause()
        assert handler.is_paused
        
        # Clear data and wait
        socket.written_data.clear()
        await asyncio.sleep(0.15)
        
        # Should not have written more data
        assert len(socket.written_data) == 0
    
    @pytest.mark.asyncio
    async def test_heartbeat_failure_pauses(self):
        """Test that heartbeat failure causes pause."""
        socket = MockWritableSocket()
        socket.should_fail = True
        handler = self.ConcreteHeartbeatHandler(0.1, socket)
        
        handler.restart()
        
        # Wait for heartbeat attempt
        await asyncio.sleep(0.15)
        
        # Should be paused due to failure
        assert handler.is_paused


class TestVitreaHeartbeatHandler:
    """Test cases for VitreaHeartbeatHandler."""
    
    @pytest.mark.asyncio
    async def test_vitrea_heartbeat_creation(self):
        """Test VitreaHeartbeatHandler creation."""
        socket = MockWritableSocket()
        handler = VitreaHeartbeatHandler(socket)
        
        assert handler.interval == 3.0
        assert handler.socket == socket
    
    def test_vitrea_heartbeat_datagram(self):
        """Test VitreaHeartbeatHandler datagram generation."""
        socket = MockWritableSocket()
        handler = VitreaHeartbeatHandler(socket)
        
        datagram = handler.get_heartbeat_datagram()
        expected = Heartbeat().build()
        
        # Both should be valid heartbeat datagrams with same structure
        # but may have different message IDs due to MessageID state
        assert len(datagram) == len(expected)
        assert datagram[:7] == expected[:7]  # Same prefix, direction, command
        # Skip message ID comparison (index 7)
        assert datagram[9:] == expected[9:]  # Same checksum calculation structure
    
    @pytest.mark.asyncio
    async def test_vitrea_heartbeat_create_and_start(self):
        """Test VitreaHeartbeatHandler.create() method."""
        socket = MockWritableSocket()
        handler = VitreaHeartbeatHandler.create(socket)
        
        assert not handler.is_paused
        
        # Clean up
        handler.pause()


class MockAbstractSocket(AbstractSocket):
    """Mock implementation of AbstractSocket for testing."""
    
    def __init__(self, host: str, port: int, socket_config: SocketConfig):
        super().__init__(host, port, socket_config)
        self.received_data = []
        self.unknown_data = []
    
    async def _handle_data(self, data: bytes) -> None:
        self.received_data.append(data)
    
    async def _handle_unknown_data(self, data: bytes) -> None:
        self.unknown_data.append(data)


class TestAbstractSocket:
    """Test cases for AbstractSocket."""
    
    def test_abstract_socket_initialization(self):
        """Test AbstractSocket initialization."""
        config = SocketConfig(
            log=NullLogger(),
            ignore_ack_logs=False,
            should_reconnect=True,
            request_buffer=0.25,
            request_timeout=10.0,
            socket_supplier=None
        )
        
        socket = MockAbstractSocket("localhost", 8080, config)
        
        assert socket.host == "localhost"
        assert socket.port == 8080
        assert socket.socket_config == config
        assert socket.log == config.log
    
    @pytest.mark.asyncio
    async def test_connection_exists_exception(self):
        """Test ConnectionExistsException when already connected."""
        config = SocketConfig(
            log=NullLogger(),
            ignore_ack_logs=False,
            should_reconnect=True,
            request_buffer=0.25,
            request_timeout=10.0,
            socket_supplier=None
        )
        
        socket = MockAbstractSocket("localhost", 8080, config)
        socket._socket = Mock()  # Simulate existing connection
        
        with pytest.raises(ConnectionExistsException):
            await socket.connect()
    
    @pytest.mark.asyncio
    async def test_write_without_connection(self):
        """Test writing without connection raises NoConnectionException."""
        config = SocketConfig(
            log=NullLogger(),
            ignore_ack_logs=False,
            should_reconnect=True,
            request_buffer=0.25,
            request_timeout=10.0,
            socket_supplier=None
        )
        
        socket = MockAbstractSocket("localhost", 8080, config)
        
        with pytest.raises(NoConnectionException):
            await socket.write(b"test data")
    
    def test_event_handling(self):
        """Test event listener functionality."""
        config = SocketConfig(
            log=NullLogger(),
            ignore_ack_logs=False,
            should_reconnect=True,
            request_buffer=0.25,
            request_timeout=10.0,
            socket_supplier=None
        )
        
        socket = MockAbstractSocket("localhost", 8080, config)
        
        # Test event listeners
        listener1 = Mock()
        listener2 = Mock()
        
        socket.on("test_event", listener1)
        socket.on("test_event", listener2)
        
        socket.emit("test_event", "arg1", "arg2", kwarg1="value1")
        
        listener1.assert_called_once_with("arg1", "arg2", kwarg1="value1")
        listener2.assert_called_once_with("arg1", "arg2", kwarg1="value1")
    
    def test_once_event_handling(self):
        """Test one-time event listener functionality."""
        config = SocketConfig(
            log=NullLogger(),
            ignore_ack_logs=False,
            should_reconnect=True,
            request_buffer=0.25,
            request_timeout=10.0,
            socket_supplier=None
        )
        
        socket = MockAbstractSocket("localhost", 8080, config)
        
        listener = Mock()
        socket.once("test_event", listener)
        
        # First emit should call listener
        socket.emit("test_event", "arg1")
        listener.assert_called_once_with("arg1")
        
        # Second emit should not call listener again
        listener.reset_mock()
        socket.emit("test_event", "arg2")
        listener.assert_not_called()
    
    def test_remove_listener(self):
        """Test removing event listeners."""
        config = SocketConfig(
            log=NullLogger(),
            ignore_ack_logs=False,
            should_reconnect=True,
            request_buffer=0.25,
            request_timeout=10.0,
            socket_supplier=None
        )
        
        socket = MockAbstractSocket("localhost", 8080, config)
        
        listener = Mock()
        socket.on("test_event", listener)
        
        # Remove listener
        socket.remove_listener("test_event", listener)
        
        # Should not be called
        socket.emit("test_event", "arg1")
        listener.assert_not_called()


class TestVitreaClient:
    """Test cases for VitreaClient."""
    
    def test_vitrea_client_creation(self):
        """Test VitreaClient creation with default configuration."""
        client = VitreaClient.create()
        
        assert isinstance(client, VitreaClient)
        assert client.connection_config.host == "192.168.1.23"
        assert client.connection_config.port == 11501
        assert client.connection_config.version == ProtocolVersion.V2
    
    def test_vitrea_client_with_custom_config(self):
        """Test VitreaClient creation with custom configuration."""
        connection_config = {
            "host": "192.168.1.100",
            "port": 12345,
            "username": "test_user",
            "password": "test_pass",
            "version": "v1"
        }
        
        socket_config = {
            "request_timeout": 5.0,
            "request_buffer": 0.5,
            "should_reconnect": False
        }
        
        client = VitreaClient.create(connection_config, socket_config)
        
        assert client.connection_config.host == "192.168.1.100"
        assert client.connection_config.port == 12345
        assert client.connection_config.username == "test_user"
        assert client.connection_config.password == "test_pass"
        assert client.connection_config.version == ProtocolVersion.V1
        assert client.socket_config.request_timeout == 5.0
        assert client.socket_config.request_buffer == 0.5
        assert client.socket_config.should_reconnect == False
    
    def test_should_log_response(self):
        """Test response logging logic."""
        from vitrea_client.responses import Acknowledgement, GenericUnusedResponse
        
        client = VitreaClient.create()
        
        # Normal response should be logged
        normal_response = RoomCountResponse(b'\x56\x54\x55\x3c\x1d\x00\x00\x00\x01\x02\x03')
        assert client._should_log_response(normal_response) == True
        
        # With ignore_ack_logs=False, ack responses should be logged
        client.socket_config.ignore_ack_logs = False
        ack_response = Acknowledgement(b'\x56\x54\x55\x3c\x00\x00\x00\x00\x01\x02\x03')
        assert client._should_log_response(ack_response) == True
        
        # With ignore_ack_logs=True, ack responses should not be logged
        client.socket_config.ignore_ack_logs = True
        assert client._should_log_response(ack_response) == False
        assert client._should_log_response(GenericUnusedResponse(b'\x56\x54\x55\x3c\x00\x00\x00\x00\x01\x02\x03')) == False
    
    def test_on_key_status_listener(self):
        """Test key status event listener registration."""
        client = VitreaClient.create()
        
        listener = Mock()
        client.on_key_status(listener)
        
        # Verify listener is registered for STATUS_UPDATE event
        from vitrea_client.utilities import Events
        assert Events.STATUS_UPDATE in client._event_listeners
        assert listener in client._event_listeners[Events.STATUS_UPDATE]
    
    @pytest.mark.asyncio
    async def test_split_multiple_buffers_handling(self):
        """Test that VitreaClient properly handles multiple buffers."""
        client = VitreaClient.create()
        
        # Mock the _process_single_buffer method
        client._process_single_buffer = AsyncMock()
        
        # Create test data with multiple buffers
        buffer1 = bytes([0x56, 0x54, 0x55, 0x3C, 0x01, 0x02, 0x03])
        buffer2 = bytes([0x56, 0x54, 0x55, 0x3C, 0x04, 0x05, 0x06])
        combined = buffer1 + buffer2
        
        await client._handle_data(combined)
        
        # Should have called _process_single_buffer twice
        assert client._process_single_buffer.call_count == 2
        client._process_single_buffer.assert_any_call(buffer1)
        client._process_single_buffer.assert_any_call(buffer2) 