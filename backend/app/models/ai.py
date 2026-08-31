"""AI Analysis and ML-related models"""

from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.database.base import Base


class TicketAIAnalysis(Base):
    """AI analysis results for tickets"""
    __tablename__ = "ticket_ai_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, unique=True)
    
    # Intent Detection
    detected_intent = Column(String(50))  # KNOWLEDGE_QUERY, CREATE_TICKET, TICKET_STATUS, etc.
    intent_confidence = Column(Float, default=0.0)
    
    # Classification
    suggested_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    category_confidence = Column(Float, default=0.0)
    
    suggested_subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id"), nullable=True)
    subcategory_confidence = Column(Float, default=0.0)
    
    # Priority
    suggested_priority = Column(String(20))  # CRITICAL, HIGH, MEDIUM, LOW
    priority_confidence = Column(Float, default=0.0)
    
    # Urgency
    suggested_urgency = Column(String(20))
    urgency_confidence = Column(Float, default=0.0)
    
    # Impact
    suggested_impact = Column(String(30))  # ORGANIZATION_WIDE, DEPARTMENT, TEAM, INDIVIDUAL
    impact_confidence = Column(Float, default=0.0)
    
    # Team Recommendation
    suggested_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    team_confidence = Column(Float, default=0.0)
    team_recommendation_reason = Column(Text)
    
    # Sentiment Analysis
    sentiment = Column(String(20))  # POSITIVE, NEUTRAL, FRUSTRATED, ANGRY, URGENT
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    
    # Summary
    ai_generated_summary = Column(Text)
    
    # Keywords/Entities
    extracted_keywords = Column(JSON)  # List of keywords
    extracted_entities = Column(JSON)  # Named entities
    
    # Confidence
    overall_confidence = Column(Float, default=0.0)
    low_confidence_flag = Column(Boolean, default=False)
    manual_verification_recommended = Column(Boolean, default=False)
    
    # Processing
    ai_provider = Column(String(50), default="ollama")  # Which provider generated this
    model_name = Column(String(100))
    processing_time_ms = Column(Float)
    
    # Resolution
    ai_suggested_resolution_summary = Column(Text)
    ai_troubleshooting_steps = Column(JSON)  # List of steps
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="ai_analysis")
    category = relationship("Category")
    subcategory = relationship("SubCategory")
    team = relationship("Team")


class RAGQuery(Base):
    """RAG chatbot queries and responses"""
    __tablename__ = "rag_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    
    # Retrieved sources
    retrieved_documents = Column(JSON)  # List of document IDs and similarity scores
    source_chunks = Column(JSON)  # Retrieved text chunks with metadata
    
    # Quality metrics
    model_name = Column(String(100))
    embedding_model = Column(String(100))
    retrieval_time_ms = Column(Float)
    generation_time_ms = Column(Float)
    similarity_scores = Column(JSON)
    
    # Feedback
    user_rating = Column(Float)  # 1-5 star rating
    user_feedback = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
