"""Timing helper for latency measurement (protocol lives in metrics.latency)."""

from __future__ import annotations

import time
from collections.abc import Callable


def timed_calls(fn: Callable[[], object], n_warmup: int, n_repeats: int) -> list[float]:
    """Run ``fn`` n_warmup untimed times, then n_repeats timed; returns seconds per call."""
    for _ in range(n_warmup):
        fn()
    durations: list[float] = []
    for _ in range(n_repeats):
        start = time.perf_counter()
        fn()
        durations.append(time.perf_counter() - start)
    return durations
