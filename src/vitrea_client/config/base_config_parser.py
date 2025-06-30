"""Base configuration parser."""

import os
from typing import TypeVar, Generic, Dict, Any, Optional, Union

T = TypeVar('T')


class BaseConfigParser(Generic[T]):
    """Base class for configuration parsers."""
    
    def __init__(self, configs: Dict[str, Any]):
        """Initialize with partial configuration dictionary."""
        self._configs = configs
    
    def _validate(self, lookup: str, found: Any) -> Any:
        """Validate that a required value is present."""
        if found is None:
            raise TypeError(f"A value for [{lookup}] is required")
        return found
    
    def get(self, key: str, fallback: Any = None, required: bool = False) -> Any:
        """Get a configuration value with fallback and environment variable support."""
        # Convert camelCase to UPPER_SNAKE_CASE for environment variable lookup
        env_key = ""
        for i, char in enumerate(key):
            if char.isupper() and i > 0:
                env_key += "_"
            env_key += char.upper()
        
        env_lookup = f"VITREA_VBOX_{env_key}"
        
        # Priority: direct config > environment variable > fallback
        found = self._configs.get(key)
        if found is None:
            found = os.getenv(env_lookup)
        if found is None:
            found = fallback
        
        if required:
            return self._validate(key, found)
        
        return found 