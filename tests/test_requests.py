"""Tests for request classes."""

import pytest

from vitrea_client.constants import CommandID
from vitrea_client.utilities.enums import KeyPowerStatus
from vitrea_client.requests import (
    AcknowledgeRequest,
    Heartbeat,
    InternalUnitStatuses,
    KeyParameters,
    KeyStatus,
    Login,
    NodeCount,
    NodeMetaData,
    NodeStatus,
    RoomCount,
    RoomMetaData,
    ToggleHeartbeat,
    ToggleKeyStatus,
)


class TestAcknowledgeRequest:
    """Test AcknowledgeRequest class."""
    
    def test_event_name(self):
        """Test event name generation."""
        request = AcknowledgeRequest(0x01)
        assert "data" in request.event_name
        # Message ID is formatted as hex (0x0f -> "0f")
        assert f"{request.message_id:02x}" in request.event_name.lower()


class TestSimpleRequests:
    """Test simple request classes without parameters."""
    
    def test_room_count(self):
        """Test RoomCount request."""
        request = RoomCount()
        assert request.command_id == CommandID.ROOM_COUNT
        assert request.data == []
    
    def test_node_count(self):
        """Test NodeCount request."""
        request = NodeCount()
        assert request.command_id == CommandID.NODE_COUNT
        assert request.data == []
    
    def test_internal_unit_statuses(self):
        """Test InternalUnitStatuses request."""
        request = InternalUnitStatuses()
        assert request.command_id == CommandID.INTERNAL_UNIT_STATUSES
        assert request.data == []
    
    def test_heartbeat(self):
        """Test Heartbeat request."""
        request = Heartbeat()
        assert request.command_id == 0x07
        assert request.data == []


class TestParameterizedRequests:
    """Test request classes that take parameters."""
    
    def test_node_meta_data(self):
        """Test NodeMetaData request."""
        request = NodeMetaData(5)
        assert request.command_id == CommandID.NODE_META_DATA
        assert request.data == [5]
    
    def test_room_meta_data(self):
        """Test RoomMetaData request."""
        request = RoomMetaData(3)
        assert request.command_id == CommandID.ROOM_META_DATA
        assert request.data == [3]
    
    def test_key_status(self):
        """Test KeyStatus request."""
        request = KeyStatus(1, 2)
        assert request.command_id == CommandID.KEY_STATUS
        assert request.data == [1, 2]
        assert request.event_name == "vitrea::status::update"
    
    def test_key_parameters(self):
        """Test KeyParameters request."""
        request = KeyParameters(1, 2)
        assert request.command_id == CommandID.KEY_PARAMETERS
        assert request.data == [1, 2]
    
    def test_node_status(self):
        """Test NodeStatus request."""
        request = NodeStatus(7)
        assert request.command_id == 0x25
        assert request.data == [7]


class TestToggleHeartbeat:
    """Test ToggleHeartbeat request."""
    
    def test_default_parameters(self):
        """Test with default parameters."""
        request = ToggleHeartbeat()
        assert request.command_id == 0x08
        assert request.data == [1, 1]  # enable=True, unsolicited=True
    
    def test_custom_parameters(self):
        """Test with custom parameters."""
        request = ToggleHeartbeat(enable=False, unsolicited=True)
        assert request.command_id == 0x08
        assert request.data == [0, 1]  # enable=False, unsolicited=True


class TestToggleKeyStatus:
    """Test ToggleKeyStatus request."""
    
    def test_basic_toggle(self):
        """Test basic key toggle."""
        request = ToggleKeyStatus(1, 2, KeyPowerStatus.ON)
        assert request.command_id == 0x28
        assert request.data == [1, 2, KeyPowerStatus.ON, 0, 0, 0]  # timer=0 -> [0, 0]
    
    def test_with_dimmer_and_timer(self):
        """Test with dimmer ratio and timer."""
        request = ToggleKeyStatus(1, 2, KeyPowerStatus.ON, dimmer_ratio=50, timer=300)
        assert request.command_id == 0x28
        # timer=300 -> high byte: 300>>8=1, low byte: 300&0xFF=44
        assert request.data == [1, 2, KeyPowerStatus.ON, 50, 1, 44]
    
    def test_event_name(self):
        """Test event name generation."""
        request = ToggleKeyStatus(1, 2, KeyPowerStatus.ON)
        assert "data" in request.event_name
        # Message ID is formatted as hex (0x0f -> "0f")
        assert f"{request.message_id:02x}" in request.event_name.lower()


class TestLogin:
    """Test Login request."""
    
    def test_login_encoding(self):
        """Test login with username and password."""
        request = Login("user", "pass")
        assert request.command_id == 0x01
        
        # Expected data: [0x0a] + utf16le(user) + [0x0a] + utf16le(pass)
        expected_data = [0x0a]
        expected_data.extend(list("user".encode('utf-16le')))
        expected_data.append(0x0a)
        expected_data.extend(list("pass".encode('utf-16le')))
        
        assert request.data == expected_data
    
    def test_login_event_name(self):
        """Test login event name."""
        request = Login("user", "pass")
        assert "data" in request.event_name


class TestRequestSerialization:
    """Test request serialization."""
    
    def test_request_to_buffer(self):
        """Test converting request to buffer."""
        request = RoomCount()
        buffer = list(request.build())
        
        # Check prefix
        assert buffer[:3] == [0x56, 0x54, 0x55]
        # Check direction (outgoing)
        assert buffer[3] == 0x3E
        # Check command
        assert buffer[4] == CommandID.ROOM_COUNT
    
    def test_request_with_data_to_buffer(self):
        """Test converting request with data to buffer."""
        request = NodeMetaData(5)
        buffer = list(request.build())
        
        # Check prefix
        assert buffer[:3] == [0x56, 0x54, 0x55]
        # Check direction (outgoing)
        assert buffer[3] == 0x3E
        # Check command
        assert buffer[4] == CommandID.NODE_META_DATA
        # Check data
        assert 5 in buffer[8:]  # Data starts at index 8 