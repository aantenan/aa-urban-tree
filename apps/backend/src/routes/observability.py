"""Observability: metrics (Prometheus) and optional health detail."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from config import METRICS_ENABLED
from observability.metrics import get_metrics_snapshot, prometheus_format

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/metrics")
def metrics_prometheus():
    """Prometheus text exposition format. Scrape this endpoint for monitoring."""
    if not METRICS_ENABLED:
        return PlainTextResponse(content="# Metrics disabled\n", status_code=404)
    return PlainTextResponse(
        content=prometheus_format(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get("/metrics/json")
def metrics_json():
    """JSON snapshot of request counts, latency sums, and LLM span count."""
    if not METRICS_ENABLED:
        return {"enabled": False}
    return get_metrics_snapshot()
