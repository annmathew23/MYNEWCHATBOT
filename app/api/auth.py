from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password
from app.core.settings import settings
from app.core.jwt import create_access_token
from app.models.user import User
from app.schemas.auth import RegisterIn, UserOut, LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        sub=user.id,
        secret=settings.jwt_secret,
        alg=settings.jwt_alg,
        minutes=settings.jwt_expire_min,
    )
    return TokenOut(access_token=token)

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)
