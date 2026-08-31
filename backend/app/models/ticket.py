"""Ticket and related models"""

from sqlalchemy import Column, String, Text, Enum, DateTime, Integer, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.database.base import Base


class TicketStatus(str, enum.Enum):
    """Ticket lifecycle status"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    AI_ANALYZING = "AI_ANALYZING"
    CLASSIFIED = "CLASSIFIED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


class TicketPriority(str, enum.Enum):
    """Ticket priority level"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TicketUrgency(str, enum.Enum):
    """Ticket urgency level"""
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TicketImpact(str, enum.Enum):
    """Ticket impact scope"""
    ORGANIZATION_WIDE = "ORGANIZATION_WIDE"
    DEPARTMENT = "DEPARTMENT"
    TEAM = "TEAM"
    INDIVIDUAL = "INDIVIDUAL"


class Category(Base):
    """Ticket category"""
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500))
    icon = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subcategories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="category")


class SubCategory(Base):
    """Ticket subcategory"""
    __tablename__ = "subcategories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="subcategories")
    tickets = relationship("Ticket", back_populates="subcategory")

    __table_args__ = (Index("idx_category_subcategory", "category_id"),)


class Ticket(Base):
    """Ticket model"""
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(20), unique=True, nullable=False, index=True)  # TK-000001
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # User
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    assigned_agent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Classification
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id"), nullable=True)
    
    # Status & Priority
    status = Column(String(30), default=TicketStatus.DRAFT.value, index=True)
    priority = Column(String(20), default=TicketPriority.MEDIUM.value, index=True)
    urgency = Column(String(20), default=TicketUrgency.MEDIUM.value)
    impact = Column(String(30), default=TicketImpact.INDIVIDUAL.value)
    
    # AI Analysis
    ai_analyzed = Column(Boolean, default=False)
    ai_summary = Column(Text)  # AI-generated summary
    ai_suggested_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    ai_sentiment = Column(String(20))  # POSITIVE, NEUTRAL, FRUSTRATED, ANGRY, URGENT
    
    # Assignment
    assigned_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    # Resolution
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # SLA
    sla_policy_id = Column(UUID(as_uuid=True), ForeignKey("sla_policies.id"), nullable=True)
    response_due_at = Column(DateTime)
    resolution_due_at = Column(DateTime)
    sla_status = Column(String(20), default="ON_TRACK")  # ON_TRACK, WARNING, BREACHED, COMPLETED
    
    # Escalation
    is_escalated = Column(Boolean, default=False, index=True)
    escalated_at = Column(DateTime)
    escalation_reason = Column(String(500))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    creator = relationship("User", back_populates="tickets", foreign_keys=[creator_id])
    assigned_to = relationship("User", back_populates="assigned_tickets", foreign_keys=[assigned_agent_id])
    category = relationship("Category", back_populates="tickets")
    subcategory = relationship("SubCategory", back_populates="tickets")
    assigned_team = relationship("Team", back_populates="assigned_tickets", foreign_keys=[assigned_team_id])
    suggested_team = relationship("Team", back_populates="suggested_tickets", foreign_keys=[ai_suggested_team_id])
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")
    ai_analysis = relationship("TicketAIAnalysis", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    status_history = relationship("TicketStatusHistory", back_populates="ticket", cascade="all, delete-orphan")
    assignments = relationship("TicketAssignment", back_populates="ticket", cascade="all, delete-orphan")
    feedback = relationship("TicketFeedback", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    sla_policy = relationship("SLAPolicy", back_populates="tickets")

    __table_args__ = (
        Index("idx_ticket_status_created", "status", "created_at"),
        Index("idx_ticket_priority_created", "priority", "created_at"),
        Index("idx_ticket_category_created", "category_id", "created_at"),
    )


class TicketMessage(Base):
    """Ticket comments/messages"""
    __tablename__ = "ticket_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes
    is_ai_generated = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="messages")
    author = relationship("User", back_populates="messages")


class TicketStatusHistory(Base):
    """Ticket status change history"""
    __tablename__ = "ticket_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, index=True)
    
    old_status = Column(String(30))
    new_status = Column(String(30), nullable=False)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reason = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="status_history")


class TicketAssignment(Base):
    """Ticket assignment history"""
    __tablename__ = "ticket_assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, index=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    
    assigned_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assignment_reason = Column(String(500))
    
    assigned_at = Column(DateTime, default=datetime.utcnow, index=True)
    unassigned_at = Column(DateTime)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="assignments")
