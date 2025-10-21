## Purpose
This file gives concise, actionable guidance to automated coding agents (Copilot-style) working on the 7ty-backend FastAPI service so they can be productive immediately.

### Big picture
- This repository hosts a single FastAPI service (entrypoint: `app/main.py`) using SQLAlchemy + PostgreSQL. The app exposes routes under `/api/*` split into `auth`, `admin`, `bills`, and `transactions` routers in `app/routers/`.
- Database models live in `app/models.py`. CRUD functions are in `app/crud.py`. Pydantic schemas are in `app/schemas.py` and security helpers are in `app/security.py`.
- The service is expected to run in Docker using `docker-compose.yml` which brings up the `api` service and a `db` postgres service.

### Run / dev commands
- Local dev (without Docker): set environment variables from `.env` and run Uvicorn from the `app` dir. Example (bash):
  - export PGUSER=..., PGPASSWORD=..., PGHOST=..., PGDATABASE=..., JWT_SECRET_KEY=..., JWT_ALGORITHM=..., ACCESS_TOKEN_EXPIRE_MINUTES=60
  - cd app && uvicorn main:app --reload --host 0.0.0.0 --port 8000
- Docker: use the provided `start.sh` or `docker-compose up --build`. `start.sh` calls `docker-compose up --build`.
- Tests: there are no test files in the repo; prefer creating small unit tests that exercise CRUD functions and routers using FastAPI's TestClient.

### Environment variables & secrets (required)
- Database: PGUSER, PGPASSWORD, PGHOST, PGDATABASE — used by `app/database.py` to build SQLALCHEMY_DATABASE_URL.
- JWT: JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES — used by `app/security.py`.
- These must be present for runtime and for schema creation (the code calls `models.Base.metadata.create_all(bind=engine)` in `app/main.py`).

### Project-specific patterns and conventions
- Routes:
  - Authentication endpoints are under `prefix="/api/auth"` (see `app/routers/auth.py`). Token endpoint accepts OAuth2PasswordRequestForm and returns `schemas.Token`.
  - Admin-only routes use a router-level dependency: `dependencies=[Depends(security.get_current_active_admin)]` (see `app/routers/admin.py`). Use `security.get_current_active_admin` to gate admin-only behavior.
  - Bills and transactions routes use `Depends(security.get_current_user)` for authenticated actions.
- Models:
  - `User.role` is an Enum (UserRole) with values `admin`, `staff`, `agent`, `customer`. Some code checks role as plain strings (e.g. `if current_user.role not in ["agent", "admin"]`), so changes to the enum should maintain string compatibility.
- CRUD: `app/crud.py` centralizes DB operations; prefer adding new DB logic here and keep routers thin.

### Common edits an agent might make (examples)
- Add a new protected endpoint for agents: create route using `Depends(security.get_current_user)` and check `current_user.role == "agent"` before calling a `crud` helper.
- Add a DB migration: currently the project uses `Base.metadata.create_all(...)`. If adding Alembic, wire it to `SQLALCHEMY_DATABASE_URL` from `app/database.py` and don't rely on `create_all` for production.
- Fix authentication issues: `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")` — ensure tests and clients POST to `/api/auth/token` with form fields `username` and `password`.

### Integration points & dependencies
- PostgreSQL (image: postgres:15 in docker-compose). Connection string format: `postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}/{PGDATABASE}`.
- Packages are listed in `requirements.txt` (FastAPI, uvicorn, SQLAlchemy, psycopg2-binary, passlib[bcrypt], python-jose, python-dotenv). When adding new dependencies, update `requirements.txt` and Dockerfile accordingly.

### Files to review when editing related logic
- Routing / endpoints: `app/routers/*.py`
- Business logic: `app/crud.py`
- Data models: `app/models.py` and `app/schemas.py`
- Auth & tokens: `app/security.py`
- DB connection & session: `app/database.py`
- Container / run scripts: `Dockerfile`, `docker-compose.yml`, `start.sh`

### Safety and observable behavior
- The app creates tables at startup (see `app/main.py`); if changing models, be aware that existing production data will not be migrated correctly without explicit migrations.
- Error handling is minimal — prefer preserving current response models when changing endpoints to avoid breaking clients.

### Quick checklist for an AI agent before submitting a PR
1. Run `uvicorn main:app --reload` locally (after setting env vars) and smoke-test the basic endpoints: `/`, `/api/auth/register`, `/api/auth/token`.
2. Ensure new imports are added to `requirements.txt` and Dockerfile rebuilt.
3. Run linting and a minimal test harness if you add new logic.
4. Keep router functions thin — move data logic to `app/crud.py`.

If anything in this file is unclear or you'd like more examples (tests, common bug patterns, or how to add Alembic), tell me which area to expand.
