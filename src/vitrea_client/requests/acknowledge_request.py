"""Acknowledge request implementation."""

from ..core.base_request import BaseRequest
from ..utilities.events import Events


class AcknowledgeRequest(BaseRequest):
    """Base class for acknowledgment requests."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    @property
    def event_name(self) -> str:
        """Get the event name for acknowledgment."""
        return Events.acknowledgement(self.message_id) 