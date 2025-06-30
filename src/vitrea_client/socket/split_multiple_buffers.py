"""Utility for splitting multiple datagrams from a single buffer."""

from typing import List


class SplitMultipleBuffers:
    """Handles splitting multiple datagrams that may be concatenated in a single buffer."""
    
    @staticmethod
    def handle(buffer: bytes) -> List[bytes]:
        """Split a buffer that may contain multiple datagrams.
        
        The Vitrea protocol can send multiple datagrams in a single TCP packet.
        This method splits them based on the datagram prefix pattern [0x56, 0x54, 0x55, 0x3C].
        
        Args:
            buffer: Raw bytes buffer that may contain multiple datagrams
            
        Returns:
            List of individual datagram buffers
        """
        if not buffer:
            return []
        
        # Convert to hex string for easier manipulation
        hex_string = buffer.hex()
        
        # Check if buffer contains the expected prefix
        if '5654553c' not in hex_string:
            return []
        
        # Split on the datagram prefix pattern: 56 54 55 3C (VTU<)
        # Add separator before each occurrence (except the first)
        hex_string = hex_string.replace('5654553c', ';;;5654553c')
        
        # Split and filter out empty strings
        hex_parts = [part for part in hex_string.split(';;;') if part]
        
        # Convert back to bytes
        return [bytes.fromhex(part) for part in hex_parts] 