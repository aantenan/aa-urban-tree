"""Backend application entry point."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError

from config import API_V1_PREFIX, CORS_ORIGINS, DEBUG
from routes import auth, health, public
from utils.errors import error_handler, validation_exception_handler
from utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup/shutdown lifecycle."""
    setup_logging()
    logger.info("Application starting")
    try:
        from database.connection import init_db
        from database.migrations.runner import run_migrations
        init_db()
        run_migrations()
    except Exception as e:
        logger.warning("Database init skipped: %s", e)
    try:
        from core.container import init_container
        init_container()
    except Exception as e:
        logger.warning("Service container init skipped: %s", e)
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Urban Tree Grant API",
    version="0.1.0",
    description="API for urban tree grant applications",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, error_handler)

# Mount routes: /api/health and /api/v1/...
app.include_router(health.router, prefix="/api")
app.include_router(health.router, prefix=API_V1_PREFIX)
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(public.router, prefix="/api")


def main() -> None:
    """Run the server. Keeps the process running until interrupted."""
    import uvicorn
    from config import HOST, PORT
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
    )


if __name__ == "__main__":
    main()
