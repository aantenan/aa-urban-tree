"""
Performance / load testing utilities for critical endpoints.
Run a request N times and report latency percentiles (no pytest dependency).
"""
from __future__ import annotations

import statistics
import time
from typing import Any, Callable


def run_load_test(
    request_fn: Callable[[], Any],
    n: int = 100,
) -> dict[str, float]:
    """
    Execute request_fn n times and return latency stats (seconds).
    request_fn should be a callable that performs one HTTP request (e.g. client.get(url)).

    Returns dict with: min, max, mean, median, stdev, p95 (95th percentile).
    """
    times_ms: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        request_fn()
        elapsed_ms = (time.perf_counter() - start) * 1000
        times_ms.append(elapsed_ms)
    times_ms.sort()
    return {
        "min_ms": min(times_ms),
        "max_ms": max(times_ms),
        "mean_ms": statistics.mean(times_ms),
        "median_ms": statistics.median(times_ms),
        "stdev_ms": statistics.stdev(times_ms) if len(times_ms) > 1 else 0,
        "p95_ms": times_ms[int(len(times_ms) * 0.95)] if times_ms else 0,
    }


def print_load_report(stats: dict[str, float], label: str = "Request") -> None:
    """Print a one-line summary of run_load_test results."""
    print(
        f"{label}: n=100 | min={stats['min_ms']:.0f}ms mean={stats['mean_ms']:.0f}ms "
        f"p95={stats['p95_ms']:.0f}ms max={stats['max_ms']:.0f}ms"
    )
