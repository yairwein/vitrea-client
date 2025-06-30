"""No connection exception."""


class NoConnectionException(Exception):
    """Exception raised when trying to use a connection that doesn't exist."""
    
    def __init__(self, message: str = "No socket connection established"):
        """Initialize the exception with a message."""
        super().__init__(message) 