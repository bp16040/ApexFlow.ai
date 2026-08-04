"""
Shared abstract base model for all database entities.

Every persistent model in ApexFlow AI should inherit from BaseModel
instead of directly inheriting from SQLAlchemy Base.
"""

from __future__ import annotations

from sqlalchemy.orm import declared_attr

from app.db.base import Base
from app.db.mixins import (
    ActiveMixin,
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
    VersionMixin,
)


class BaseModel(
    Base,
    UUIDMixin,
    TimestampMixin,
    AuditMixin,
    ActiveMixin,
    SoftDeleteMixin,
    VersionMixin,
):
    """Common abstract model inherited by every entity."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generate table names.

        Example:
            User -> users
            Department -> departments
            WorkRequest -> work_requests
        """
        import re

        name = cls.__name__
        snake = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

        if snake.endswith("s"):
            return snake

        return f"{snake}s"
