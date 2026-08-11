"""Probability calibration, selected on the VALIDATION split only.

Hand-rolled calibrators (instead of ``CalibratedClassifierCV``) sidestep
sklearn's prefit/refit semantics entirely and work identically for all three
model families. Platt = unregularized logistic fit on logit(p); isotonic =
``IsotonicRegression`` with clipping. The winner is chosen by validation log
loss (a proper scoring rule; ECE is reported for context but never used for
selection). The frozen decision — method + threshold — is written to
``calibration.json``; the evaluate step only ever reads that frozen record, so
no code path exists from test data to any selection.

Threshold policy (predeclared): t* = Quantile_{1-r}(calibrated validation
probabilities), where r is the validation base default rate — i.e. the
threshold at which the validation flag rate equals the observed base rate.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Protocol

import numpy as np
from scipy.special import logit
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from credit_xai.config import Config
from credit_xai.constants import FEATURES, TARGET
from credit_xai.data.prepare import load_processed
from credit_xai.metrics.core import clip_probs, point_metrics
from credit_xai.models.persistence import load_model, save_calibrator
from credit_xai.models.registry import get_adapter
from credit_xai.types import Array
from credit_xai.utils.io import atomic_write_json, ensure_dir

logger = logging.getLogger(__name__)


class Calibrator(Protocol):
    method: str

    def fit(self, p: Array, y: Array) -> Calibrator: ...

    def predict(self, p: Array) -> Array: ...


class IdentityCalibrator:
    method = "none"

    def fit(self, p: Array, y: Array) -> IdentityCalibrator:
        return self

    def predict(self, p: Array) -> Array:
        return np.asarray(p, dtype=float)


class PlattCalibrator:
    """Sigmoid recalibration: a*logit(p) + b via unregularized logistic regression."""

    method = "sigmoid"

    def __init__(self) -> None:
        self._lr = LogisticRegression(C=1e10, solver="lbfgs", max_iter=1000)

    def fit(self, p: Array, y: Array) -> PlattCalibrator:
        z = logit(clip_probs(p)).reshape(-1, 1)
        self._lr.fit(z, np.asarray(y))
        return self

    def predict(self, p: Array) -> Array:
        z = logit(clip_probs(p)).reshape(-1, 1)
        return np.asarray(self._lr.predict_proba(z)[:, 1], dtype=float)


class IsotonicCalibrator:
    method = "isotonic"

    def __init__(self) -> None:
        self._iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")

    def fit(self, p: Array, y: Array) -> IsotonicCalibrator:
        self._iso.fit(np.asarray(p, dtype=float), np.asarray(y, dtype=float))
        return self

    def predict(self, p: Array) -> Array:
        return np.asarray(self._iso.predict(np.asarray(p, dtype=float)), dtype=float)


_CALIBRATORS: dict[str, type] = {
    "sigmoid": PlattCalibrator,
    "isotonic": IsotonicCalibrator,
}


def fit_and_select(
    p_val: Array, y_val: Array, methods: tuple[str, ...], ece_bins: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Fit each requested method on validation arrays; select by val log loss.

    Returns (fitted calibrators by method, per-method validation metrics with
    the selected method marked). This function never sees test data.
    """
    fitted: dict[str, Any] = {}
    val_metrics: dict[str, Any] = {
        "uncalibrated": point_metrics(y_val, p_val, ece_bins),
    }
    for method in methods:
        calibrator = _CALIBRATORS[method]().fit(p_val, y_val)
        fitted[method] = calibrator
        val_metrics[method] = point_metrics(y_val, calibrator.predict(p_val), ece_bins)
    selected = min(methods, key=lambda m: val_metrics[m]["log_loss"])
    return fitted, {"per_method_val": val_metrics, "selected_method": selected}


def base_rate_threshold(p_cal_val: Array, y_val: Array) -> tuple[float, float]:
    """Threshold at which the validation flag rate equals the validation base rate."""
    base_rate = float(np.asarray(y_val).mean())
    threshold = float(np.quantile(np.asarray(p_cal_val, dtype=float), 1.0 - base_rate))
    return threshold, base_rate


def run(cfg: Config, model_name: str) -> None:
    adapter = get_adapter(model_name, cfg)
    estimator = load_model(cfg, model_name)
    splits = load_processed(cfg)
    X_val, y_val = splits["val"][FEATURES], splits["val"][TARGET].to_numpy()

    p_val = adapter.predict_proba(estimator, X_val)
    fitted, selection = fit_and_select(
        p_val, y_val, cfg.calibration.methods, cfg.evaluation.ece_bins
    )
    selected = selection["selected_method"]
    winner = fitted[selected]

    threshold, base_rate = base_rate_threshold(winner.predict(p_val), y_val)
    save_calibrator(cfg, model_name, winner)

    out_dir = ensure_dir(cfg.raw_results_dir / model_name)
    record = {
        "generated_at": datetime.now(UTC).isoformat(),
        "config_hash": cfg.config_hash,
        "run_name": cfg.run.name,
        "model_name": model_name,
        "methods": list(cfg.calibration.methods),
        "selection_metric": cfg.calibration.selection_metric,
        "selection_split": "val",
        **selection,
        "threshold_policy": (
            "quantile of calibrated validation probabilities at (1 - validation base rate); "
            "frozen before any test evaluation"
        ),
        "threshold": threshold,
        "val_base_rate": base_rate,
    }
    atomic_write_json(out_dir / "calibration.json", record)
    logger.info(
        "%s calibration: selected=%s (val log_loss %s), threshold=%.4f",
        model_name,
        selected,
        {m: round(selection["per_method_val"][m]["log_loss"], 4) for m in cfg.calibration.methods},
        threshold,
    )
