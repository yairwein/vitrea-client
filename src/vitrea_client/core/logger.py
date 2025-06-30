"""Logging interfaces and implementations for the Vitrea client."""

from typing import Protocol, Any, runtime_checkable
import sys


@runtime_checkable
class LoggerProtocol(Protocol):
    """Protocol defining the logging interface."""
    
    def log(self, message: str, level: str) -> None:
        """Log a message with a specific level."""
        ...
    
    def error(self, message: str, *args: Any) -> None:
        """Log an error message."""
        ...
    
    def warn(self, message: str, *args: Any) -> None:
        """Log a warning message."""
        ...
    
    def info(self, message: str, *args: Any) -> None:
        """Log an info message."""
        ...
    
    def debug(self, message: str, *args: Any) -> None:
        """Log a debug message."""
        ...


class ConsoleLogger:
    """Logger implementation that outputs to console."""
    
    def log(self, message: str, level: str) -> None:
        """Log a message with a specific level."""
        print(f"{message} (level: {level})")
    
    def error(self, message: str, *args: Any) -> None:
        """Log an error message."""
        print(f"ERROR: {message}", *args, file=sys.stderr)
    
    def warn(self, message: str, *args: Any) -> None:
        """Log a warning message."""
        print(f"WARN: {message}", *args, file=sys.stderr)
    
    def info(self, message: str, *args: Any) -> None:
        """Log an info message."""
        print(f"INFO: {message}", *args)
    
    def debug(self, message: str, *args: Any) -> None:
        """Log a debug message."""
        print(f"DEBUG: {message}", *args)


class NullLogger:
    """Logger implementation that discards all messages."""
    
    def log(self, message: str, level: str) -> None:
        """Log a message with a specific level."""
        pass
    
    def error(self, message: str, *args: Any) -> None:
        """Log an error message."""
        pass
    
    def warn(self, message: str, *args: Any) -> None:
        """Log a warning message."""
        pass
    
    def info(self, message: str, *args: Any) -> None:
        """Log an info message."""
        pass
    
    def debug(self, message: str, *args: Any) -> None:
        """Log a debug message."""
        pass 