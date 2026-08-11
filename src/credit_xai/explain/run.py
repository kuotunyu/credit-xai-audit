"""The `explain` step orchestrator: reference attributions, global importance,
EBM shapes, fixed local cases, stability loops, and the faithfulness test."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import FEATURES, TARGET
from credit_xai.data.prepare import CLEANED_PARQUET, load_local_cases, load_processed
from credit_xai.explain.ebm_shapes import export_shapes
from credit_xai.explain.explainers import build_attributor, global_importance, top_k_features
from credit_xai.explain.faithfulness import run_faithfulness
from credit_xai.explain.stability import run_stability
from credit_xai.models.persistence import PersistenceError, load_calibrator, load_model
from credit_xai.models.registry import get_adapter
from credit_xai.types import Array
from credit_xai.utils.io import atomic_write_json, ensure_dir
from credit_xai.utils.sampling import stratified_sample
from credit_xai.utils.seeding import rng

logger = logging.getLogger(__name__)

STEP_BACKGROUND = "explain/background"  # shared across models: same rows everywhere
STEP_SAMPLE = "explain/sample"


def run(cfg: Config, model_name: str, resume: bool = False, force: bool = False) -> None:
    adapter = get_adapter(model_name, cfg)
    estimator = load_model(cfg, model_name)
    splits = load_processed(cfg)
    train, val, test = splits["train"], splits["val"], splits["test"]
    out_dir = ensure_dir(cfg.raw_results_dir / model_name / "explain")

    # -- shared, deterministic samples (same rows for every model) ------------
    g_bg = rng(cfg.run.seed, STEP_BACKGROUND)
    bg_pos = stratified_sample(train[TARGET].to_numpy(), cfg.explain.shap.background_size, g_bg)
    background = train.iloc[bg_pos][FEATURES].reset_index(drop=True)

    g_sample = rng(cfg.run.seed, STEP_SAMPLE)
    n_sample = min(cfg.explain.shap.test_sample_size, len(test))
    explain_pos = np.sort(g_sample.choice(len(test), size=n_sample, replace=False))
    X_explain = test.iloc[explain_pos][FEATURES].reset_index(drop=True)

    # -- reference attributions + global importance ---------------------------
    attributor = build_attributor(adapter, estimator, background)
    matrix = attributor.attributions(X_explain)
    sample_frame = pd.DataFrame(matrix, columns=FEATURES)
    sample_frame.insert(0, "test_row_position", explain_pos)
    sample_frame.to_parquet(out_dir / "attributions_test_sample.parquet", index=False)

    importance = global_importance(matrix)
    top_k = top_k_features(importance, cfg.explain.top_k)
    atomic_write_json(
        out_dir / "global_importance.json",
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "config_hash": cfg.config_hash,
            "model_name": model_name,
            "method": attributor.method,
            "method_detail": attributor.detail,
            "base_value_link_scale": attributor.base_value,
            "definition": "mean |attribution| per feature over the explained test sample",
            "n_explained": int(n_sample),
            "background_train_positions": bg_pos.tolist(),
            "explained_test_positions": explain_pos.tolist(),
            "importance": importance,
            "top_k": top_k,
        },
    )
    logger.info("%s global top-%d: %s", model_name, cfg.explain.top_k, top_k)

    # -- EBM shape functions --------------------------------------------------
    if adapter.explainer_kind == "ebm_native":
        shapes = export_shapes(estimator)
        shapes["generated_at"] = datetime.now(UTC).isoformat()
        shapes["config_hash"] = cfg.config_hash
        atomic_write_json(out_dir / "ebm_shapes.json", shapes)

    # -- fixed local cases (model-independent, from the validation split) -----
    cases = load_local_cases(cfg)
    case_positions = sorted(int(i) for values in cases["indices_by_class"].values() for i in values)
    cleaned = pd.read_parquet(cfg.data.processed_dir / CLEANED_PARQUET)
    case_rows = cleaned.iloc[case_positions]
    X_cases = case_rows[FEATURES].reset_index(drop=True)
    case_matrix = attributor.attributions(X_cases)
    p_unc = adapter.predict_proba(estimator, X_cases)
    p_cal: Array | None = None
    try:
        calibrator = load_calibrator(cfg, model_name)
        p_cal = calibrator.predict(p_unc)
    except PersistenceError:
        logger.info(
            "no calibrator yet for %s; local cases carry uncalibrated probs only", model_name
        )
    local_records: list[dict[str, Any]] = []
    for j, position in enumerate(case_positions):
        record: dict[str, Any] = {
            "canonical_position": position,
            "split": cases["split"],
            "label": int(case_rows.iloc[j][TARGET]),
            "features": {f: int(case_rows.iloc[j][f]) for f in FEATURES},
            "prob_uncalibrated": float(p_unc[j]),
            "attributions_link_scale": {
                f: float(case_matrix[j, i]) for i, f in enumerate(FEATURES)
            },
        }
        if p_cal is not None:
            record["prob_calibrated"] = float(p_cal[j])
        local_records.append(record)
    atomic_write_json(
        out_dir / "local_cases.json",
        {
            "generated_at": datetime.now(UTC).isoformat(),
            "config_hash": cfg.config_hash,
            "model_name": model_name,
            "method": attributor.method,
            "base_value_link_scale": attributor.base_value,
            "selection_rule": cases["selection_rule"],
            "cases": local_records,
        },
    )

    # -- stability (refits + explanation resamples, checkpointed) -------------
    run_stability(
        cfg=cfg,
        adapter=adapter,
        train=train,
        val=val,
        X_explain=X_explain,
        background=background,
        reference_importance=importance,
        reference_matrix=matrix,
        local_case_rows=X_cases,
        out_dir=out_dir,
        resume=resume,
        force=force,
    )

    # -- faithfulness perturbation (checkpointed) -----------------------------
    run_faithfulness(
        cfg=cfg,
        adapter=adapter,
        estimator=estimator,
        X_explain=X_explain,
        attribution_matrix=matrix,
        X_val=val[FEATURES].reset_index(drop=True),
        out_dir=out_dir,
        resume=resume,
        force=force,
    )
    logger.info("explain complete for %s", model_name)
