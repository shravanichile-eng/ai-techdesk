"""User and authentication schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class RoleSchema(BaseModel):
    """Role schema"""
    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DepartmentSchema(BaseModel):
    """Department schema"""
    id: UUID
    name: str
    description: Optional[str] = None
    code: Optional[str] = None

    class Config:
        from_attributes = True


class UserBaseSchema(BaseModel):
    """User base schema"""
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreateSchema(UserBaseSchema):
    """User creation schema"""
    password: str = Field(..., min_length=8)
    role_id: UUID
    department_id: Optional[UUID] = None


class UserUpdateSchema(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    department_id: Optional[UUID] = None


class UserSchema(UserBaseSchema):
    """User response schema"""
    id: UUID
    role: RoleSchema
    department: Optional[DepartmentSchema] = None
    status: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailSchema(UserSchema):
    """Detailed user schema with statistics"""
    total_tickets: int = 0
    open_tickets: int = 0
    assigned_tickets: int = 0


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)
    department_id: Optional[UUID] = None


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str
