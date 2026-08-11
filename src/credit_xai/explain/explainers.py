"""Per-model exact/analytic attributors over the 23 canonical features.

Framing (also in MODEL_CARD.md): TreeSHAP is defined for tree ensembles and is
applied only to LightGBM. Each model family gets the attribution method
appropriate to its class — TreeSHAP for LightGBM, exact linear SHAP for
logistic regression (one-hot attributions summed back to their parent feature),
and EBM's own additive term contributions (exact by construction; interaction
terms split 50/50 between their two parent features, a declared convention).
All attributions live on the model's link (log-odds) scale against different
baselines and are compared qualitatively, never numerically, across models.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.constants import FEATURES
from credit_xai.models.base import ModelAdapter
from credit_xai.models.logistic import LogisticAdapter

logger = logging.getLogger(__name__)


class Attributor(ABC):
    """Uniform local-attribution interface: (n, 23) matrix on the link scale."""

    method: str
    detail: dict[str, Any]

    @abstractmethod
    def attributions(self, X: pd.DataFrame) -> np.ndarray: ...


class LinearShapAttributor(Attributor):
    """Exact linear SHAP for the logistic pipeline: phi_j = w_j * (x_j - mu_j)
    in the transformed space (independence assumption), with one-hot columns
    summed back to their parent feature."""

    method = "linear_shap"

    def __init__(self, adapter: LogisticAdapter, estimator: Any, background: pd.DataFrame):
        self._adapter = adapter
        self._estimator = estimator
        transformed_bg = adapter.transform(estimator, background)
        self._mu = np.asarray(transformed_bg, dtype=float).mean(axis=0)
        clf = adapter.final_estimator(estimator)
        self._w = np.asarray(clf.coef_, dtype=float).ravel()
        parents = adapter.transformed_parents(estimator)
        self._parent_idx = np.array([FEATURES.index(p) for p in parents])
        self.base_value = float(self._w @ self._mu + float(clf.intercept_[0]))
        self.detail = {
            "assumption": "feature independence (interventional), background = train sample mean",
            "background_rows": int(len(background)),
        }

    def attributions(self, X: pd.DataFrame) -> np.ndarray:
        Z = np.asarray(self._adapter.transform(self._estimator, X), dtype=float)
        phi_transformed = (Z - self._mu) * self._w  # (n, n_transformed)
        out = np.zeros((len(X), len(FEATURES)))
        for col, parent in enumerate(self._parent_idx):
            out[:, parent] += phi_transformed[:, col]
        return out


class TreeShapAttributor(Attributor):
    """TreeSHAP for LightGBM. Prefers shap's interventional TreeExplainer with a
    background sample; falls back to LightGBM's built-in pred_contrib
    (path-dependent TreeSHAP) if the shap path fails — the mode actually used is
    recorded in ``detail`` and surfaced in FAILURES.md if the fallback fired."""

    method = "tree_shap"

    def __init__(self, adapter: ModelAdapter, estimator: Any, background: pd.DataFrame):
        self._adapter = adapter
        self._estimator = estimator
        self._explainer = None
        mode = "interventional"
        try:
            import shap

            bg = adapter.prepare_features(background)
            self._explainer = shap.TreeExplainer(
                estimator, data=bg, feature_perturbation="interventional", model_output="raw"
            )
            # probe one row so failures surface here, not mid-run
            probe = self._explainer.shap_values(bg.iloc[[0]])
            _ = self._normalize(probe, 1)
            self.base_value = float(np.ravel(self._explainer.expected_value)[-1])
        except Exception as exc:  # documented fallback path
            logger.warning(
                "interventional TreeExplainer unavailable (%s: %s); falling back to "
                "path-dependent pred_contrib TreeSHAP",
                type(exc).__name__,
                exc,
            )
            self._explainer = None
            mode = "tree_path_dependent(pred_contrib)"
            self.base_value = float("nan")  # set on first attribution call
        self.detail = {"feature_perturbation": mode, "background_rows": int(len(background))}

    def attributions(self, X: pd.DataFrame) -> np.ndarray:
        prepared = self._adapter.prepare_features(X)
        if self._explainer is not None:
            values = self._explainer.shap_values(prepared)
            return self._normalize(values, len(X))
        booster = getattr(self._estimator, "booster_", self._estimator)
        contrib = booster.predict(prepared, pred_contrib=True)
        contrib = np.asarray(contrib)
        if np.isnan(self.base_value):
            self.base_value = float(contrib[0, -1])
        return contrib[:, :-1]  # last column is the expected value

    @staticmethod
    def _normalize(values: Any, n_rows: int) -> np.ndarray:
        """shap returns (n, m), [neg, pos] lists, or (n, m, 2) depending on version."""
        if isinstance(values, list):
            values = values[-1]
        values = np.asarray(values)
        if values.ndim == 3:
            values = values[:, :, -1]
        if values.shape != (n_rows, len(FEATURES)):
            raise ValueError(f"unexpected SHAP output shape {values.shape}")
        return values


class EbmNativeAttributor(Attributor):
    """EBM's exact additive term contributions via ``eval_terms``; interaction
    contributions split 50/50 between the two parent features."""

    method = "ebm_native"

    def __init__(self, adapter: ModelAdapter, estimator: Any, background: pd.DataFrame):
        del background  # EBM attributions are exact; no background needed
        self._adapter = adapter
        self._estimator = estimator
        self.base_value = float(np.ravel(estimator.intercept_)[-1])
        self.detail = {
            "note": "exact additive contributions; interactions split 50/50 to parents",
            "n_terms": len(estimator.term_features_),
        }

    def attributions(self, X: pd.DataFrame) -> np.ndarray:
        contributions = np.asarray(self._estimator.eval_terms(X), dtype=float)  # (n, n_terms)
        out = np.zeros((len(X), len(FEATURES)))
        for t, feature_idx in enumerate(self._estimator.term_features_):
            share = contributions[:, t] / len(feature_idx)
            for f in feature_idx:
                out[:, f] += share
        return out


def build_attributor(adapter: ModelAdapter, estimator: Any, background: pd.DataFrame) -> Attributor:
    kind = adapter.explainer_kind
    if kind == "linear_shap":
        assert isinstance(adapter, LogisticAdapter)
        return LinearShapAttributor(adapter, estimator, background)
    if kind == "tree_shap":
        return TreeShapAttributor(adapter, estimator, background)
    if kind == "ebm_native":
        return EbmNativeAttributor(adapter, estimator, background)
    raise ValueError(f"unknown explainer kind {kind!r}")


def global_importance(attribution_matrix: np.ndarray) -> dict[str, float]:
    """Mean |attribution| per feature over the explained sample (uniform
    definition across all three models)."""
    means = np.abs(attribution_matrix).mean(axis=0)
    return {feature: float(means[i]) for i, feature in enumerate(FEATURES)}


def top_k_features(importance: dict[str, float], k: int) -> list[str]:
    return sorted(importance, key=importance.__getitem__, reverse=True)[:k]
