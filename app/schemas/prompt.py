from pydantic import BaseModel, Field

class PromptCreate(BaseModel):
    role: str = Field(pattern="^(system|assistant|user)$")
    content: str

class PromptOut(BaseModel):
    id: str
    role: str
    content: str
    class Config:
        from_attributes = True
