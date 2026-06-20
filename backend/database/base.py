# Import all models so that Base.metadata has them registered before
# creating tables. This is imported by initialization scripts or the main entrypoint.
from backend.database.session import Base
from backend.models.user import User
from backend.models.prediction_log import PredictionLog
from backend.models.chat_session import ChatSession
from backend.models.chat_message import ChatMessage
from backend.models.chatbot_feedback import ChatbotFeedback
