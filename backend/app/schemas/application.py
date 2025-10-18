from pydantic import BaseModel
from typing import Optional, List


class ApplicationCreate(BaseModel):
    vacancy_id: int
    candidate_name: str
    candidate_email: str


class ApplicationRead(BaseModel):
    id: int
    vacancy_id: int
    candidate_name: str
    candidate_email: str
    relevance_score: Optional[int] = None
    mismatch_reasons: Optional[List[str]] = None
    summary_text: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationSummary(BaseModel):
    relevance_score: Optional[int] = None
    mismatch_reasons: Optional[List[str]] = None
    summary_text: Optional[str] = None


class ApplicationListItem(BaseModel):
    id: int
    vacancy_id: int
    vacancy_title: str
    relevance_score: Optional[int] = None
    status: Optional[str] = None
    created_at: Optional[str] = None

