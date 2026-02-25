# Monitoring and Observability (WO-17)

## Implemented

- **Health**: `GET /api/health` returns `{"status": "ok"}`. Use `?detail=true` for database and storage checks.
- **Metrics**: In-memory request counts and latency per path. Export:
  - **Prometheus**: `GET /api/observability/metrics` (text exposition format).
  - **JSON**: `GET /api/observability/metrics/json` (request_count, latency sums, error_count, llm_span_count).
- **Middleware**: `MetricsMiddleware` records each request (path, method, status_code, latency). Disable with `METRICS_ENABLED=false`.
- **LLM spans**: `observability.metrics.record_llm_span(name, model, latency_sec)` for future LLM calls; count exposed in metrics.

## Configuration

- `METRICS_ENABLED` (default: true): enable/disable metrics collection and endpoints.
- `OTEL_EXPORTER_OTLP_ENDPOINT`: optional OpenTelemetry OTLP endpoint for exporting traces.
- `PHOENIX_COLLECTOR_ENDPOINT`: optional Arize Phoenix collector URL for LLM observability.

## Arize Phoenix (optional)

To use [Arize Phoenix](https://docs.phoenix.arize.com/) for LLM observability:

1. Run Phoenix (e.g. Docker or cloud).
2. Set `PHOENIX_COLLECTOR_ENDPOINT` (or use OpenTelemetry with Phoenix as the backend).
3. Instrument LLM calls with OpenTelemetry and send spans to the collector; Phoenix will ingest them for tracing and evals.

The app exposes `record_llm_span` and metrics so you can wire OTLP export when adding LLM features.
