import os
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.core.exceptions import DocumentProcessingError, DocumentNotFoundError
from app.models.models import User, Document
from app.schemas.schemas import (
    Document as DocumentSchema,
    DocumentCreate,
    DocumentUpdate,
    FileUploadResponse,
    ResponseBase,
)
from app.services.document_processor import DocumentProcessor
from app.services.user_service import UserService

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a new document.
    """
    print("upload_document called")
    print(f"file: {file.filename if file else None}, title: {title}, user: {getattr(current_user, 'id', None)}")
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
                )
            buffer.write(content)

        # Create document record
        document = Document(
            title=title,
            file_path=file_path,
            file_type=os.path.splitext(file.filename)[1],
            file_size=len(content),
            owner_id=current_user.id,
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # Process document in background
        processor = DocumentProcessor(db)
        processor.process_document(document)

        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "document_id": document.id,
        }

    except Exception as e:
        print("UPLOAD ENDPOINT ERROR:", e)
        import traceback; traceback.print_exc()
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/", response_model=List[DocumentSchema])
def read_documents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve documents.
    """
    documents = db.query(Document).filter(
        Document.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
def read_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get document by ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise DocumentNotFoundError()
    return document


@router.put("/{document_id}", response_model=DocumentSchema)
def update_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    document_in: DocumentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise DocumentNotFoundError()
    
    for field, value in document_in.dict(exclude_unset=True).items():
        setattr(document, field, value)
    
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.delete("/{document_id}", response_model=ResponseBase)
def delete_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise DocumentNotFoundError()
    
    # Delete file if it exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/process", response_model=ResponseBase)
def process_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Process a document (reprocess if already processed).
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise DocumentNotFoundError()
    
    try:
        processor = DocumentProcessor(db)
        processor.process_document(document)
        return {"message": "Document processing started successfully"}
    except DocumentProcessingError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/{document_id}/summary", response_model=ResponseBase)
def get_document_summary(
    *,
    db: Session = Depends(deps.get_db),
    document_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a summary of the document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise DocumentNotFoundError()
    
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document processing is not complete"
        )
    
    try:
        processor = DocumentProcessor(db)
        summary = processor.get_document_summary(document_id)
        return {
            "message": "Document summary generated successfully",
            "detail": {"summary": summary}
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) 