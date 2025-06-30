"""Node status request implementation."""

from ..core.base_request import BaseRequest


class NodeStatus(BaseRequest):
    """Request to get the status of a specific node."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self, node_id: int):
        """Initialize a node status request.
        
        Args:
            node_id: The ID of the node to get status for.
        """
        super().__init__(0x25, [node_id]) 