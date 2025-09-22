from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import httpx
from app.core.deps import get_db, get_current_user
from app.models.project import Project
from app.models.file_ref import FileRef
from app.schemas.file import FileOut
from app.services.files import openai_upload_file

router = APIRouter(prefix="/projects/{project_id}/files", tags=["files"])

@router.get("", response_model=list[FileOut])
def list_files(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = db.get(Project, project_id)
    if not proj or proj.user_id != user.id:
        raise HTTPException(404, "Project not found")
    rows = db.scalars(select(FileRef).where(FileRef.project_id == project_id)).all()
    return rows

@router.post("", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    project_id: str,
    purpose: str = Form("assistants"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    proj = db.get(Project, project_id)
    if not proj or proj.user_id != user.id:
        raise HTTPException(404, "Project not found")

    content = await file.read()
    try:
        res = await openai_upload_file(content, file.filename, purpose)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"Upstream openai error: {e.response.status_code} {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {e}")

    fr = FileRef(
        project_id=project_id,
        provider="openai",
        provider_file_id=res.get("id", ""),
        filename=file.filename,
        purpose=purpose,
        bytes=len(content),
    )
    db.add(fr); db.commit(); db.refresh(fr)
    return fr
