from __future__ import annotations

import numpy as np

from credit_xai.calibration.calibrate import run as calibrate_run
from credit_xai.explain.run import run as explain_run
from credit_xai.training.train import run as train_run
from credit_xai.utils.checkpoints import require_complete
from credit_xai.utils.io import read_json


def test_explain_end_to_end_logistic(prepared_config) -> None:
    cfg = prepared_config
    train_run(cfg, "logistic")
    calibrate_run(cfg, "logistic")
    explain_run(cfg, "logistic")

    out_dir = cfg.raw_results_dir / "logistic" / "explain"

    gi = read_json(out_dir / "global_importance.json")
    assert gi["method"] == "linear_shap"
    assert len(gi["importance"]) == 23
    assert len(gi["top_k"]) == cfg.explain.top_k
    assert (out_dir / "attributions_test_sample.parquet").exists()

    local = read_json(out_dir / "local_cases.json")
    n_cases = 2 * cfg.data.local_cases_per_class
    assert len(local["cases"]) == n_cases
    case = local["cases"][0]
    assert set(case["attributions_link_scale"]) == set(gi["importance"])
    assert 0 <= case["prob_uncalibrated"] <= 1
    assert "prob_calibrated" in case

    st_cfg = cfg.explain.rank_stability
    stability = require_complete(out_dir, "stability")
    assert len(stability) == st_cfg.n_refits + st_cfg.n_resamples
    refits = [r for r in stability if r["kind"] == "refit"]
    assert len(refits) == st_cfg.n_refits
    for r in refits:
        assert 0 <= r["jaccard_vs_reference"] <= 1
        assert np.asarray(r["local_attributions"]).shape == (n_cases, 23)
    resamples = [r for r in stability if r["kind"] == "resample"]
    assert all("local_attributions" not in r for r in resamples)

    faith = require_complete(out_dir, "faithfulness")
    assert len(faith) == cfg.explain.faithfulness.n_instances
    delta_top = np.array([r["delta_top"] for r in faith])
    delta_rand = np.array([r["delta_random"] for r in faith])
    # synthetic data has genuine signal: top-attributed replacement must move
    # predictions more than matched-random replacement on average
    assert delta_top.mean() > delta_rand.mean()


def test_explain_end_to_end_ebm_writes_shapes(prepared_config) -> None:
    cfg = prepared_config
    train_run(cfg, "ebm")
    explain_run(cfg, "ebm")

    out_dir = cfg.raw_results_dir / "ebm" / "explain"
    shapes = read_json(out_dir / "ebm_shapes.json")
    assert len(shapes["terms"]) >= 1
    gi = read_json(out_dir / "global_importance.json")
    assert gi["method"] == "ebm_native"

    stability = require_complete(out_dir, "stability")
    assert (
        len(stability)
        == cfg.explain.rank_stability.n_refits + cfg.explain.rank_stability.n_resamples
    )
