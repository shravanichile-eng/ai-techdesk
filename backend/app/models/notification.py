"""Notification model"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database.base import Base


class Notification(Base):
    """User notification"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # TICKET_CREATED, STATUS_CHANGED, etc.
    
    # Reference
    related_entity_type = Column(String(50))  # TICKET, MESSAGE, etc.
    related_entity_id = Column(UUID(as_uuid=True))
    
    # Status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)
    
    # Metadata
    action_url = Column(String(500))  # Link to navigate to
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
