"""Ticket feedback model"""

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database.base import Base


class TicketFeedback(Base):
    """Ticket resolution feedback from user"""
    __tablename__ = "ticket_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Rating
    rating = Column(Integer, nullable=False)  # 1-5 stars
    
    # Feedback
    comment = Column(Text)
    
    # Categories (for insight)
    resolution_helpful = Column(Integer)  # 1-5
    agent_professional = Column(Integer)  # 1-5
    speed_of_resolution = Column(Integer)  # 1-5
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
