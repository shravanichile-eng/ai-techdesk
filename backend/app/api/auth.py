"""Authentication router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.base import get_db
from app.schemas.user import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserSchema,
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    service = AuthService(db)
    return await service.register_user(request)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    service = AuthService(db)
    return await service.login(request)


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token"""
    # Implementation in AuthService
    return {"message": "Token refresh endpoint"}


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile"""
    service = AuthService(db)
    return await service.get_user_by_id(current_user["user_id"])
