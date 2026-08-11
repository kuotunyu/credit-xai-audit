"""The `train` step: fit one model on the train split, report validation point
metrics, and persist the bundle."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

from credit_xai.config import Config
from credit_xai.constants import FEATURES, TARGET
from credit_xai.data.prepare import load_processed
from credit_xai.metrics.core import point_metrics
from credit_xai.models.persistence import save_aux_parquet, save_model
from credit_xai.models.registry import get_adapter
from credit_xai.utils.io import atomic_write_json, ensure_dir
from credit_xai.utils.sampling import stratified_sample
from credit_xai.utils.seeding import rng

logger = logging.getLogger(__name__)


def run(cfg: Config, model_name: str) -> None:
    adapter = get_adapter(model_name, cfg)
    splits = load_processed(cfg)
    X_train, y_train = splits["train"][FEATURES], splits["train"][TARGET]
    X_val, y_val = splits["val"][FEATURES], splits["val"][TARGET]

    estimator = adapter.build(cfg)
    logger.info("fitting %s (%s) on %d rows", model_name, type(estimator).__name__, len(X_train))
    started = time.perf_counter()
    fitted = adapter.fit(estimator, X_train, y_train, X_val, y_val)
    fit_seconds = time.perf_counter() - started

    p_val = adapter.predict_proba(fitted, X_val)
    val_metrics = point_metrics(y_val.to_numpy(), p_val, cfg.evaluation.ece_bins)
    logger.info(
        "%s validation metrics (uncalibrated): %s",
        model_name,
        {k: round(v, 4) for k, v in val_metrics.items()},
    )

    save_model(cfg, adapter, fitted, extra={"fit_seconds": fit_seconds})

    # Background sample stored with the bundle so serving/explanation never
    # needs the raw dataset. Same derivation as the explain step -> same rows.
    g_bg = rng(cfg.run.seed, "explain/background")
    bg_pos = stratified_sample(y_train.to_numpy(), cfg.explain.shap.background_size, g_bg)
    save_aux_parquet(
        cfg, model_name, "background.parquet", X_train.iloc[bg_pos].reset_index(drop=True)
    )

    out_dir = ensure_dir(cfg.raw_results_dir / model_name)
    atomic_write_json(
        out_dir / "train_meta.json",
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "config_hash": cfg.config_hash,
            "run_name": cfg.run.name,
            "model_name": model_name,
            "estimator_class": adapter.estimator_class(fitted),
            "is_fallback": adapter.is_fallback,
            "params": cfg.models.model_dump()[model_name],
            "n_train_rows": int(len(X_train)),
            "fit_seconds": fit_seconds,
            "val_point_metrics_uncalibrated": val_metrics,
        },
    )
    logger.info("train complete for %s (%.1fs)", model_name, fit_seconds)
