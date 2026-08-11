"""Model adapter interface.

Each adapter wraps one estimator family behind a uniform surface so training,
calibration, evaluation, and explanation never special-case model types beyond
the declared ``explainer_kind``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar

import numpy as np
import pandas as pd

from credit_xai.config import Config


class ModelUnavailableError(RuntimeError):
    """An optional model dependency is not installed."""


class ModelAdapter(ABC):
    #: canonical CLI name ("logistic" | "ebm" | "lightgbm")
    name: ClassVar[str]
    #: which explainer family applies: "linear_shap" | "ebm_native" | "tree_shap"
    explainer_kind: ClassVar[str]
    #: True when this adapter is a stand-in for an unavailable dependency
    is_fallback: ClassVar[bool] = False

    @abstractmethod
    def build(self, cfg: Config) -> Any:
        """Unfitted estimator with a config-derived random_state."""

    def prepare_features(self, X: pd.DataFrame) -> pd.DataFrame:
        """Frame the estimator consumes (default: cleaned frame as-is)."""
        return X

    def fit(
        self,
        estimator: Any,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
    ) -> Any:
        """Fit on train; validation data is available for early stopping only."""
        del X_val, y_val
        estimator.fit(self.prepare_features(X_train), y_train)
        return estimator

    def predict_proba(self, estimator: Any, X: pd.DataFrame) -> np.ndarray:
        """P(default=1) as a 1-D array."""
        proba = estimator.predict_proba(self.prepare_features(X))
        return np.asarray(proba)[:, 1]

    def estimator_class(self, estimator: Any) -> str:
        return type(estimator).__name__
