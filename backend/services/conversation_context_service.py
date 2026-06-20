import time
import uuid
from typing import List, Dict, Any, Optional

class ConversationContextService:
    def __init__(self, timeout_seconds: int = 1800):
        # Format: { user_id: { "messages": [...], "session_uuid": str, "last_activity": float } }
        self._conversation_context: Dict[int, Dict[str, Any]] = {}
        self.timeout_seconds = timeout_seconds

    def _check_timeout(self, user_id: int) -> None:
        if user_id in self._conversation_context:
            state = self._conversation_context[user_id]
            now = time.time()
            if now - state.get("last_activity", now) > self.timeout_seconds:
                # Idle timeout reached, clear context
                self.clear_context(user_id)

    def get_context(self, user_id: int) -> List[Dict[str, Any]]:
        self._check_timeout(user_id)
        if user_id in self._conversation_context:
            return self._conversation_context[user_id]["messages"]
        return []

    def get_session_uuid(self, user_id: int) -> Optional[str]:
        self._check_timeout(user_id)
        if user_id in self._conversation_context:
            return self._conversation_context[user_id].get("session_uuid")
        return None

    def set_session_uuid(self, user_id: int, session_uuid: str) -> None:
        self._check_timeout(user_id)
        if user_id not in self._conversation_context:
            self._conversation_context[user_id] = {
                "messages": [],
                "session_uuid": session_uuid,
                "last_activity": time.time()
            }
        else:
            state = self._conversation_context[user_id]
            # If the session UUID changes, start a fresh memory context
            if state.get("session_uuid") != session_uuid:
                state["messages"] = []
                state["session_uuid"] = session_uuid
            state["last_activity"] = time.time()

    def append_message(
        self,
        user_id: int,
        role: str,
        message: str,
        intent: Optional[str] = None,
        confidence: Optional[str] = None
    ) -> None:
        self._check_timeout(user_id)
        now = time.time()
        if user_id not in self._conversation_context:
            self._conversation_context[user_id] = {
                "messages": [],
                "session_uuid": str(uuid.uuid4()),
                "last_activity": now
            }
        
        state = self._conversation_context[user_id]
        state["messages"].append({
            "role": role,
            "message": message,
            "intent": intent,
            "confidence": confidence
        })
        state["last_activity"] = now
        
        # Enforce limit of 20 messages total
        if len(state["messages"]) > 20:
            state["messages"] = state["messages"][-20:]

    def clear_context(self, user_id: int) -> None:
        if user_id in self._conversation_context:
            self._conversation_context[user_id] = {
                "messages": [],
                "session_uuid": str(uuid.uuid4()),
                "last_activity": time.time()
            }

# Instantiate global service instance
conversation_context_service = ConversationContextService()
