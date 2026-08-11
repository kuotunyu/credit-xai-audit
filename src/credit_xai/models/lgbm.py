"""LightGBM with native categorical handling, plus the sklearn
HistGradientBoosting fallback used when lightgbm is not installed."""

from __future__ import annotations

import logging
from typing import Any, ClassVar

import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import CATEGORICAL_FEATURES, step_train
from credit_xai.data.schema import CATEGORICAL_DOMAINS
from credit_xai.models.base import ModelAdapter
from credit_xai.utils.seeding import seed_int

logger = logging.getLogger(__name__)


def _as_categorical(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    for col in CATEGORICAL_FEATURES:
        X[col] = pd.Categorical(X[col], categories=CATEGORICAL_DOMAINS[col])
    return X


class LightGBMAdapter(ModelAdapter):
    name: ClassVar[str] = "lightgbm"
    explainer_kind: ClassVar[str] = "tree_shap"

    def build(self, cfg: Config) -> Any:
        import lightgbm as lgb

        params = cfg.models.lightgbm
        return lgb.LGBMClassifier(
            n_estimators=params.n_estimators,
            num_leaves=params.num_leaves,
            learning_rate=params.learning_rate,
            min_child_samples=params.min_child_samples,
            num_threads=params.num_threads,
            deterministic=True,
            force_row_wise=True,
            random_state=seed_int(cfg.run.seed, step_train(self.name)),
            verbosity=-1,
        )

    def prepare_features(self, X: pd.DataFrame) -> pd.DataFrame:
        return _as_categorical(X)

    def fit(
        self,
        estimator: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Any:
        import lightgbm as lgb

        stopping = estimator.get_params().get("n_estimators", 100)
        rounds = self._early_stopping_rounds
        estimator.fit(
            self.prepare_features(X_train),
            y_train,
            eval_set=[(self.prepare_features(X_val), y_val)],
            eval_metric="binary_logloss",
            callbacks=[lgb.early_stopping(rounds, verbose=False), lgb.log_evaluation(0)],
        )
        best = getattr(estimator, "best_iteration_", None)
        logger.info("lightgbm fitted: best_iteration=%s (cap %d)", best, stopping)
        return estimator

    def __init__(self, early_stopping_rounds: int = 50):
        self._early_stopping_rounds = early_stopping_rounds

    @classmethod
    def from_config(cls, cfg: Config) -> LightGBMAdapter:
        return cls(early_stopping_rounds=cfg.models.lightgbm.early_stopping_rounds)


class HistGradientBoostingAdapter(ModelAdapter):
    """Documented fallback when the lightgbm wheel is unavailable (FAILURES.md)."""

    name: ClassVar[str] = "lightgbm"  # keeps CLI names and artifact paths stable
    explainer_kind: ClassVar[str] = "tree_shap"
    is_fallback: ClassVar[bool] = True

    def build(self, cfg: Config) -> Any:
        from sklearn.ensemble import HistGradientBoostingClassifier

        params = cfg.models.lightgbm
        return HistGradientBoostingClassifier(
            max_iter=params.n_estimators,
            learning_rate=params.learning_rate,
            min_samples_leaf=params.min_child_samples,
            categorical_features=CATEGORICAL_FEATURES,
            early_stopping=False,
            random_state=seed_int(cfg.run.seed, step_train(self.name)),
        )
