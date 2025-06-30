"""Key status response implementation."""

from ..core.base_response import BaseResponse
from ..utilities.enums import KeyPowerStatus
from ..utilities.events import Events


class KeyStatus(BaseResponse):
    """Response containing key status information."""
    
    # Index constants
    NODE_ID_INDEX = 8
    KEY_ID_INDEX = 9
    POWER_INDEX = 10
    
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
    def power(self) -> KeyPowerStatus:
        """Get the power status."""
        return KeyPowerStatus(self.get(self.POWER_INDEX))
    
    @property
    def is_on(self) -> bool:
        """Check if the key is on."""
        return self.power == KeyPowerStatus.ON
    
    @property
    def is_off(self) -> bool:
        """Check if the key is off."""
        return self.power == KeyPowerStatus.OFF
    
    @property
    def is_released(self) -> bool:
        """Check if the key is released."""
        return self.power == KeyPowerStatus.RELEASED
    
    @property
    def event_name(self) -> str:
        """Get the event name for status updates."""
        return Events.STATUS_UPDATE 