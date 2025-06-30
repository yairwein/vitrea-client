"""Acknowledgement response implementation."""

from typing import Union, List

from ..core.base_response import BaseResponse


class Acknowledgement(BaseResponse):
    """Response for acknowledgement messages."""
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass 