"""Custom exceptions for the Vitrea client."""

from .connection_exists_exception import ConnectionExistsException
from .no_connection_exception import NoConnectionException
from .timeout_exception import TimeoutException

__all__ = [
    "ConnectionExistsException",
    "NoConnectionException", 
    "TimeoutException",
] 