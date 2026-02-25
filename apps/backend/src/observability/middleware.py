"""Middleware to record request metrics for observability."""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import METRICS_ENABLED
from observability.metrics import record_request


class MetricsMiddleware(BaseHTTPMiddleware):
    """Record request count and latency per path."""

    async def dispatch(self, request: Request, call_next) -> Response:
        if not METRICS_ENABLED:
            return await call_next(request)
        start = time.perf_counter()
        response = await call_next(request)
        latency = time.perf_counter() - start
        path = request.scope.get("path", "")
        method = request.scope.get("method", "GET")
        record_request(path, method, response.status_code, latency)
        return response
