"""Tests for the utilities module."""

import pytest

from vitrea_client.utilities import (
    DataGramDirection,
    KeyPowerStatus,
    LEDBackgroundBrightness,
    LockStatus,
    KeyCategory,
    MessageID,
    Events,
)


class TestEnums:
    """Test the enum classes."""
    
    def test_datagram_direction_values(self):
        """Test DataGramDirection enum values."""
        assert DataGramDirection.OUTGOING == 0x3E
        assert DataGramDirection.INCOMING == 0x3C
    
    def test_key_power_status_values(self):
        """Test KeyPowerStatus enum values."""
        assert KeyPowerStatus.ON == 0x4F
        assert KeyPowerStatus.OFF == 0x46
        assert KeyPowerStatus.LONG == 0x4C
        assert KeyPowerStatus.SHORT == 0x53
        assert KeyPowerStatus.RELEASED == 0x52
    
    def test_led_background_brightness_values(self):
        """Test LEDBackgroundBrightness enum values."""
        assert LEDBackgroundBrightness.OFF == 0
        assert LEDBackgroundBrightness.LOW == 1
        assert LEDBackgroundBrightness.HIGH == 2
        assert LEDBackgroundBrightness.MAX == 3
    
    def test_lock_status_values(self):
        """Test LockStatus enum values."""
        assert LockStatus.UNLOCKED == 0
        assert LockStatus.LOCKED == 1
    
    def test_key_category_values(self):
        """Test KeyCategory enum values."""
        assert KeyCategory.UNDEFINED == 0
        assert KeyCategory.LIGHT == 1
        assert KeyCategory.FAN == 6
        assert KeyCategory.BOILER == 7
    
    def test_enums_are_integers(self):
        """Test that enum values can be used as integers."""
        assert int(DataGramDirection.OUTGOING) == 0x3E
        assert int(KeyPowerStatus.ON) == 0x4F
        assert int(LEDBackgroundBrightness.MAX) == 3
        assert int(LockStatus.LOCKED) == 1
        assert int(KeyCategory.LIGHT) == 1


class TestMessageID:
    """Test the MessageID utility class."""
    
    def setup_method(self):
        """Reset MessageID before each test."""
        MessageID.reset_id()
    
    def test_initial_state(self):
        """Test the initial state of MessageID."""
        # After reset, the next ID should be 1
        assert MessageID.get_next_id() == 1
    
    def test_get_next_id_increments(self):
        """Test that get_next_id increments correctly."""
        assert MessageID.get_next_id() == 1
        assert MessageID.get_next_id() == 2
        assert MessageID.get_next_id() == 3
    
    def test_reset_id_with_default(self):
        """Test reset_id with default value."""
        MessageID.get_next_id()  # Make it 1
        MessageID.get_next_id()  # Make it 2
        
        result = MessageID.reset_id()
        assert result == 0
        assert MessageID.get_next_id() == 1
    
    def test_reset_id_with_custom_value(self):
        """Test reset_id with custom value."""
        result = MessageID.reset_id(0x10)
        assert result == 0x10
        assert MessageID.get_next_id() == 0x11
    
    def test_set_next_id(self):
        """Test set_next_id method."""
        MessageID.set_next_id(0x20)
        assert MessageID.get_next_id() == 0x20
        assert MessageID.get_next_id() == 0x21
    
    def test_wraparound_at_max_value(self):
        """Test that message ID wraps around at 0xFF."""
        MessageID.reset_id(0xFE)
        
        assert MessageID.get_next_id() == 0xFF
        assert MessageID.get_next_id() == 0x01  # Should wrap to 1, not 0
        assert MessageID.get_next_id() == 0x02
    
    def test_class_state_persistence(self):
        """Test that MessageID state persists across instances."""
        # MessageID is a class-level utility, so state should persist
        MessageID.reset_id(0x05)
        
        # Even though we're calling class methods, state should be shared
        assert MessageID.get_next_id() == 0x06
        assert MessageID.get_next_id() == 0x07


class TestEvents:
    """Test the Events utility class."""
    
    def test_class_constants(self):
        """Test the class constants."""
        assert Events.STATUS_UPDATE == "vitrea::status::update"
        assert Events.UNKNOWN_DATA == "vitrea::data::unknown"
    
    def test_generate_with_integers(self):
        """Test generate method with integer arguments."""
        result = Events.generate(0x01, 0x05)
        assert result == "data::01-05"
        
        result = Events.generate(0xFF, 0x00)
        assert result == "data::ff-00"
    
    def test_generate_with_mixed_types(self):
        """Test generate method with mixed argument types."""
        result = Events.generate(0x01, "test", 0x05)
        assert result == "data::01-test-05"
    
    def test_generate_with_strings(self):
        """Test generate method with string arguments."""
        result = Events.generate("hello", "world")
        assert result == "data::hello-world"
    
    def test_generate_with_single_argument(self):
        """Test generate method with single argument."""
        result = Events.generate(0x42)
        assert result == "data::42"
    
    def test_generate_with_no_arguments(self):
        """Test generate method with no arguments."""
        result = Events.generate()
        assert result == "data::"
    
    def test_acknowledgement_method(self):
        """Test the acknowledgement method."""
        result = Events.acknowledgement(0x05)
        assert result == "data::00-05"
        
        result = Events.acknowledgement(0xFF)
        assert result == "data::00-ff"
    
    def test_hex_formatting(self):
        """Test that integers are properly formatted as hex."""
        result = Events.generate(1, 15, 255)
        assert result == "data::01-0f-ff"
    
    def test_zero_padding(self):
        """Test that hex values are zero-padded to 2 digits."""
        result = Events.generate(0, 1, 15)
        assert result == "data::00-01-0f" 