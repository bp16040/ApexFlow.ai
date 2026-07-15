# Development guide

## Configuration

Copy the root `.env.example` file to `.env`. Backend settings are loaded from environment variables and fall back to safe local-development values.

## Quality checks

Run backend tests with `pytest` from `backend/` and frontend tests with `npm test` from `frontend/`.

## Migrations

Alembic is initialized in `backend/alembic`. Create revisions only after a domain model is introduced:

```powershell
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```
