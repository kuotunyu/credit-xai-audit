from __future__ import annotations

import numpy as np
import pytest
from sklearn.metrics import log_loss

from credit_xai.calibration.calibrate import (
    IsotonicCalibrator,
    PlattCalibrator,
    base_rate_threshold,
    fit_and_select,
)
from credit_xai.calibration.calibrate import (
    run as calibrate_run,
)
from credit_xai.metrics.core import clip_probs
from credit_xai.models.persistence import load_calibrator
from credit_xai.training.train import run as train_run
from credit_xai.utils.io import read_json
from credit_xai.utils.seeding import rng


def _miscalibrated_sample(n: int, seed_step: str):
    """True probabilities p, labels y, and overconfident reported scores p**3."""
    g = rng(99, seed_step)
    p_true = g.beta(2, 5, n)
    y = (g.random(n) < p_true).astype(int)
    p_reported = p_true**3  # systematically too low -> calibrators must fix it
    return p_reported, y


@pytest.mark.parametrize("cls", [PlattCalibrator, IsotonicCalibrator])
def test_calibrators_reduce_log_loss_out_of_sample(cls) -> None:
    p_fit, y_fit = _miscalibrated_sample(4000, "cal/fit")
    p_new, y_new = _miscalibrated_sample(4000, "cal/new")
    calibrator = cls().fit(p_fit, y_fit)
    before = log_loss(y_new, clip_probs(p_new), labels=[0, 1])
    after = log_loss(y_new, clip_probs(calibrator.predict(p_new)), labels=[0, 1])
    assert after < before
    out = calibrator.predict(p_new)
    assert np.all((out >= 0) & (out <= 1))


def test_platt_preserves_ranking() -> None:
    p_fit, y_fit = _miscalibrated_sample(2000, "cal/rank")
    calibrator = PlattCalibrator().fit(p_fit, y_fit)
    p = np.linspace(0.01, 0.99, 50)
    out = calibrator.predict(p)
    assert np.all(np.diff(out) > 0)  # strictly monotone -> AUC unchanged


def test_fit_and_select_uses_validation_log_loss_only() -> None:
    p_val, y_val = _miscalibrated_sample(3000, "cal/select")
    fitted, selection = fit_and_select(p_val, y_val, ("sigmoid", "isotonic"), ece_bins=10)
    assert set(fitted) == {"sigmoid", "isotonic"}
    per_method = selection["per_method_val"]
    winner = selection["selected_method"]
    losing = [m for m in ("sigmoid", "isotonic") if m != winner]
    assert per_method[winner]["log_loss"] <= per_method[losing[0]]["log_loss"]


def test_base_rate_threshold_matches_flag_rate() -> None:
    g = rng(7, "cal/thr")
    p = g.random(10_000)
    y = (g.random(10_000) < 0.22).astype(int)
    threshold, base_rate = base_rate_threshold(p, y)
    flag_rate = float((p >= threshold).mean())
    assert base_rate == pytest.approx(0.22, abs=0.02)
    assert flag_rate == pytest.approx(base_rate, abs=0.01)


def test_calibrate_step_end_to_end(prepared_config) -> None:
    train_run(prepared_config, "logistic")
    calibrate_run(prepared_config, "logistic")

    record = read_json(prepared_config.raw_results_dir / "logistic" / "calibration.json")
    assert record["selected_method"] in ("sigmoid", "isotonic")
    assert record["selection_split"] == "val"
    assert 0.0 < record["threshold"] < 1.0
    assert "uncalibrated" in record["per_method_val"]

    calibrator = load_calibrator(prepared_config, "logistic")
    out = calibrator.predict(np.array([0.1, 0.5, 0.9]))
    assert out.shape == (3,)
    assert np.all((out >= 0) & (out <= 1))
