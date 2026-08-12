from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from app.gradio_presenter import (
    FEATURE_GROUPS,
    EvidenceModelRow,
    PublicEvidence,
    analyze_values,
    case_values,
    feature_mapping,
    load_public_evidence,
    render_empty_result,
    render_public_evidence,
)

from credit_xai.constants import DEMO_SCOPE, DISCLAIMER, FEATURES, TARGET


def _summary_payload() -> dict[str, Any]:
    methods = {
        "logistic": "linear_shap",
        "ebm": "ebm_native",
        "lightgbm": "tree_shap",
    }
    return {
        "models": {
            model: {
                "calibration": {"selection_split": "val"},
                "test_metrics": {"calibrated_ci": {"roc_auc": {"n_boot": 1000}}},
                "explain": {
                    "method": method,
                    "rank_stability": {
                        "refit": {"n_iterations": 20},
                        "resample": {"n_iterations": 200},
                    },
                    "faithfulness": {"n_instances": 2000},
                },
                "groups": {"by_group": {"age=60+": {"small_cell": True, "ci": None}}},
            }
            for model, method in methods.items()
        }
    }


def test_load_public_evidence_accepts_committed_contract(tmp_path: Path) -> None:
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(_summary_payload()), encoding="utf-8")

    evidence = load_public_evidence(path)

    assert evidence is not None
    assert evidence.model_count == 3
    assert evidence.bootstrap_iterations == 1000
    assert evidence.explainer_count == 3
    assert [row.explanation for row in evidence.models] == [
        "Linear SHAP",
        "EBM Native",
        "TreeSHAP",
    ]
    assert evidence.small_cell_ci_suppressed is True


@pytest.mark.parametrize(
    "mutation",
    [
        lambda data: data["models"].pop("ebm"),
        lambda data: data["models"]["logistic"]["calibration"].update(selection_split="test"),
        lambda data: data["models"]["lightgbm"]["explain"].update(method="linear_shap"),
        lambda data: data["models"]["ebm"]["test_metrics"]["calibrated_ci"]["roc_auc"].update(
            n_boot=999
        ),
        lambda data: data["models"]["logistic"]["explain"]["rank_stability"]["refit"].update(
            n_iterations=19
        ),
        lambda data: data["models"]["ebm"]["explain"]["faithfulness"].update(n_instances=1999),
        lambda data: data["models"]["lightgbm"]["groups"]["by_group"]["age=60+"].update(
            ci={"roc_auc": {"low": 0.1, "high": 0.9}}
        ),
    ],
)
def test_load_public_evidence_fails_closed(tmp_path: Path, mutation: Any) -> None:
    payload = _summary_payload()
    mutation(payload)
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    assert load_public_evidence(path) is None


def test_render_public_evidence_hides_unverified_values() -> None:
    rendered = render_public_evidence(None)

    assert "公開證據暫時無法載入" in rendered
    for hidden in ("1,000", "Linear SHAP", "EBM Native", "TreeSHAP"):
        assert hidden not in rendered


def test_render_public_evidence_escapes_verified_rows() -> None:
    evidence = PublicEvidence(
        model_count=3,
        bootstrap_iterations=1000,
        explainer_count=3,
        models=(EvidenceModelRow("<script>", "Validation-only", "Linear SHAP"),),
        stability_complete=True,
        faithfulness_complete=True,
        small_cell_ci_suppressed=True,
    )

    rendered = render_public_evidence(evidence)

    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered


def test_feature_groups_cover_features_once_in_approved_visual_order() -> None:
    flattened = [feature for _, group in FEATURE_GROUPS for feature in group]

    assert set(flattened) == set(FEATURES)
    assert len(flattened) == len(set(flattened)) == len(FEATURES) == 23
    assert FEATURE_GROUPS[0][1] == (
        "LIMIT_BAL",
        "AGE",
        "SEX",
        "EDUCATION",
        "MARRIAGE",
    )


def test_feature_mapping_preserves_canonical_integer_values() -> None:
    values = list(range(len(FEATURES)))

    assert feature_mapping(values) == dict(zip(FEATURES, values, strict=True))


@pytest.mark.parametrize(
    "values",
    [[0] * 22, [0] * 22 + [None], [0] * 22 + [1.5], [0] * 22 + ["invalid"]],
)
def test_feature_mapping_rejects_incomplete_or_fractional_input(
    values: list[object],
) -> None:
    with pytest.raises(ValueError, match="23 個整數欄位"):
        feature_mapping(values)


class _FakeService:
    def explain(self, features: dict[str, int]) -> dict[str, Any]:
        return {
            "model": "lightgbm",
            "output_type": "historical_model_replay",
            "probability_calibrated": 0.184,
            "probability_uncalibrated": 0.201,
            "calibration_method": "isotonic",
            "method": "tree_shap",
            "base_value_link_scale": -1.2,
            "attributions_link_scale": {
                "PAY_0": 0.42,
                "LIMIT_BAL": -0.17,
            },
            "top_attributions": [
                {"feature": "PAY_0", "attribution": 0.42},
                {"feature": "LIMIT_BAL", "attribution": -0.17},
            ],
        }


class _ExplodingService:
    def explain(self, features: dict[str, int]) -> dict[str, Any]:
        raise RuntimeError(str(Path.home() / "models" / "internal.joblib"))


class _MismatchedExplainerService(_FakeService):
    def explain(self, features: dict[str, int]) -> dict[str, Any]:
        result = super().explain(features)
        result["method"] = "linear_shap"
        return result


def test_case_values_reports_unavailable_processed_cases() -> None:
    values, note = case_values(None, 0)

    assert values is None
    assert "沒有已處理的測試案例" in note
    assert "23 個欄位" in note


def test_case_values_uses_modulo_and_canonical_feature_order() -> None:
    cases = pd.DataFrame(
        [
            {**dict(zip(FEATURES, range(23), strict=True)), TARGET: 0},
            {**dict(zip(FEATURES, range(100, 123), strict=True)), TARGET: 1},
        ]
    )

    values, note = case_values(cases, 3)

    assert values == tuple(range(100, 123))
    assert "測試案例 1" in note
    assert "歷史觀察結果：1" in note


def test_case_values_rejects_invalid_index_without_raw_error() -> None:
    cases = pd.DataFrame([{**dict.fromkeys(FEATURES, 0), TARGET: 0}])

    values, note = case_values(cases, "not-a-number")

    assert values is None
    assert note == "案例編號必須是整數。"


def test_empty_result_uses_honest_model_absent_state() -> None:
    rendered = render_empty_result()

    assert "尚未載入" in rendered
    assert "公開版本不包含 model bundle" in rendered
    assert "—" in rendered
    assert "示意數值" in rendered


def test_analyze_values_returns_honest_no_model_state() -> None:
    rendered, attributions = analyze_values(None, list(range(23)))

    assert "尚未載入" in rendered
    assert "—" in rendered
    assert attributions.empty


def test_analyze_values_formats_verified_service_result() -> None:
    rendered, attributions = analyze_values(_FakeService(), list(range(23)))

    for expected in (
        "18.4%",
        "20.1%",
        "LightGBM",
        "isotonic",
        "TreeSHAP",
        DISCLAIMER,
        DEMO_SCOPE,
    ):
        assert expected in rendered
    assert list(attributions.columns) == ["特徵", "影響值 (link scale)", "方向"]
    assert attributions.to_dict(orient="records") == [
        {"特徵": "PAY_0", "影響值 (link scale)": 0.42, "方向": "增加"},
        {"特徵": "LIMIT_BAL", "影響值 (link scale)": -0.17, "方向": "降低"},
    ]


def test_analyze_values_sanitizes_service_errors() -> None:
    rendered, attributions = analyze_values(_ExplodingService(), list(range(23)))

    assert "輸入資料無法完成審計" in rendered
    assert str(Path.home()) not in rendered
    assert "internal.joblib" not in rendered
    assert attributions.empty


def test_analyze_values_rejects_fractional_input_before_service() -> None:
    rendered, attributions = analyze_values(_FakeService(), [0] * 22 + [1.5])

    assert "必須提供 23 個整數欄位" in rendered
    assert "18.4%" not in rendered
    assert attributions.empty


def test_analyze_values_rejects_model_explainer_mismatch() -> None:
    rendered, attributions = analyze_values(_MismatchedExplainerService(), list(range(23)))

    assert "輸入資料無法完成審計" in rendered
    assert "Linear SHAP" not in rendered
    assert attributions.empty
