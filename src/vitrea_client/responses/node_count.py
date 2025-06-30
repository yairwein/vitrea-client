"""Node count response implementation."""

from typing import List, Dict, Any

from ..core.base_response import BaseResponse


class NodeCount(BaseResponse):
    """Response containing node count information."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    @property
    def total(self) -> int:
        """Get the total number of nodes."""
        return len(self.list)
    
    @property
    def list(self) -> List[int]:
        """Get the list of node IDs."""
        return self.data[1:] if len(self.data) > 1 else []
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data for node count."""
        return {
            **super()._to_log,
            "total": self.total,
            "list": self.list
        } 