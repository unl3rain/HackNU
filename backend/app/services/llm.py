from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence
import httpx
import json
import re

import google.generativeai as genai
from app.core.config import settings


SYSTEM_INSTRUCTION = (
    "Ты — бот-ассистент для подбора кандидатов. Говоришь дружелюбно, понятно, без давления. "
    "Верни СТРОГО JSON без какого‑либо дополнительного текста вне JSON. Ключи — на английском. "
    "ВСЕ текстовые значения (включая items в mismatches и поля внутри candidate_profile) — на русском языке, краткие и по делу."
)

_GEMINI_MODELS_CACHE: dict[str, Any] = {}
_OPENROUTER_CLIENT: Optional[httpx.Client] = None

# Configure Gemini SDK once at import time to avoid per-call overhead
if getattr(settings, "GEMINI_API_KEY", None):
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception:
        pass


def _get_http_client() -> httpx.Client:
    global _OPENROUTER_CLIENT
    if _OPENROUTER_CLIENT is None:
        _OPENROUTER_CLIENT = httpx.Client(timeout=30)
    return _OPENROUTER_CLIENT


def _clip_text(text: str, limit: int = 12000) -> str:
    if not isinstance(text, str):
        return ""
    if len(text) <= limit:
        return text
    head = text[: int(limit * 0.8)]
    tail = text[-int(limit * 0.2) :]
    return head + "\n…\n" + tail


def _normalize_model_name(name: str) -> str:
    return name.split("/", 1)[-1]


def _get_model(model_name: str):
    if not settings.GEMINI_API_KEY:
        return None
    name = _normalize_model_name(model_name)
    if name in _GEMINI_MODELS_CACHE:
        return _GEMINI_MODELS_CACHE[name]
    try:
        model = genai.GenerativeModel(
            name,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.6,
                "top_p": 0.9,
            },
        )
    except TypeError:
        model = genai.GenerativeModel(
            name,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.6,
                "top_p": 0.9,
            },
        )
    _GEMINI_MODELS_CACHE[name] = model
    return model


def _resolve_model_candidates() -> list[str]:
    return [
        "gemini-2.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
    ]


def _format_chat_context(chat_context: Optional[Sequence[dict]] = None) -> str:
    if not chat_context:
        return ""
    lines: list[str] = []
    for m in chat_context:
        role = (m.get("role") or m.get("sender") or "").lower()
        content = (m.get("content") or "").strip()
        if not content:
            continue
        if role in ("user", "candidate"):
            lines.append(f"Кандидат: {content}")
        elif role in ("assistant", "bot", "system"):
            lines.append(f"Бот: {content}")
        else:
            lines.append(content)
    if not lines:
        return ""
    return "\n".join(lines[-15:])  


def _requirements_text(vacancy: dict) -> str:
    """Build a concise text of vacancy requirements from a dict.
    Accepts keys: title, city, description, min_experience_years, employment_type,
    education_level, languages (list|csv), salary_min, salary_max, currency, skills (list|csv).
    """
    parts: list[str] = []
    title = vacancy.get("title")
    if title:
        parts.append(f"Позиция: {title}")
    city = vacancy.get("city")
    if city:
        parts.append(f"Город: {city}")
    desc = vacancy.get("description")
    if desc:
        parts.append(f"Описание: {desc}")
    exp = vacancy.get("min_experience_years")
    if isinstance(exp, (int, float)) and exp > 0:
        parts.append(f"Мин. опыт: {int(exp)} лет")
    emp = vacancy.get("employment_type")
    if emp:
        parts.append(f"Тип занятости: {emp}")
    edu = vacancy.get("education_level")
    if edu:
        parts.append(f"Образование: {edu}")
    langs = vacancy.get("languages")
    if isinstance(langs, str):
        langs = [x.strip() for x in langs.split(",") if x.strip()]
    if isinstance(langs, list) and langs:
        parts.append("Языки: " + ", ".join(langs))
    sal_min = vacancy.get("salary_min")
    sal_max = vacancy.get("salary_max")
    cur = vacancy.get("currency") or ""
    if sal_min or sal_max:
        if sal_min and sal_max:
            parts.append(f"Зарплата: {sal_min}-{sal_max} {cur}".strip())
        elif sal_min:
            parts.append(f"Зарплата от: {sal_min} {cur}".strip())
        elif sal_max:
            parts.append(f"Зарплата до: {sal_max} {cur}".strip())
    skills = vacancy.get("skills")
    if isinstance(skills, str):
        skills = [x.strip() for x in skills.split(",") if x.strip()]
    if isinstance(skills, list) and skills:
        parts.append("Навыки: " + ", ".join(skills))
    return "\n".join(parts)


def _sanitize_and_parse_json(text: str) -> Optional[dict[str, Any]]:
    """Attempt to parse JSON, tolerating code fences and trailing text."""
    t = (text or "").strip()
    if not t:
        return None
    if t.startswith("```"):
        t = re.sub(r"^```json\s*", "", t, flags=re.IGNORECASE).lstrip("`").rstrip("`").strip()
    try:
        return json.loads(t)
    except Exception:
        m = re.search(r"\{[\s\S]*\}$", t, flags=re.MULTILINE)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None


def analyze_cv_with_gemini(cv_text: str, vacancy: dict, chat_context: Optional[Sequence[dict]] = None) -> Optional[dict[str, Any]]:
    model_names = _resolve_model_candidates()

    chat_block = _format_chat_context(chat_context)
    req_text = _requirements_text(vacancy)

    prompt = (
        f"ТРЕБОВАНИЯ ВАКАНСИИ (текст):\n{_clip_text(req_text, 4000)}\n\n"
        f"ВАКАНСИЯ(JSON): {json.dumps(vacancy, ensure_ascii=False)}\n\n"
        f"РЕЗЮМЕ(ПОЛНЫЙ ТЕКСТ):\n{_clip_text(cv_text, 12000)}\n\n"
        + (f"КОНТЕКСТ ИЗ ЧАТА (последние сообщения):\n{chat_block}\n\n" if chat_block else "") +
        "Требования к ответу: верни СТРОГО JSON следующей структуры, без текста вне JSON. \n"
        "Все значения-строки — НА РУССКОМ ЯЗЫКЕ. Тексты — короткие и понятные. Если данных нет, ставь null или пустой список.\n"
        "{\n"
        "  \"candidate_profile\": {\"city\": str|null, \"experience_years\": number|null, \"education\": str|null, \"languages\": [str]|null, \"skills\": [str]|null, \"employment_type\": str|null, \"salary_expectation\": number|null},\n"
        "  \"mismatches\": [str],\n"
        "  \"summary\": str,\n"
        "  \"score\": number,\n"
        "  \"question\": str\n"
        "}\n"
        "Пояснения: \n"
        "- mismatches — это КОРОТКИЕ формулировки ключевых несоответствий ТОЛЬКО относительно требований ВАКАНСИИ (не добавляй пункты, которых нет в описании вакансии).\n"
        "- score — целое число 0..100, основанное на соответствии требованиям.\n"
        "- question — один естественный вопрос кандидату по САМЫМ критичным несоответствиям из mismatches (без перечислений, 1–2 предложения).\n"
        "- summary — краткая выжимка по соответствию кандидата вакансии.\n"
    )
    for name in model_names:
        try:
            model = _get_model(name)
            if not model:
                return None
            resp = model.generate_content([prompt])
            text = (getattr(resp, "text", None) or "").strip()
            data = _sanitize_and_parse_json(text)
            if not data:
                raise ValueError("invalid JSON from model")
            return data
        except Exception:
            continue
    return None


def analyze_cv_with_openrouter(cv_text: str, vacancy: dict, chat_context: Optional[Sequence[dict]] = None) -> Optional[dict[str, Any]]:
    if not settings.OPENROUTER_API_KEY:
        return None
    chat_block = _format_chat_context(chat_context)
    req_text = _requirements_text(vacancy)
    prompt = (
        f"ТРЕБОВАНИЯ ВАКАНСИИ (текст):\n{_clip_text(req_text, 4000)}\n\n"
        f"ВАКАНСИЯ(JSON): {json.dumps(vacancy, ensure_ascii=False)}\n\n"
        f"РЕЗЮМЕ(ПОЛНЫЙ ТЕКСТ):\n{_clip_text(cv_text, 16000)}\n\n"
        + (f"КОНТЕКСТ ИЗ ЧАТА (последние сообщения):\n{chat_block}\n\n" if chat_block else "") +
        "Требования к ответу: верни СТРОГО JSON следующей структуры, без текста вне JSON. \n"
        "Все значения-строки — НА РУССКОМ ЯЗЫКЕ. Тексты — короткие и понятные. Если данных нет, ставь null или пустой список.\n"
        "{\n"
        "  \"candidate_profile\": {\"city\": str|null, \"experience_years\": number|null, \"education\": str|null, \"languages\": [str]|null, \"skills\": [str]|null, \"employment_type\": str|null, \"salary_expectation\": number|null},\n"
        "  \"mismatches\": [str],\n"
        "  \"summary\": str,\n"
        "  \"score\": number,\n"
        "  \"question\": str  \n"
        "}\n"
        "Пояснения: \n"
        "- mismatches — КОРОТКИЕ формулировки ключевых несоответствий ТОЛЬКО относительно требований ВАКАНСИИ (не добавляй пункты, которых нет в описании вакансии).\n"
        "- score — целое число 0..100, чем выше, тем лучше соответствие.\n"
        "- question — один естественный вопрос кандидату по САМЫМ критичным несоответствиям из mismatches (без перечислений, 1–2 предложения).\n"
        "- summary — краткая выжимка.\n"
    )
    model = settings.LLM_MODEL or "deepseek/deepseek-v3"
    try:
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        client = _get_http_client()
        r = client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
        if not content:
            return None
        return json.loads(content)
    except Exception:
        return None


def analyze_cv(cv_text: str, vacancy: dict, chat_context: Optional[Sequence[dict]] = None) -> Optional[dict[str, Any]]:
    provider = (settings.LLM_PROVIDER or "").lower()
    if provider == "openrouter":
        out = analyze_cv_with_openrouter(cv_text, vacancy, chat_context)
        if out is not None:
            return out
    out = analyze_cv_with_gemini(cv_text, vacancy, chat_context)
    return out


def score_from_llm_result(llm: dict[str, Any], vacancy: dict) -> tuple[int, list[str], str]:
    mismatches = llm.get("mismatches") or []
    summary = llm.get("summary") or ""
    score_raw = llm.get("score")
    score: int
    try:
        if isinstance(score_raw, (int, float)):
            score = int(max(0, min(100, round(score_raw))))
        else:
            raise ValueError()
    except Exception:
        score = max(30, 100 - 10 * len(mismatches))
    return score, mismatches, summary
