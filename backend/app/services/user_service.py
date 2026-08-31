"""User service layer"""

import logging
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, Role, Department
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserSchema
from app.core.security import hash_password

logger = logging.getLogger(__name__)


class UserService:
    """User service"""

    def __init__(self, db: Session):
        self.db = db

    async def list_users(self, skip: int = 0, limit: int = 10) -> list:
        """List all users"""
        return self.db.query(User).offset(skip).limit(limit).all()

    async def get_user_by_id(self, user_id: UUID) -> UserSchema:
        """Get user by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserSchema.from_orm(user)

    async def create_user(self, request: UserCreateSchema) -> UserSchema:
        """Create new user"""
        # Check email exists
        if self.db.query(User).filter(User.email == request.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Verify role exists
        role = self.db.query(Role).filter(Role.id == request.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role not found"
            )

        # Verify department exists if provided
        if request.department_id:
            department = self.db.query(Department).filter(Department.id == request.department_id).first()
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department not found"
                )

        new_user = User(
            email=request.email,
            full_name=request.full_name,
            password_hash=hash_password(request.password),
            role_id=request.role_id,
            department_id=request.department_id,
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        logger.info(f"User created: {new_user.email}")
        return UserSchema.from_orm(new_user)

    async def update_user(self, user_id: UUID, request: UserUpdateSchema) -> UserSchema:
        """Update user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_data = request.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User updated: {user.email}")
        return UserSchema.from_orm(user)

    async def delete_user(self, user_id: UUID) -> None:
        """Delete user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        self.db.delete(user)
        self.db.commit()

        logger.info(f"User deleted: {user.email}")
