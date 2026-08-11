"""The `evaluate` step: TEST-set metrics with bootstrap CIs, latency, and the
group snapshot. Reads only frozen decisions (calibration method + threshold)
made on validation — nothing here can influence any selection."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import (
    FEATURES,
    TARGET,
    step_eval_bootstrap,
    step_group_bootstrap,
)
from credit_xai.data.prepare import load_processed
from credit_xai.fairness.groups import group_masks
from credit_xai.fairness.metrics import group_auc, group_snapshot
from credit_xai.metrics.bootstrap import run_checkpointed_bootstrap, stratified_indices
from credit_xai.metrics.core import ece_quantile, point_metrics, rate_metrics
from credit_xai.metrics.latency import measure_latency
from credit_xai.models.persistence import load_calibrator, load_model
from credit_xai.models.registry import get_adapter
from credit_xai.types import Array
from credit_xai.utils.io import atomic_write_json, ensure_dir, read_json
from credit_xai.utils.seeding import rng

logger = logging.getLogger(__name__)


def run(cfg: Config, model_name: str, resume: bool = False, force: bool = False) -> None:
    adapter = get_adapter(model_name, cfg)
    estimator = load_model(cfg, model_name)
    calibrator = load_calibrator(cfg, model_name)
    calibration_record = read_json(cfg.raw_results_dir / model_name / "calibration.json")
    threshold = float(calibration_record["threshold"])

    splits = load_processed(cfg)
    X_test = splits["test"][FEATURES]
    y_test = splits["test"][TARGET].to_numpy()

    p_unc = adapter.predict_proba(estimator, X_test)
    p_cal = np.asarray(calibrator.predict(p_unc), dtype=float)
    y_hat = p_cal >= threshold

    eval_dir = ensure_dir(cfg.raw_results_dir / model_name / "eval")
    ece_bins = cfg.evaluation.ece_bins

    # -- test predictions (raw artifact: ROC/PR/reliability figures derive
    #    from this file, never from re-running the model) ----------------------
    pd.DataFrame(
        {
            "test_row_position": np.arange(len(y_test)),
            "y": y_test,
            "p_uncalibrated": p_unc,
            "p_calibrated": p_cal,
        }
    ).to_parquet(eval_dir / "predictions.parquet", index=False)

    # -- point metrics + reliability bins -------------------------------------
    ece_cal, reliability = ece_quantile(y_test, p_cal, ece_bins)
    point = {
        "generated_at": datetime.now(UTC).isoformat(),
        "config_hash": cfg.config_hash,
        "run_name": cfg.run.name,
        "model_name": model_name,
        "n_test_rows": int(len(y_test)),
        "calibration_method": calibration_record["selected_method"],
        "threshold": threshold,
        "uncalibrated": point_metrics(y_test, p_unc, ece_bins),
        "calibrated": point_metrics(y_test, p_cal, ece_bins),
        "rates_at_threshold": rate_metrics(y_test, y_hat),
    }
    atomic_write_json(eval_dir / "reliability_bins.json", reliability)

    # -- latency (full serving path: model + calibrator) ----------------------
    def _predict(frame: pd.DataFrame) -> Array:
        return np.asarray(calibrator.predict(adapter.predict_proba(estimator, frame)), dtype=float)

    point["latency"] = measure_latency(_predict, X_test, cfg.evaluation.latency, cfg.run.seed)
    atomic_write_json(eval_dir / "point_metrics.json", point)
    logger.info(
        "%s test point metrics (calibrated): %s",
        model_name,
        {k: round(v, 4) for k, v in point["calibrated"].items()},
    )

    # -- metric bootstrap (uncalibrated + calibrated + rates per iteration) ---
    boot_cfg = cfg.evaluation.bootstrap
    step_name = step_eval_bootstrap(model_name)

    def metric_iteration(i: int) -> dict[str, Any]:
        g = rng(cfg.run.seed, step_name, i)
        idx = stratified_indices(y_test, g)
        y_b, unc_b, cal_b = y_test[idx], p_unc[idx], p_cal[idx]
        record: dict[str, Any] = {}
        for prefix, p_b in (("unc", unc_b), ("cal", cal_b)):
            for key, value in point_metrics(y_b, p_b, ece_bins).items():
                record[f"{prefix}_{key}"] = value
        for key, rate_value in rate_metrics(y_b, cal_b >= threshold).items():
            record[f"cal_{key}"] = rate_value
        return record

    run_checkpointed_bootstrap(
        directory=eval_dir,
        name="bootstrap_metrics",
        n_iterations=boot_cfg.n_iterations,
        checkpoint_every=boot_cfg.checkpoint_every,
        config_hash=cfg.config_hash,
        compute_fn=metric_iteration,
        resume=resume,
        force=force,
    )

    # -- group snapshot (calibrated probabilities, frozen threshold) ----------
    masks = group_masks(splits["test"], cfg)
    snapshot = group_snapshot(y_test, p_cal, y_hat, masks, cfg.fairness.small_cell_min)
    atomic_write_json(
        eval_dir / "group_metrics.json",
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "config_hash": cfg.config_hash,
            "model_name": model_name,
            "threshold": threshold,
            "note": (
                "Descriptive snapshot of model behavior on 2005 historical data. "
                "Not evidence of discrimination; supports no conclusions about "
                "individuals or lending practices."
            ),
            "groups": snapshot,
        },
    )

    group_step = step_group_bootstrap(model_name)
    group_ids = list(masks)

    def group_iteration(i: int) -> dict[str, Any]:
        g = rng(cfg.run.seed, group_step, i)
        record: dict[str, Any] = {}
        for group_id in group_ids:
            mask = masks[group_id]
            y_g, p_g = y_test[mask], p_cal[mask]
            if len(np.unique(y_g)) < 2:
                record[group_id] = {"auc": None, "fpr": None, "fnr": None, "selection_rate": None}
                continue
            idx = stratified_indices(y_g, g)
            y_b, p_b = y_g[idx], p_g[idx]
            record[group_id] = {
                "auc": group_auc(y_b, p_b),
                **rate_metrics(y_b, p_b >= threshold),
            }
        return record

    run_checkpointed_bootstrap(
        directory=eval_dir,
        name="group_bootstrap",
        n_iterations=boot_cfg.n_iterations,
        checkpoint_every=boot_cfg.checkpoint_every,
        config_hash=cfg.config_hash,
        compute_fn=group_iteration,
        resume=resume,
        force=force,
    )
    logger.info("evaluate complete for %s", model_name)
