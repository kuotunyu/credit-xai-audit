from __future__ import annotations

import numpy as np
import pytest

from credit_xai.metrics.core import clip_probs, ece_quantile, point_metrics, rate_metrics


def test_ece_zero_when_perfectly_calibrated() -> None:
    y = np.array([0, 0, 0, 1])
    p = np.array([0.25, 0.25, 0.25, 0.25])
    ece, detail = ece_quantile(y, p, n_bins=5)
    assert ece == pytest.approx(0.0)
    assert detail["bins"][0]["n"] == 4


def test_ece_hand_computed_two_bins() -> None:
    # bin A: 5 preds at 0.2, observed rate 0.2 -> contributes 0
    # bin B: 5 preds at 0.8, observed rate 0.6 -> contributes 0.5 * 0.2 = 0.1
    p = np.array([0.2] * 5 + [0.8] * 5)
    y = np.array([1, 0, 0, 0, 0, 1, 1, 1, 0, 0])
    ece, _ = ece_quantile(y, p, n_bins=2)
    assert ece == pytest.approx(0.1)


def test_point_metrics_perfect_separation() -> None:
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.15, 0.9, 0.85, 0.95])
    m = point_metrics(y, p, ece_bins=3)
    assert m["roc_auc"] == pytest.approx(1.0)
    assert m["pr_auc"] == pytest.approx(1.0)
    assert m["brier"] < 0.03
    assert m["log_loss"] < 0.2


def test_log_loss_survives_hard_zero_one() -> None:
    y = np.array([0, 1])
    p = np.array([0.0, 1.0])
    m = point_metrics(y, p, ece_bins=2)
    assert np.isfinite(m["log_loss"])
    assert m["brier"] == pytest.approx(0.0)


def test_clip_probs_bounds() -> None:
    out = clip_probs(np.array([-0.1, 0.0, 0.5, 1.0, 1.1]))
    assert out.min() > 0 and out.max() < 1
    assert out[2] == pytest.approx(0.5)


def test_rate_metrics_confusion() -> None:
    y = np.array([0, 0, 1, 1])
    y_hat = np.array([1, 0, 1, 0])
    r = rate_metrics(y, y_hat)
    assert r["fpr"] == pytest.approx(0.5)
    assert r["fnr"] == pytest.approx(0.5)
    assert r["selection_rate"] == pytest.approx(0.5)


def test_rate_metrics_degenerate_slice() -> None:
    r = rate_metrics(np.array([0, 0]), np.array([1, 0]))
    assert r["fnr"] is None
    assert r["fpr"] == pytest.approx(0.5)


def test_point_metrics_rejects_single_class() -> None:
    with pytest.raises(ValueError, match="both classes"):
        point_metrics(np.array([1, 1]), np.array([0.5, 0.6]), ece_bins=2)
