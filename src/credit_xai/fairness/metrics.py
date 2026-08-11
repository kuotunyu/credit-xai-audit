"""Per-group descriptive metrics. This is a snapshot of model behavior on 2005
historical data — it supports no conclusions about discrimination, lending
practices, or any individual."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import roc_auc_score

from credit_xai.metrics.core import rate_metrics
from credit_xai.types import Array


def group_auc(y: Array, p: Array) -> float | None:
    if len(np.unique(y)) < 2:
        return None
    return float(roc_auc_score(y, p))


def group_snapshot(
    y: Array,
    p: Array,
    y_hat: Array,
    masks: dict[str, Array],
    small_cell_min: int,
) -> dict[str, dict[str, Any]]:
    """Point estimates per group; groups with fewer than ``small_cell_min``
    members of either class are flagged unstable (CIs suppressed downstream)."""
    y = np.asarray(y)
    p = np.asarray(p, dtype=float)
    y_hat = np.asarray(y_hat)
    out: dict[str, dict[str, Any]] = {}
    for group_id, mask in masks.items():
        y_g, p_g, y_hat_g = y[mask], p[mask], y_hat[mask]
        n = int(mask.sum())
        n_pos = int(y_g.sum())
        n_neg = n - n_pos
        record: dict[str, Any] = {
            "n": n,
            "n_positive": n_pos,
            "prevalence": float(y_g.mean()) if n else None,
            "auc": group_auc(y_g, p_g) if n else None,
            **(
                rate_metrics(y_g, y_hat_g)
                if n
                else {"selection_rate": None, "fpr": None, "fnr": None}
            ),
            "small_cell": bool(n_pos < small_cell_min or n_neg < small_cell_min),
        }
        out[group_id] = record
    return out
