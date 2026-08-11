"""CPU latency measurement: batch and per-row, warmup + repeats.

Latency gets no bootstrap CI — the repeats give spread directly. Environment
(CPU, thread settings) is recorded alongside the numbers.
"""

from __future__ import annotations

import os
import platform
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.config import LatencyConfig
from credit_xai.utils.seeding import rng
from credit_xai.utils.timing import timed_calls

STEP_LATENCY = "eval/latency"


def measure_latency(
    predict_fn: Callable[[pd.DataFrame], np.ndarray],
    X: pd.DataFrame,
    settings: LatencyConfig,
    global_seed: int,
) -> dict[str, Any]:
    # Batch: full-frame predict, reported per 1,000 rows.
    batch_secs = timed_calls(lambda: predict_fn(X), settings.n_warmup, settings.n_repeats)
    per_1k = [s / len(X) * 1000 * 1000 for s in batch_secs]  # ms per 1000 rows

    # Per-row: fixed sample of single-row frames, one loop per repeat.
    g = rng(global_seed, STEP_LATENCY)
    n_rows = min(settings.per_row_samples, len(X))
    row_ids = g.choice(len(X), size=n_rows, replace=False)
    single_rows = [X.iloc[[int(i)]] for i in row_ids]

    def _loop() -> None:
        for row in single_rows:
            predict_fn(row)

    loop_secs = timed_calls(_loop, min(settings.n_warmup, 1), settings.n_repeats)
    per_row_ms = [s / n_rows * 1000 for s in loop_secs]

    return {
        "batch_ms_per_1k_rows": {
            "median": float(np.median(per_1k)),
            "min": float(np.min(per_1k)),
            "max": float(np.max(per_1k)),
            "n_repeats": settings.n_repeats,
            "batch_rows": int(len(X)),
        },
        "per_row_ms": {
            "median": float(np.median(per_row_ms)),
            "min": float(np.min(per_row_ms)),
            "max": float(np.max(per_row_ms)),
            "n_repeats": settings.n_repeats,
            "sampled_rows": n_rows,
        },
        "environment": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        },
    }
