# Local Docker Setup

Services:
- db (Postgres 16)
- backend (FastAPI)
- frontend (Nginx + built React)

Run:
- docker compose up --build

URLs:
 - Frontend: http://localhost:8081/
 - Backend API: http://localhost:8001/api/v1
 - Backend uploads: http://localhost:8001/uploads
 - Postgres (host): localhost:5433 (internal 5432)

Notes:
- Set GEMINI_API_KEY in your shell before `docker compose up` if you want real LLM analysis.
- Data persists in volumes `db-data` and `backend-uploads`.
