from app.db.session import SessionLocal, engine
from app.db import models
from app.core.security import get_password_hash


def run():
    db = SessionLocal()
    try:
        # Ensure tables exist
        models.Base.metadata.create_all(bind=engine)

        # Upsert admins
        admin1 = db.query(models.User).filter(models.User.email == "admin1@example.com").first()
        if not admin1:
            admin1 = models.User(email="admin1@example.com", password_hash=get_password_hash("admin1"), role="admin")
            db.add(admin1)
            db.commit()
            db.refresh(admin1)
        else:
            admin1.password_hash = get_password_hash("admin1")
            admin1.role = "admin"
            db.commit()

        admin2 = db.query(models.User).filter(models.User.email == "admin2@example.com").first()
        if not admin2:
            admin2 = models.User(email="admin2@example.com", password_hash=get_password_hash("admin2"), role="admin")
            db.add(admin2)
            db.commit()
            db.refresh(admin2)
        else:
            admin2.password_hash = get_password_hash("admin2")
            admin2.role = "admin"
            db.commit()

        # Create vacancies: frontend and backend by admin1, ml by admin2
        vacancies = [
            models.Vacancy(
                title="Frontend Developer (React)",
                city="Алматы",
                description="Разработка SPA на React/TypeScript",
                min_experience_years=1,
                employment_type="full-time",
                skills=",".join(["React", "TypeScript", "CSS"]),
                created_by=admin1.id,
            ),
            models.Vacancy(
                title="Backend Engineer (FastAPI)",
                city="Астана",
                description="API разработка на Python FastAPI, SQLAlchemy, PostgreSQL",
                min_experience_years=2,
                employment_type="full-time",
                skills=",".join(["Python", "FastAPI", "SQLAlchemy", "PostgreSQL"]),
                created_by=admin1.id,
            ),
            models.Vacancy(
                title="ML Engineer",
                city="Шымкент",
                description="Разработка и продакшен ML-пайплайнов",
                min_experience_years=1,
                employment_type="full-time",
                skills=",".join(["Python", "scikit-learn", "Pandas"]),
                created_by=admin2.id,
            ),
        ]
        # Insert vacancies if they don't already exist (by title/owner)
        created_titles = []
        for v in vacancies:
            exists = db.query(models.Vacancy).filter(
                models.Vacancy.title == v.title,
                models.Vacancy.created_by == v.created_by,
            ).first()
            if not exists:
                db.add(v)
                db.commit()
                created_titles.append(v.title)

        print(
            f"Seeded/updated users: admin1@example.com (pwd: admin1), admin2@example.com (pwd: admin2); "
            f"vacancies created: {created_titles or 'none (already present)'}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
