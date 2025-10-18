from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.security import require_roles, get_current_user
from app.db import models

router = APIRouter(prefix="/employer", tags=["employer"], dependencies=[Depends(require_roles("employer", "admin"))])


@router.get("/applications")
def list_my_applications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    my_vac_ids = [v.id for v in db.query(models.Vacancy).filter(models.Vacancy.created_by == user.id).all()]
    if not my_vac_ids:
        return []
    rows = (
        db.query(models.Application, models.Vacancy)
        .join(models.Vacancy, models.Application.vacancy_id == models.Vacancy.id)
        .filter(models.Application.vacancy_id.in_(my_vac_ids))
        .order_by(models.Application.created_at.desc())
        .all()
    )
    return [
        {
            "id": app.id,
            "vacancyTitle": vac.title,
            "candidate": app.candidate_name,
            "score": app.relevance_score,
        }
        for app, vac in rows
    ]


@router.get("/applications/{application_id}")
def get_my_application(application_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    app = db.get(models.Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    vac = db.get(models.Vacancy, app.vacancy_id)
    if not vac or (vac.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {
        "id": app.id,
        "vacancyTitle": vac.title if vac else None,
        "candidate_name": app.candidate_name,
        "candidate_email": app.candidate_email,
        "relevance_score": app.relevance_score,
        "cv_url": f"/uploads/{app.cv_file_path.split('/')[-1]}",
        "created_at": app.created_at.isoformat(),
    }


@router.get("/applications/{application_id}/messages")
def list_my_application_messages(application_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    app = db.get(models.Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    vac = db.get(models.Vacancy, app.vacancy_id)
    if not vac or (vac.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
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
