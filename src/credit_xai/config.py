"""Typed, validated run configuration loaded from YAML.

Every artifact produced by the pipeline is stamped with ``Config.config_hash`` so
that partial results from a different configuration can never be silently mixed.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, model_validator


class _Frozen(BaseModel):
    model_config = {"frozen": True, "extra": "forbid"}


class RunConfig(_Frozen):
    name: str
    seed: int = 42
    results_dir: Path = Path("results")
    models_dir: Path = Path("models")
    manifests_dir: Path = Path("manifests")


class SplitConfig(_Frozen):
    train: float = Field(gt=0, lt=1)
    val: float = Field(gt=0, lt=1)
    test: float = Field(gt=0, lt=1)

    @model_validator(mode="after")
    def _sums_to_one(self) -> SplitConfig:
        total = self.train + self.val + self.test
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"split fractions must sum to 1.0, got {total}")
        return self


class DataConfig(_Frozen):
    source: Literal["uci_static", "ucimlrepo", "synthetic"]
    cache_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    split: SplitConfig
    synthetic_rows: int = Field(default=4000, ge=200)
    local_cases_per_class: int = Field(default=3, ge=1)


class LogisticConfig(_Frozen):
    C: float = Field(default=1.0, gt=0)
    max_iter: int = Field(default=2000, ge=100)


class EbmConfig(_Frozen):
    max_bins: int = Field(default=256, ge=8)
    interactions: int = Field(default=0, ge=0)
    outer_bags: int = Field(default=8, ge=1)
    max_rounds: int = Field(default=5000, ge=10)


class LightGBMConfig(_Frozen):
    n_estimators: int = Field(default=500, ge=10)
    num_leaves: int = Field(default=31, ge=2)
    learning_rate: float = Field(default=0.05, gt=0)
    min_child_samples: int = Field(default=20, ge=1)
    early_stopping_rounds: int = Field(default=50, ge=1)
    num_threads: int = Field(default=4, ge=1)


class ModelsConfig(_Frozen):
    logistic: LogisticConfig = LogisticConfig()
    ebm: EbmConfig = EbmConfig()
    lightgbm: LightGBMConfig = LightGBMConfig()


class CalibrationConfig(_Frozen):
    methods: tuple[Literal["sigmoid", "isotonic"], ...] = ("sigmoid", "isotonic")
    selection_metric: Literal["log_loss"] = "log_loss"

    @model_validator(mode="after")
    def _non_empty(self) -> CalibrationConfig:
        if not self.methods:
            raise ValueError("calibration.methods must not be empty")
        return self


class BootstrapConfig(_Frozen):
    n_iterations: int = Field(ge=10)
    checkpoint_every: int = Field(default=25, ge=1)
    ci_level: float = Field(default=0.95, gt=0, lt=1)


class LatencyConfig(_Frozen):
    n_warmup: int = Field(default=3, ge=0)
    n_repeats: int = Field(default=5, ge=1)
    per_row_samples: int = Field(default=200, ge=10)


class EvaluationConfig(_Frozen):
    bootstrap: BootstrapConfig
    ece_bins: int = Field(default=15, ge=2)
    latency: LatencyConfig = LatencyConfig()


class ShapConfig(_Frozen):
    background_size: int = Field(ge=10)
    test_sample_size: int = Field(ge=10)


class RankStabilityConfig(_Frozen):
    n_refits: int = Field(ge=1)
    n_resamples: int = Field(ge=0)


class FaithfulnessConfig(_Frozen):
    n_instances: int = Field(ge=10)
    n_draws: int = Field(default=5, ge=1)


class ExplainConfig(_Frozen):
    shap: ShapConfig
    top_k: int = Field(default=10, ge=1)
    rank_stability: RankStabilityConfig
    faithfulness: FaithfulnessConfig


class FairnessConfig(_Frozen):
    sex_column: str = "SEX"
    # [lo, hi] inclusive; hi = null means open-ended (e.g. 60+). Predeclared, never tuned.
    age_bins: tuple[tuple[int, int | None], ...] = (
        (21, 29),
        (30, 39),
        (40, 49),
        (50, 59),
        (60, None),
    )
    small_cell_min: int = Field(default=20, ge=1)


class ServeConfig(_Frozen):
    model: Literal["logistic", "ebm", "lightgbm"] = "lightgbm"
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)


class Config(_Frozen):
    run: RunConfig
    data: DataConfig
    models: ModelsConfig = ModelsConfig()
    calibration: CalibrationConfig = CalibrationConfig()
    evaluation: EvaluationConfig
    explain: ExplainConfig
    fairness: FairnessConfig = FairnessConfig()
    serve: ServeConfig = ServeConfig()

    @property
    def config_hash(self) -> str:
        payload = canonical_json(self.model_dump(mode="json"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # Frequently used derived paths
    @property
    def raw_results_dir(self) -> Path:
        return self.run.results_dir / "raw"

    @property
    def derived_results_dir(self) -> Path:
        return self.run.results_dir / "derived"


def canonical_json(obj: Any) -> str:
    """Deterministic JSON encoding (sorted keys, compact separators)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def load_config(path: str | Path) -> Config:
    """Load and validate a YAML config file."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise ValueError(f"config file {path} must contain a YAML mapping")
    return Config.model_validate(raw)
