FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml ./
COPY apps/backend/pyproject.toml apps/backend/
COPY libs/ libs/

RUN uv sync --project apps/backend --no-dev

COPY apps/backend/ apps/backend/

WORKDIR /app/apps/backend
ENV PYTHONPATH=/app/apps/backend/src
CMD ["uv", "run", "--project", "/app/apps/backend", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
