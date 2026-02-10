#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
echo "Formatting Python (Black)..."
uv run black apps/backend libs/
echo "Formatting JavaScript (Prettier)..."
(cd apps/frontend && npm exec -- prettier --write "src/**/*.{js,jsx,ts,tsx,json}" 2>/dev/null) || true
