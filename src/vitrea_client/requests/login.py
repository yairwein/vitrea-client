"""Login request implementation."""

from .acknowledge_request import AcknowledgeRequest


class Login(AcknowledgeRequest):
    """Request to login with username and password."""
    
    def __init__(self, username: str, password: str):
        """Initialize a login request.
        
        Args:
            username: The username for authentication.
            password: The password for authentication.
        """
        # Convert strings to UTF-16LE bytes
        username_bytes = username.encode('utf-16le')
        password_bytes = password.encode('utf-16le')
        
        # Build data array: 0x0a + username + 0x0a + password
        data = [0x0a] + list(username_bytes) + [0x0a] + list(password_bytes)
        
        super().__init__(0x01, data) 