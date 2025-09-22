from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Prompt(Base):
    __tablename__ = "prompts"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "system" | "assistant" | "user"
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
