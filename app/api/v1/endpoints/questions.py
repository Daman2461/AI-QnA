from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.exceptions import DocumentNotFoundError
from app.models.models import User, Question, Document
from app.schemas.schemas import (
    Question as QuestionSchema,
    QuestionCreate,
    QuestionUpdate,
    ResponseBase,
)
from app.services.qa_service import QAService
from app.services.rl_service import RLService

router = APIRouter()


@router.post("/", response_model=QuestionSchema)
def create_question(
    *,
    db: Session = Depends(deps.get_db),
    question_in: QuestionCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new question.
    """
    # Verify document exists and belongs to user
    document = db.query(Document).filter(
        Document.id == question_in.document_id,
        Document.owner_id == current_user.id
    ).first()
    if not document:
        raise DocumentNotFoundError()
    
    if document.processing_status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Document processing is not complete"
        )

    # Create question
    question = Question(
        question_text=question_in.question_text,
        document_id=question_in.document_id,
        user_id=current_user.id,
        metadata=question_in.metadata
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Get answer using QA service
    try:
        qa_service = QAService(db)
        rl_service = RLService(db)
        
        # Get initial answer
        answer = qa_service.answer_question(
            document_id=question.document_id,
            question=question.question_text
        )
        
        # Optimize answer using RL
        optimized_answer = rl_service.optimize_response(question, answer)
        
        # Update question with answer
        question.answer_text = optimized_answer["answer"]
        question.confidence_score = optimized_answer["confidence_score"]
        question.metadata = {
            **(question.metadata or {}),
            "sources": optimized_answer["sources"]
        }
        
        db.add(question)
        db.commit()
        db.refresh(question)
        
        return question

    except Exception as e:
        db.delete(question)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/", response_model=List[QuestionSchema])
def read_questions(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve questions.
    """
    questions = db.query(Question).filter(
        Question.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return questions


@router.get("/{question_id}", response_model=QuestionSchema)
def read_question(
    *,
    db: Session = Depends(deps.get_db),
    question_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get question by ID.
    """
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )
    return question


@router.put("/{question_id}/feedback", response_model=QuestionSchema)
def update_question_feedback(
    *,
    db: Session = Depends(deps.get_db),
    question_id: int,
    feedback_score: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update question feedback score.
    """
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )
    
    if not 0 <= feedback_score <= 100:
        raise HTTPException(
            status_code=400,
            detail="Feedback score must be between 0 and 100"
        )
    
    question.feedback_score = feedback_score
    db.add(question)
    db.commit()
    db.refresh(question)
    
    # Update RL model with feedback
    try:
        rl_service = RLService(db)
        rl_service.train_on_historical_data()
    except Exception as e:
        # Log error but don't fail the request
        print(f"Error updating RL model: {str(e)}")
    
    return question


@router.delete("/{question_id}", response_model=ResponseBase)
def delete_question(
    *,
    db: Session = Depends(deps.get_db),
    question_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a question.
    """
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.user_id == current_user.id
    ).first()
    if not question:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )
    
    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"} 