"""Shared fixtures: temp configs and (from Phase 1 on) synthetic data."""

from __future__ import annotations

from pathlib import Path

import pytest

from credit_xai.config import Config

REPO_ROOT = Path(__file__).resolve().parents[1]


def make_config(tmp_path: Path, **overrides: object) -> Config:
    """A small, fully-valid synthetic-source config rooted in tmp_path."""
    base: dict = {
        "run": {
            "name": "test",
            "seed": 7,
            "results_dir": str(tmp_path / "results"),
            "models_dir": str(tmp_path / "models"),
            "manifests_dir": str(tmp_path / "manifests"),
        },
        "data": {
            "source": "synthetic",
            "cache_dir": str(tmp_path / "data" / "raw"),
            "processed_dir": str(tmp_path / "data" / "processed"),
            "split": {"train": 0.70, "val": 0.15, "test": 0.15},
            "synthetic_rows": 600,
            "local_cases_per_class": 2,
        },
        "models": {
            "logistic": {"C": 1.0, "max_iter": 500},
            "ebm": {"max_bins": 16, "interactions": 0, "outer_bags": 2, "max_rounds": 50},
            "lightgbm": {
                "n_estimators": 30,
                "num_leaves": 7,
                "learning_rate": 0.1,
                "min_child_samples": 5,
                "early_stopping_rounds": 5,
                "num_threads": 1,
            },
        },
        "evaluation": {
            "bootstrap": {"n_iterations": 20, "checkpoint_every": 5, "ci_level": 0.95},
            "ece_bins": 5,
            "latency": {"n_warmup": 1, "n_repeats": 2, "per_row_samples": 10},
        },
        "explain": {
            "shap": {"background_size": 30, "test_sample_size": 40},
            "top_k": 5,
            "rank_stability": {"n_refits": 2, "n_resamples": 3},
            "faithfulness": {"n_instances": 20, "n_draws": 2},
        },
        "fairness": {
            "sex_column": "SEX",
            "age_bins": [[21, 39], [40, None]],
            "small_cell_min": 5,
        },
    }
    _deep_update(base, overrides)
    return Config.model_validate(base)


def _deep_update(base: dict, overrides: dict) -> None:
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_update(base[key], value)
        else:
            base[key] = value


@pytest.fixture
def test_config(tmp_path: Path) -> Config:
    return make_config(tmp_path)


@pytest.fixture
def prepared_config(tmp_path: Path) -> Config:
    """Config whose synthetic dataset has been fully prepared (splits on disk)."""
    from credit_xai.data.prepare import run as prepare_run

    cfg = make_config(tmp_path)
    prepare_run(cfg)
    return cfg


@pytest.fixture(scope="module")
def prepared_config_module(tmp_path_factory) -> Config:
    """Module-scoped prepared config for expensive multi-model fixtures."""
    from credit_xai.data.prepare import run as prepare_run

    cfg = make_config(tmp_path_factory.mktemp("prepared"))
    prepare_run(cfg)
    return cfg
