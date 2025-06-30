"""Tests for custom exception classes."""

import pytest

from vitrea_client.exceptions import (
    ConnectionExistsException,
    NoConnectionException,
    TimeoutException,
)


class TestConnectionExistsException:
    """Test the ConnectionExistsException class."""
    
    def test_instantiation_with_default_message(self):
        """Test exception instantiation with default message."""
        exception = ConnectionExistsException()
        
        assert str(exception) == "Socket connection already exists"
        assert isinstance(exception, Exception)
    
    def test_instantiation_with_custom_message(self):
        """Test exception instantiation with custom message."""
        custom_message = "Custom connection exists message"
        exception = ConnectionExistsException(custom_message)
        
        assert str(exception) == custom_message
    
    def test_can_be_raised(self):
        """Test that the exception can be raised."""
        with pytest.raises(ConnectionExistsException) as exc_info:
            raise ConnectionExistsException("Test message")
        
        assert str(exc_info.value) == "Test message"


class TestNoConnectionException:
    """Test the NoConnectionException class."""
    
    def test_instantiation_with_default_message(self):
        """Test exception instantiation with default message."""
        exception = NoConnectionException()
        
        assert str(exception) == "No socket connection established"
        assert isinstance(exception, Exception)
    
    def test_instantiation_with_custom_message(self):
        """Test exception instantiation with custom message."""
        custom_message = "Custom no connection message"
        exception = NoConnectionException(custom_message)
        
        assert str(exception) == custom_message
    
    def test_can_be_raised(self):
        """Test that the exception can be raised."""
        with pytest.raises(NoConnectionException) as exc_info:
            raise NoConnectionException("Test message")
        
        assert str(exc_info.value) == "Test message"


class TestTimeoutException:
    """Test the TimeoutException class."""
    
    def test_instantiation_with_no_message(self):
        """Test exception instantiation with no message."""
        exception = TimeoutException()
        
        assert isinstance(exception, Exception)
    
    def test_instantiation_with_custom_message(self):
        """Test exception instantiation with custom message."""
        custom_message = "Operation timed out"
        exception = TimeoutException(custom_message)
        
        assert str(exception) == custom_message
    
    def test_can_be_raised(self):
        """Test that the exception can be raised."""
        with pytest.raises(TimeoutException) as exc_info:
            raise TimeoutException("Test timeout")
        
        assert str(exc_info.value) == "Test timeout" 