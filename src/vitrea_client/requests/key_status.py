"""Key status request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID
from ..utilities.events import Events


class KeyStatus(BaseRequest):
    """Request to get the status of a specific key."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, node_id: int, key_id: int):
        """Initialize a key status request.
        
        Args:
            node_id: The ID of the node.
            key_id: The ID of the key.
        """
        super().__init__(CommandID.KEY_STATUS, [node_id, key_id])
    
    @property
    def event_name(self) -> str:
        """Get the event name for status updates."""
        return Events.STATUS_UPDATE 