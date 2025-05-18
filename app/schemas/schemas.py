from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_superuser: bool

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str


# Document schemas
class DocumentBase(BaseModel):
    title: str
    file_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    title: Optional[str] = None
    processing_status: Optional[str] = None


class DocumentInDBBase(DocumentBase):
    id: int
    owner_id: int
    file_path: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    processing_status: str

    class Config:
        from_attributes = True


class Document(DocumentInDBBase):
    pass


class DocumentWithContent(Document):
    content: Optional[str] = None


# Document Embedding schemas
class DocumentEmbeddingBase(BaseModel):
    chunk_index: int
    chunk_text: str
    embedding: List[float]


class DocumentEmbeddingCreate(DocumentEmbeddingBase):
    document_id: int


class DocumentEmbedding(DocumentEmbeddingBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Question schemas
class QuestionBase(BaseModel):
    question_text: str
    document_id: int
    metadata: Optional[Dict[str, Any]] = None


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    answer_text: Optional[str] = None
    confidence_score: Optional[int] = Field(None, ge=0, le=100)
    feedback_score: Optional[int] = Field(None, ge=0, le=100)
    metadata: Optional[Dict[str, Any]] = None


class QuestionInDBBase(QuestionBase):
    id: int
    user_id: int
    answer_text: Optional[str]
    confidence_score: Optional[int]
    created_at: datetime
    updated_at: datetime
    feedback_score: Optional[int]

    class Config:
        from_attributes = True


class Question(QuestionInDBBase):
    pass


# RL Model schemas
class RLModelStateBase(BaseModel):
    model_name: str
    version: str
    state_dict: Dict[str, Any]
    metrics: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class RLModelStateCreate(RLModelStateBase):
    pass


class RLModelStateUpdate(BaseModel):
    state_dict: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class RLModelState(RLModelStateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


# Response schemas
class ResponseBase(BaseModel):
    message: str
    detail: Optional[Any] = None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: List[Any]


# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_path: str
    file_type: str
    file_size: int
    document_id: int 