"""Generic unused response implementation."""

from typing import Union, List

from ..core.base_response import BaseResponse


class GenericUnusedResponse(BaseResponse):
    """Response for unused/ignored message types."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass 