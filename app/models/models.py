from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship("Document", back_populates="owner")
    questions = relationship("Question", back_populates="user")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    file_path = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)  # in bytes
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    metadata = Column(JSON, nullable=True)  # Store document metadata

    owner = relationship("User", back_populates="documents")
    questions = relationship("Question", back_populates="document")
    embeddings = relationship("DocumentEmbedding", back_populates="document")


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    chunk_text = Column(Text)
    embedding = Column(JSON)  # Store vector embeddings
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="embeddings")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text)
    confidence_score = Column(Integer)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    feedback_score = Column(Integer, nullable=True)  # User feedback on answer quality
    metadata = Column(JSON, nullable=True)  # Store additional question metadata

    user = relationship("User", back_populates="questions")
    document = relationship("Document", back_populates="questions")


class RLModelState(Base):
    __tablename__ = "rl_model_states"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    state_dict = Column(JSON)  # Store model state
    metrics = Column(JSON)  # Store training metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    version = Column(String, nullable=False)
    metadata = Column(JSON, nullable=True)  # Store additional model metadata 