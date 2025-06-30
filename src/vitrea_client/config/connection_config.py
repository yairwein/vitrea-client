"""Connection configuration for VBox settings."""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .base_config_parser import BaseConfigParser


class ProtocolVersion(Enum):
    """Protocol version enumeration."""
    V1 = "v1"
    V2 = "v2"


@dataclass
class ConnectionConfig:
    """Configuration for VBox connection."""
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    version: ProtocolVersion
    
    @classmethod
    def create(cls, configs: Dict[str, Any] = None) -> "ConnectionConfig":
        """Create a ConnectionConfig instance from partial configuration."""
        if configs is None:
            configs = {}
        
        parser = BaseConfigParser(configs)
        
        return cls(
            host=parser.get("host", "192.168.1.23"),
            port=int(parser.get("port", 11501)),
            username=parser.get("username"),
            password=parser.get("password"),
            version=ProtocolVersion(parser.get("version", ProtocolVersion.V2.value)),
        ) 