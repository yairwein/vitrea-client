"""Base request class for all Vitrea requests."""

from typing import List, Optional, Dict, Any

from .datagram import DataGram
from ..utilities.enums import DataGramDirection
from ..utilities.message_id import MessageID


class BaseRequest(DataGram):
    """Base class for all request types."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, command_id: int = 0x00, data: Optional[List[int]] = None):
        """Initialize a base request with command ID and optional data."""
        super().__init__()
        
        # Add direction and command ID
        self._buffer.append(DataGramDirection.OUTGOING)
        self._buffer.append(command_id)
        
        # Set message ID at the correct index
        # First, ensure the buffer is long enough
        while len(self._buffer) <= self.MESSAGE_ID_INDEX:
            self._buffer.append(0)
        
        self._buffer[self.MESSAGE_ID_INDEX] = MessageID.get_next_id()
        
        # Add data if provided
        if data is not None:
            self._buffer.extend(data)
        
        # Set the data length
        self._set_data_length()
    
    def _set_data_length(self) -> None:
        """Set the data length bytes in the buffer."""
        length_bytes = self.data_length
        
        # Ensure buffer is long enough for data length bytes
        while len(self._buffer) <= self.DATA_LENGTH_INDEX + 1:
            self._buffer.append(0)
        
        # Insert/replace the data length bytes
        self._buffer[self.DATA_LENGTH_INDEX:self.DATA_LENGTH_INDEX + 2] = length_bytes
    
    def build(self) -> bytes:
        """Build the final request buffer with checksum."""
        return bytes(self._buffer + [self.checksum])
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data for requests."""
        return {"data": self._to_hex_string(self.data)} 