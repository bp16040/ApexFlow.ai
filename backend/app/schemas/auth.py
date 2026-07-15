from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class MagicLinkRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)


class MagicLinkVerifyRequest(BaseModel):
    token: str = Field(min_length=20)


class UserProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    avatar_url: str | None
    is_active: bool
    is_superuser: bool


class RoleCreate(BaseModel):
    key: str = Field(pattern=r"^[a-z0-9_.-]+$", max_length=100)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class PermissionCreate(BaseModel):
    code: str = Field(pattern=r"^[a-z0-9_.-]+$", max_length=150)
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    key: str
    name: str
    description: str | None
    is_system: bool


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None


class RolePermissionUpdate(BaseModel):
    permission_ids: list[UUID]


class UserRoleAssign(BaseModel):
    role_id: UUID
    organization_id: UUID | None = None
