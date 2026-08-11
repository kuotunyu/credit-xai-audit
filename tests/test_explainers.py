from __future__ import annotations

import numpy as np
import pytest
from scipy.special import expit

from credit_xai.constants import FEATURES, TARGET
from credit_xai.data.prepare import load_processed
from credit_xai.explain.ebm_shapes import export_shapes
from credit_xai.explain.explainers import (
    build_attributor,
    global_importance,
    top_k_features,
)
from credit_xai.models.registry import get_adapter


@pytest.fixture(scope="module")
def fitted(prepared_config_module):
    """Fit all three models once for this module."""
    cfg = prepared_config_module
    splits = load_processed(cfg)
    out = {}
    for name in ("logistic", "ebm", "lightgbm"):
        adapter = get_adapter(name, cfg)
        est = adapter.fit(
            adapter.build(cfg),
            splits["train"][FEATURES],
            splits["train"][TARGET],
            splits["val"][FEATURES],
            splits["val"][TARGET],
        )
        out[name] = (adapter, est)
    background = splits["train"][FEATURES].head(50).reset_index(drop=True)
    X = splits["test"][FEATURES].head(30).reset_index(drop=True)
    return cfg, out, background, X


@pytest.mark.parametrize("name", ["logistic", "ebm", "lightgbm"])
def test_attributions_are_additive_on_link_scale(fitted, name) -> None:
    """base_value + sum(attributions) must reproduce the model's own log-odds."""
    _, models, background, X = fitted
    adapter, est = models[name]
    attributor = build_attributor(adapter, est, background)
    matrix = attributor.attributions(X)
    assert matrix.shape == (len(X), len(FEATURES))
    reconstructed = expit(attributor.base_value + matrix.sum(axis=1))
    p = adapter.predict_proba(est, X)
    np.testing.assert_allclose(reconstructed, p, atol=1e-4)


def test_ebm_shape_export_is_consistent(fitted) -> None:
    _, models, _, _ = fitted
    _, est = models["ebm"]
    shapes = export_shapes(est)
    assert shapes["classes"] == [0, 1]
    assert len(shapes["terms"]) == len(est.term_features_)
    for term in shapes["terms"]:
        assert len(term["scores"]) == len(term["bin_weights"])
        if term["kind"] == "continuous":
            # scores has missing + unknown slots beyond the cut intervals
            assert len(term["scores"]) == len(term["cut_points"]) + 1 + 2
        assert term["features"][0] in FEATURES


def test_global_importance_and_topk() -> None:
    matrix = np.zeros((10, len(FEATURES)))
    matrix[:, 2] = 3.0
    matrix[:, 5] = -1.0
    imp = global_importance(matrix)
    assert imp[FEATURES[2]] == pytest.approx(3.0)
    assert imp[FEATURES[5]] == pytest.approx(1.0)
    top2 = top_k_features(imp, 2)
    assert top2 == [FEATURES[2], FEATURES[5]]
