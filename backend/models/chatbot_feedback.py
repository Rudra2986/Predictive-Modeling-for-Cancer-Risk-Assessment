from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base

class ChatbotFeedback(Base):
    __tablename__ = "chatbot_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chat_message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(String(20), nullable=False)  # HELPFUL or NOT_HELPFUL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")
    chat_message = relationship("ChatMessage", back_populates="feedbacks")

    __table_args__ = (
        UniqueConstraint("user_id", "chat_message_id", name="uq_user_message_feedback"),
    )
