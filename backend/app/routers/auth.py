from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import get_db
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user
from app.db import models


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identity = (payload.email or "").strip()
    user = db.query(models.User).filter(models.User.email == identity).first()
    if not user and "@" not in identity:
        alt = f"{identity}@example.com"
        user = db.query(models.User).filter(models.User.email == alt).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(subject=f"user:{user.id}", extra_claims={"role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "email": user.email}


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str | None = None  


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email_norm = (payload.email or "").strip().lower()
    exists = db.query(models.User).filter(models.User.email == email_norm).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    role = (payload.role or "user").lower()
    user = models.User(email=email_norm, password_hash=get_password_hash(payload.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(subject=f"user:{user.id}", extra_claims={"role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role, "email": user.email}


@router.get("/me")
def me(current=Depends(get_current_user)):
    return {"id": current.id, "email": current.email, "role": current.role}
