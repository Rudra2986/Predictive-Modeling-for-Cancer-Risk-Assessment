from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_data = Column(JSON, nullable=False)
    predicted_class = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    explanation_narrative = Column(Text, nullable=False)
    
    # Associated user who ran the prediction (nullable to allow guest queries)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="prediction_logs")
