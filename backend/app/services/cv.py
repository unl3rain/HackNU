from pypdf import PdfReader
from typing import List, Tuple, Dict, Any
import io
from app.core.config import settings


def extract_text_from_pdf(path: str) -> str:
    """Extract text from a PDF. Supports local file paths and s3://bucket/key URLs."""
    if isinstance(path, str) and path.startswith("s3://"):
        _, _, rest = path.partition("s3://")
        bucket, _, key = rest.partition("/")
        if not bucket or not key:
            raise ValueError("Invalid S3 URL for PDF: expected s3://<bucket>/<key>")
        try:
            import boto3  # type: ignore
        except Exception as e:
            raise RuntimeError("boto3 is required to read PDFs from S3") from e
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        obj = s3.get_object(Bucket=bucket, Key=key)
        data: bytes = obj["Body"].read()
        reader = PdfReader(io.BytesIO(data))
    else:
        reader = PdfReader(path)
    texts: list[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def compute_relevance(cv_text: str, vacancy: Dict[str, Any]) -> Tuple[int, List[str], str]:
    text = cv_text.lower()
    score = 40
    mismatches: List[str] = []
    notes: List[str] = []

    skills = [s.lower() for s in (vacancy.get("skills", []) or [])]
    matched_skills = sum(1 for s in skills if s and s in text)
    if skills:
        skills_weight = 35
        score += int(skills_weight * (matched_skills / max(1, len(skills))))
        notes.append(f"навыки {matched_skills}/{len(skills)}")

    city = (vacancy.get("city") or "").lower()
    if city:
        if city in text:
            score += 6
            notes.append("город совпадает")
        else:
            mismatches.append("город")

    min_exp = int(vacancy.get("min_experience_years") or 0)
    if min_exp:
        import re
        exp_match = re.search(r"(опыт\s*(\d+))|((\d+)\+?\s*год)", text)
        years = 0
        if exp_match:
            years = int(next((g for g in exp_match.groups() if g and g.isdigit()), "0"))
        if years >= min_exp:
            score += 6
            notes.append(f"опыт {years} >= {min_exp}")
        else:
            mismatches.append("опыт")

    emp = (vacancy.get("employment_type") or "").lower()
    if emp:
        if emp in text:
            score += 3
        else:
            mismatches.append("занятость")

    edu = (vacancy.get("education_level") or "").lower()
    if edu:
        if edu in text or ("бакалавр" in edu and "бакалавр" in text):
            score += 3
        else:
            mismatches.append("образование")

    langs = [l.lower() for l in (vacancy.get("languages") or [])]
    if langs:
        lang_hit = sum(1 for l in langs if l and l in text)
        if lang_hit == 0:
            mismatches.append("языки")
        else:
            score += 3
            notes.append(f"языки {lang_hit}/{len(langs)}")

    try:
        smin = float(vacancy.get("salary_min") or 0.0)
    except Exception:
        smin = 0.0
    if smin:
        import re
        sal_match = re.search(r"(\d{2,6})\s*(k|тыс|тг|₸)?", text)
        if sal_match:
            claimed = float(sal_match.group(1))
            if claimed <= smin * 1.2:  
                score += 4
            else:
                mismatches.append("зарплата")

    title = (vacancy.get("title") or "").lower()
    if title:
        key = title.split("(")[0].strip()
        if any(tok for tok in key.split() if tok in text):
            score += 5
            notes.append("позиция релевантна")

    score = max(0, min(100, score))
    summary = "; ".join(notes) if notes else ""
    return score, mismatches, summary
