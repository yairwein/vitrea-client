"""Key parameters response implementation."""

from typing import Dict, Any

from ..core.base_response import BaseResponse
from ..utilities.enums import KeyCategory


class KeyParameters(BaseResponse):
    """Response containing key parameters information."""
    
    # Index constants
    NODE_ID_INDEX = 8
    KEY_ID_INDEX = 9
    CATEGORY_INDEX = 10
    DIMMER_RATIO_INDEX = 11
    NAME_INDEX = 20
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    @property
    def node_id(self) -> int:
        """Get the node ID."""
        return self.get(self.NODE_ID_INDEX)
    
    @property
    def key_id(self) -> int:
        """Get the key ID."""
        return self.get(self.KEY_ID_INDEX)
    
    @property
    def category(self) -> KeyCategory:
        """Get the key category."""
        return KeyCategory(self.get(self.CATEGORY_INDEX))
    
    @property
    def dimmer_ratio(self) -> int:
        """Get the dimmer ratio."""
        return self.get(self.DIMMER_RATIO_INDEX)
    
    @property
    def name(self) -> str:
        """Get the key name."""
        try:
            return self._buffer_to_string(self.NAME_INDEX).rstrip('\x00')
        except (UnicodeDecodeError, IndexError):
            return ""
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data for key parameters."""
        return {
            **super()._to_log,
            "name": self.name,
            "nodeID": self.node_id,
            "keyID": self.key_id,
            "category": self.category,
            "dimmerRatio": self.dimmer_ratio
        } 