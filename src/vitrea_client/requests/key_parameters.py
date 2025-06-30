"""Key parameters request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID


class KeyParameters(BaseRequest):
    """Request to get parameters for a specific key."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, node_id: int, key_id: int):
        """Initialize a key parameters request.
        
        Args:
            node_id: The ID of the node.
            key_id: The ID of the key.
        """
        super().__init__(CommandID.KEY_PARAMETERS, [node_id, key_id]) 