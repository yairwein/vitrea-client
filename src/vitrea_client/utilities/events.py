"""Event name generation utility."""

from typing import Union


class Events:
    """Utility class for generating event names."""
    
    STATUS_UPDATE: str = "vitrea::status::update"
    UNKNOWN_DATA: str = "vitrea::data::unknown"
    
    @classmethod
    def acknowledgement(cls, message_id: int) -> str:
        """Generate an acknowledgement event name."""
        return cls.generate(0x00, message_id)
    
    @classmethod
    def generate(cls, *keys: Union[str, int]) -> str:
        """Generate an event name from keys."""
        to_join = [
            format(int(key), '02x') if isinstance(key, int) else key
            for key in keys
        ]
        return f"data::{'-'.join(to_join)}" 