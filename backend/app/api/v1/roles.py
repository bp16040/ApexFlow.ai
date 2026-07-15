from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.db.session import get_db
from app.models.auth import Permission, Role, RolePermission, User
from app.schemas.auth import (
    PermissionCreate,
    PermissionResponse,
    RoleCreate,
    RolePermissionUpdate,
    RoleResponse,
)

router = APIRouter(prefix="/roles", tags=["roles and permissions"])


@router.get("", response_model=list[RoleResponse])
def list_roles(_: User = Depends(require_permissions("roles.read")), db: Session = Depends(get_db)) -> list[Role]:
    return list(db.scalars(select(Role).order_by(Role.key)))


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate, _: User = Depends(require_permissions("roles.manage")), db: Session = Depends(get_db)
) -> Role:
    role = Role(**payload.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(
    _: User = Depends(require_permissions("roles.read")), db: Session = Depends(get_db)
) -> list[Permission]:
    return list(db.scalars(select(Permission).order_by(Permission.code)))


@router.post("/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
def create_permission(
    payload: PermissionCreate, _: User = Depends(require_permissions("roles.manage")), db: Session = Depends(get_db)
) -> Permission:
    permission = Permission(**payload.model_dump())
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


@router.put("/{role_id}/permissions", status_code=status.HTTP_204_NO_CONTENT)
def set_role_permissions(
    role_id: str,
    payload: RolePermissionUpdate,
    _: User = Depends(require_permissions("roles.manage")),
    db: Session = Depends(get_db),
) -> None:
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    found = list(db.scalars(select(Permission.id).where(Permission.id.in_(payload.permission_ids))))
    if len(found) != len(set(payload.permission_ids)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unknown permission")
    db.execute(delete(RolePermission).where(RolePermission.role_id == role.id))
    db.add_all([RolePermission(role_id=role.id, permission_id=permission_id) for permission_id in payload.permission_ids])
    db.commit()


@router.get("/matrix")
def permission_matrix(
    _: User = Depends(require_permissions("roles.read")), db: Session = Depends(get_db)
) -> dict[str, list[str]]:
    rows = db.execute(
        select(Role.key, Permission.code)
        .join(RolePermission, RolePermission.role_id == Role.id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .order_by(Role.key, Permission.code)
    )
    matrix: dict[str, list[str]] = {role.key: [] for role in db.scalars(select(Role))}
    for role_key, permission_code in rows:
        matrix[role_key].append(permission_code)
    return matrix
