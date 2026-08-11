"""Serialize EBM global shape functions to JSON (no interpret dashboard needed).

Slot convention in ``term_scores_`` (documented by interpret): index 0 is the
*missing* bin and the last index the *unknown* bin; the payload keeps the full
arrays and records this convention so plots can slice them off explicitly.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from credit_xai.constants import CATEGORICAL_FEATURES, FEATURES


def export_shapes(estimator: Any) -> dict[str, Any]:
    terms: list[dict[str, Any]] = []
    for t, feature_idx in enumerate(estimator.term_features_):
        scores = np.asarray(estimator.term_scores_[t], dtype=float)
        record: dict[str, Any] = {
            "term_index": t,
            "name": estimator.term_names_[t],
            "features": [FEATURES[f] for f in feature_idx],
            "kind": "interaction"
            if len(feature_idx) > 1
            else ("nominal" if FEATURES[feature_idx[0]] in CATEGORICAL_FEATURES else "continuous"),
            "scores": scores.tolist(),
            "score_standard_deviations": np.asarray(
                estimator.standard_deviations_[t], dtype=float
            ).tolist(),
            "bin_weights": np.asarray(estimator.bin_weights_[t], dtype=float).tolist(),
        }
        if len(feature_idx) == 1:
            f = feature_idx[0]
            bins = estimator.bins_[f][0]
            if isinstance(bins, dict):  # nominal: category -> bin index
                record["categories"] = {str(k): int(v) for k, v in bins.items()}
            else:  # continuous: cut points
                record["cut_points"] = np.asarray(bins, dtype=float).tolist()
        terms.append(record)
    return {
        "intercept": float(np.ravel(estimator.intercept_)[-1]),
        "link": str(getattr(estimator, "link_", "logit")),
        "classes": np.asarray(estimator.classes_).tolist(),
        "slot_convention": "scores[0] = missing bin; scores[-1] = unknown bin",
        "term_importances_mean_abs": {
            estimator.term_names_[t]: float(v) for t, v in enumerate(estimator.term_importances())
        },
        "terms": terms,
    }
