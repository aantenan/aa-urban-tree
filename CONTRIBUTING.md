# Contributing

## Development workflow

1. **Clone and setup**
   - Clone the repo, then run `uv sync` and `cd apps/frontend && npm install`.
   - Copy `.env.example` to `.env` and set variables as needed.

2. **Run locally**
   - Backend: from repo root, `uv run --project apps/backend uvicorn main:app --reload` with `PYTHONPATH=apps/backend/src`, or use the **Backend** run configuration in PyCharm.
   - Frontend: `cd apps/frontend && npm run dev`, or use the **Frontend** run configuration in PyCharm.

3. **Code quality**
   - Format: `tools/scripts/format.sh` (Black for Python, Prettier for JS).
   - Lint: `tools/scripts/lint.sh` (Pylint, ESLint).
   - Tests: `tools/scripts/test.sh` (pytest, Vitest).
   - Optional: install pre-commit (`pip install pre-commit && pre-commit install`) to run formatters on commit.

4. **Database**
   - Use `DATABASE_URL=sqlite:///./local.db` for local development.
   - Run migrations: `tools/scripts/migrate.sh`.

5. **Before submitting**
   - Ensure format and lint pass; run tests.
   - Open a PR; CI will run format check and tests.

## Coding standards

- **Python**: Type hints, Black formatting, Pylint for linting. Use Pydantic for request/response validation.
- **JavaScript**: ESLint and Prettier. Prefer functional components and hooks.
- **API**: RESTful resource paths under `/api/v1/`; consistent error responses.

## Environment variables

See `.env.example` for required and optional variables. Never commit `.env`; use `.env.example` as the template.
