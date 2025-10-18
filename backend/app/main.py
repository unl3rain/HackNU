from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import vacancies, applications, admin
from app.routers import auth
from app.routers import ws_chat
from app.routers import employer
from app.db.session import engine, SessionLocal
from app.db import models
from app.core.security import get_password_hash


app = FastAPI(title=settings.APP_NAME)

import os as _os
_os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(vacancies.router, prefix=settings.API_PREFIX)
app.include_router(applications.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(employer.router, prefix=settings.API_PREFIX)
app.include_router(ws_chat.router)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.email == "admin@example.com").first()
        if not admin:
            db.add(models.User(email="admin@example.com", password_hash=get_password_hash("admin123"), role="admin"))
            db.commit()
        hr = db.query(models.User).filter(models.User.email == "hr@example.com").first()
        if not hr:
            db.add(models.User(email="hr@example.com", password_hash=get_password_hash("hr123"), role="employer"))
            db.commit()
        count = db.query(models.Vacancy).count()
        if count == 0:
            samples = [
                models.Vacancy(
                    title="Frontend Developer (React)",
                    city="Алматы",
                    description="Разработка SPA и виджетов на React.",
                    min_experience_years=2,
                    employment_type="full-time",
                    skills=",".join(["React", "TypeScript", "HTML", "CSS"]),
                ),
                models.Vacancy(
                    title="Data Analyst",
                    city="Астана",
                    description="SQL, Python, визуализация.",
                    min_experience_years=1,
                    employment_type="full-time",
                    skills=",".join(["SQL", "Python", "Tableau"]),
                ),
            ]
            db.add_all(samples)
            db.commit()
    finally:
        db.close()
