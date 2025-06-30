"""Message ID generation utility."""


class MessageID:
    """Utility class for generating unique message IDs."""
    
    _message_id_index: int = 0
    
    @classmethod
    def reset_id(cls, base_id: int = 0x00) -> int:
        """Reset the message ID index to a base value."""
        cls._message_id_index = base_id
        return cls._message_id_index
    
    @classmethod
    def get_next_id(cls) -> int:
        """Get the next unique message ID."""
        cls._message_id_index += 1
        
        if cls._message_id_index > 0xFF:
            cls._message_id_index = 0x01
            
        return cls._message_id_index
    
    @classmethod
    def set_next_id(cls, next_id: int) -> None:
        """Set the next message ID by resetting to next_id - 1."""
        cls.reset_id(next_id - 1) 