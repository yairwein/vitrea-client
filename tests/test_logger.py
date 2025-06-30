"""Tests for the logging system."""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from vitrea_client.core.logger import LoggerProtocol, ConsoleLogger, NullLogger


class TestLoggerProtocol:
    """Test the LoggerProtocol interface."""
    
    def test_protocol_methods_exist(self):
        """Test that the protocol defines the required methods."""
        # This is more of a static analysis test, but we can verify the protocol exists
        assert hasattr(LoggerProtocol, '__annotations__')
        
        # Check that all expected methods are in the protocol
        expected_methods = ['log', 'error', 'warn', 'info', 'debug']
        protocol_methods = [name for name in dir(LoggerProtocol) if not name.startswith('_')]
        
        for method in expected_methods:
            assert method in protocol_methods or hasattr(LoggerProtocol, method)


class TestConsoleLogger:
    """Test the ConsoleLogger implementation."""
    
    def test_instantiation(self):
        """Test that ConsoleLogger can be instantiated."""
        logger = ConsoleLogger()
        assert logger is not None
    
    @patch('builtins.print')
    def test_log_method(self, mock_print):
        """Test the log method."""
        logger = ConsoleLogger()
        logger.log("test message", "DEBUG")
        
        mock_print.assert_called_once_with("test message (level: DEBUG)")
    
    @patch('builtins.print')
    def test_error_method(self, mock_print):
        """Test the error method."""
        logger = ConsoleLogger()
        logger.error("error message", "arg1", "arg2")
        
        mock_print.assert_called_once_with("ERROR: error message", "arg1", "arg2", file=sys.stderr)
    
    @patch('builtins.print')
    def test_warn_method(self, mock_print):
        """Test the warn method."""
        logger = ConsoleLogger()
        logger.warn("warning message")
        
        mock_print.assert_called_once_with("WARN: warning message", file=sys.stderr)
    
    @patch('builtins.print')
    def test_info_method(self, mock_print):
        """Test the info method."""
        logger = ConsoleLogger()
        logger.info("info message")
        
        mock_print.assert_called_once_with("INFO: info message")
    
    @patch('builtins.print')
    def test_debug_method(self, mock_print):
        """Test the debug method."""
        logger = ConsoleLogger()
        logger.debug("debug message")
        
        mock_print.assert_called_once_with("DEBUG: debug message")


class TestNullLogger:
    """Test the NullLogger implementation."""
    
    def test_instantiation(self):
        """Test that NullLogger can be instantiated."""
        logger = NullLogger()
        assert logger is not None
    
    @patch('builtins.print')
    def test_log_method_does_nothing(self, mock_print):
        """Test that the log method does nothing."""
        logger = NullLogger()
        logger.log("test message", "DEBUG")
        
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    def test_error_method_does_nothing(self, mock_print):
        """Test that the error method does nothing."""
        logger = NullLogger()
        logger.error("error message", "arg1", "arg2")
        
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    def test_warn_method_does_nothing(self, mock_print):
        """Test that the warn method does nothing."""
        logger = NullLogger()
        logger.warn("warning message")
        
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    def test_info_method_does_nothing(self, mock_print):
        """Test that the info method does nothing."""
        logger = NullLogger()
        logger.info("info message")
        
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    def test_debug_method_does_nothing(self, mock_print):
        """Test that the debug method does nothing."""
        logger = NullLogger()
        logger.debug("debug message")
        
        mock_print.assert_not_called() 