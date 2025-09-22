from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.deps import get_db, get_current_user
from app.models.project import Project
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptOut

router = APIRouter(prefix="/projects/{project_id}/prompts", tags=["prompts"])

@router.post("", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
def add_prompt(project_id: str, data: PromptCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = db.get(Project, project_id)
    if not proj or proj.user_id != user.id:
        raise HTTPException(404, "Project not found")
    pr = Prompt(project_id=project_id, role=data.role, content=data.content)
    db.add(pr); db.commit(); db.refresh(pr)
    return pr

@router.get("", response_model=list[PromptOut])
def list_prompts(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = db.get(Project, project_id)
    if not proj or proj.user_id != user.id:
        raise HTTPException(404, "Project not found")
    rows = db.scalars(select(Prompt).where(Prompt.project_id == project_id)).all()
    return rows
