from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.db.session import Base, engine

# models
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.prompt import Prompt  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.file_ref import FileRef  # noqa: F401

# routers
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.prompts import router as prompts_router
from app.api.chat import router as chat_router
from app.api.files import router as files_router

app = FastAPI(title=settings.app_name)

# CORS (handy if you add a web client later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(prompts_router)
app.include_router(chat_router)
app.include_router(files_router)

@app.get("/health")
def health():
    return {"ok": True, "app": settings.app_name}

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
