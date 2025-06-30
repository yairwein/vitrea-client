"""Constants for command IDs and response codes."""

from enum import IntEnum


class CommandID(IntEnum):
    """Command IDs for requests and responses."""
    ROOM_META_DATA = 0x1A
    ROOM_COUNT = 0x1D
    NODE_META_DATA = 0x1F
    NODE_COUNT = 0x24
    KEY_STATUS = 0x29
    KEY_PARAMETERS = 0x2B
    ACKNOWLEDGEMENT = 0x00
    NODE_EXISTENCE_STATUS = 0xC8
    INTERNAL_UNIT_STATUSES = 0x60 