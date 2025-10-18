from pydantic import BaseModel, Field
from typing import Optional, List


class VacancyBase(BaseModel):
    title: str
    city: str
    description: str
    min_experience_years: int = 0
    employment_type: str
    education_level: Optional[str] = None
    languages: Optional[List[str]] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: Optional[str] = None
    skills: Optional[List[str]] = None


class VacancyCreate(VacancyBase):
    pass


class VacancyRead(VacancyBase):
    id: int

    class Config:
        from_attributes = True
