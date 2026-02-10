"""Environment-based configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root or apps/backend
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
_backend_dir = Path(__file__).resolve().parent.parent
for _p in (_repo_root / ".env", _backend_dir / ".env"):
    if _p.exists():
        load_dotenv(_p)
        break

# Server
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# API
API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
CORS_ORIGINS: list[str] = [
    o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()
]

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
