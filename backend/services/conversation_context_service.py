from typing import List, Dict, Any, Optional

class ConversationContextService:
    def __init__(self):
        # In-memory dictionary holding active conversation context per user.
        # Format: { user_id: [{"role": "user"|"assistant", "message": str, "intent": str, "confidence": str}] }
        self._conversation_context: Dict[int, List[Dict[str, Any]]] = {}

    def get_context(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the conversation context for the specified user.
        Returns a list of message dicts.
        """
        return self._conversation_context.get(user_id, [])

    def append_message(
        self,
        user_id: int,
        role: str,
        message: str,
        intent: Optional[str] = None,
        confidence: Optional[str] = None
    ) -> None:
        """
        Appends a new message to the user's active session conversation context.
        Restricts active history to the last 5 message pairs (10 entries maximum).
        """
        if user_id not in self._conversation_context:
            self._conversation_context[user_id] = []
        
        self._conversation_context[user_id].append({
            "role": role,
            "message": message,
            "intent": intent,
            "confidence": confidence
        })
        
        # Enforce limit of 5 pairs (10 messages total)
        if len(self._conversation_context[user_id]) > 10:
            self._conversation_context[user_id] = self._conversation_context[user_id][-10:]

    def clear_context(self, user_id: int) -> None:
        """
        Clears the conversation context for the specified user.
        """
        if user_id in self._conversation_context:
            self._conversation_context[user_id] = []

# Instantiate global service instance
conversation_context_service = ConversationContextService()
