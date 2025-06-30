"""Toggle heartbeat request implementation."""

from .acknowledge_request import AcknowledgeRequest


class ToggleHeartbeat(AcknowledgeRequest):
    """Request to toggle heartbeat functionality."""
    
    def __init__(self, enable: bool = True, unsolicited: bool = True):
        """Initialize a toggle heartbeat request.
        
        Args:
            enable: Whether to enable heartbeat.
            unsolicited: Whether to enable unsolicited updates.
        """
        data = [int(enable), int(unsolicited)]
        super().__init__(0x08, data) 