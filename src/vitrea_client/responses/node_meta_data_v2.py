"""Node metadata V2 response implementation."""

from .node_meta_data import NodeMetaData


class NodeMetaDataV2(NodeMetaData):
    """Response for node metadata in protocol V2."""
    
    # V2 format has shifted indices compared to V1
    TOTAL_KEYS_INDEX = 19
    OFFSET_START_INDEX = 20
    
    def _abstract_method(self):
        """Implementation of abstract method from DataGram."""
        pass 