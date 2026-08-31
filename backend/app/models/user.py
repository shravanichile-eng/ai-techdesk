"""User and Role models"""

from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "USER"
    AGENT = "AGENT"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"


class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"
    SUSPENDED = "SUSPENDED"


class Role(Base):
    """Role model"""
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="role")


class Department(Base):
    """Department model"""
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    code = Column(String(10), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="department")
    teams = relationship("Team", back_populates="department")


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Relationships
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    
    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    
    # Status
    status = Column(String(20), default=UserStatus.ACTIVE.value)
    is_active = Column(Boolean, default=True, index=True)
    
    # Contact
    phone = Column(String(20))
    avatar_url = Column(String(500))
    
    # Metadata
    last_login = Column(DateTime)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.creator_id")
    assigned_tickets = relationship("Ticket", back_populates="assigned_to", foreign_keys="Ticket.assigned_agent_id")
    messages = relationship("TicketMessage", back_populates="author")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    team_memberships = relationship("TeamMember", back_populates="user")
    feedback = relationship("TicketFeedback", back_populates="user")
