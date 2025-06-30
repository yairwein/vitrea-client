"""Key parameters V2 response implementation."""

from .key_parameters import KeyParameters


class KeyParametersV2(KeyParameters):
    """Response for key parameters in protocol V2."""
    
    # V2 format has different name index
    NAME_INDEX = 21
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass 