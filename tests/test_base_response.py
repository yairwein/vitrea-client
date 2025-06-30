"""Tests for the BaseResponse class."""

import pytest

from vitrea_client.core.base_response import BaseResponse
from vitrea_client.utilities.enums import DataGramDirection


class ConcreteResponse(BaseResponse):
    """Concrete implementation of BaseResponse for testing."""
    
    def _abstract_method(self):
        """Implementation of abstract method."""
        pass


class TestBaseResponse:
    """Test the BaseResponse class."""
    
    def test_instantiation_with_bytes(self):
        """Test BaseResponse instantiation with bytes buffer."""
        # Create a buffer with checksum as last byte
        buffer = bytes([0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF])
        response = ConcreteResponse(buffer)
        
        # Checksum should be extracted
        assert response._raw_checksum == 0xFF
        
        # Buffer should not include checksum
        assert response._buffer == [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05]
        assert response.length == 8
    
    def test_instantiation_with_list(self):
        """Test BaseResponse instantiation with list buffer."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response._raw_checksum == 0xFF
        assert response._buffer == [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05]
    
    def test_instantiation_with_empty_buffer(self):
        """Test BaseResponse instantiation with empty buffer."""
        buffer = []
        response = ConcreteResponse(buffer)
        
        assert response._raw_checksum == 0
        assert response._buffer == []
    
    def test_data_length_property(self):
        """Test the data_length property."""
        # Create buffer with data length bytes at positions 5 and 6
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x04, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response.data_length == (0x00, 0x04)
    
    def test_has_valid_checksum_true(self):
        """Test has_valid_checksum when checksum is valid."""
        # Create a buffer where the checksum matches
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01]
        expected_checksum = sum(buffer) & 0xFF
        buffer.append(expected_checksum)
        
        response = ConcreteResponse(buffer)
        
        assert response.has_valid_checksum is True
    
    def test_has_valid_checksum_false(self):
        """Test has_valid_checksum when checksum is invalid."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0xFF]  # Wrong checksum
        response = ConcreteResponse(buffer)
        
        assert response.has_valid_checksum is False
    
    def test_direction_property(self):
        """Test that direction property works correctly."""
        # Test incoming direction
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response.direction == DataGramDirection.INCOMING
    
    def test_command_id_property(self):
        """Test the command_id property."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response.command_id == 0x01
    
    def test_message_id_property(self):
        """Test the message_id property."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response.message_id == 0x05
    
    def test_data_property_with_data(self):
        """Test the data property when response has data."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xAA, 0xBB, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response.has_data is True
        assert response.data == [0xAA, 0xBB]
    
    def test_data_property_without_data(self):
        """Test the data property when response has no data."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        assert response.has_data is False
        assert response.data == []
    
    def test_log_data_includes_checksum_validity(self):
        """Test that log data includes checksum validity."""
        # Valid checksum - need buffer long enough for MESSAGE_ID_INDEX (7)
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05]
        expected_checksum = sum(buffer) & 0xFF
        buffer.append(expected_checksum)
        
        response = ConcreteResponse(buffer)
        log_data = response.log_data
        
        assert "hasValidChecksum" in log_data
        assert log_data["hasValidChecksum"] is True
        
        # Invalid checksum
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]  # Wrong checksum
        response = ConcreteResponse(buffer)
        log_data = response.log_data
        
        assert log_data["hasValidChecksum"] is False
    
    def test_checksum_calculation(self):
        """Test that checksum is calculated correctly."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        # Checksum should be calculated on buffer without the raw checksum
        expected_checksum = sum([0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05]) & 0xFF
        assert response.checksum == expected_checksum
    
    def test_inheritance_from_datagram(self):
        """Test that BaseResponse properly inherits from DataGram."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        # Should have all DataGram properties
        assert hasattr(response, 'direction')
        assert hasattr(response, 'command_id')
        assert hasattr(response, 'message_id')
        assert hasattr(response, 'checksum')
        assert hasattr(response, 'log_data')
        assert hasattr(response, 'event_name')
    
    def test_event_name_generation(self):
        """Test that event name is generated correctly."""
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01, 0x00, 0x02, 0x05, 0xFF]
        response = ConcreteResponse(buffer)
        
        # Event name should be generated from command_id (0x01) and message_id (0x05)
        assert response.event_name == "data::01-05" 