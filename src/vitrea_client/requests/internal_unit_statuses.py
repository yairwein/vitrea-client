"""Internal unit statuses request implementation."""

from ..core.base_request import BaseRequest
from ..constants import CommandID


class InternalUnitStatuses(BaseRequest):
    """Request to get internal unit statuses."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def __init__(self):
        """Initialize an internal unit statuses request."""
        super().__init__(CommandID.INTERNAL_UNIT_STATUSES) 