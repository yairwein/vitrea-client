"""Tests for the DataGram class."""

import pytest

from vitrea_client.core.datagram import DataGram
from vitrea_client.utilities.enums import DataGramDirection


class ConcreteDataGram(DataGram):
    """Concrete implementation of DataGram for testing."""
    
    def _abstract_method(self):
        """Implementation of abstract method."""
        pass


class TestDataGram:
    """Test the DataGram class."""
    
    def test_instantiation_with_no_buffer(self):
        """Test DataGram instantiation with no buffer."""
        datagram = ConcreteDataGram()
        
        assert datagram.length == 3
        assert datagram._buffer == [0x56, 0x54, 0x55]
    
    def test_instantiation_with_bytes_buffer(self):
        """Test DataGram instantiation with bytes buffer."""
        buffer = bytes([0x56, 0x54, 0x55, 0x3E, 0x01])
        datagram = ConcreteDataGram(buffer)
        
        assert datagram.length == 5
        assert datagram._buffer == [0x56, 0x54, 0x55, 0x3E, 0x01]
    
    def test_instantiation_with_list_buffer(self):
        """Test DataGram instantiation with list buffer."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01]
        datagram = ConcreteDataGram(buffer)
        
        assert datagram.length == 5
        assert datagram._buffer == [0x56, 0x54, 0x55, 0x3E, 0x01]
    
    def test_get_method(self):
        """Test the get method."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01]
        datagram = ConcreteDataGram(buffer)
        
        assert datagram.get(0) == 0x56
        assert datagram.get(3) == 0x3E
        assert datagram.get(4) == 0x01
    
    def test_get_data_method(self):
        """Test the get_data method."""
        # Create a buffer with data beyond the DATA_INDEX
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x01, 0xAA, 0xBB]
        datagram = ConcreteDataGram(buffer)
        
        data = datagram.get_data()
        assert data == [0xAA, 0xBB]
        
        # Ensure it's a copy
        data[0] = 0xFF
        assert datagram.get_data()[0] == 0xAA
    
    def test_direction_property(self):
        """Test the direction property."""
        # Test outgoing direction
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01]
        datagram = ConcreteDataGram(buffer)
        assert datagram.direction == DataGramDirection.OUTGOING
        
        # Test incoming direction
        buffer = [0x56, 0x54, 0x55, 0x3C, 0x01]
        datagram = ConcreteDataGram(buffer)
        assert datagram.direction == DataGramDirection.INCOMING
    
    def test_checksum_property(self):
        """Test the checksum property."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01]
        datagram = ConcreteDataGram(buffer)
        
        expected_checksum = (0x56 + 0x54 + 0x55 + 0x3E + 0x01) & 0xFF
        assert datagram.checksum == expected_checksum
    
    def test_command_id_property(self):
        """Test the command_id property."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01]
        datagram = ConcreteDataGram(buffer)
        
        assert datagram.command_id == 0x01
    
    def test_message_id_property(self):
        """Test the message_id property."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05]
        datagram = ConcreteDataGram(buffer)
        
        assert datagram.message_id == 0x05
    
    def test_has_data_property(self):
        """Test the has_data property."""
        # Buffer without data
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05]
        datagram = ConcreteDataGram(buffer)
        assert not datagram.has_data
        
        # Buffer with data
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05, 0xAA]
        datagram = ConcreteDataGram(buffer)
        assert datagram.has_data
    
    def test_data_property(self):
        """Test the data property."""
        # Buffer without data
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05]
        datagram = ConcreteDataGram(buffer)
        assert datagram.data == []
        
        # Buffer with data
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05, 0xAA, 0xBB]
        datagram = ConcreteDataGram(buffer)
        assert datagram.data == [0xAA, 0xBB]
    
    def test_data_length_property(self):
        """Test the data_length property."""
        # Buffer with 2 bytes of data
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05, 0xAA, 0xBB]
        datagram = ConcreteDataGram(buffer)
        
        # Data length should be len(data) + 2 = 2 + 2 = 4
        # Split into two bytes: 4 = 0x00, 0x04
        assert datagram.data_length == (0x00, 0x04)
    
    def test_event_name_property(self):
        """Test the event_name property."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05]
        datagram = ConcreteDataGram(buffer)
        
        # Should generate event name from command_id (0x01) and message_id (0x05)
        assert datagram.event_name == "data::01-05"
    
    def test_command_name_property(self):
        """Test the command_name property."""
        datagram = ConcreteDataGram()
        assert datagram.command_name == "ConcreteDataGram"
    
    def test_to_hex_method(self):
        """Test the _to_hex method."""
        datagram = ConcreteDataGram()
        
        assert datagram._to_hex(0x01) == "0x01"
        assert datagram._to_hex(0xFF) == "0xFF"
        assert datagram._to_hex(0x00) == "0x00"
    
    def test_to_hex_string_method(self):
        """Test the _to_hex_string method."""
        buffer = [0x56, 0x54, 0x55]
        datagram = ConcreteDataGram(buffer)
        
        assert datagram._to_hex_string() == "56:54:55"
        assert datagram._to_hex_string([0xAA, 0xBB]) == "AA:BB"
    
    def test_log_data_property(self):
        """Test the log_data property."""
        buffer = [0x56, 0x54, 0x55, 0x3E, 0x01, 0x00, 0x02, 0x05]
        datagram = ConcreteDataGram(buffer)
        
        log_data = datagram.log_data
        
        assert log_data["command"] == "ConcreteDataGram"
        assert log_data["direction"] == "Outgoing"
        assert log_data["commandID"] == "0x01"
        assert log_data["messageID"] == "0x05"
        assert log_data["raw"] == "56:54:55:3E:01:00:02:05"
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Test that DataGram cannot be instantiated directly."""
        with pytest.raises(TypeError):
            DataGram() 