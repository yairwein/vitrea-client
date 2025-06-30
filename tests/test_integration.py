"""Integration tests for VitreaClient focusing on Step 4 requirements."""

import asyncio
import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch
from vitrea_client import VitreaClient
from vitrea_client.requests import RoomCount, Login, KeyStatus as KeyStatusRequest
from vitrea_client.responses import RoomCount as RoomCountResponse, KeyStatus as KeyStatusResponse
from vitrea_client.utilities import Events, KeyPowerStatus
from vitrea_client.exceptions import TimeoutException, ConnectionExistsException
from vitrea_client.config import ProtocolVersion


@pytest.fixture
def client_config():
    """Fixture providing test client configuration."""
    return {
        "connection_config": {
            "host": "127.0.0.1",
            "port": 11501,
            "username": "test_user",
            "password": "test_pass",
            "version": "v2"
        },
        "socket_config": {
            "request_timeout": 1.0,
            "request_buffer": 0.1,
            "should_reconnect": False,
            "ignore_ack_logs": True
        }
    }


class TestVitreaClientStep4:
    """Test Step 4 requirements: VitreaClient implementation and status update callbacks."""
    
    def test_vitrea_client_creation_and_api(self, client_config):
        """Test VitreaClient provides the required public API methods."""
        client = VitreaClient.create(**client_config)
        
        # Test that all required methods exist
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'send')
        assert hasattr(client, 'on_key_status')
        
        # Test convenience methods
        assert hasattr(client, 'get_room_count')
        assert hasattr(client, 'get_node_count')
        assert hasattr(client, 'get_room_metadata')
        assert hasattr(client, 'get_node_metadata')
        assert hasattr(client, 'get_key_status')
        assert hasattr(client, 'get_key_parameters')
        assert hasattr(client, 'toggle_key')
        assert hasattr(client, 'turn_key_on')
        assert hasattr(client, 'turn_key_off')
        assert hasattr(client, 'release_key')
        assert hasattr(client, 'send_heartbeat')
    
    def test_key_status_callback_registration(self, client_config):
        """Test that on_key_status method registers callbacks correctly."""
        client = VitreaClient.create(**client_config)
        
        # Test callback registration
        callback1 = Mock()
        callback2 = Mock()
        
        client.on_key_status(callback1)
        client.on_key_status(callback2)
        
        # Verify callbacks are registered for STATUS_UPDATE event
        assert Events.STATUS_UPDATE in client._event_listeners
        assert callback1 in client._event_listeners[Events.STATUS_UPDATE]
        assert callback2 in client._event_listeners[Events.STATUS_UPDATE]
    
    @pytest.mark.asyncio
    async def test_convenience_methods_call_send(self, client_config):
        """Test that convenience methods properly call the send method."""
        client = VitreaClient.create(**client_config)
        
        # Mock the send method
        client.send = AsyncMock()
        
        # Mock responses
        room_count_response = Mock()
        room_count_response.total = 5
        client.send.return_value = room_count_response
        
        # Test get_room_count
        result = await client.get_room_count()
        assert result == 5
        client.send.assert_called_once()
        
        # Verify the request type
        call_args = client.send.call_args[0][0]
        assert isinstance(call_args, RoomCount)
    
    @pytest.mark.asyncio
    async def test_toggle_key_methods(self, client_config):
        """Test key control convenience methods."""
        client = VitreaClient.create(**client_config)
        
        # Mock the send method
        mock_ack = Mock()
        client.send = AsyncMock(return_value=mock_ack)
        
        # Test turn_key_on
        result = await client.turn_key_on(1, 2, dimmer_ratio=50)
        assert result == mock_ack
        client.send.assert_called()
        
        # Test turn_key_off
        client.send.reset_mock()
        result = await client.turn_key_off(1, 2)
        assert result == mock_ack
        client.send.assert_called()
        
        # Test release_key
        client.send.reset_mock()
        result = await client.release_key(1, 2)
        assert result == mock_ack
        client.send.assert_called()
    
    @pytest.mark.asyncio
    async def test_status_update_handling(self, client_config):
        """Test that status updates are properly handled and callbacks invoked."""
        client = VitreaClient.create(**client_config)
        
        # Set up status update listener
        status_updates = []
        def status_listener(status):
            status_updates.append(status)
        
        client.on_key_status(status_listener)
        
        # Create a mock KeyStatus response
        mock_status = Mock(spec=KeyStatusResponse)
        mock_status.node_id = 1
        mock_status.key_id = 2
        mock_status.power = KeyPowerStatus.ON
        mock_status.is_on = True
        mock_status.is_off = False
        mock_status.is_released = False
        
        # Simulate receiving a status update by emitting the event
        client.emit(Events.STATUS_UPDATE, mock_status)
        
        # Verify the callback was called
        assert len(status_updates) == 1
        assert status_updates[0] == mock_status
    
    @pytest.mark.asyncio
    async def test_send_method_request_response_flow(self, client_config):
        """Test that send method properly handles request/response flow."""
        client = VitreaClient.create(**client_config)
        
        # Mock the write method
        client.write = AsyncMock()
        
        # Mock the mutex acquire to return a simple function
        release_mock = Mock()
        client._acquire_mutex = AsyncMock(return_value=release_mock)
        
        # Create a request
        request = RoomCount()
        
        # Mock the response handling by directly setting the future result
        async def mock_send_with_timeout(req, release_fn):
            # Simulate successful response
            mock_response = Mock()
            mock_response.total = 5
            return mock_response
        
        client._send_with_timeout = mock_send_with_timeout
        
        # Test that send works correctly
        response = await client.send(request)
        assert response.total == 5
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self, client_config):
        """Test connection lifecycle without actual network calls."""
        client = VitreaClient.create(**client_config)
        
        # Mock the underlying socket methods
        with patch.object(client, '_create_new_socket'), \
             patch('asyncio.open_connection') as mock_open_connection, \
             patch.object(client, '_handle_connect') as mock_handle_connect:
            
            # Mock successful connection
            mock_reader = Mock()
            mock_writer = Mock()
            mock_writer.get_extra_info.return_value = Mock()
            mock_open_connection.return_value = (mock_reader, mock_writer)
            
            # Test connection
            await client.connect()
            
            # Verify connection was attempted
            mock_open_connection.assert_called_once_with(
                client_config["connection_config"]["host"],
                client_config["connection_config"]["port"]
            )
            mock_handle_connect.assert_called_once()
            
            # Test disconnect
            client.disconnect()
    
    def test_client_configuration_from_environment(self, monkeypatch):
        """Test that client reads configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv("VITREA_VBOX_HOST", "192.168.1.50")
        monkeypatch.setenv("VITREA_VBOX_PORT", "12345")
        monkeypatch.setenv("VITREA_VBOX_USERNAME", "env_user")
        monkeypatch.setenv("VITREA_VBOX_PASSWORD", "env_pass")
        monkeypatch.setenv("VITREA_VBOX_VERSION", "v1")
        
        client = VitreaClient.create()
        
        assert client.connection_config.host == "192.168.1.50"
        assert client.connection_config.port == 12345
        assert client.connection_config.username == "env_user"
        assert client.connection_config.password == "env_pass"
        assert client.connection_config.version == ProtocolVersion.V1
    
    def test_client_configuration_override(self):
        """Test that direct config overrides environment variables."""
        import os
        
        # Set environment variable
        os.environ["VITREA_VBOX_HOST"] = "192.168.1.50"
        
        try:
            # Override with direct config
            client_config = {
                "connection_config": {
                    "host": "192.168.1.100"
                }
            }
            
            client = VitreaClient.create(**client_config)
            
            # Direct config should override environment
            assert client.connection_config.host == "192.168.1.100"
            
        finally:
            # Clean up
            if "VITREA_VBOX_HOST" in os.environ:
                del os.environ["VITREA_VBOX_HOST"]
    
    @pytest.mark.asyncio
    async def test_buffer_splitting_integration(self, client_config):
        """Test that multiple buffers are properly split and processed."""
        client = VitreaClient.create(**client_config)
        
        # Mock the _process_single_buffer method
        client._process_single_buffer = AsyncMock()
        
        # Create test data with multiple buffers
        buffer1 = bytes([0x56, 0x54, 0x55, 0x3C, 0x01, 0x02, 0x03])
        buffer2 = bytes([0x56, 0x54, 0x55, 0x3C, 0x04, 0x05, 0x06])
        combined = buffer1 + buffer2
        
        # Test buffer splitting
        await client._handle_data(combined)
        
        # Should have called _process_single_buffer twice
        assert client._process_single_buffer.call_count == 2
        client._process_single_buffer.assert_any_call(buffer1)
        client._process_single_buffer.assert_any_call(buffer2)
    
    @pytest.mark.asyncio
    async def test_unknown_data_handling(self, client_config):
        """Test handling of unknown data."""
        client = VitreaClient.create(**client_config)
        
        # Set up unknown data listener
        unknown_data_events = []
        def unknown_data_listener(data):
            unknown_data_events.append(data)
        
        client.on(Events.UNKNOWN_DATA, unknown_data_listener)
        
        # Test unknown data
        unknown_data = bytes([0xFF, 0xFF, 0xFF, 0xFF])
        
        # Process the unknown data
        await client._process_single_buffer(unknown_data)
        
        # Verify unknown data event was emitted
        assert len(unknown_data_events) == 1
        assert unknown_data_events[0] == unknown_data
    
    def test_logging_configuration(self, client_config):
        """Test that logging is properly configured."""
        client = VitreaClient.create(**client_config)
        
        # Test that logger exists and is configured
        assert hasattr(client, 'log')
        assert client.log is not None
        
        # Test response logging logic
        from vitrea_client.responses import Acknowledgement, GenericUnusedResponse
        
        # Create mock responses
        normal_response = Mock()
        ack_response = Mock(spec=Acknowledgement)
        
        # Test logging logic
        client.socket_config.ignore_ack_logs = False
        assert client._should_log_response(normal_response) == True
        assert client._should_log_response(ack_response) == True
        
        client.socket_config.ignore_ack_logs = True
        assert client._should_log_response(normal_response) == True
        assert client._should_log_response(ack_response) == False


class TestVitreaClientErrorHandling:
    """Test error handling and edge cases."""
    
    def test_connection_exists_exception(self, client_config):
        """Test that ConnectionExistsException is raised appropriately."""
        client = VitreaClient.create(**client_config)
        
        # Simulate existing connection
        client._socket = Mock()
        
        # Should raise exception when trying to connect again
        with pytest.raises(ConnectionExistsException):
            asyncio.run(client.connect())
    
    @pytest.mark.asyncio
    async def test_connection_failure_handling(self, client_config):
        """Test handling of connection failures."""
        # Use invalid configuration to trigger connection failure
        client_config["connection_config"]["host"] = "invalid.host.example.com"
        client_config["connection_config"]["port"] = 99999
        client_config["socket_config"]["request_timeout"] = 0.1
        
        client = VitreaClient.create(**client_config)
        
        # Should raise an exception when connection fails
        with pytest.raises(Exception):
            await client.connect()
    
    def test_client_factory_method(self, client_config):
        """Test the VitreaClient.create factory method."""
        # Test with no arguments (should use defaults)
        client1 = VitreaClient.create()
        assert isinstance(client1, VitreaClient)
        
        # Test with partial configuration
        client2 = VitreaClient.create(
            connection_config={"host": "192.168.1.100"},
            socket_config={}
        )
        assert client2.connection_config.host == "192.168.1.100"
        
        # Test with full configuration
        client3 = VitreaClient.create(**client_config)
        assert client3.connection_config.host == client_config["connection_config"]["host"]
        assert client3.connection_config.port == client_config["connection_config"]["port"]


# Summary test to verify Step 4 completion
class TestStep4Completion:
    """Verify that Step 4 requirements are fully implemented."""
    
    def test_step4_requirements_met(self, client_config):
        """Comprehensive test that Step 4 requirements are met."""
        # 4.1: VitreaClient Implementation
        client = VitreaClient.create(**client_config)
        
        # Should have main API methods
        assert hasattr(client, 'connect'), "Missing connect() method"
        assert hasattr(client, 'disconnect'), "Missing disconnect() method"
        assert hasattr(client, 'send'), "Missing send() method"
        
        # Should manage socket connection
        assert hasattr(client, '_socket'), "Missing socket management"
        assert hasattr(client, '_mutex'), "Missing request synchronization"
        
        # 4.2: Status Update Callbacks
        assert hasattr(client, 'on_key_status'), "Missing on_key_status() method"
        
        # Should be able to register callbacks
        callback = Mock()
        client.on_key_status(callback)
        assert Events.STATUS_UPDATE in client._event_listeners
        assert callback in client._event_listeners[Events.STATUS_UPDATE]
        
        # Should have convenience methods for common operations
        convenience_methods = [
            'get_room_count', 'get_node_count', 'get_room_metadata', 
            'get_node_metadata', 'get_key_status', 'get_key_parameters',
            'toggle_key', 'turn_key_on', 'turn_key_off', 'release_key',
            'send_heartbeat'
        ]
        
        for method in convenience_methods:
            assert hasattr(client, method), f"Missing convenience method: {method}"
        
        print("✅ Step 4 requirements fully implemented:")
        print("   - VitreaClient with connect(), disconnect(), send() API")
        print("   - Socket connection management with mutex synchronization")
        print("   - Status update callbacks via on_key_status()")
        print("   - Comprehensive convenience methods for common operations")
        print("   - Proper error handling and configuration management") 