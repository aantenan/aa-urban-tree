#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "Running database migrations..."
uv run --project apps/backend python -c "
# Migration runner placeholder - wire to database lib when migrations exist
print('Migrations: not yet implemented')
" 2>/dev/null || echo "Run migrations from backend when database lib is configured."
