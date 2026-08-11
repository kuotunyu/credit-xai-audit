from __future__ import annotations

from credit_xai.calibration.calibrate import run as calibrate_run
from credit_xai.evaluation.evaluate import run as evaluate_run
from credit_xai.training.train import run as train_run
from credit_xai.utils.checkpoints import require_complete
from credit_xai.utils.io import read_json


def test_evaluate_end_to_end_logistic(prepared_config) -> None:
    cfg = prepared_config
    train_run(cfg, "logistic")
    calibrate_run(cfg, "logistic")
    evaluate_run(cfg, "logistic")

    eval_dir = cfg.raw_results_dir / "logistic" / "eval"
    point = read_json(eval_dir / "point_metrics.json")
    assert point["config_hash"] == cfg.config_hash
    for section in ("uncalibrated", "calibrated"):
        for metric in ("roc_auc", "pr_auc", "log_loss", "brier", "ece"):
            assert 0 <= point[section][metric] <= 2
    assert point["latency"]["per_row_ms"]["median"] > 0
    assert point["latency"]["batch_ms_per_1k_rows"]["median"] > 0
    assert 0 <= point["rates_at_threshold"]["selection_rate"] <= 1

    n_boot = cfg.evaluation.bootstrap.n_iterations
    metric_records = require_complete(eval_dir, "bootstrap_metrics")
    assert len(metric_records) == n_boot
    assert {"cal_roc_auc", "unc_roc_auc", "cal_selection_rate"} <= set(metric_records[0])

    group_records = require_complete(eval_dir, "group_bootstrap")
    assert len(group_records) == n_boot

    groups = read_json(eval_dir / "group_metrics.json")["groups"]
    assert any(g.startswith("sex=") for g in groups)
    assert any(g.startswith("age=") for g in groups)
    total_sex_n = sum(v["n"] for k, v in groups.items() if k.startswith("sex="))
    assert total_sex_n == point["n_test_rows"]

    reliability = read_json(eval_dir / "reliability_bins.json")
    assert sum(b["n"] for b in reliability["bins"]) == point["n_test_rows"]
