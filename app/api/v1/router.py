from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    documents,
    questions,
    rl
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(rl.router, prefix="/rl", tags=["reinforcement learning"]) 