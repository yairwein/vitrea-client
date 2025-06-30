"""Base response class for all Vitrea responses."""

from typing import List, Union, Tuple, Dict, Any

from .datagram import DataGram


class BaseResponse(DataGram):
    """Base class for all response types."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, raw_buffer: Union[bytes, List[int]]):
        """Initialize a base response from raw buffer data."""
        # Convert to list if bytes
        if isinstance(raw_buffer, bytes):
            buffer_list = list(raw_buffer)
        else:
            buffer_list = list(raw_buffer)
        
        # Extract checksum (last byte) before calling super()
        self._raw_checksum = buffer_list.pop() if buffer_list else 0
        
        # Initialize with the buffer minus the checksum
        super().__init__(buffer_list)
    
    @property
    def data_length(self) -> Tuple[int, int]:
        """Get the data length from the buffer."""
        start = self.DATA_LENGTH_INDEX
        return (self.get(start), self.get(start + 1))
    
    @property
    def has_valid_checksum(self) -> bool:
        """Check if the response has a valid checksum."""
        return self.checksum == self._raw_checksum
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data for responses."""
        return {"hasValidChecksum": self.has_valid_checksum} 