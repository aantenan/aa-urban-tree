# AA Urban Tree – Grant Application Monorepo

Monorepo for the urban tree grant application: backend API, frontend, shared libraries, and infrastructure templates.

## Structure

- **`apps/backend/`** – FastAPI Python backend (API, auth, applications, documents, notifications)
- **`apps/frontend/`** – React (Vite) single-page application
- **`libs/`** – Shared Python libraries: `shared-models`, `database`, `authentication`, `storage`, `email`
- **`infra/`** – Terraform templates for AWS (VPC, RDS, ECS, ALB, S3, IAM, CloudWatch)
- **`tools/`** – Scripts (`format.sh`, `lint.sh`, `test.sh`, `migrate.sh`) and Docker Compose for local dev

## Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python
- Node.js 18+ and npm for the frontend
- Docker and Docker Compose (optional, for full stack)

### Install dependencies

```bash
# From repo root: generate lockfile (first time or after dependency changes)
uv lock

# Install all Python workspace dependencies
uv sync

# Frontend
cd apps/frontend && npm install
```

### Environment

```bash
cp .env.example .env
# Edit .env as needed (database, auth, storage, etc.)
```

## Development

- **Backend (local):** `cd apps/backend && uv run uvicorn main:app --reload` (run from repo root with `PYTHONPATH=apps/backend/src` or from `apps/backend` with `uv run`)
- **Frontend:** `cd apps/frontend && npm run dev`
- **Full stack (Docker):** `docker compose up` (requires `uv lock` and `.env`)

## Scripts (from repo root)

- `tools/scripts/format.sh` – Black (Python) + Prettier (JS)
- `tools/scripts/lint.sh` – Pylint + ESLint
- `tools/scripts/test.sh` – pytest + frontend tests
- `tools/scripts/migrate.sh` – Database migrations (when implemented)

## Contributing

1. Create a branch, make changes, run format/lint/tests.
2. Open a PR; ensure CI (if configured) passes.
