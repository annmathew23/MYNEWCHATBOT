from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
import httpx
from app.core.deps import get_db, get_current_user
from app.models.project import Project
from app.models.prompt import Prompt
from app.models.message import Message
from app.schemas.chat import ChatIn, ChatOut
from app.services.providers import llm_response
from app.core.settings import settings

router = APIRouter(prefix="/projects/{project_id}/chat", tags=["chat"])

@router.post("", response_model=ChatOut)
async def chat(project_id: str, data: ChatIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = db.get(Project, project_id)
    if not proj or proj.user_id != user.id:
        raise HTTPException(status_code=404, detail="Project not found")

    system_prompt = db.scalar(
        select(Prompt.content).where(Prompt.project_id == project_id, Prompt.role == "system")
    ) or "You are a helpful assistant."

    # persist user message
    um = Message(project_id=project_id, user_id=user.id, role="user", content=data.message)
    db.add(um); db.commit(); db.refresh(um)

    provider = (proj.provider or "openai").lower()
    model = proj.model

    try:
        reply_text = await llm_response(provider, model, system_prompt, data.message)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream {provider} error: {e.response.status_code} {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {e}")

    am = Message(project_id=project_id, user_id=user.id, role="assistant", content=reply_text)
    db.add(am); db.commit()

    return ChatOut(reply=reply_text)
