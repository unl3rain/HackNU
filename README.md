# HackNU SmartBot

A full‑stack job application assistant:
- FastAPI backend (JWT auth, SQLAlchemy, WebSocket chat, PDF parsing, S3 optional, LLM integration)
- React + Vite + Tailwind frontend
- Postgres via Docker Compose (or SQLite for simple local runs)

## Quick start (Docker Compose)
Recommended for a clean, reproducible setup.

Prerequisites:
- Docker and Docker Compose
- Optionally set LLM keys for better chat quality

Steps:
1. In a terminal at repo root:
   - Linux/macOS: `export GEMINI_API_KEY=...` (optional)
   - Linux/macOS: `export OPENROUTER_API_KEY=...` (optional)
2. Start the stack:
   - `cd infra`
   - `docker compose up --build`
3. Open the app:
   - Frontend: http://localhost:8081
   - Backend API: http://localhost:8001/api/v1

The compose file provisions Postgres, builds backend and frontend images, and seeds demo data.

Demo accounts (compose):
- admin@example.com / admin123 (role: admin)
- hr@example.com / hr123 (role: employer)
- You can self‑register as a regular user from the login page

## Local development (no Docker)
Useful for quick iteration.

### Backend (FastAPI)
Prerequisites: Python 3.11+, virtualenv

1. Create and activate a venv:
   - `python -m venv .venv`
   - `source .venv/bin/activate` (Linux/macOS)
2. Install deps:
   - `pip install -r backend/requirements.txt`
3. Configure env (optional: defaults are sane):
   - Create `backend/.env` with any overrides, e.g.:
```
DATABASE_URL=sqlite:///./smartbot.db
JWT_SECRET=devsecret
API_PREFIX=/api/v1
# LLM provider: gemini or openrouter
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
# For S3 uploads (optional)
STORAGE_PROVIDER=local
AWS_S3_BUCKET=your-bucket
AWS_REGION=eu-central-1
```
4. Run API (http://localhost:8002):
   - `uvicorn backend.app.main:app --reload --port 8002`
5. Seed demo data (optional, creates admin/employer users and sample vacancies):
   - `python backend/scripts/seed_admins_vacancies.py`

API base (local): http://localhost:8002/api/v1

### Frontend (React/Vite)
Prerequisites: Node 18+

1. Install deps:
   - `cd frontend && npm ci`
2. Start dev server:
   - `npm run dev`
3. Open http://localhost:5173

The frontend proxies `/api` to `http://localhost:8002` in dev, and uses `VITE_API_BASE` when built.

## Features
- Auth with roles (admin, employer, user), JWT-based
- Vacancies list and details
- Apply with PDF CV upload, automatic analysis, realtime chat via WebSocket
- Admin/employer can view and delete vacancies and applications
- Optional S3 storage for CVs
- LLM provider agnostic (Gemini or OpenRouter)

## Troubleshooting
- Port conflicts: change host ports in `infra/docker-compose.yml` (`5433`, `8001`, `8081`).
- Fonts/CORS: Frontend is served with Vite/NGINX; backend CORS origins are configured in `backend/app/core/config.py`.
- LLM disabled: If no API key set, the system falls back to simple heuristics; chat still works but may be less informative.
- PDF parsing: Ensure PDFs are text based; scanned images may need OCR (not enabled by default).
- If compose backend can't reach the DB, ensure the `db` service is healthy first, or run `docker compose down -v && docker compose up --build` to reset volumes.

## Admin credentials recap
- Local (no Docker): created on first run or by seeding
   - admin@example.com / admin123 (role: admin)
   - hr@example.com / hr123 (role: employer)
- Docker Compose: same as above via `seed` service

## Tech stack
- Backend: FastAPI, SQLAlchemy, Pydantic v2, python-jose, passlib (pbkdf2 / bcrypt), boto3, pypdf, httpx
- Frontend: React 18, Vite 5, Tailwind v4
- Infra: Docker Compose, Postgres 16

## License
MIT
