"""Shared enumeration definitions for ApexFlow AI core domains."""

from enum import Enum


class UserStatus(str, Enum):
    """Represent the lifecycle status of a user account."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
