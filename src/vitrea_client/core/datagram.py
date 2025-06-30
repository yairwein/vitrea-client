"""DataGram implementation for low-level data format."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Union

from ..utilities.enums import DataGramDirection
from ..utilities.events import Events


class DataGram(ABC):
    """Abstract base class for handling low-level data format."""
    
    # Index constants
    DIRECTION_INDEX = 3
    COMMAND_ID_INDEX = 4
    DATA_LENGTH_INDEX = 5
    MESSAGE_ID_INDEX = 7
    DATA_INDEX = 8
    
    # First 3 bytes of every DataGram
    PREFIX = [0x56, 0x54, 0x55]
    
    def __init__(self, raw_buffer: Union[bytes, List[int], None] = None):
        """Initialize the DataGram with an optional raw buffer."""
        if raw_buffer is not None:
            if isinstance(raw_buffer, bytes):
                self._buffer = list(raw_buffer)
            else:
                self._buffer = list(raw_buffer)
        else:
            self._buffer = self.PREFIX.copy()
    
    @abstractmethod
    def _abstract_method(self):
        """Abstract method to prevent direct instantiation."""
        pass
    
    def get(self, index: int) -> int:
        """Get a byte at the specified index."""
        return self._buffer[index]
    
    def get_data(self) -> List[int]:
        """Get a copy of the data portion."""
        return self.data.copy()
    
    def _to_hex(self, number: int) -> str:
        """Convert a number to hex string format."""
        return f"0x{number:02X}"
    
    def _to_hex_string(self, buffer: List[int] = None) -> str:
        """Convert buffer to hex string representation."""
        if buffer is None:
            buffer = self._buffer
        
        return ":".join(f"{byte:02X}" for byte in buffer)
    
    def _buffer_to_string(self, offset: int) -> str:
        """Convert buffer slice to UTF-16LE string."""
        slice_data = self._buffer[offset:]
        return bytes(slice_data).decode('utf-16le', errors='ignore')
    
    @property
    def length(self) -> int:
        """Get the length of the buffer."""
        return len(self._buffer)
    
    @property
    def direction(self) -> DataGramDirection:
        """Get the direction of the datagram."""
        return DataGramDirection(self.get(self.DIRECTION_INDEX))
    
    @property
    def checksum(self) -> int:
        """Calculate the checksum for the datagram."""
        return sum(self._buffer) & 0xFF
    
    @property
    def command_id(self) -> int:
        """Get the command ID."""
        return self.get(self.COMMAND_ID_INDEX)
    
    @property
    def message_id(self) -> int:
        """Get the message ID."""
        return self.get(self.MESSAGE_ID_INDEX)
    
    @property
    def data(self) -> List[int]:
        """Get the data portion of the datagram."""
        if self.has_data:
            return self._buffer[self.DATA_INDEX:]
        return []
    
    @property
    def has_data(self) -> bool:
        """Check if the datagram has data."""
        return self.length > self.DATA_INDEX
    
    @property
    def data_length(self) -> Tuple[int, int]:
        """Get the data length as a tuple of two bytes."""
        length = len(self.data) + 2
        return (length >> 8 & 0xFF, length & 0xFF)
    
    @property
    def event_name(self) -> str:
        """Get the event name for this datagram."""
        return Events.generate(self.command_id, self.message_id)
    
    @property
    def command_name(self) -> str:
        """Get the command name (class name)."""
        return self.__class__.__name__
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data (to be overridden by subclasses)."""
        return {}
    
    @property
    def log_data(self) -> Dict[str, Any]:
        """Get comprehensive log data for this datagram."""
        return {
            "command": self.command_name,
            "direction": "Incoming" if self.direction == DataGramDirection.INCOMING else "Outgoing",
            "commandID": self._to_hex(self.command_id),
            "messageID": self._to_hex(self.message_id),
            **self._to_log,
            "raw": self._to_hex_string()
        } 