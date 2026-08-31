"""Users router"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database.base import get_db
from app.schemas.user import UserSchema, UserCreateSchema, UserUpdateSchema, UserDetailSchema
from app.services.user_service import UserService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=List[UserSchema])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all users (admin only)"""
    service = UserService(db)
    return await service.list_users(skip, limit)


@router.get("/{user_id}", response_model=UserDetailSchema)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user by ID"""
    service = UserService(db)
    return await service.get_user_by_id(user_id)


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new user (admin only)"""
    service = UserService(db)
    return await service.create_user(request)


@router.patch("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: UUID,
    request: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user (admin or self)"""
    service = UserService(db)
    return await service.update_user(user_id, request)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete user (admin only)"""
    service = UserService(db)
    await service.delete_user(user_id)
    return None
