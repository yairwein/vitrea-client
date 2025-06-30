"""Socket configuration parser."""

from typing import Dict, Any, Optional, Union
from .base_config_parser import BaseConfigParser
from .socket_config import SocketConfig
from ..core import LoggerProtocol, NullLogger


class SocketConfigParser(BaseConfigParser):
    """Parser for socket configuration with environment variable support."""
    
    def to_boolean(self, value: Union[str, bool]) -> bool:
        """Convert string or boolean to boolean value.
        
        Args:
            value: Value to convert
            
        Returns:
            Boolean representation of the value
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['1', 'true', 'yes', 'on']
        return bool(value)
    
    @classmethod
    def create(cls, config_overrides: Optional[Dict[str, Any]] = None) -> SocketConfig:
        """Create a SocketConfig instance from environment variables and overrides.
        
        Args:
            config_overrides: Optional dictionary of configuration overrides
            
        Returns:
            Configured SocketConfig instance
        """
        config_overrides = config_overrides or {}
        instance = cls(config_overrides)
        
        # Get logger from overrides or use default
        logger = config_overrides.get('logger') or config_overrides.get('log')
        if not isinstance(logger, LoggerProtocol):
            logger = NullLogger()
        
        # Parse configuration values with defaults
        ignore_ack_logs = instance.to_boolean(instance.get('ignore_ack_logs', False))
        should_reconnect = instance.to_boolean(instance.get('should_reconnect', True))
        request_buffer = float(instance.get('request_buffer', 0.25))  # 250ms in seconds
        request_timeout = float(instance.get('request_timeout', 10.0))  # 10 seconds
        
        return SocketConfig(
            log=logger,
            ignore_ack_logs=ignore_ack_logs,
            should_reconnect=should_reconnect,
            request_buffer=request_buffer,
            request_timeout=request_timeout,
            socket_supplier=None
        ) 