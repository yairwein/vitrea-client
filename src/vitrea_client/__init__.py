"""Vitrea Smart Home API Client for Python."""

from .core import (
    LoggerProtocol,
    ConsoleLogger,
    NullLogger,
    DataGram,
    BaseRequest,
    BaseResponse,
)

from .config import (
    ConnectionConfig,
    ProtocolVersion,
    SocketConfig,
)

from .exceptions import (
    ConnectionExistsException,
    NoConnectionException,
    TimeoutException,
)

from .utilities import (
    DataGramDirection,
    KeyPowerStatus,
    LEDBackgroundBrightness,
    LockStatus,
    KeyCategory,
    MessageID,
    Events,
)

from .socket import (
    Timeout,
    AbstractSocket,
    AbstractHeartbeatHandler,
    VitreaHeartbeatHandler,
    WritableSocketProtocol,
    SplitMultipleBuffers,
)

from .vitrea_client import VitreaClient

__version__ = "0.1.0"

__all__ = [
    # Core components
    "LoggerProtocol",
    "ConsoleLogger",
    "NullLogger",
    "DataGram",
    "BaseRequest",
    "BaseResponse",
    
    # Configuration
    "ConnectionConfig",
    "ProtocolVersion",
    "SocketConfig",
    
    # Exceptions
    "ConnectionExistsException",
    "NoConnectionException",
    "TimeoutException",
    
    # Utilities
    "DataGramDirection",
    "KeyPowerStatus",
    "LEDBackgroundBrightness",
    "LockStatus",
    "KeyCategory",
    "MessageID",
    "Events",
    
    # Socket components
    "Timeout",
    "AbstractSocket",
    "AbstractHeartbeatHandler",
    "VitreaHeartbeatHandler",
    "WritableSocketProtocol",
    "SplitMultipleBuffers",
    
    # Main client
    "VitreaClient",
] 