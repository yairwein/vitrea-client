"""Heartbeat request implementation."""

from .acknowledge_request import AcknowledgeRequest


class Heartbeat(AcknowledgeRequest):
    """Request to send a heartbeat."""
    
    def __init__(self):
        """Initialize a heartbeat request."""
        super().__init__(0x07) 