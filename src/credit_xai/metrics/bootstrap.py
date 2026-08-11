"""Checkpointed, deterministic bootstrap engine.

- Stratified resampling: draw with replacement *within each class*, preserving
  class counts, so no replicate is ever single-class (documented trade-off: this
  conditions on the observed prevalence).
- Every iteration derives its own RNG from (seed, step_name, iteration), so a
  resumed run produces byte-identical results to an uninterrupted one, and the
  same replicate index uses the same resample across models (paired bootstrap).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from credit_xai.utils.checkpoints import JsonlCheckpoint

logger = logging.getLogger(__name__)


def stratified_indices(y: np.ndarray, g: np.random.Generator) -> np.ndarray:
    """Within-class resample with replacement, preserving class counts."""
    y = np.asarray(y)
    parts = []
    for label in np.unique(y):
        pos = np.flatnonzero(y == label)
        parts.append(g.choice(pos, size=len(pos), replace=True))
    return np.concatenate(parts)


def run_checkpointed_bootstrap(
    *,
    directory: str | Path,
    name: str,
    n_iterations: int,
    checkpoint_every: int,
    config_hash: str,
    compute_fn: Callable[[int], dict[str, Any]],
    resume: bool = False,
    force: bool = False,
) -> list[dict[str, Any]]:
    """Run ``compute_fn(i)`` for every missing iteration, appending each result
    to a JSONL checkpoint; returns the complete record list."""
    store = JsonlCheckpoint(directory, name, n_iterations, config_hash)
    done = store.begin(resume=resume, force=force)
    try:
        if len(done) < n_iterations:
            for i in range(n_iterations):
                if i in done:
                    continue
                store.append({"iter": i, **compute_fn(i)})
                if (i + 1) % checkpoint_every == 0:
                    store.sync()
        if not store.is_complete():
            store.finish()
    finally:
        store.close()
    records = store.records()
    logger.info("%s: %d bootstrap iterations complete", name, len(records))
    return records


def percentile_ci(values: np.ndarray, ci_level: float) -> tuple[float, float]:
    alpha = (1.0 - ci_level) / 2.0
    low, high = np.percentile(np.asarray(values, dtype=float), [alpha * 100, (1 - alpha) * 100])
    return float(low), float(high)


def summarize_records(
    records: list[dict[str, Any]], keys: list[str], ci_level: float
) -> dict[str, dict[str, float | int | None]]:
    """Mean + percentile CI per key; None-valued entries are skipped and counted."""
    out: dict[str, dict[str, float | int | None]] = {}
    for key in keys:
        values = [r[key] for r in records if r.get(key) is not None]
        if not values:
            out[key] = {"mean": None, "ci_low": None, "ci_high": None, "n_boot": 0}
            continue
        arr = np.asarray(values, dtype=float)
        low, high = percentile_ci(arr, ci_level)
        out[key] = {
            "mean": float(arr.mean()),
            "ci_low": low,
            "ci_high": high,
            "n_boot": int(len(arr)),
        }
    return out
