from pathlib import Path
from app.db.session import SessionLocal
from app.db import models
from app.core.config import settings
from pypdf import PdfWriter
from app.core.security import get_password_hash

def _ensure_sample_pdfs() -> dict[str, str]:
    """Create 2-3 minimal sample CV PDFs in uploads dir and return mapping name->path."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    samples = {
        "cv_python.pdf": "Python FastAPI SQLAlchemy PostgreSQL. Опыт 2+ года. Город Алматы.",
        "cv_frontend.pdf": "React TypeScript CSS. Опыт 1+ год. Город Шымкент.",
        "cv_data.pdf": "SQL Python Tableau. Опыт 1+ год. Город Астана.",
    }
    created_paths: dict[str, str] = {}
    for filename, text in samples.items():
        path = Path(settings.UPLOAD_DIR) / filename
        if not path.exists():
            # Create a simple blank-page PDF; cv_text will hold textual content separately
            writer = PdfWriter()
            writer.add_blank_page(width=595, height=842)
            with path.open("wb") as f:
                writer.write(f)
        created_paths[filename] = str(path)
    return created_paths


def run():
    db = SessionLocal()
    try:
        # Demo users
        if db.query(models.User).count() == 0:
            admin = models.User(email="admin@example.com", password_hash=get_password_hash("admin123"), role="admin")
            employer = models.User(email="hr@example.com", password_hash=get_password_hash("hr123"), role="admin")
            db.add_all([admin, employer])
            db.commit()
            db.refresh(admin)
            db.refresh(employer)
        pdfs = _ensure_sample_pdfs()
        # Vacancies
        if db.query(models.Vacancy).count() < 6:
            samples = [
                models.Vacancy(title="Backend Engineer (FastAPI)", city="Алматы", description="API разработка на FastAPI", min_experience_years=2, employment_type="full-time", skills=",".join(["Python","FastAPI","SQLAlchemy","PostgreSQL"]), created_by=1),
                models.Vacancy(title="ML Engineer", city="Астана", description="ML пайплайны и прод", min_experience_years=1, employment_type="full-time", skills=",".join(["Python","scikit-learn","Pandas"]), created_by=1) ,
                models.Vacancy(title="DevOps Engineer", city="Алматы", description="CI/CD и облака", min_experience_years=2, employment_type="full-time", skills=",".join(["Docker","Kubernetes","CI/CD"]), created_by=1),
                models.Vacancy(title="Frontend Developer (React)", city="Шымкент", description="SPA на React", min_experience_years=1, employment_type="full-time", skills=",".join(["React","TypeScript","CSS"]), created_by=1),
                models.Vacancy(title="Data Analyst", city="Астана", description="SQL, визуализация", min_experience_years=1, employment_type="full-time", skills=",".join(["SQL","Python","Tableau"]), created_by=1),
                models.Vacancy(title="QA Engineer", city="Алматы", description="Тестирование веб и API", min_experience_years=1, employment_type="full-time", skills=",".join(["Manual","API testing","Postman"]), created_by=1)
            ]
            db.add_all(samples)
            db.commit()
        # Seed a few demo applications linked to PDFs
        if db.query(models.Application).count() == 0:
            vacancies = db.query(models.Vacancy).all()
            if vacancies:
                demo_apps = [
                    {
                        "vac_title_contains": "Backend",
                        "name": "Айдар Нурлан",
                        "email": "aidar@example.com",
                        "pdf": pdfs.get("cv_python.pdf"),
                        "cv_text": "Python FastAPI SQLAlchemy PostgreSQL. Алматы.",
                        "score": 78,
                        "mismatches": ["график"],
                        "summary": "Хорошее совпадение по стеку, уточнить график.",
                    },
                    {
                        "vac_title_contains": "Frontend",
                        "name": "Диана К.",
                        "email": "diana@example.com",
                        "pdf": pdfs.get("cv_frontend.pdf"),
                        "cv_text": "React TypeScript CSS. Шымкент.",
                        "score": 72,
                        "mismatches": ["опыт"],
                        "summary": "Немного не хватает опыта, но стек совпадает.",
                    },
                    {
                        "vac_title_contains": "Data Analyst",
                        "name": "Марат А.",
                        "email": "marat@example.com",
                        "pdf": pdfs.get("cv_data.pdf"),
                        "cv_text": "SQL Python Tableau. Астана.",
                        "score": 69,
                        "mismatches": ["город"],
                        "summary": "Подходит по навыкам, локация на уточнении.",
                    },
                ]
                for da in demo_apps:
                    vac = next((v for v in vacancies if da["vac_title_contains"] in v.title), vacancies[0])
                    app = models.Application(
                        vacancy_id=vac.id,
                        candidate_name=da["name"],
                        candidate_email=da["email"],
                        cv_file_path=da["pdf"] or "",
                        cv_text=da["cv_text"],
                        relevance_score=da["score"],
                        mismatch_reasons=",".join(da["mismatches"]) if da["mismatches"] else None,
                        summary_text=da["summary"],
                    )
                    db.add(app)
                db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    run()
