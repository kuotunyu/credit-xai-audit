"""Explanation stability: bootstrap top-k rank stability + fixed-case local
attribution stability, in one checkpointed loop.

Two iteration kinds, both recorded per line:
- ``refit``: refit the model on a stratified bootstrap resample of TRAIN, then
  recompute global importance on the fixed explain sample (measures pipeline
  stability — honest but expensive). Each refit record also carries the fixed
  local cases' attributions, so local stability reuses the same refits.
- ``resample``: keep the reference model, bootstrap-resample the explain-sample
  rows of the reference attribution matrix (cheap; measures estimator noise
  only). The two kinds are aggregated separately downstream.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

from credit_xai.config import Config
from credit_xai.constants import FEATURES, TARGET, step_rank_stability
from credit_xai.explain.explainers import build_attributor, global_importance, top_k_features
from credit_xai.metrics.bootstrap import run_checkpointed_bootstrap, stratified_indices
from credit_xai.models.base import ModelAdapter
from credit_xai.utils.seeding import rng

logger = logging.getLogger(__name__)


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb)


def run_stability(
    *,
    cfg: Config,
    adapter: ModelAdapter,
    train: pd.DataFrame,
    val: pd.DataFrame,
    X_explain: pd.DataFrame,
    background: pd.DataFrame,
    reference_importance: dict[str, float],
    reference_matrix: np.ndarray,
    local_case_rows: pd.DataFrame,
    out_dir: Any,
    resume: bool,
    force: bool,
) -> list[dict[str, Any]]:
    st_cfg = cfg.explain.rank_stability
    n_total = st_cfg.n_refits + st_cfg.n_resamples
    step_name = step_rank_stability(adapter.name)
    k = cfg.explain.top_k
    ref_topk = top_k_features(reference_importance, k)
    ref_values = np.array([reference_importance[f] for f in FEATURES])

    X_train, y_train = train[FEATURES], train[TARGET]

    def iteration(i: int) -> dict[str, Any]:
        g = rng(cfg.run.seed, step_name, i)
        if i < st_cfg.n_refits:
            idx = stratified_indices(y_train.to_numpy(), g)
            boot_X = X_train.iloc[idx].reset_index(drop=True)
            boot_y = y_train.iloc[idx].reset_index(drop=True)
            estimator = adapter.build(cfg)
            adapter.fit(estimator, boot_X, boot_y, val[FEATURES], val[TARGET])
            attributor = build_attributor(adapter, estimator, background)
            matrix = attributor.attributions(X_explain)
            importance = global_importance(matrix)
            local_attr = attributor.attributions(local_case_rows)
            kind = "refit"
        else:
            row_idx = g.integers(0, len(reference_matrix), size=len(reference_matrix))
            importance = global_importance(reference_matrix[row_idx])
            local_attr = None
            kind = "resample"
        topk = top_k_features(importance, k)
        values = np.array([importance[f] for f in FEATURES])
        tau = kendalltau(ref_values, values).statistic
        record: dict[str, Any] = {
            "kind": kind,
            "top_k": topk,
            "jaccard_vs_reference": jaccard(topk, ref_topk),
            "kendall_tau_vs_reference": None if np.isnan(tau) else float(tau),
        }
        if local_attr is not None:
            record["local_attributions"] = np.round(local_attr, 6).tolist()
        return record

    return run_checkpointed_bootstrap(
        directory=out_dir,
        name="stability",
        n_iterations=n_total,
        checkpoint_every=1,  # refits are expensive; checkpoint every iteration
        config_hash=cfg.config_hash,
        compute_fn=iteration,
        resume=resume,
        force=force,
    )
