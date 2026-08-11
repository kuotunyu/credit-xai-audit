"""Explainable Boosting Machine (interpret). Optional dependency — install with
``uv sync --extra ebm``."""

from __future__ import annotations

from typing import Any, ClassVar

from credit_xai.config import Config
from credit_xai.constants import CATEGORICAL_FEATURES, FEATURES, step_train
from credit_xai.models.base import ModelAdapter
from credit_xai.utils.seeding import seed_int


class EbmAdapter(ModelAdapter):
    name: ClassVar[str] = "ebm"
    explainer_kind: ClassVar[str] = "ebm_native"

    def build(self, cfg: Config) -> Any:
        from interpret.glassbox import ExplainableBoostingClassifier

        params = cfg.models.ebm
        feature_types = ["nominal" if c in CATEGORICAL_FEATURES else "continuous" for c in FEATURES]
        return ExplainableBoostingClassifier(
            feature_names=list(FEATURES),
            feature_types=feature_types,
            max_bins=params.max_bins,
            interactions=params.interactions,
            outer_bags=params.outer_bags,
            max_rounds=params.max_rounds,
            random_state=seed_int(cfg.run.seed, step_train(self.name)),
        )
