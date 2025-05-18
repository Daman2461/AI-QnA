from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core.exceptions import RLModelError
from app.models.models import User, RLModelState
from app.schemas.schemas import RLModelState as RLModelStateSchema, ResponseBase
from app.services.rl_service import RLService

router = APIRouter()


@router.get("/model/status", response_model=RLModelStateSchema)
def get_model_status(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get current RL model status.
    """
    try:
        latest_model = db.query(RLModelState).filter(
            RLModelState.is_active == True
        ).order_by(RLModelState.updated_at.desc()).first()
        
        if not latest_model:
            raise HTTPException(
                status_code=404,
                detail="No active model found"
            )
        
        return latest_model
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/model/train", response_model=ResponseBase)
def train_model(
    *,
    db: Session = Depends(deps.get_db),
    batch_size: int = 32,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Train RL model on historical data.
    """
    try:
        rl_service = RLService(db)
        metrics = rl_service.train_on_historical_data(batch_size=batch_size)
        return {
            "message": "Model training completed successfully",
            "detail": metrics
        }
    except RLModelError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/model/metrics", response_model=Dict[str, Any])
def get_model_metrics(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get RL model training metrics.
    """
    try:
        latest_model = db.query(RLModelState).filter(
            RLModelState.is_active == True
        ).order_by(RLModelState.updated_at.desc()).first()
        
        if not latest_model:
            raise HTTPException(
                status_code=404,
                detail="No active model found"
            )
        
        return latest_model.metrics
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/model/reset", response_model=ResponseBase)
def reset_model(
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reset RL model to initial state.
    """
    try:
        # Deactivate all existing models
        db.query(RLModelState).update({"is_active": False})
        
        # Create new model with initial state
        rl_service = RLService(db)
        rl_service.save_model_state({
            "status": "initialized",
            "average_reward": 0.0,
            "training_samples": 0
        })
        
        return {"message": "Model reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) 