from uuid import uuid4
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.sql import func
from app.db.session import Base

class FileRef(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False, default="openai")
    provider_file_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # assistants, fine-tune, batch, etc.
    bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
