"""Tests for the BaseRequest class."""

import pytest

from vitrea_client.core.base_request import BaseRequest
from vitrea_client.utilities.enums import DataGramDirection
from vitrea_client.utilities.message_id import MessageID


class ConcreteRequest(BaseRequest):
    """Concrete implementation of BaseRequest for testing."""
    
    def _abstract_method(self):
        """Implementation of abstract method."""
        pass


class TestBaseRequest:
    """Test the BaseRequest class."""
    
    def setup_method(self):
        """Reset MessageID before each test."""
        MessageID.reset_id()
    
    def test_instantiation_with_defaults(self):
        """Test BaseRequest instantiation with default parameters."""
        request = ConcreteRequest()
        
        # Should have prefix + direction + command_id + padding for message_id
        assert request.length >= 8
        assert request._buffer[:3] == [0x56, 0x54, 0x55]  # prefix
        assert request.direction == DataGramDirection.OUTGOING
        assert request.command_id == 0x00  # default command_id
        assert request.message_id == 1  # first message ID
    
    def test_instantiation_with_command_id(self):
        """Test BaseRequest instantiation with custom command ID."""
        request = ConcreteRequest(command_id=0x05)
        
        assert request.command_id == 0x05
        assert request.direction == DataGramDirection.OUTGOING
    
    def test_instantiation_with_data(self):
        """Test BaseRequest instantiation with data."""
        data = [0xAA, 0xBB, 0xCC]
        request = ConcreteRequest(command_id=0x01, data=data)
        
        assert request.command_id == 0x01
        assert request.has_data
        assert request.data == data
    
    def test_message_id_increments(self):
        """Test that message IDs increment for each request."""
        request1 = ConcreteRequest()
        request2 = ConcreteRequest()
        request3 = ConcreteRequest()
        
        assert request1.message_id == 1
        assert request2.message_id == 2
        assert request3.message_id == 3
    
    def test_data_length_is_set_correctly(self):
        """Test that data length is set correctly in the buffer."""
        data = [0xAA, 0xBB]
        request = ConcreteRequest(data=data)
        
        # Data length should be len(data) + 2 = 2 + 2 = 4
        # Split into two bytes: 4 = 0x00, 0x04
        expected_length = (0x00, 0x04)
        actual_length = (
            request.get(request.DATA_LENGTH_INDEX),
            request.get(request.DATA_LENGTH_INDEX + 1)
        )
        
        assert actual_length == expected_length
    
    def test_build_method(self):
        """Test the build method returns bytes with checksum."""
        request = ConcreteRequest(command_id=0x01)
        built = request.build()
        
        assert isinstance(built, bytes)
        
        # The last byte should be the checksum
        expected_checksum = request.checksum
        actual_checksum = built[-1]
        
        assert actual_checksum == expected_checksum
        
        # The rest should match the buffer
        assert list(built[:-1]) == request._buffer
    
    def test_build_with_data(self):
        """Test the build method with data."""
        data = [0xAA, 0xBB]
        request = ConcreteRequest(command_id=0x01, data=data)
        built = request.build()
        
        assert isinstance(built, bytes)
        assert len(built) == len(request._buffer) + 1  # +1 for checksum
        
        # Verify data is included
        assert 0xAA in built
        assert 0xBB in built
    
    def test_log_data_includes_data_hex(self):
        """Test that log data includes hex representation of data."""
        data = [0xAA, 0xBB]
        request = ConcreteRequest(command_id=0x01, data=data)
        
        log_data = request.log_data
        
        assert "data" in log_data
        assert "AA:BB" in log_data["data"]
    
    def test_empty_data_log(self):
        """Test log data when there's no data."""
        request = ConcreteRequest()
        log_data = request.log_data
        
        assert "data" in log_data
        assert log_data["data"] == ""
    
    def test_set_data_length_method(self):
        """Test the _set_data_length method."""
        request = ConcreteRequest()
        
        # Add some data manually
        request._buffer.extend([0xAA, 0xBB, 0xCC])
        
        # Call _set_data_length to update
        request._set_data_length()
        
        # Check that data length bytes are correct
        # Data length should be 3 + 2 = 5 = 0x00, 0x05
        assert request.get(request.DATA_LENGTH_INDEX) == 0x00
        assert request.get(request.DATA_LENGTH_INDEX + 1) == 0x05
    
    def test_inheritance_from_datagram(self):
        """Test that BaseRequest properly inherits from DataGram."""
        request = ConcreteRequest()
        
        # Should have all DataGram properties
        assert hasattr(request, 'direction')
        assert hasattr(request, 'command_id')
        assert hasattr(request, 'message_id')
        assert hasattr(request, 'checksum')
        assert hasattr(request, 'log_data') 