# ApexFlow AI

Production-ready foundation for the ApexFlow AI platform. Business modules are intentionally not included yet.

Phase 2 provides authentication, users and roles, organization hierarchy, and directory foundations. Task management, workflows, Gmail, AI, dashboards, and reporting are intentionally not included.

## Phase 2 APIs

All application APIs are versioned under `/api/v1`.

- `/auth` — Google Workspace OAuth, passwordless sign-in, access-token refresh, logout, and current profile.
- `/users` — user profiles and scoped multi-role assignments.
- `/roles` — roles, permissions, assignments, and permission matrix.
- `/organization` — organizations, departments, programs, academic sessions, designations, coordinators, reporting lines, and directory profiles.

See [docs/authentication-and-organization.md](docs/authentication-and-organization.md) for access-control and operational details.

## Structure

- `backend/` — FastAPI service, SQLAlchemy/Alembic configuration, and Python tests.
- `frontend/` — Next.js web application and frontend test configuration.
- `docs/` — project and operational documentation.
- `docker/` — optional container definitions; Docker is not required for local development.

## Local development

Copy `.env.example` to `.env` and adjust values as needed.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The health endpoint is available at `http://localhost:8000/health`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The application is available at `http://localhost:3000`.

### Tests

```powershell
cd backend; pytest
cd frontend; npm test
```

## Database migrations

With PostgreSQL running and `DATABASE_URL` configured:

```powershell
cd backend
alembic upgrade head
```

See [docs/development.md](docs/development.md) and [docs/architecture.md](docs/architecture.md) for details.
