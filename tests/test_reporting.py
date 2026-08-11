from __future__ import annotations

import json
from pathlib import Path

import pytest

from credit_xai.calibration.calibrate import run as calibrate_run
from credit_xai.constants import MODEL_NAMES
from credit_xai.data.prepare import run as prepare_run
from credit_xai.evaluation.evaluate import run as evaluate_run
from credit_xai.explain.run import run as explain_run
from credit_xai.reporting.aggregate import AggregationError, build_summary
from credit_xai.reporting.render import RenderError, inject
from credit_xai.reporting.run import run as report_run
from credit_xai.reporting.tables import all_tables
from credit_xai.training.train import run as train_run
from credit_xai.utils.io import read_json
from tests.conftest import make_config

_MARKERS = "\n".join(
    f"<!-- AUTOGEN:{s}:START -->\nplaceholder\n<!-- AUTOGEN:{s}:END -->"
    for s in ("METRICS", "CALIBRATION", "XAI", "GROUPS")
)


@pytest.fixture(scope="module")
def full_run_config(tmp_path_factory):
    """Complete synthetic pipeline for all three models (module-scoped)."""
    tmp = tmp_path_factory.mktemp("fullrun")
    cfg = make_config(tmp)
    prepare_run(cfg)
    for name in MODEL_NAMES:
        train_run(cfg, name)
        calibrate_run(cfg, name)
        evaluate_run(cfg, name)
        explain_run(cfg, name)
    return cfg


def test_summary_is_complete_and_consistent(full_run_config) -> None:
    summary = build_summary(full_run_config)
    assert set(summary["models"]) == set(MODEL_NAMES)
    assert summary["run"]["config_hash"] == full_run_config.config_hash
    for name in MODEL_NAMES:
        model = summary["models"][name]
        ci = model["test_metrics"]["calibrated_ci"]["roc_auc"]
        assert ci["ci_low"] <= ci["mean"] <= ci["ci_high"]
        assert ci["n_boot"] == full_run_config.evaluation.bootstrap.n_iterations
        faith = model["explain"]["faithfulness"]
        assert faith["n_instances"] == full_run_config.explain.faithfulness.n_instances
        assert model["explain"]["local_stability"]["aggregate"]["sign_consistency_top5_mean"] <= 1
    assert len(summary["provenance"]) > 10
    # committed artifacts must never contain local absolute paths
    assert "C:\\" not in json.dumps(summary)


def test_report_writes_summary_tables_figures_and_injects(full_run_config, tmp_path) -> None:
    readme_dir = tmp_path / "docs"
    readme_dir.mkdir()
    for name in ("README.md", "README_zh-TW.md"):
        (readme_dir / name).write_text(f"# t\n{_MARKERS}\n", encoding="utf-8")
    assets_dir = tmp_path / "assets"

    report_run(full_run_config, readme_dir=readme_dir, assets_dir=assets_dir)

    summary = read_json(full_run_config.derived_results_dir / "summary.json")
    tables_dir = full_run_config.derived_results_dir / "tables"
    assert {p.name for p in tables_dir.glob("*.md")} == {
        "metrics.md",
        "calibration.md",
        "xai.md",
        "groups.md",
    }
    pngs = {p.name for p in Path(assets_dir).glob("*.png")}
    assert {
        "roc_pr_curves.png",
        "reliability_diagram.png",
        "global_importance.png",
        "ebm_shapes_top.png",
        "faithfulness.png",
        "group_auc.png",
    } <= pngs

    # README numbers come from summary.json: spot-check one injected value
    readme_text = (readme_dir / "README.md").read_text(encoding="utf-8")
    auc = summary["models"]["logistic"]["test_metrics"]["calibrated_ci"]["roc_auc"]["mean"]
    assert f"{auc:.3f}" in readme_text
    assert "placeholder" not in readme_text

    # idempotent: re-injecting produces identical text
    tables = all_tables(summary)
    inject(readme_dir / "README.md", tables, "again")
    inject(readme_dir / "README.md", tables, "again")
    assert (readme_dir / "README.md").read_text(encoding="utf-8").count(
        "AUTOGEN:METRICS:START"
    ) == 1


def test_aggregate_refuses_missing_artifacts(test_config) -> None:
    with pytest.raises(AggregationError, match="missing raw artifact"):
        build_summary(test_config)


def test_inject_requires_markers(tmp_path, full_run_config) -> None:
    bad = tmp_path / "README.md"
    bad.write_text("# no markers\n", encoding="utf-8")
    summary = build_summary(full_run_config)
    with pytest.raises(RenderError, match="missing AUTOGEN markers"):
        inject(bad, all_tables(summary), "x")
