from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_department_code"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50))


class Program(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_program_code"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    department_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50))


class AcademicSession(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "academic_sessions"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_session_code"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(50))
    starts_on: Mapped[date] = mapped_column(Date)
    ends_on: Mapped[date] = mapped_column(Date)


class Designation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "designations"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_designation_code"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(150))
    code: Mapped[str] = mapped_column(String(50))
    rank: Mapped[int] = mapped_column(Integer, default=0)


class DirectoryProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "directory_profiles"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_directory_profile_user"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    department_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    program_id: Mapped[UUID | None] = mapped_column(ForeignKey("programs.id", ondelete="SET NULL"))
    designation_id: Mapped[UUID | None] = mapped_column(ForeignKey("designations.id", ondelete="SET NULL"))
    directory_type: Mapped[str] = mapped_column(String(50), index=True)
    employee_code: Mapped[str | None] = mapped_column(String(100))


class CoordinatorAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "coordinator_assignments"

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    department_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    program_id: Mapped[UUID | None] = mapped_column(ForeignKey("programs.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(150))


class ReportingLine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reporting_lines"
    __table_args__ = (UniqueConstraint("organization_id", "report_id", name="uq_reporting_line_report"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    manager_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    report_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    notes: Mapped[str | None] = mapped_column(Text)
