from uuid import uuid4
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

# String UUID so it works on SQLite too
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
