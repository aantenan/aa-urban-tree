#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "Linting Python (Pylint)..."
uv run pylint apps/backend libs/ --ignore=venv,.venv 2>/dev/null || true
echo "Linting JavaScript (ESLint)..."
(cd apps/frontend && npm exec -- eslint "src/**/*.{js,jsx}" 2>/dev/null) || true
