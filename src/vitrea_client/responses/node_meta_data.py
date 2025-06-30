"""Node metadata response implementation."""

from typing import List, Dict, Any

from ..core.base_response import BaseResponse
from ..utilities.enums import LEDBackgroundBrightness, LockStatus


class NodeMetaData(BaseResponse):
    """Response containing node metadata information."""
    
    # Index constants
    ID_INDEX = 8
    MAC_ADDRESS_INDEX = 9
    TOTAL_KEYS_INDEX = 18
    OFFSET_START_INDEX = 19
    
    # Raw offset indices
    RAW_LOCKED_STATE_INDEX = 0
    RAW_LED_LEVEL_INDEX = 1
    RAW_VERSION_INDEX = 3
    RAW_ROOM_ID_INDEX = 7
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass
    
    def _offset(self, by_index: int) -> int:
        """Calculate offset position."""
        return self.OFFSET_START_INDEX + self.total_keys + by_index
    
    def _at_offset(self, by_index: int) -> int:
        """Get value at offset position."""
        return self.get(self._offset(by_index))
    
    @property
    def id(self) -> int:
        """Get the node ID."""
        return self.get(self.ID_INDEX)
    
    @property
    def room_id(self) -> int:
        """Get the room ID."""
        return self._at_offset(self.RAW_ROOM_ID_INDEX)
    
    @property
    def version(self) -> str:
        """Get the version string."""
        offset = self._offset(self.RAW_VERSION_INDEX)
        if offset + 2 < len(self._buffer):
            version, subversion, patch = self._buffer[offset:offset + 3]
            return f"{version}.{subversion}{patch}"
        return "0.0.0"
    
    @property
    def mac_address(self) -> str:
        """Get the MAC address as hex string."""
        start = self.MAC_ADDRESS_INDEX
        if start + 8 <= len(self._buffer):
            mac_bytes = self._buffer[start:start + 8]
            return self._to_hex_string(mac_bytes)
        return ""
    
    @property
    def total_keys(self) -> int:
        """Get the total number of keys."""
        return self.get(self.TOTAL_KEYS_INDEX)
    
    @property
    def keys(self) -> List[int]:
        """Get the list of key IDs."""
        return list(range(self.total_keys))
    
    @property
    def keys_list(self) -> List[Dict[str, int]]:
        """Get the list of keys with their types."""
        keys = []
        for i in range(self.total_keys):
            keys.append({
                "id": i,
                "type": self._at_offset(i)
            })
        return keys
    
    @property
    def lock_status(self) -> LockStatus:
        """Get the lock status."""
        return LockStatus(self._at_offset(self.RAW_LOCKED_STATE_INDEX))
    
    @property
    def is_locked(self) -> bool:
        """Check if the node is locked."""
        return self.lock_status == LockStatus.LOCKED
    
    @property
    def led_level(self) -> LEDBackgroundBrightness:
        """Get the LED background brightness level."""
        return LEDBackgroundBrightness(self._at_offset(self.RAW_LED_LEVEL_INDEX))
    
    @property
    def _to_log(self) -> Dict[str, Any]:
        """Get additional log data for node metadata."""
        return {
            **super()._to_log,
            "nodeID": self.id,
            "totalKeys": self.total_keys,
            "isLocked": self.is_locked,
            "keysList": self.keys_list,
            "version": self.version,
            "macAddress": self.mac_address,
            "ledLevel": self.led_level
        } 