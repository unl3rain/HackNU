from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.db import models
from app.core.security import require_roles, get_current_user
from app.schemas.vacancy import VacancyCreate, VacancyRead


router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=List[VacancyRead])
def list_vacancies(db: Session = Depends(get_db)):
    rows = db.query(models.Vacancy).order_by(models.Vacancy.created_at.desc()).all()
    return [to_read(v) for v in rows]


@router.get("/{vacancy_id}", response_model=VacancyRead)
def get_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    v = db.get(models.Vacancy, vacancy_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return to_read(v)


@router.post("", response_model=VacancyRead, dependencies=[Depends(require_roles("admin", "employer"))])
def create_vacancy(payload: VacancyCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    v = models.Vacancy(
        title=payload.title,
        city=payload.city,
        description=payload.description,
        min_experience_years=payload.min_experience_years,
        employment_type=payload.employment_type,
        education_level=payload.education_level,
        languages=",".join(payload.languages) if payload.languages else None,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        currency=payload.currency,
        skills=",".join(payload.skills) if payload.skills else None,
        created_by=user.id if getattr(user, "id", None) else None,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return to_read(v)


def to_read(v: models.Vacancy) -> VacancyRead:
    return VacancyRead(
        id=v.id,
        title=v.title,
        city=v.city,
        description=v.description,
        min_experience_years=v.min_experience_years,
        employment_type=v.employment_type,
        education_level=v.education_level,
        languages=v.languages.split(",") if v.languages else None,
        salary_min=v.salary_min,
        salary_max=v.salary_max,
        currency=v.currency,
        skills=v.skills.split(",") if v.skills else None,
    )


@router.delete("/{vacancy_id}", dependencies=[Depends(require_roles("admin", "employer"))])
def delete_vacancy(vacancy_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    v = db.get(models.Vacancy, vacancy_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    if (user.role or "").lower() != "admin" and v.created_by != getattr(user, "id", None):
        raise HTTPException(status_code=403, detail="Forbidden")

    apps = db.query(models.Application).filter(models.Application.vacancy_id == v.id).all()
    if apps:
        app_ids = [a.id for a in apps]
        sessions = db.query(models.ChatSession).filter(models.ChatSession.application_id.in_(app_ids)).all()
        if sessions:
            session_ids = [s.id for s in sessions]
            if session_ids:
                db.query(models.ChatMessage).filter(models.ChatMessage.session_id.in_(session_ids)).delete(synchronize_session=False)
                db.query(models.ChatSession).filter(models.ChatSession.id.in_(session_ids)).delete(synchronize_session=False)
        db.query(models.Application).filter(models.Application.vacancy_id == v.id).delete(synchronize_session=False)

    db.delete(v)
    db.commit()
    return {"deleted": True}
