"""
Simple in-memory metrics for request counts and latency.
Can be replaced or supplemented with OpenTelemetry/Phoenix (see PHOENIX_COLLECTOR_ENDPOINT).
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Any

_lock = Lock()
_request_count: dict[str, int] = defaultdict(int)
_request_latency_sum: dict[str, float] = defaultdict(float)
_request_latency_count: dict[str, int] = defaultdict(int)
_llm_span_count = 0
_error_count: dict[str, int] = defaultdict(int)


def record_request(path: str, method: str, status_code: int, latency_sec: float) -> None:
    key = f"{method}_{path}"
    with _lock:
        _request_count[key] += 1
        _request_latency_sum[key] += latency_sec
        _request_latency_count[key] += 1
        if status_code >= 400:
            _error_count[key] += 1


def record_llm_span(name: str, model: str | None = None, latency_sec: float | None = None) -> None:
    """Record an LLM call for observability (Arize Phoenix can consume via OTLP)."""
    global _llm_span_count
    with _lock:
        _llm_span_count += 1


def get_metrics_snapshot() -> dict[str, Any]:
    with _lock:
        requests = dict(_request_count)
        latency_sum = dict(_request_latency_sum)
        latency_count = dict(_request_latency_count)
        errors = dict(_error_count)
        llm_spans = _llm_span_count
    return {
        "request_count": requests,
        "request_latency_sum": latency_sum,
        "request_latency_count": latency_count,
        "error_count": errors,
        "llm_span_count": llm_spans,
    }


def prometheus_format() -> str:
    """Export metrics in Prometheus text exposition format."""
    snap = get_metrics_snapshot()
    lines = []
    for key, count in snap["request_count"].items():
        lines.append(f'http_requests_total{{path="{key}"}} {count}')
    for key, count in snap["request_latency_count"].items():
        total = snap["request_latency_sum"].get(key, 0)
        if count > 0:
            lines.append(f'http_request_duration_seconds_sum{{path="{key}"}} {total}')
            lines.append(f'http_request_duration_seconds_count{{path="{key}"}} {count}')
    for key, count in snap["error_count"].items():
        lines.append(f'http_errors_total{{path="{key}"}} {count}')
    lines.append(f"llm_spans_total {snap['llm_span_count']}")
    return "\n".join(lines) + "\n"
