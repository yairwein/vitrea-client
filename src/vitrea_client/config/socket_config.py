"""Socket configuration for connection settings."""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import socket

from .base_config_parser import BaseConfigParser
from ..core.logger import LoggerProtocol, NullLogger


@dataclass
class SocketConfig:
    """Configuration for socket connection."""
    log: LoggerProtocol
    ignore_ack_logs: bool
    should_reconnect: bool
    request_buffer: float  # in seconds
    request_timeout: float  # in seconds
    socket_supplier: Optional[Callable[[], socket.socket]]
    
    @classmethod
    def create(cls, configs: Dict[str, Any] = None) -> "SocketConfig":
        """Create a SocketConfig instance from partial configuration."""
        if configs is None:
            configs = {}
        
        parser = BaseConfigParser(configs)
        
        def to_boolean(value: Any) -> bool:
            """Convert various value types to boolean."""
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ['1', 'true', 'yes', 'on']
            return bool(value)
        
        return cls(
            log=configs.get("log", NullLogger()),
            ignore_ack_logs=to_boolean(parser.get("ignoreAckLogs", False)),
            should_reconnect=to_boolean(parser.get("shouldReconnect", True)),
            request_buffer=float(parser.get("requestBuffer", 250)),
            request_timeout=float(parser.get("requestTimeout", 1000)),
            socket_supplier=configs.get("socketSupplier"),
        ) 