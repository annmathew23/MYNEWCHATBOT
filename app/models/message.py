from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    role = Column(String, nullable=False)   # "user" | "assistant"
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
