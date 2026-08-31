"""Team and TeamMember models"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database.base import Base


class Team(Base):
    """Support team model"""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Department
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    
    # Team Lead
    team_lead_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # SLA
    default_sla_policy_id = Column(UUID(as_uuid=True), ForeignKey("sla_policies.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = relationship("Department", back_populates="teams")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    assigned_tickets = relationship("Ticket", back_populates="assigned_team", foreign_keys="Ticket.assigned_team_id")
    suggested_tickets = relationship("Ticket", back_populates="suggested_team", foreign_keys="Ticket.ai_suggested_team_id")
    categories = relationship("TeamCategory", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    """Team member assignment"""
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    role = Column(String(50), default="MEMBER")  # LEAD, SENIOR, MEMBER, INTERN
    is_active = Column(Boolean, default=True)
    
    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


class TeamCategory(Base):
    """Categories handled by team"""
    __tablename__ = "team_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    
    priority = Column(Integer, default=0)  # For prioritization
    
    # Relationships
    team = relationship("Team", back_populates="categories")
