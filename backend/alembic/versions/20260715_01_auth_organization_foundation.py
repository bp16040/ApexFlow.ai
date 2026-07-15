"""authentication and organization foundation

Revision ID: 20260715_01
Revises:
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa
from uuid import UUID


revision = "20260715_01"
down_revision = None
branch_labels = None
depends_on = None

ADMIN_ROLE_ID = UUID("00000000-0000-0000-0000-000000000001")
PERMISSIONS = [
    (UUID("00000000-0000-0000-0000-000000000101"), "users.read", "Read users"),
    (UUID("00000000-0000-0000-0000-000000000102"), "roles.read", "Read roles and permissions"),
    (UUID("00000000-0000-0000-0000-000000000103"), "roles.manage", "Manage roles and permissions"),
    (UUID("00000000-0000-0000-0000-000000000104"), "roles.assign", "Assign roles to users"),
    (UUID("00000000-0000-0000-0000-000000000105"), "organization.read", "Read organization directory"),
    (UUID("00000000-0000-0000-0000-000000000106"), "organization.manage", "Manage organization structure"),
]


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(2048)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        *timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"], unique=True)
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        *timestamps(),
    )
    op.create_index("ix_roles_key", "roles", ["key"], unique=True)
    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("code", sa.String(150), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.Text()),
        *timestamps(),
    )
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)
    op.create_table(
        "departments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", sa.Uuid(), sa.ForeignKey("departments.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "code", name="uq_department_code"),
    )
    op.create_table(
        "programs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", sa.Uuid(), sa.ForeignKey("departments.id", ondelete="SET NULL")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "code", name="uq_program_code"),
    )
    op.create_table(
        "academic_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("ends_on", sa.Date(), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "code", name="uq_session_code"),
    )
    op.create_table(
        "designations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False, server_default="0"),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "code", name="uq_designation_code"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.Uuid(), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        *timestamps(),
        sa.UniqueConstraint("user_id", "role_id", "organization_id", name="uq_user_role_scope"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])
    op.create_index("ix_user_roles_organization_id", "user_roles", ["organization_id"])
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("user_agent", sa.String(512)),
        *timestamps(),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_refresh_token_hash", "sessions", ["refresh_token_hash"], unique=True)
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"])
    op.create_table(
        "passwordless_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True)),
        *timestamps(),
    )
    op.create_index("ix_passwordless_tokens_email", "passwordless_tokens", ["email"])
    op.create_index("ix_passwordless_tokens_user_id", "passwordless_tokens", ["user_id"])
    op.create_index("ix_passwordless_tokens_token_hash", "passwordless_tokens", ["token_hash"], unique=True)
    op.create_index("ix_passwordless_tokens_expires_at", "passwordless_tokens", ["expires_at"])
    op.create_table(
        "directory_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", sa.Uuid(), sa.ForeignKey("departments.id", ondelete="SET NULL")),
        sa.Column("program_id", sa.Uuid(), sa.ForeignKey("programs.id", ondelete="SET NULL")),
        sa.Column("designation_id", sa.Uuid(), sa.ForeignKey("designations.id", ondelete="SET NULL")),
        sa.Column("directory_type", sa.String(50), nullable=False),
        sa.Column("employee_code", sa.String(100)),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_directory_profile_user"),
    )
    op.create_index("ix_directory_profiles_directory_type", "directory_profiles", ["directory_type"])
    op.create_table(
        "coordinator_assignments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("department_id", sa.Uuid(), sa.ForeignKey("departments.id", ondelete="SET NULL")),
        sa.Column("program_id", sa.Uuid(), sa.ForeignKey("programs.id", ondelete="SET NULL")),
        sa.Column("title", sa.String(150), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "reporting_lines",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("organization_id", sa.Uuid(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("manager_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("notes", sa.Text()),
        *timestamps(),
        sa.UniqueConstraint("organization_id", "report_id", name="uq_reporting_line_report"),
    )
    roles = sa.table("roles", sa.column("id", sa.Uuid()), sa.column("key", sa.String()), sa.column("name", sa.String()), sa.column("is_system", sa.Boolean()))
    permissions = sa.table("permissions", sa.column("id", sa.Uuid()), sa.column("code", sa.String()), sa.column("name", sa.String()))
    role_permissions = sa.table("role_permissions", sa.column("role_id", sa.Uuid()), sa.column("permission_id", sa.Uuid()))
    op.bulk_insert(roles, [{"id": ADMIN_ROLE_ID, "key": "platform_admin", "name": "Platform administrator", "is_system": True}])
    op.bulk_insert(permissions, [{"id": item[0], "code": item[1], "name": item[2]} for item in PERMISSIONS])
    op.bulk_insert(role_permissions, [{"role_id": ADMIN_ROLE_ID, "permission_id": item[0]} for item in PERMISSIONS])


def downgrade() -> None:
    for table in [
        "reporting_lines", "coordinator_assignments", "directory_profiles", "passwordless_tokens", "sessions",
        "user_roles", "role_permissions", "designations", "academic_sessions", "programs", "departments",
        "permissions", "roles", "organizations", "users",
    ]:
        op.drop_table(table)
