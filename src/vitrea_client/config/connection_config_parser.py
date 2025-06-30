"""Connection configuration parser."""

from typing import Dict, Any, Optional
from .base_config_parser import BaseConfigParser
from .connection_config import ConnectionConfig, ProtocolVersion


class ConnectionConfigParser(BaseConfigParser):
    """Parser for connection configuration with environment variable support."""
    
    @classmethod
    def create(cls, config_overrides: Optional[Dict[str, Any]] = None) -> ConnectionConfig:
        """Create a ConnectionConfig instance from environment variables and overrides.
        
        Args:
            config_overrides: Optional dictionary of configuration overrides
            
        Returns:
            Configured ConnectionConfig instance
        """
        config_overrides = config_overrides or {}
        instance = cls(config_overrides)
        
        # Parse configuration values with defaults
        host = instance.get('host', '192.168.1.23')
        port = int(instance.get('port', 11501))
        username = instance.get('username', '')
        password = instance.get('password', '')
        version_str = instance.get('version', ProtocolVersion.V2.value)
        
        # Convert version string to enum
        if isinstance(version_str, ProtocolVersion):
            version = version_str
        else:
            try:
                version = ProtocolVersion(version_str.lower())
            except ValueError:
                version = ProtocolVersion.V2
        
        return ConnectionConfig(
            host=host,
            port=port,
            username=username,
            password=password,
            version=version
        ) 