"""Enums and constants for the Vitrea client."""

from enum import IntEnum


class KeyPowerStatus(IntEnum):
    """Key power status constants."""
    ON = 0x4F
    OFF = 0x46
    LONG = 0x4C
    SHORT = 0x53
    RELEASED = 0x52


class LEDBackgroundBrightness(IntEnum):
    """LED background brightness levels."""
    OFF = 0
    LOW = 1
    HIGH = 2
    MAX = 3


class LockStatus(IntEnum):
    """Lock status constants."""
    UNLOCKED = 0
    LOCKED = 1


class DataGramDirection(IntEnum):
    """Data gram direction constants."""
    OUTGOING = 0x3E
    INCOMING = 0x3C


class KeyCategory(IntEnum):
    """Key category constants."""
    UNDEFINED = 0
    LIGHT = 1
    FAN = 6
    BOILER = 7 