from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.core.deps import get_db, get_current_user
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = Project(user_id=user.id, name=data.name, provider=(data.provider or "openai"), model=data.model)
    db.add(proj); db.commit(); db.refresh(proj)
    return proj

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.scalars(select(Project).where(Project.user_id == user.id)).all()
    return rows

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = db.get(Project, project_id)
    if not proj or proj.user_id != user.id:
        raise HTTPException(404, "Project not found")
    db.execute(delete(Project).where(Project.id == project_id))
    db.commit()
