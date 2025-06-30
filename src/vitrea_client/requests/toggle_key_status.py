"""Toggle key status request implementation."""

from typing import Optional

from ..core.base_request import BaseRequest
from ..utilities.enums import KeyPowerStatus
from ..utilities.events import Events


class ToggleKeyStatus(BaseRequest):
    """Request to toggle the status of a specific key."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(
        self, 
        node_id: int, 
        key_id: int, 
        status: KeyPowerStatus,
        dimmer_ratio: int = 0,
        timer: int = 0
    ):
        """Initialize a toggle key status request.
        
        Args:
            node_id: The ID of the node.
            key_id: The ID of the key.
            status: The power status to set.
            dimmer_ratio: Dimmer ratio (0-100).
            timer: Timer value in seconds.
        """
        # Convert timer to byte array (high byte, low byte)
        timer_bytes = [(timer >> 8) & 0xFF, timer & 0xFF]
        
        data = [node_id, key_id, status, dimmer_ratio] + timer_bytes
        super().__init__(0x28, data)
    
    @property
    def event_name(self) -> str:
        """Get the event name for acknowledgment."""
        return Events.acknowledgement(self.message_id) 