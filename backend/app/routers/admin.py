from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token, verify_password, require_roles
from app.db import models
from pydantic import BaseModel


router = APIRouter(prefix="/admin", tags=["admin"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(subject=f"user:{user.id}", extra_claims={"role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}


@router.get("/applications", dependencies=[Depends(require_roles("admin"))])
def list_applications(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Application, models.Vacancy)
        .join(models.Vacancy, models.Application.vacancy_id == models.Vacancy.id)
        .order_by(models.Application.created_at.desc())
        .all()
    )
    data = []
    for app, vac in rows:
        data.append(
            {
                "id": app.id,
                "vacancyTitle": vac.title,
                "candidate": app.candidate_name,
                "score": app.relevance_score,
                "mismatches": (app.mismatch_reasons or "").split(",") if app.mismatch_reasons else [],
            }
        )
    return data


@router.get("/applications/{application_id}/messages", dependencies=[Depends(require_roles("admin"))])
def list_application_messages(application_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.application_id == application_id)
        .all()
    )
    if not sessions:
        return []
    session_ids = [s.id for s in sessions]
    rows = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id.in_(session_ids))
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "sender": m.sender,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in rows
    ]


@router.get("/applications/{application_id}", dependencies=[Depends(require_roles("admin"))])
def get_application_details(application_id: int, db: Session = Depends(get_db)):
    app = db.get(models.Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    vac = db.get(models.Vacancy, app.vacancy_id)
    return {
        "id": app.id,
        "vacancyTitle": vac.title if vac else None,
        "candidate_name": app.candidate_name,
        "candidate_email": app.candidate_email,
        "relevance_score": app.relevance_score,
        "mismatches": (app.mismatch_reasons or "").split(",") if app.mismatch_reasons else [],  # visible only in admin
        "summary_text": app.summary_text,  # visible only in admin
        "cv_url": f"/uploads/{app.cv_file_path.split('/')[-1]}",
        "created_at": app.created_at.isoformat(),
    }
