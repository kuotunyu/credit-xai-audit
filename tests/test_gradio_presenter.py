from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from app.gradio_presenter import (
    EvidenceModelRow,
    PublicEvidence,
    load_public_evidence,
    render_public_evidence,
)


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
