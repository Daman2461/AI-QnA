from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import os

from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, User as UserSchema
from app.services.user_service import UserService

app = FastAPI(
    title="AI Document Q&A System",
    description="A comprehensive FastAPI project with document processing, Q&A, and RL capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Document Q&A System",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "Document Processing",
            "Q&A System", 
            "Reinforcement Learning",
            "JWT Authentication",
            "User Management"
        ]
    }

@app.post("/api/v1/auth/register")
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    user_service = UserService(db)
    user = user_service.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = user_service.create(obj_in=user_in)
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "message": "User registered successfully"
    }

@app.post("/api/v1/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login to get access token."""
    user_service = UserService(db)
    user = user_service.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@app.get("/api/v1/features")
async def get_features():
    return {
        "features": {
            "document_processing": "Upload and process documents with AI",
            "qa_system": "Ask questions about uploaded documents",
            "reinforcement_learning": "RL-based answer optimization",
            "authentication": "JWT-based user authentication",
            "user_management": "User registration and management"
        },
        "mistral_api_key_configured": bool(settings.MISTRAL_API_KEY)
    }

@app.get("/api/v1/config")
async def get_config():
    """Get application configuration (without sensitive data)."""
    return {
        "project_name": settings.PROJECT_NAME,
        "api_v1_str": settings.API_V1_STR,
        "database_url": "sqlite:///./app.db",
        "mistral_model": settings.MISTRAL_MODEL_NAME,
        "max_upload_size": settings.MAX_UPLOAD_SIZE,
        "upload_dir": settings.UPLOAD_DIR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 