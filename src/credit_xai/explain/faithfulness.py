"""Faithfulness perturbation test (sanity check, not causal evidence).

Hypothesis: if attributions are faithful, replacing the *top-attributed* feature
of a test case with donor values drawn from the validation marginal should move
the model's predicted probability more than replacing a uniformly chosen other
feature under the identical mechanism (same donor rows, same number of draws —
the "matched" in matched-random). Donor-row replacement keeps each value
realistic per feature while deliberately breaking joint dependence.

Per instance record: mean |delta p| for the top feature vs the random feature.
Aggregation (ratio + paired bootstrap CI over instances) happens in reporting.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import FEATURES, step_faithfulness
from credit_xai.metrics.bootstrap import run_checkpointed_bootstrap
from credit_xai.models.base import ModelAdapter
from credit_xai.utils.seeding import rng

logger = logging.getLogger(__name__)


def run_faithfulness(
    *,
    cfg: Config,
    adapter: ModelAdapter,
    estimator: Any,
    X_explain: pd.DataFrame,
    attribution_matrix: np.ndarray,
    X_val: pd.DataFrame,
    out_dir: Any,
    resume: bool,
    force: bool,
) -> list[dict[str, Any]]:
    n_instances = min(cfg.explain.faithfulness.n_instances, len(X_explain))
    n_draws = cfg.explain.faithfulness.n_draws
    step_name = step_faithfulness(adapter.name)

    def iteration(i: int) -> dict[str, Any]:
        g = rng(cfg.run.seed, step_name, i)
        row = X_explain.iloc[[i]]
        phi = attribution_matrix[i]
        top_idx = int(np.argmax(np.abs(phi)))
        other = [j for j in range(len(FEATURES)) if j != top_idx]
        rand_idx = int(g.choice(other))
        donor_rows = g.integers(0, len(X_val), size=n_draws)

        # one batched predict: original + n_draws top-replaced + n_draws rand-replaced
        variants = pd.concat([row] * (1 + 2 * n_draws), ignore_index=True)
        for m, donor in enumerate(donor_rows):
            variants.iloc[1 + m, top_idx] = X_val.iloc[int(donor), top_idx]
            variants.iloc[1 + n_draws + m, rand_idx] = X_val.iloc[int(donor), rand_idx]
        p = adapter.predict_proba(estimator, variants)
        p0 = p[0]
        delta_top = float(np.abs(p[1 : 1 + n_draws] - p0).mean())
        delta_rand = float(np.abs(p[1 + n_draws :] - p0).mean())
        return {
            "top_feature": FEATURES[top_idx],
            "random_feature": FEATURES[rand_idx],
            "delta_top": delta_top,
            "delta_random": delta_rand,
        }

    return run_checkpointed_bootstrap(
        directory=out_dir,
        name="faithfulness",
        n_iterations=n_instances,
        checkpoint_every=cfg.evaluation.bootstrap.checkpoint_every,
        config_hash=cfg.config_hash,
        compute_fn=iteration,
        resume=resume,
        force=force,
    )
