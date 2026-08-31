"""SLA policy models"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database.base import Base


class SLAPolicy(Base):
    """SLA policy definition"""
    __tablename__ = "sla_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # SLA times (in minutes)
    response_time_minutes = Column(Integer, nullable=False)  # Time to first response
    resolution_time_minutes = Column(Integer, nullable=False)  # Time to resolution
    
    # Applicable to
    applicable_priority = Column(String(20))  # NULL = all, or specific priority
    
    # Escalation
    warning_threshold_percent = Column(Integer, default=80)  # Escalate at 80% of time
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="sla_policy")
