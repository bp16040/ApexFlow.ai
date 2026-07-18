"""
Reusable SQLAlchemy mixins used across ApexFlow AI.

Every database model should inherit from BaseModel, which combines
these mixins to provide common auditing, lifecycle, and concurrency
features.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


class UUIDMixin:
    """Adds a UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class TimestampMixin:
    """Automatically maintain creation and modification timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class AuditMixin:
    """
    Stores the user responsible for creating and updating a record.

    These fields will later reference the User table.
    """

    created_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )

    updated_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
    )


class SoftDeleteMixin:
    """Implements logical deletion."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ActiveMixin:
    """Marks whether a record is active."""

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class VersionMixin:
    """Provides optimistic locking support."""

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
