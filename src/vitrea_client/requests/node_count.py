"""Node count request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID


class NodeCount(BaseRequest):
    """Request to get the count of nodes."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self):
        """Initialize a node count request."""
        super().__init__(CommandID.NODE_COUNT) 