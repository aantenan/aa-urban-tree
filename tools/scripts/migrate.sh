#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "Running database migrations..."
uv run --project apps/backend python -c "
from database.connection import init_db
from database.migrations.runner import run_migrations
init_db()
run_migrations()
print('Migrations complete.')
" 2>/dev/null || echo "Ensure uv sync and DATABASE_URL is set."
