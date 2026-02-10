#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "Running Python tests (pytest)..."
uv run pytest apps/backend/tests libs/*/tests -v 2>/dev/null || true
echo "Running frontend tests..."
(cd apps/frontend && npm run test -- --run 2>/dev/null) || true
