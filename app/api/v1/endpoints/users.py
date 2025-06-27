from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.exceptions import AuthorizationError
from app.models.models import User
from app.schemas.schemas import User as UserSchema
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    user_service = UserService(db)
    users = user_service.get_multi(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user_service = UserService(db)
    user = user_service.get(id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise AuthorizationError("Not enough permissions")
    return user 