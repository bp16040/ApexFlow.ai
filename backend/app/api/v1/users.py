from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permissions
from app.db.session import get_db
from app.models.auth import User, UserRole
from app.schemas.auth import UserProfileUpdate, UserResponse, UserRoleAssign

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(_: User = Depends(require_permissions("users.read")), db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.email)))


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, _: User = Depends(require_permissions("users.read")), db: Session = Depends(get_db)) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    payload: UserProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> User:
    user.full_name = payload.full_name
    db.commit()
    db.refresh(user)
    return user


@router.post("/{user_id}/roles", status_code=status.HTTP_201_CREATED)
def assign_role(
    user_id: UUID,
    payload: UserRoleAssign,
    _: User = Depends(require_permissions("roles.assign")),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    assignment = UserRole(user_id=user_id, role_id=payload.role_id, organization_id=payload.organization_id)
    db.add(assignment)
    db.commit()
    return {"detail": "Role assigned"}
