#!/usr/bin/env python3
"""
Run migrations and seed the database (without starting the server).
Usage from apps/backend:
  uv run python scripts/seed_db.py
  PYTHONPATH=src uv run python scripts/seed_db.py
"""
import os
import sys

# Ensure src is on path when run from apps/backend
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(backend_dir, "src")
if src not in sys.path:
    sys.path.insert(0, src)

os.chdir(src)


def main() -> None:
    import config  # noqa: F401 - load .env (DATABASE_URL, etc.) before DB access
    from database.connection import init_db
    from database.migrations.runner import run_migrations
    from utils.seed_counties import seed_counties
    from utils.seed_project_options import seed_project_options
    from utils.seed_budget_categories import seed_budget_categories
    from utils.seed_users import seed_users

    print("Initializing database...")
    init_db()
    print("Running migrations...")
    run_migrations()
    print("Seeding counties...")
    seed_counties()
    print("Seeding project options...")
    seed_project_options()
    print("Seeding budget categories...")
    seed_budget_categories()
    print("Seeding users...")
    seed_users()
    print("Done.")


if __name__ == "__main__":
    main()
