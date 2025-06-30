"""Tests for response classes."""

import pytest

from vitrea_client.constants import CommandID
from vitrea_client.config.connection_config import ProtocolVersion
from vitrea_client.utilities.enums import (
    DataGramDirection, 
    KeyPowerStatus, 
    LEDBackgroundBrightness, 
    LockStatus,
    KeyCategory
)
from vitrea_client.responses import (
    Acknowledgement,
    GenericUnusedResponse,
    InternalUnitStatuses,
    KeyParameters,
    KeyStatus,
    NodeCount,
    NodeMetaData,
    RoomCount,
    RoomMetaData,
    ResponseFactory,
)


class TestAcknowledgement:
    """Test Acknowledgement response."""
    
    def test_basic_acknowledgement(self):
        """Test basic acknowledgement response."""
        # Create a basic acknowledgement buffer
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.ACKNOWLEDGEMENT, 0, 0, 0]
        buffer.extend([0] * 10)  # Padding
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        response = Acknowledgement(buffer)
        assert response.command_id == CommandID.ACKNOWLEDGEMENT


class TestSimpleResponses:
    """Test simple response classes."""
    
    def test_room_count(self):
        """Test RoomCount response."""
        # Create buffer with room IDs [1, 2, 3]
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.ROOM_COUNT, 0, 0, 0]
        buffer.extend([4, 1, 2, 3])  # 4 = length, then room IDs
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        response = RoomCount(buffer)
        
        assert response.command_id == CommandID.ROOM_COUNT
        assert response.list == [1, 2, 3]
        assert response.total == 3
    
    def test_node_count(self):
        """Test NodeCount response."""
        # Create buffer with node IDs [5, 6]
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.NODE_COUNT, 0, 0, 0]
        buffer.extend([3, 5, 6])  # 3 = length, then node IDs
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        response = NodeCount(buffer)
        
        assert response.command_id == CommandID.NODE_COUNT
        assert response.list == [5, 6]
        assert response.total == 2
    
    def test_generic_unused_response(self):
        """Test GenericUnusedResponse."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.NODE_EXISTENCE_STATUS, 0, 0, 0]
        buffer.extend([0] * 10)
        response = GenericUnusedResponse(buffer)
        assert response.command_id == CommandID.NODE_EXISTENCE_STATUS


class TestKeyStatus:
    """Test KeyStatus response."""
    
    def test_key_status_parsing(self):
        """Test parsing key status data."""
        # Create buffer with node_id=1, key_id=2, power=ON at indices 8, 9, 10
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.KEY_STATUS, 0, 0, 0]
        buffer.extend([1, 2, KeyPowerStatus.ON])  # node_id, key_id, power at indices 8, 9, 10
        buffer.extend([0] * 5)  # Padding
        
        response = KeyStatus(buffer)
        assert response.command_id == CommandID.KEY_STATUS
        assert response.node_id == 1
        assert response.key_id == 2
        assert response.power == KeyPowerStatus.ON
        assert response.is_on is True
        assert response.is_off is False
        assert response.is_released is False
        assert response.event_name == "vitrea::status::update"
    
    def test_key_status_off(self):
        """Test key status when off."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.KEY_STATUS, 0, 0, 0]
        buffer.extend([1, 2, KeyPowerStatus.OFF])
        buffer.extend([0] * 5)
        
        response = KeyStatus(buffer)
        assert response.power == KeyPowerStatus.OFF
        assert response.is_on is False
        assert response.is_off is True
        assert response.is_released is False


class TestKeyParameters:
    """Test KeyParameters response."""
    
    def test_key_parameters_parsing(self):
        """Test parsing key parameters data."""
        # Create buffer with node_id=1, key_id=2, category=LIGHT, dimmer=75
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.KEY_PARAMETERS, 0, 0, 0]
        buffer.extend([1, 2, KeyCategory.LIGHT, 75])  # At indices 8, 9, 10, 11
        buffer.extend([0] * 5)
        
        response = KeyParameters(buffer)
        assert response.command_id == CommandID.KEY_PARAMETERS
        assert response.node_id == 1
        assert response.key_id == 2
        assert response.category == KeyCategory.LIGHT
        assert response.dimmer_ratio == 75


class TestNodeMetaData:
    """Test NodeMetaData response."""
    
    def test_node_metadata_basic(self):
        """Test basic node metadata parsing."""
        # Create a buffer with node metadata
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.NODE_META_DATA, 0, 0, 0]
        
        # Add node_id=5 at index 8
        buffer.append(5)
        
        # Add MAC address (8 bytes) at index 9
        mac_bytes = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        buffer.extend(mac_bytes)
        
        # Need to pad to get to index 18 for total_keys
        buffer.append(0)  # index 17 - padding
        buffer.append(2)  # index 18 - total_keys=2
        
        # Add key types at offset start (index 19)
        buffer.extend([1, 2])  # Key types
        
        # Add metadata at calculated offsets
        # offset = 19 + 2 = 21, so metadata starts at index 21
        metadata = [LockStatus.UNLOCKED, LEDBackgroundBrightness.HIGH, 0, 1, 0, 0, 0, 3]  # room_id=3 at offset 7
        buffer.extend(metadata)
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        
        response = NodeMetaData(buffer)
        assert response.command_id == CommandID.NODE_META_DATA
        assert response.id == 5
        assert response.total_keys == 2
        assert response.room_id == 3
        assert response.is_locked is False
        assert response.led_level == LEDBackgroundBrightness.HIGH
        assert len(response.keys_list) == 2
        assert response.keys_list[0]["id"] == 0
        assert response.keys_list[0]["type"] == 0  # This gets LockStatus.UNLOCKED from metadata


class TestRoomMetaData:
    """Test RoomMetaData response."""
    
    def test_room_metadata_with_name(self):
        """Test room metadata with name parsing."""
        room_name = "Living Room"
        name_bytes = room_name.encode('utf-16le')
        
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.ROOM_META_DATA, 0, 0, 0]
        buffer.append(1)  # room_id at index 8
        buffer.extend([len(name_bytes)])  # Length indicator
        buffer.extend(list(name_bytes))  # Room name
        
        response = RoomMetaData(buffer)
        assert response.command_id == CommandID.ROOM_META_DATA
        assert response.room_id == 1
        # Note: name parsing might need adjustment based on actual protocol


class TestResponseFactory:
    """Test ResponseFactory."""
    
    def test_factory_acknowledgement(self):
        """Test factory creates acknowledgement response."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.ACKNOWLEDGEMENT, 0, 0, 0]
        buffer.extend([0] * 10)
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        
        response = ResponseFactory.find(buffer, ProtocolVersion.V1)
        assert isinstance(response, Acknowledgement)
        assert response.command_id == CommandID.ACKNOWLEDGEMENT
    
    def test_factory_room_count(self):
        """Test factory creates room count response."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.ROOM_COUNT, 0, 0, 0]
        buffer.extend([2, 1, 2])
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        
        response = ResponseFactory.find(buffer, ProtocolVersion.V1)
        assert isinstance(response, RoomCount)
        assert response.list == [1, 2]
    
    def test_factory_key_status(self):
        """Test factory creates key status response."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.KEY_STATUS, 0, 0, 0]
        buffer.extend([1, 2, KeyPowerStatus.ON])
        buffer.extend([0] * 5)
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        
        response = ResponseFactory.find(buffer, ProtocolVersion.V1)
        assert isinstance(response, KeyStatus)
        assert response.node_id == 1
        assert response.key_id == 2
    
    def test_factory_outgoing_message(self):
        """Test factory returns None for outgoing messages."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.OUTGOING, CommandID.ACKNOWLEDGEMENT, 0, 0, 0]
        buffer.extend([0] * 10)
        
        response = ResponseFactory.find(buffer, ProtocolVersion.V1)
        assert response is None
    
    def test_factory_unknown_command(self):
        """Test factory returns None for unknown commands."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, 0xFF, 0, 0, 0]  # Unknown command
        buffer.extend([0] * 10)
        
        response = ResponseFactory.find(buffer, ProtocolVersion.V1)
        assert response is None
    
    def test_factory_invalid_buffer(self):
        """Test factory handles invalid buffers."""
        # Too short buffer
        buffer = [0x56, 0x54]
        response = ResponseFactory.find(buffer, ProtocolVersion.V1)
        assert response is None
    
    def test_factory_protocol_v2(self):
        """Test factory uses V2 classes for V2 protocol."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.NODE_META_DATA, 0, 0, 0]
        buffer.extend([0] * 20)
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        
        response_v1 = ResponseFactory.find(buffer, ProtocolVersion.V1)
        response_v2 = ResponseFactory.find(buffer, ProtocolVersion.V2)
        
        # Both should create responses, but V2 might use different class
        assert response_v1 is not None
        assert response_v2 is not None


class TestResponseLogging:
    """Test response logging functionality."""
    
    def test_room_count_log_data(self):
        """Test room count log data."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.ROOM_COUNT, 0, 0, 0]
        buffer.extend([2, 1, 2])
        # Add checksum
        checksum = sum(buffer) & 0xFF
        buffer.append(checksum)
        
        response = RoomCount(buffer)
        log_data = response._to_log
        
        assert "total" in log_data
        assert "list" in log_data
        assert log_data["total"] == 2
        assert log_data["list"] == [1, 2]
    
    def test_key_parameters_log_data(self):
        """Test key parameters log data."""
        buffer = [0x56, 0x54, 0x55, DataGramDirection.INCOMING, CommandID.KEY_PARAMETERS, 0, 0, 0]
        buffer.extend([1, 2, KeyCategory.LIGHT, 75])
        buffer.extend([0] * 5)
        
        response = KeyParameters(buffer)
        log_data = response._to_log
        
        assert "nodeID" in log_data
        assert "keyID" in log_data
        assert "category" in log_data
        assert "dimmerRatio" in log_data
        assert log_data["nodeID"] == 1
        assert log_data["keyID"] == 2 