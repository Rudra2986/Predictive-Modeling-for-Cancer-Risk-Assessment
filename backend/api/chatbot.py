from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.session import get_db
from backend.api.deps import get_current_user
from backend.models.user import User
from backend.services import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message text sent by the user")

class ChatResponse(BaseModel):
    answer: str
    confidence: str

@router.post("/message", response_model=ChatResponse)
def post_chatbot_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Post a user query message to the rule-based medical assessment chatbot.
    Returns the generated answer along with the classification confidence level.
    """
    try:
        answer, confidence = chatbot_service.generate_response(
            db=db,
            current_user=current_user,
            message=payload.message
        )
        return ChatResponse(answer=answer, confidence=confidence)
    except HTTPException as http_exc:
        # Keep rate limiting 429 / authentication 401 exceptions active
        raise http_exc
    except Exception as e:
        # Prevent stack trace leakage or database path leaks on unhandled errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected system error occurred. Please contact admin support."
        )

@router.post("/clear")
def clear_chatbot_session(
    current_user: User = Depends(get_current_user)
):
    """
    Clear the active in-memory conversation context for the authenticated user.
    """
    try:
        chatbot_service.clear_user_chatbot_context(current_user.id)
        return {"status": "success", "message": "Conversation context cleared successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not clear conversation context."
        )

