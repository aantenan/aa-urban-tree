#!/usr/bin/env bash
# Validate and deploy program data updates; optionally trigger cache invalidation.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

PROGRAM_DATA="${PROGRAM_DATA_PATH:-config/program_data.json}"
RESOURCES_DATA="${STATIC_RESOURCES_PATH:-config/static_resources.json}"

echo "Validating program data..."
for f in "$PROGRAM_DATA" "$RESOURCES_DATA"; do
  if [[ -f "$f" ]]; then
    if ! python3 -c "import json; json.load(open('$f'))"; then
      echo "Invalid JSON: $f" >&2
      exit 1
    fi
    echo "  OK $f"
  else
    echo "  Skip (not found): $f"
  fi
done

echo "Program data validation passed."
echo "To refresh cached config: restart the backend, or call the cache invalidation endpoint if implemented."
