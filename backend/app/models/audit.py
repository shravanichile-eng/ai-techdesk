"""Audit logging model"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database.base import Base


class AuditLog(Base):
    """Audit log for tracking system actions"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    user_email = Column(String(255))  # Cached in case user is deleted
    
    # Action
    action = Column(String(50), nullable=False, index=True)  # USER_CREATED, TICKET_ASSIGNED, etc.
    description = Column(Text)
    
    # Entity
    entity_type = Column(String(50))  # USER, TICKET, TEAM, etc.
    entity_id = Column(UUID(as_uuid=True), index=True)
    
    # Changes
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    changed_fields = Column(JSON)  # List of fields that changed
    
    # Metadata
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
