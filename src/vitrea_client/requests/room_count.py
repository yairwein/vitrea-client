"""Room count request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID


class RoomCount(BaseRequest):
    """Request to get the count of rooms."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self):
        """Initialize a room count request."""
        super().__init__(CommandID.ROOM_COUNT) 