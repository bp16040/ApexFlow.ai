"""Authentication, authorization, and canonical user SQLAlchemy models."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.core.enums import UserStatus
from app.db.base import Base
from app.db.base_model import BaseModel
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(BaseModel):
    """Represent the canonical authenticated ApexFlow user account."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    corporate_email: Mapped[str] = synonym("email")
    personal_email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True)
    employee_id: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    google_workspace_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    middle_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    full_name: Mapped[str] = mapped_column(String(255))
    mobile_number: Mapped[str | None] = mapped_column(String(32))
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    password_hash: Mapped[str | None] = mapped_column(String(255))
    failed_login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SqlEnum(UserStatus, name="user_status", native_enum=False, length=20),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    role_assignments: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        foreign_keys="UserRole.user_id",
    )
    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        foreign_keys="Session.user_id",
    )
    passwordless_tokens: Mapped[list["PasswordlessToken"]] = relationship(
        "PasswordlessToken",
        foreign_keys="PasswordlessToken.user_id",
    )


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )


class UserRole(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", "organization_id", name="uq_user_role_scope"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )


class Session(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    user_agent: Mapped[str | None] = mapped_column(String(512))


class PasswordlessToken(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "passwordless_tokens"

    email: Mapped[str] = mapped_column(String(320), index=True)
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
