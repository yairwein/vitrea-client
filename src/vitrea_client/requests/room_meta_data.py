"""Room metadata request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID


class RoomMetaData(BaseRequest):
    """Request to get metadata for a specific room."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, room_id: int):
        """Initialize a room metadata request.
        
        Args:
            room_id: The ID of the room to get metadata for.
        """
        super().__init__(CommandID.ROOM_META_DATA, [room_id]) 