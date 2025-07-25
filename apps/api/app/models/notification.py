from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime
import uuid

class Notification(Base):
    __tablename__ = "notification"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    priority = Column(String, nullable=False, default="normal")
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    channel = Column(String, nullable=False, default="in_app")
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications") 