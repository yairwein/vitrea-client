"""Node metadata request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID


class NodeMetaData(BaseRequest):
    """Request to get metadata for a specific node."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, node_id: int):
        """Initialize a node metadata request.
        
        Args:
            node_id: The ID of the node to get metadata for.
        """
        super().__init__(CommandID.NODE_META_DATA, [node_id]) 