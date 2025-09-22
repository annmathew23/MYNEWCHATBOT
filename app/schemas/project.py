from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    name: str
    provider: Optional[str] = "openai"
    model: Optional[str] = None

class ProjectOut(BaseModel):
    id: str
    name: str
    provider: str
    model: str | None
    class Config:
        from_attributes = True
