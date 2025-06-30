"""Tests for the configuration system."""

import os
from unittest.mock import patch

import pytest

from vitrea_client.config import (
    BaseConfigParser,
    ConnectionConfig,
    ProtocolVersion,
    SocketConfig,
)
from vitrea_client.core.logger import NullLogger, ConsoleLogger


class TestBaseConfigParser:
    """Test the BaseConfigParser class."""
    
    def test_instantiation(self):
        """Test BaseConfigParser instantiation."""
        configs = {"test_key": "test_value"}
        parser = BaseConfigParser(configs)
        
        assert parser._configs == configs
    
    def test_get_with_direct_config(self):
        """Test get method with direct configuration."""
        configs = {"testKey": "direct_value"}
        parser = BaseConfigParser(configs)
        
        result = parser.get("testKey")
        assert result == "direct_value"
    
    @patch.dict(os.environ, {"VITREA_VBOX_TEST_KEY": "env_value"})
    def test_get_with_environment_variable(self):
        """Test get method with environment variable."""
        parser = BaseConfigParser({})
        
        result = parser.get("testKey")
        assert result == "env_value"
    
    def test_get_with_fallback(self):
        """Test get method with fallback value."""
        parser = BaseConfigParser({})
        
        result = parser.get("nonExistentKey", "fallback_value")
        assert result == "fallback_value"
    
    def test_get_priority_order(self):
        """Test that get method follows correct priority order."""
        configs = {"testKey": "direct_value"}
        
        with patch.dict(os.environ, {"VITREA_VBOX_TEST_KEY": "env_value"}):
            parser = BaseConfigParser(configs)
            
            # Direct config should take priority over env var
            result = parser.get("testKey", "fallback_value")
            assert result == "direct_value"
    
    def test_get_required_with_value(self):
        """Test get method with required=True when value exists."""
        configs = {"testKey": "test_value"}
        parser = BaseConfigParser(configs)
        
        result = parser.get("testKey", required=True)
        assert result == "test_value"
    
    def test_get_required_without_value(self):
        """Test get method with required=True when value is missing."""
        parser = BaseConfigParser({})
        
        with pytest.raises(TypeError, match="A value for \\[testKey\\] is required"):
            parser.get("testKey", required=True)
    
    def test_camel_case_to_snake_case_conversion(self):
        """Test that camelCase keys are converted to SNAKE_CASE for env vars."""
        with patch.dict(os.environ, {"VITREA_VBOX_CAMEL_CASE_KEY": "env_value"}):
            parser = BaseConfigParser({})
            
            result = parser.get("camelCaseKey")
            assert result == "env_value"


class TestConnectionConfig:
    """Test the ConnectionConfig class."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_with_defaults(self):
        """Test ConnectionConfig creation with default values."""
        config = ConnectionConfig.create()
        
        assert config.host == "192.168.1.23"
        assert config.port == 11501
        assert config.username is None
        assert config.password is None
        assert config.version == ProtocolVersion.V2
    
    def test_create_with_custom_values(self):
        """Test ConnectionConfig creation with custom values."""
        configs = {
            "host": "192.168.1.100",
            "port": 12345,
            "username": "admin",
            "password": "secret",
            "version": "v1"
        }
        
        config = ConnectionConfig.create(configs)
        
        assert config.host == "192.168.1.100"
        assert config.port == 12345
        assert config.username == "admin"
        assert config.password == "secret"
        assert config.version == ProtocolVersion.V1
    
    @patch.dict(os.environ, {
        "VITREA_VBOX_HOST": "env.host.com",
        "VITREA_VBOX_PORT": "9999",
        "VITREA_VBOX_USERNAME": "env_user",
        "VITREA_VBOX_PASSWORD": "env_pass",
        "VITREA_VBOX_VERSION": "v1"
    })
    def test_create_with_environment_variables(self):
        """Test ConnectionConfig creation with environment variables."""
        config = ConnectionConfig.create()
        
        assert config.host == "env.host.com"
        assert config.port == 9999
        assert config.username == "env_user"
        assert config.password == "env_pass"
        assert config.version == ProtocolVersion.V1
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_with_none_configs(self):
        """Test ConnectionConfig creation with None configs."""
        config = ConnectionConfig.create(None)
        
        # Should use defaults
        assert config.host == "192.168.1.23"
        assert config.port == 11501
        assert config.version == ProtocolVersion.V2


class TestProtocolVersion:
    """Test the ProtocolVersion enum."""
    
    def test_enum_values(self):
        """Test that ProtocolVersion has correct values."""
        assert ProtocolVersion.V1.value == "v1"
        assert ProtocolVersion.V2.value == "v2"
    
    def test_enum_creation_from_string(self):
        """Test that ProtocolVersion can be created from string."""
        assert ProtocolVersion("v1") == ProtocolVersion.V1
        assert ProtocolVersion("v2") == ProtocolVersion.V2


class TestSocketConfig:
    """Test the SocketConfig class."""
    
    def test_create_with_defaults(self):
        """Test SocketConfig creation with default values."""
        config = SocketConfig.create()
        
        assert isinstance(config.log, NullLogger)
        assert config.ignore_ack_logs is False
        assert config.should_reconnect is True
        assert config.request_buffer == 250
        assert config.request_timeout == 1000
        assert config.socket_supplier is None
    
    def test_create_with_custom_values(self):
        """Test SocketConfig creation with custom values."""
        custom_logger = ConsoleLogger()
        custom_socket_supplier = lambda: None
        
        configs = {
            "log": custom_logger,
            "ignoreAckLogs": "true",
            "shouldReconnect": "false",
            "requestBuffer": "500",
            "requestTimeout": "2000",
            "socketSupplier": custom_socket_supplier,
        }
        
        config = SocketConfig.create(configs)
        
        assert config.log is custom_logger
        assert config.ignore_ack_logs is True
        assert config.should_reconnect is False
        assert config.request_buffer == 500
        assert config.request_timeout == 2000
        assert config.socket_supplier is custom_socket_supplier
    
    @patch.dict(os.environ, {
        "VITREA_VBOX_IGNORE_ACK_LOGS": "1",
        "VITREA_VBOX_SHOULD_RECONNECT": "false",
        "VITREA_VBOX_REQUEST_BUFFER": "750",
        "VITREA_VBOX_REQUEST_TIMEOUT": "1500"
    })
    def test_create_with_environment_variables(self):
        """Test SocketConfig creation with environment variables."""
        config = SocketConfig.create()
        
        assert config.ignore_ack_logs is True
        assert config.should_reconnect is False
        assert config.request_buffer == 750
        assert config.request_timeout == 1500
    
    def test_to_boolean_method(self):
        """Test the to_boolean conversion logic."""
        config = SocketConfig.create()
        
        # Test various boolean conversions through the config creation
        test_cases = [
            ({"ignoreAckLogs": True}, True),
            ({"ignoreAckLogs": False}, False),
            ({"ignoreAckLogs": "true"}, True),
            ({"ignoreAckLogs": "false"}, False),
            ({"ignoreAckLogs": "1"}, True),
            ({"ignoreAckLogs": "0"}, False),
            ({"ignoreAckLogs": "yes"}, True),
            ({"ignoreAckLogs": "no"}, False),
            ({"ignoreAckLogs": "on"}, True),
            ({"ignoreAckLogs": "off"}, False),
        ]
        
        for test_config, expected in test_cases:
            config = SocketConfig.create(test_config)
            assert config.ignore_ack_logs == expected
    
    def test_create_with_none_configs(self):
        """Test SocketConfig creation with None configs."""
        config = SocketConfig.create(None)
        
        # Should use defaults
        assert isinstance(config.log, NullLogger)
        assert config.ignore_ack_logs is False
        assert config.should_reconnect is True 