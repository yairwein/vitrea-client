"""Room metadata response implementation."""

from typing import List, Dict, Any

from ..core.base_response import BaseResponse


class RoomMetaData(BaseResponse):
    """Response containing room metadata information."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    @property
    def room_id(self) -> int:
        """Get the room ID."""
        return self.get(8) if len(self._buffer) > 8 else 0
    
    @property
    def name(self) -> str:
        """Get the room name."""
        if len(self.data) > 1:
            # Room name is encoded in UTF-16LE after the first byte
            name_bytes = bytes(self.data[1:])
            return name_bytes.decode('utf-16le', errors='ignore').rstrip('\x00')
        return ""
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data for room metadata."""
        return {
            **super()._to_log,
            "roomID": self.room_id,
            "name": self.name
        } 