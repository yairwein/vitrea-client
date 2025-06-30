"""Connection exists exception."""


class ConnectionExistsException(Exception):
    """Exception raised when trying to create a connection that already exists."""
    
    def __init__(self, message: str = "Socket connection already exists"):
        """Initialize the exception with a message."""
        super().__init__(message) 