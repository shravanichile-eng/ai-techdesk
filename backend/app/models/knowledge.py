"""Knowledge base and document models"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from datetime import datetime
import uuid

from app.database.base import Base


class KnowledgeDocument(Base):
    """Knowledge base document"""
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File info
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)  # in bytes
    file_type = Column(String(20))  # PDF, DOCX, TXT, MD
    mime_type = Column(String(100))
    
    # Content
    title = Column(String(255))
    description = Column(Text)
    content = Column(Text)  # Full text content
    
    # Processing
    status = Column(String(20), default="UPLOADED")  # UPLOADED, PROCESSING, INDEXED, FAILED
    processing_error = Column(Text)  # If failed
    
    # Chunking
    total_chunks = Column(Integer, default=0)
    chunk_size = Column(Integer, default=500)  # Characters per chunk
    chunk_overlap = Column(Integer, default=50)  # Character overlap between chunks
    
    # Metadata
    category = Column(String(100))  # E.g., "VPN Troubleshooting", "Password Policies"
    tags = Column(JSON)  # List of tags
    author = Column(String(255))
    document_date = Column(DateTime)
    version = Column(String(20), default="1.0")
    
    # Indexing
    is_indexed = Column(Boolean, default=False, index=True)
    embedding_status = Column(String(20), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED
    
    # Admin metadata
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    uploaded_by = relationship("User")


class DocumentChunk(Base):
    """Document text chunks for RAG retrieval"""
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    
    # Chunk content
    chunk_index = Column(Integer, nullable=False)  # Position in document
    content = Column(Text, nullable=False)
    
    # Metadata
    token_count = Column(Integer)
    
    # Embedding
    embedding = Column(VECTOR(384))  # Using 384-dim embeddings (nomic-embed-text)
    embedding_model = Column(String(100), default="nomic-embed-text")
    embedding_timestamp = Column(DateTime)
    
    # Search optimization
    is_indexed = Column(Boolean, default=False, index=True)
    search_score = Column(Float, default=0.0)  # For ranking
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("KnowledgeDocument", back_populates="chunks")
