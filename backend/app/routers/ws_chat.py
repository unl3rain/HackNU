from __future__ import annotations
from typing import Optional
import asyncio
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import decode_token
from app.db import models
from app.services.llm import analyze_cv, score_from_llm_result
from app.services.cv import compute_relevance


router = APIRouter()


def _question_for(mismatch: str) -> str:
    m = (mismatch or "").strip().lower()

    city_templates = [
        "Вакансия привязана к конкретному городу. Рассматриваете переезд или готовы работать на месте?",
        "Подскажите, пожалуйста, вы сейчас находитесь в нужном городе или готовы переехать?",
        "Локация важна для роли. Готовы ли вы к переезду либо уже живёте в нужном городе?",
    ]
    experience_templates = [
        "Сколько лет у вас коммерческого опыта по ключным требованиям этой роли?",
        "Расскажите, пожалуйста, об опыте: сколько лет вы работали с основным стеком?",
        "Чтобы оценить соответствие: сколько лет практического опыта по основным технологиям?",
    ]
    schedule_templates = [
        "Формат — полный рабочий день. Насколько вам подходит такой график?",
        "Рассматриваете ли вы полноценную занятость (полный день)?",
        "Уточните, пожалуйста: удобен ли вам режим полной занятости?",
    ]
    css_templates = [
        "В резюме не увидел упоминания CSS. Работали ли вы с CSS? На каком уровне?",
        "Расскажите, пожалуйста, про опыт с CSS: насколько уверенно себя чувствуете?",
        "Есть ли практический опыт верстки и стилизации интерфейсов (CSS)?",
    ]
    fe_focus_templates = [
        "Вы упоминаете бэкенд‑опыт. Насколько комфортно вам сфокусироваться именно на фронтенде?",
        "Роль чисто фронтендная. Готовы ли вы сконцентрироваться на фронте?",
        "Подтвердите, пожалуйста: для этой позиции нужен фокус на фронтенде — это вам подходит?",
    ]

    if "город" in m or "локац" in m or "relocate" in m or "city" in m or "location" in m:
        return random.choice(city_templates)
    if "опыт" in m or "experience" in m:
        return random.choice(experience_templates)
    if "график" in m or "schedule" in m or "full time" in m or "полный" in m:
        return random.choice(schedule_templates)
    if "css" in m and ("missing" in m or "нет" in m or "lack" in m or "не упом" in m):
        return random.choice(css_templates)
    if ("frontend" in m and "backend" in m) or ("фронт" in m and "бэк" in m):
        return random.choice(fe_focus_templates)

    generic_templates = [
        "Расскажите, пожалуйста, подробнее по этому пункту.",
        "Можете уточнить этот момент в паре предложений?",
        "Немного деталей по этому аспекту поможет точнее оценить соответствие.",
    ]
    return random.choice(generic_templates)


@router.websocket("/ws/applications/{application_id}")
async def ws_app_chat(websocket: WebSocket, application_id: int, token: str, db: Session = Depends(get_db)):
    await websocket.accept()

    payload = decode_token(token)
    if not payload or not str(payload.get("sub", "")).startswith("app:"):
        await websocket.send_json({"type": "error", "message": "invalid token"})
        await websocket.close()
        return
    sub = str(payload["sub"])  # e.g. app:1
    if sub != f"app:{application_id}":
        await websocket.send_json({"type": "error", "message": "token-app mismatch"})
        await websocket.close()
        return

    app = db.get(models.Application, application_id)
    if not app:
        await websocket.send_json({"type": "error", "message": "application not found"})
        await websocket.close()
        return

    session = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.application_id == app.id, models.ChatSession.state == "open")
        .first()
    )
    if not session:
        session = models.ChatSession(application_id=app.id, last_relevance_score=app.relevance_score)
        db.add(session)
        db.commit()
        db.refresh(session)

    vacancy = db.get(models.Vacancy, app.vacancy_id)
    vacancy_dict = {
        "title": vacancy.title if vacancy else None,
        "city": vacancy.city if vacancy else None,
        "description": vacancy.description if vacancy else None,
        "min_experience_years": vacancy.min_experience_years if vacancy else None,
        "employment_type": vacancy.employment_type if vacancy else None,
        "education_level": vacancy.education_level if vacancy else None,
        "languages": vacancy.languages.split(",") if vacancy and vacancy.languages else [],
        "salary_min": vacancy.salary_min if vacancy else None,
        "salary_max": vacancy.salary_max if vacancy else None,
        "currency": vacancy.currency if vacancy else None,
        "skills": vacancy.skills.split(",") if vacancy and vacancy.skills else [],
    }

    existing_msgs = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session.id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )
    chat_ctx = [
        {"role": (m.sender or "bot"), "content": (m.content or "")}
        for m in existing_msgs
    ]

    await websocket.send_json({
        "type": "welcome",
        "session_id": session.id,
    })

    asked = set()
    asked_texts: set[str] = set()
    max_turns = 8 
    mismatches = (app.mismatch_reasons or "").split(",") if app.mismatch_reasons else []
    llm_first_question = None
    try:
        await websocket.send_json({"type": "analysis_status", "message": "Идёт оценка портфолио…"})
        await websocket.send_json({"type": "bot_typing", "value": True})
        llm_once = await asyncio.to_thread(analyze_cv, app.cv_text or "", vacancy_dict)
        if isinstance(llm_once, dict):
            llm_first_question = (llm_once.get("question") or "").strip() or None
    except Exception:
        llm_first_question = None
    finally:
        await websocket.send_json({"type": "bot_typing", "value": False})

    if llm_first_question:
        q = llm_first_question
    elif mismatches:
        q = _question_for(mismatches[0])
    else:
        q = None
    if q:
        await websocket.send_json({"type": "question", "id": 1, "text": q})
        db.add(models.ChatMessage(session_id=session.id, sender="bot", content=q))
        chat_ctx.append({"role": "bot", "content": q})
        asked.add(1)
        asked_texts.add(q.strip().lower())

    try:
        qid = 1
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "answer":
                user_text = data.get("text", "").strip()
                db.add(models.ChatMessage(session_id=session.id, sender="user", content=user_text))
                chat_ctx.append({"role": "user", "content": user_text})
                await websocket.send_json({"type": "bot_typing", "value": True})
                updated = await asyncio.to_thread(analyze_cv, app.cv_text or "", vacancy_dict, chat_ctx)
                if updated is not None:
                    score, new_mismatches, summary = score_from_llm_result(updated, vacancy_dict)
                    next_q = (updated.get("question") or "").strip() or None
                else:
                    score, new_mismatches, summary = compute_relevance(app.cv_text or "", vacancy_dict)
                    next_q = _question_for(new_mismatches[0]) if new_mismatches else None
                await websocket.send_json({"type": "bot_typing", "value": False})
                app.relevance_score = score
                app.mismatch_reasons = ",".join(new_mismatches) if new_mismatches else None
                app.summary_text = summary
                ack_messages = [
                    "Спасибо, учёл ваш ответ.",
                    "Принял, спасибо за ответ.",
                    "Отлично, записал.",
                    "Спасибо, учту при оценке.",
                ]
                await websocket.send_json({
                    "type": "analysis_update",
                    "message": random.choice(ack_messages),
                })

                if not new_mismatches or len(asked) >= max_turns:
                    await websocket.send_json({
                        "type": "final_summary",
                        "message": "Спасибо! Мы учли ваши ответы и передадим их рекрутеру.",
                    })
                    session.state = "closed"
                    db.commit()
                    await websocket.close()
                    break

                if next_q and next_q.strip().lower() not in asked_texts:
                    qid += 1
                    await websocket.send_json({"type": "question", "id": qid, "text": next_q})
                    db.add(models.ChatMessage(session_id=session.id, sender="bot", content=next_q))
                    chat_ctx.append({"role": "bot", "content": next_q})
                    db.commit()
                    asked.add(qid)
                    asked_texts.add(next_q.strip().lower())
                elif new_mismatches:
                    qid += 1
                    q = _question_for(new_mismatches[0])
                    if q.strip().lower() in asked_texts:
                        await websocket.send_json({
                            "type": "final_summary",
                            "message": "Спасибо! Мы учли ваши ответы и передадим их рекрутеру.",
                        })
                        session.state = "closed"
                        db.commit()
                        await websocket.close()
                        break
                    await websocket.send_json({"type": "question", "id": qid, "text": q})
                    db.add(models.ChatMessage(session_id=session.id, sender="bot", content=q))
                    chat_ctx.append({"role": "bot", "content": q})
                    db.commit()
                    asked.add(qid)
                    asked_texts.add(q.strip().lower())
                else:
                    await websocket.send_json({
                        "type": "final_summary",
                        "message": "Спасибо! Мы передадим ваши ответы рекрутеру.",
                    })
                    session.state = "closed"
                    db.commit()
                    await websocket.close()
                    break
            elif data.get("type") == "end":
                updated = await asyncio.to_thread(analyze_cv, app.cv_text or "", vacancy_dict, chat_ctx)
                if updated is not None:
                    score, new_mismatches, summary = score_from_llm_result(updated, vacancy_dict)
                else:
                    score, new_mismatches, summary = compute_relevance(app.cv_text or "", vacancy_dict)

                app.relevance_score = score
                app.mismatch_reasons = ",".join(new_mismatches) if new_mismatches else None
                app.summary_text = summary
                session.state = "closed"
                if summary:
                    db.add(models.ChatMessage(session_id=session.id, sender="system", content=f"Итоговая выжимка: {summary}"))
                    chat_ctx.append({"role": "system", "content": f"Итоговая выжимка: {summary}"})
                db.commit()

                await websocket.send_json({
                    "type": "final_summary",
                    "message": "Спасибо! Мы учли ваши ответы и передадим их рекрутеру.",
                })
                await websocket.close()
                break
            else:
                await websocket.send_json({"type": "error", "message": "unknown message"})
    except WebSocketDisconnect:
        pass
