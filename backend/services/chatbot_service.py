import json
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from backend.models.chat_message import ChatMessage
from backend.models.chat_session import ChatSession
from backend.models.user import User
from backend.services.guardrail_service import guardrail
from backend.services.rate_limiter_service import rate_limiter
from backend.services.context_builder_service import context_builder_service
from backend.services.conversation_context_service import conversation_context_service
from backend.services.ai_service import ai_service
from backend.services.cache_service import cache_service

def clear_user_chatbot_context(user_id: int) -> None:
    """
    Clears the active conversation context for the specified user.
    """
    conversation_context_service.clear_context(user_id)

def generate_session_title(message: str) -> str:
    """
    Intelligently generates a clean title for a chat session from the first query.
    """
    import re
    clean_msg = message.strip().lower()
    
    # 1. Check for greetings or very short queries
    greetings = {"hi", "hello", "thanks", "thank you", "hey", "hola", "good morning", "good afternoon"}
    if clean_msg in greetings or len(clean_msg.split()) <= 1:
        return "General Health Discussion"
        
    # 2. Key phrase overrides
    if any(x in clean_msg for x in ["high risk", "my risk", "why is my risk", "risk explanation"]):
        return "High Risk Explanation"
    if "obesity profile" in clean_msg:
        return "Obesity Profile Index"
    if "smoking score" in clean_msg:
        return "Smoking Score Guidance"
    if any(x in clean_msg for x in ["view", "see", "history", "previous assessments", "prediction history"]):
        return "Viewing Assessment History"
    if any(x in clean_msg for x in ["compare", "assessments", "trend"]):
        return "Assessment Comparison"
    if "lung cancer" in clean_msg:
        return "Lung Cancer Overview"
    if "breast cancer" in clean_msg:
        return "Breast Cancer Overview"
    if "colon cancer" in clean_msg or "colorectal" in clean_msg:
        return "Colorectal Cancer Overview"
    if "prostate" in clean_msg:
        return "Prostate Cancer Overview"
    if "skin cancer" in clean_msg:
        return "Skin Cancer Overview"
    if "mammogram" in clean_msg:
        return "Mammogram Screening"
    if "colonoscopy" in clean_msg:
        return "Colonoscopy Screening"
    if "lifestyle" in clean_msg:
        return "Lifestyle Recommendations"
    if "screening" in clean_msg:
        return "Screening Guidelines"

    # 3. Rules-based generic parsing
    words_to_remove = ["what", "how", "can", "should", "explain", "please", "tell me"]
    processed = clean_msg
    for w in words_to_remove:
        processed = re.sub(r'\b' + re.escape(w) + r'\b', '', processed)
        
    # Strip common helper verbs/pronouns/articles
    processed = re.sub(r'\b(is\s+a|is|does|mean|for|do|i|my|the|about)\b', '', processed)
    
    # Clean non-alphanumeric and multiple spaces
    processed = re.sub(r'[^\w\s-]', '', processed)
    processed = re.sub(r'\s+', ' ', processed).strip()
    
    title = processed.title()
    
    generic_titles = {"", "new chat", "chat session", "conversation", "untitled"}
    if title.lower() in generic_titles:
        return "General Health Discussion"
        
    if len(title) > 40:
        title = title[:37] + "..."
        
    return title

def generate_response(db: Session, current_user: User, message: str, session_uuid: Optional[str] = None) -> Dict[str, Any]:
    """
    Orchestrates response generation using the V2.1 conversational AI architecture.
    """
    # 1. Enforce Rate Limit per user
    rate_limiter.check_rate_limit(current_user.id)
    
    # Standard refusal message for security sensitive and out-of-scope questions
    refusal_msg = (
        "I can only assist with health-related assessment guidance and interpretation "
        "of your OncoRisk results. I cannot assist with out-of-scope technical, programming, "
        "or administration commands."
    )

    # 2. Safety & Allow-list Validation Classify
    category, refusal_reason = guardrail.classify_message(message, current_user.id)
    if category == guardrail.PROMPT_INJECTION:
        return {
            "answer": "I cannot assist with requests that attempt to bypass system safety or access restricted information.",
            "confidence": "LOW",
            "sources": [],
            "suggestions": [],
            "intent": "PROMPT_INJECTION"
        }
    elif category in [guardrail.SECURITY_SENSITIVE, guardrail.OUT_OF_SCOPE]:
        return {
            "answer": refusal_msg,
            "confidence": "LOW",
            "sources": [],
            "suggestions": [],
            "intent": category
        }

    # 3. Retrieve or create database ChatSession
    session_record = None
    if session_uuid:
        session_record = db.query(ChatSession).filter(
            ChatSession.session_uuid == session_uuid,
            ChatSession.user_id == current_user.id,
            ChatSession.is_deleted == False
        ).first()
        if not session_record:
            raise ValueError("Invalid session UUID or unauthorized access.")
    else:
        # Check for the user's most recent active session
        session_record = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.is_deleted == False
        ).order_by(ChatSession.updated_at.desc()).first()
        
        if not session_record:
            # Auto-create session
            import uuid
            session_record = ChatSession(
                user_id=current_user.id,
                title="New Chat",
                session_uuid=str(uuid.uuid4())
            )
            db.add(session_record)
            db.commit()
            db.refresh(session_record)

    # Align memory context with database session
    conversation_context_service.set_session_uuid(current_user.id, session_record.session_uuid)

    # 4. Assemble context for the user
    context = context_builder_service.build_context(db, current_user)

    # Generate a stable hash of the user context
    context_str = json.dumps(context, default=str)
    context_hash = hashlib.sha256(context_str.encode('utf-8')).hexdigest()

    # 5. Determine intent class
    intent = ai_service._classify_intent(message, context, category)

    # 6. Check cache for general answers
    cached_res = cache_service.get(message, context_hash, intent)
    if cached_res:
        # Cache hit: append to memory context
        conversation_context_service.append_message(current_user.id, "user", message)
        conversation_context_service.append_message(
            current_user.id, 
            "assistant", 
            cached_res["answer"], 
            intent=intent, 
            confidence=cached_res["confidence"]
        )
        
        # Persist to database
        try:
            # Generate title if this is the first message in the session
            msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_record.id).count()
            if msg_count == 0:
                session_record.title = generate_session_title(message)

            chat_log = ChatMessage(
                user_id=current_user.id,
                session_id=session_record.id,
                question=message,
                answer=cached_res["answer"]
            )
            db.add(chat_log)
            # Update session timestamp
            session_record.updated_at = func.now()
            db.commit()
            cached_res["message_id"] = chat_log.id
        except Exception as db_err:
            print(f"Chatbot Service Warning: Failed to persist cache hit chat log: {db_err}")
            
        return cached_res

    # 7. Cache miss: Invoke AIService to generate response (falls back to local logic if APIs unavailable)
    res = ai_service.generate_ai_response(
        message=message,
        patient_context=context,
        conversation_context=conversation_context_service.get_context(current_user.id),
        guardrail_category=category
    )

    # 8. Store in cache if general and allowed
    cache_service.set(message, context_hash, res["intent"], res)

    # 9. Append conversation context
    conversation_context_service.append_message(current_user.id, "user", message)
    conversation_context_service.append_message(
        current_user.id, 
        "assistant", 
        res["answer"], 
        intent=res["intent"], 
        confidence=res["confidence"]
    )

    # 10. Persist to database
    try:
        # Generate title if this is the first message in the session
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_record.id).count()
        if msg_count == 0:
            session_record.title = generate_session_title(message)

        chat_log = ChatMessage(
            user_id=current_user.id,
            session_id=session_record.id,
            question=message,
            answer=res["answer"]
        )
        db.add(chat_log)
        # Update session timestamp
        session_record.updated_at = func.now()
        db.commit()
        res["message_id"] = chat_log.id
    except Exception as db_err:
        print(f"Chatbot Service Warning: Failed to persist chat log: {db_err}")

    return res
