from pydantic import BaseModel

class FileOut(BaseModel):
    id: str
    filename: str
    purpose: str
    provider: str
    provider_file_id: str
    bytes: int
    class Config:
        from_attributes = True
