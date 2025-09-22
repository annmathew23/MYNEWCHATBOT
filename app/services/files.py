import os
import httpx
from app.core.settings import settings

OPENAI_BASE = "https://api.openai.com/v1"

async def openai_upload_file(content: bytes, filename: str, purpose: str) -> dict:
    key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    headers = {"Authorization": f"Bearer {key}"}
    files = {"file": (filename, content, "application/octet-stream")}
    data = {"purpose": purpose}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OPENAI_BASE}/files", headers=headers, files=files, data=data)
        r.raise_for_status()
        return r.json()
