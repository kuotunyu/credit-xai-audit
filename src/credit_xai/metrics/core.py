"""Point metrics: ROC-AUC, PR-AUC, log loss, Brier, ECE (equal-frequency bins).

ECE uses quantile (equal-frequency) binning: with ~22% positives most predicted
probabilities sit low, and equal-width bins would leave many near-empty, noisy
bins. Bin edges are returned so plots and numbers are regenerable.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score

from credit_xai.types import Array

PROB_EPS = 1e-6


def clip_probs(p: Array) -> Array:
    return np.clip(np.asarray(p, dtype=float), PROB_EPS, 1 - PROB_EPS)


def ece_quantile(y: Array, p: Array, n_bins: int) -> tuple[float, dict[str, Any]]:
    """Expected calibration error with equal-frequency bins.

    ECE = sum_b (n_b / N) * | mean(p in b) - mean(y in b) |
    """
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    if len(y) != len(p) or len(y) == 0:
        raise ValueError("y and p must be equal-length, non-empty arrays")
    quantiles = np.linspace(0, 1, n_bins + 1)
    edges = np.unique(np.quantile(p, quantiles))
    if len(edges) < 2:  # all predictions identical
        edges = np.array([p.min() - PROB_EPS, p.max() + PROB_EPS])
    # assign each prediction to a bin; rightmost edge inclusive
    bin_ids = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    total = len(p)
    ece = 0.0
    bins: list[dict[str, float]] = []
    for b in range(len(edges) - 1):
        mask = bin_ids == b
        n_b = int(mask.sum())
        if n_b == 0:
            continue
        conf = float(p[mask].mean())
        acc = float(y[mask].mean())
        ece += (n_b / total) * abs(conf - acc)
        bins.append({"bin": b, "n": n_b, "mean_predicted": conf, "observed_rate": acc})
    detail = {"n_bins_requested": n_bins, "edges": edges.tolist(), "bins": bins}
    return float(ece), detail


def point_metrics(y: Array, p: Array, ece_bins: int) -> dict[str, float]:
    """The five probability-quality metrics on one (y, p) pair."""
    y = np.asarray(y)
    p = np.asarray(p, dtype=float)
    if len(np.unique(y)) < 2:
        raise ValueError("point_metrics requires both classes present")
    ece, _ = ece_quantile(y, p, ece_bins)
    return {
        "roc_auc": float(roc_auc_score(y, p)),
        "pr_auc": float(average_precision_score(y, p)),
        "log_loss": float(log_loss(y, clip_probs(p), labels=[0, 1])),
        "brier": float(brier_score_loss(y, p)),
        "ece": ece,
    }


def rate_metrics(y: Array, y_hat: Array) -> dict[str, float | None]:
    """Threshold-based rates. FPR/FNR are None when undefined for a slice."""
    y = np.asarray(y).astype(bool)
    y_hat = np.asarray(y_hat).astype(bool)
    negatives = int((~y).sum())
    positives = int(y.sum())
    fpr = float((y_hat & ~y).sum() / negatives) if negatives else None
    fnr = float((~y_hat & y).sum() / positives) if positives else None
    return {
        "selection_rate": float(y_hat.mean()) if len(y_hat) else None,
        "fpr": fpr,
        "fnr": fnr,
    }
