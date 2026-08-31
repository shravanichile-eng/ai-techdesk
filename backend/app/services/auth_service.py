"""Service layer for authentication"""

import logging
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.user import User, Role, UserStatus
from app.schemas.user import LoginRequest, RegisterRequest, UserSchema
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service"""

    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, request: RegisterRequest) -> UserSchema:
        """Register a new user"""
        # Check if email exists
        existing_user = self.db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate password
        if len(request.password) < settings.PASSWORD_MIN_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
            )

        # Get USER role (default for new registrations)
        user_role = self.db.query(Role).filter(Role.name == "USER").first()
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User role not found. Please seed database."
            )

        # Create new user
        new_user = User(
            email=request.email,
            full_name=request.full_name,
            password_hash=hash_password(request.password),
            role_id=user_role.id,
            department_id=request.department_id,
            status=UserStatus.ACTIVE.value,
            is_active=True
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        logger.info(f"New user registered: {new_user.email}")
        return UserSchema.from_orm(new_user)

    async def login(self, request: LoginRequest) -> dict:
        """Authenticate user and return JWT token"""
        # Find user
        user = self.db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Check account status
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )

        if user.status == UserStatus.LOCKED.value:
            if user.locked_until and user.locked_until > datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is locked. Try again later."
                )

        # Verify password
        if not verify_password(request.password, user.password_hash):
            # Increment login attempts
            user.login_attempts += 1
            if user.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.status = UserStatus.LOCKED.value
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
            self.db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Reset login attempts and update last login
        user.login_attempts = 0
        user.status = UserStatus.ACTIVE.value
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Create token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role.name}
        )

        logger.info(f"User logged in: {user.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserSchema.from_orm(user)
        }

    async def get_user_by_id(self, user_id: str) -> UserSchema:
        """Get user by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserSchema.from_orm(user)
