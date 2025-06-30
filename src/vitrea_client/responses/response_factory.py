"""Response factory for creating response objects from raw data."""

from typing import Optional, Type, Dict, Union, List

from ..constants import CommandID
from ..config.connection_config import ProtocolVersion
from ..utilities.enums import DataGramDirection
from ..core.datagram import DataGram
from ..core.base_response import BaseResponse

from . import (
    Acknowledgement,
    GenericUnusedResponse,
    InternalUnitStatuses,
    KeyParameters,
    KeyParametersV2,
    KeyStatus,
    NodeCount,
    NodeMetaData,
    NodeMetaDataV2,
    RoomCount,
    RoomMetaData,
)


class ResponseFactory:
    """Factory for creating response objects from raw buffer data."""
    
    # Lookup table for V1 protocol
    _LOOKUP_V1: Dict[CommandID, Type[BaseResponse]] = {
        CommandID.ACKNOWLEDGEMENT: Acknowledgement,
        CommandID.INTERNAL_UNIT_STATUSES: InternalUnitStatuses,
        CommandID.KEY_PARAMETERS: KeyParameters,
        CommandID.KEY_STATUS: KeyStatus,
        CommandID.NODE_COUNT: NodeCount,
        CommandID.NODE_META_DATA: NodeMetaData,
        CommandID.ROOM_COUNT: RoomCount,
        CommandID.ROOM_META_DATA: RoomMetaData,
        CommandID.NODE_EXISTENCE_STATUS: GenericUnusedResponse,
    }
    
    # Lookup table for V2 protocol
    _LOOKUP_V2: Dict[CommandID, Type[BaseResponse]] = {
        **_LOOKUP_V1,
        CommandID.NODE_META_DATA: NodeMetaDataV2,
        CommandID.KEY_PARAMETERS: KeyParametersV2,
    }
    
    # Combined lookup tables
    _LOOKUP_TABLE = {
        ProtocolVersion.V1: _LOOKUP_V1,
        ProtocolVersion.V2: _LOOKUP_V2,
    }
    
    @classmethod
    def _is_incoming(cls, raw_buffer: Union[bytes, List[int]]) -> bool:
        """Check if the buffer represents an incoming message."""
        if isinstance(raw_buffer, bytes):
            buffer = list(raw_buffer)
        else:
            buffer = raw_buffer
        
        if len(buffer) <= DataGram.DIRECTION_INDEX:
            return False
            
        return buffer[DataGram.DIRECTION_INDEX] == DataGramDirection.INCOMING
    
    @classmethod
    def _lookup(
        cls, 
        raw_buffer: Union[bytes, List[int]], 
        version: ProtocolVersion
    ) -> Optional[Type[BaseResponse]]:
        """Look up the response class for the given buffer and protocol version."""
        if isinstance(raw_buffer, bytes):
            buffer = list(raw_buffer)
        else:
            buffer = raw_buffer
        
        if len(buffer) <= DataGram.COMMAND_ID_INDEX:
            return None
            
        try:
            command_id = CommandID(buffer[DataGram.COMMAND_ID_INDEX])
            return cls._LOOKUP_TABLE[version].get(command_id)
        except ValueError:
            # Unknown command ID
            return None
    
    @classmethod
    def find(
        cls, 
        raw_buffer: Union[bytes, List[int]], 
        version: ProtocolVersion
    ) -> Optional[BaseResponse]:
        """Create a response object from raw buffer data.
        
        Args:
            raw_buffer: The raw buffer data.
            version: The protocol version to use.
            
        Returns:
            A response object if successful, None otherwise.
        """
        if not cls._is_incoming(raw_buffer):
            return None
        
        response_class = cls._lookup(raw_buffer, version)
        if response_class is None:
            return None
        
        try:
            instance = response_class(raw_buffer)
            return instance if instance.has_valid_checksum else None
        except Exception:
            # Failed to create response instance
            return None 