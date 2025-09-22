from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False, default="openai")  # "openai" | "openrouter"
    model = Column(String, nullable=True)  # optional override
    created_at = Column(DateTime(timezone=True), server_default=func.now())
