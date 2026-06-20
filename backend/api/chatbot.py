from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

from backend.database.session import get_db
from backend.api.deps import get_current_user
from backend.models.user import User
from backend.models.chat_session import ChatSession
from backend.models.chat_message import ChatMessage
from backend.models.chatbot_feedback import ChatbotFeedback
from backend.services import chatbot_service

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Message text sent by the user")
    session_uuid: Optional[str] = Field(None, description="Optional UUID of the chat session")

class ChatResponse(BaseModel):
    answer: str
    confidence: str
    sources: List[str] = []
    suggestions: List[str] = []

class SessionCreateResponse(BaseModel):
    session_uuid: str
    title: str

class SessionListResponse(BaseModel):
    session_uuid: str
    title: str
    created_at: str

class MessageResponse(BaseModel):
    role: str
    message: str
    created_at: str

class FeedbackRequest(BaseModel):
    message_id: int
    feedback_type: str = Field(..., description="Must be HELPFUL or NOT_HELPFUL")

@router.post("/message", response_model=ChatResponse)
def post_chatbot_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Post a user query message to the conversational assistant.
    """
    try:
        res = chatbot_service.generate_response(
            db=db,
            current_user=current_user,
            message=payload.message,
            session_uuid=payload.session_uuid
        )
        return ChatResponse(
            answer=res["answer"],
            confidence=res["confidence"],
            sources=res.get("sources", []),
            suggestions=res.get("suggestions", [])
        )
    except HTTPException as http_exc:
        raise http_exc
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(val_err)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
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

@router.post("/feedback", status_code=status.HTTP_200_OK)
def post_chatbot_feedback(
    payload: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stores or updates feedback (HELPFUL/NOT_HELPFUL) for a message.
    """
    if payload.feedback_type not in ["HELPFUL", "NOT_HELPFUL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback type must be HELPFUL or NOT_HELPFUL."
        )
        
    # Check that message exists and belongs to user
    msg = db.query(ChatMessage).filter(
        ChatMessage.id == payload.message_id,
        ChatMessage.user_id == current_user.id
    ).first()
    if not msg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found."
        )
        
    # Upsert feedback
    feedback = db.query(ChatbotFeedback).filter(
        ChatbotFeedback.chat_message_id == payload.message_id,
        ChatbotFeedback.user_id == current_user.id
    ).first()
    
    if feedback:
        feedback.feedback_type = payload.feedback_type
    else:
        feedback = ChatbotFeedback(
            user_id=current_user.id,
            chat_message_id=payload.message_id,
            feedback_type=payload.feedback_type
        )
        db.add(feedback)
        
    try:
        db.commit()
        return {"status": "success", "message": "Feedback submitted successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback."
        )

@router.get("/sessions", response_model=List[SessionListResponse])
def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all active chat sessions (where is_deleted == False) for the logged-in user.
    """
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_deleted == False
    ).order_by(ChatSession.updated_at.desc()).all()
    
    return [
        SessionListResponse(
            session_uuid=s.session_uuid,
            title=s.title,
            created_at=s.created_at.isoformat()
        ) for s in sessions
    ]

@router.post("/sessions", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session.
    """
    session_title = title or "New Assessment Chat"
    new_session = ChatSession(
        user_id=current_user.id,
        title=session_title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return SessionCreateResponse(
        session_uuid=new_session.session_uuid,
        title=new_session.title
    )

@router.get("/sessions/{session_uuid}/messages", response_model=List[MessageResponse])
def get_session_messages(
    session_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Load historical messages in a session. Validate session ownership or raise 403.
    """
    session = db.query(ChatSession).filter(
        ChatSession.session_uuid == session_uuid,
        ChatSession.is_deleted == False
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )
        
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session."
        )
        
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id,
        ChatMessage.user_id == current_user.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    res = []
    for m in messages:
        res.append(MessageResponse(
            role="user",
            message=m.question,
            created_at=m.created_at.isoformat()
        ))
        res.append(MessageResponse(
            role="assistant",
            message=m.answer,
            created_at=m.created_at.isoformat()
        ))
    return res

@router.delete("/sessions/{session_uuid}", status_code=status.HTTP_200_OK)
def delete_chat_session(
    session_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a session. Verify session ownership.
    """
    session = db.query(ChatSession).filter(
        ChatSession.session_uuid == session_uuid,
        ChatSession.is_deleted == False
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found."
        )
        
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this session."
        )
        
    session.is_deleted = True
    db.commit()
    return {"status": "success", "message": "Session deleted successfully."}
