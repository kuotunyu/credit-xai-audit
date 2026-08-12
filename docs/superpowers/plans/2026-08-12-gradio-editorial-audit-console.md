# Gradio Editorial Audit Console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current wide-table Gradio demo with the owner-approved Traditional Chinese Editorial Audit Console while preserving every modeling, evidence, privacy, and non-decision boundary.

**Architecture:** Add one pure presentation module for committed-evidence parsing, feature grouping, and safe result formatting; keep `app/gradio_ui.py` responsible only for Gradio component assembly and event wiring. Put the approved visual system in one CSS resource, then verify the mounted page in model-absent and synthetic-bundle states without changing pipeline or API behavior.

**Tech Stack:** Python 3.11, Gradio 5, pandas, pytest, Ruff, strict mypy, FastAPI/Uvicorn, CSS, Docker Compose, Codex in-app browser.

## Global Constraints

- Work from the `credit-xai-audit` repository root on existing `main`; do not create a worktree, branch, remote, tag, PR, release, deployment, or upload.
- Do not use a subagent; execute this plan inline with `superpowers:executing-plans` because the owner has retained the no-subagent boundary.
- Use CPU only. Do not use GPU/CUDA, paid APIs, real UCI downloads, raw local UCI data, or committed model bundles.
- Do not retrain or alter accepted Logistic, EBM, or LightGBM results. Any synthetic model used for UI smoke writes only under ignored `tmp/`.
- 正體中文 (`zh-TW`) is the primary UI language. Keep precise ML/XAI terms such as `Logistic`, `EBM`, `LightGBM`, `Calibration`, `Bootstrap`, `SHAP`, `Faithfulness`, `Stability`, and `model bundle` in English.
- Use square geometry. Do not add decorative rounded cards, pill badges, rounded buttons, shadows, gradients, glass effects, or ornamental animation.
- Use the approved palette: warm field `#F6F3EC`, structural indigo `#202D65`, action indigo `#283B86`, amber `#C88725`/`#E4AD4F`, result field `#F0F1F6`, text `#202838`/`#606777`, and rules `#BFC1C8`/`#C8C7C2`.
- Ordinary UI copy is at least 14 px; compact metadata is at least 12 px; short input values are 15–17 px. Desktop content width is approximately 1440 px.
- Center short equal-weight status, KPI, tab, compact case-control, numeric-value, and primary-action content on both axes. Keep narrative, form groups, result detail, attribution, and evidence rows left-aligned.
- Preserve all 23 features. Their service payload is always assembled in canonical `FEATURES` order; the visual basic-data tab keeps the approved `LIMIT_BAL`, `AGE`, `SEX`, `EDUCATION`, `MARRIAGE` order. Input semantics remain integer-only.
- Never display fabricated case probabilities, performance metrics, model states, or claims. Missing or inconsistent public evidence fails closed.
- The UI must say this is a 2005 historical educational audit and must not imply approval, eligibility, lending decisions, financial advice, causal proof, discrimination, or current-market fairness.
- Do not expose raw exceptions, credentials, absolute paths, requests, responses, model bundles, or runtime caches in the public repository.
- Use TDD for all behavior. Use `apply_patch` for file edits. Use small English commits with `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` and no contributor trailers.

---

## File Structure

- Create `app/gradio_presenter.py`: pure feature grouping, public-evidence parsing, safe Traditional Chinese state rendering, and attribution-table formatting.
- Create `app/gradio_theme.css`: the approved Editorial Audit Console tokens, square component grammar, desktop density, focus states, and compact breakpoint.
- Modify `app/gradio_ui.py`: Gradio component composition, service/test-case loading, and event wiring only.
- Create `tests/test_gradio_presenter.py`: unit tests for evidence, input, result, and privacy/error behavior.
- Modify `tests/test_gradio.py`: Gradio configuration, component count, `zh-TW` copy, safe language, CSS, and test-count baseline assertions.
- Create `DESIGN.md`: post-build scan record of the shipped visual system.
- Create `.impeccable/design.json`: machine-readable extensions for breakpoints and representative square controls; it contains no machine path or session data.
- Modify `CHANGELOG.md`: record the approved UI redesign without claiming a new modeling capability.
- Modify `docs/release/VERIFICATION.md`: record fresh UI, package, Docker, privacy, and release-gate evidence and re-enter Feature Freeze.
- Regenerate `manifests/release_manifest.json`: include every final public file and hash.

---

### Task 1: Fail-closed public evidence presenter

**Files:**
- Create: `app/gradio_presenter.py`
- Create: `tests/test_gradio_presenter.py`

**Interfaces:**
- Consumes: `results/derived/summary.json`, `credit_xai.constants.MODEL_NAMES`.
- Produces: `EvidenceModelRow`, `PublicEvidence`, `load_public_evidence(path: Path) -> PublicEvidence | None`, and `render_public_evidence(evidence: PublicEvidence | None) -> str`.

- [ ] **Step 1: Write the failing happy-path evidence test**

Add a minimal committed-summary-shaped fixture and assertions:

```python
from __future__ import annotations

import json
from pathlib import Path

from app.gradio_presenter import load_public_evidence


def _summary_payload() -> dict[str, object]:
    methods = {
        "logistic": "linear_shap",
        "ebm": "ebm_native",
        "lightgbm": "tree_shap",
    }
    return {
        "models": {
            model: {
                "calibration": {"selection_split": "val"},
                "test_metrics": {
                    "calibrated_ci": {"roc_auc": {"n_boot": 1000}}
                },
                "explain": {
                    "method": method,
                    "rank_stability": {
                        "refit": {"n_iterations": 20},
                        "resample": {"n_iterations": 200},
                    },
                    "faithfulness": {"n_instances": 2000},
                },
                "groups": {
                    "by_group": {
                        "age=60+": {"small_cell": True, "ci": None}
                    }
                },
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
```

- [ ] **Step 2: Run the focused test and confirm the expected red state**

Run:

```powershell
$env:PYTHONPATH = "src;."
.\.venv\Scripts\python.exe -m pytest tests\test_gradio_presenter.py::test_load_public_evidence_accepts_committed_contract -v
```

Expected: collection fails with `ModuleNotFoundError: No module named 'app.gradio_presenter'`.

- [ ] **Step 3: Implement the typed evidence contract**

Create the module with these exact public types and validation rules:

```python
from __future__ import annotations

import html
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from credit_xai.constants import MODEL_NAMES

logger = logging.getLogger(__name__)

_MODEL_LABELS = {"logistic": "Logistic", "ebm": "EBM", "lightgbm": "LightGBM"}
_EXPLANATION_LABELS = {
    "linear_shap": "Linear SHAP",
    "ebm_native": "EBM Native",
    "tree_shap": "TreeSHAP",
}
_EXPECTED_EXPLANATIONS = {
    "logistic": "linear_shap",
    "ebm": "ebm_native",
    "lightgbm": "tree_shap",
}


@dataclass(frozen=True)
class EvidenceModelRow:
    model: str
    calibration: str
    explanation: str


@dataclass(frozen=True)
class PublicEvidence:
    model_count: int
    bootstrap_iterations: int
    explainer_count: int
    models: tuple[EvidenceModelRow, ...]
    stability_complete: bool
    faithfulness_complete: bool
    small_cell_ci_suppressed: bool


def load_public_evidence(path: Path) -> PublicEvidence | None:
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
        models = payload["models"]
        if set(models) != set(MODEL_NAMES):
            return None
        rows: list[EvidenceModelRow] = []
        bootstraps: set[int] = set()
        stability_complete = True
        faithfulness_complete = True
        small_cell_ci_suppressed = True
        for name in MODEL_NAMES:
            model = models[name]
            if model["calibration"]["selection_split"] != "val":
                return None
            method = str(model["explain"]["method"])
            if method != _EXPECTED_EXPLANATIONS[name]:
                return None
            bootstraps.add(
                int(model["test_metrics"]["calibrated_ci"]["roc_auc"]["n_boot"])
            )
            rank = model["explain"]["rank_stability"]
            stability_complete &= (
                int(rank["refit"]["n_iterations"]) == 20
                and int(rank["resample"]["n_iterations"]) == 200
            )
            faithfulness_complete &= int(
                model["explain"]["faithfulness"]["n_instances"]
            ) == 2000
            small_groups = [
                group
                for group in model["groups"]["by_group"].values()
                if group["small_cell"]
            ]
            small_cell_ci_suppressed &= bool(small_groups) and all(
                group["ci"] is None for group in small_groups
            )
            rows.append(
                EvidenceModelRow(
                    model=_MODEL_LABELS[name],
                    calibration="Validation-only",
                    explanation=_EXPLANATION_LABELS[method],
                )
            )
        if bootstraps != {1000}:
            return None
        return PublicEvidence(
            model_count=len(rows),
            bootstrap_iterations=bootstraps.pop(),
            explainer_count=len({row.explanation for row in rows}),
            models=tuple(rows),
            stability_complete=stability_complete,
            faithfulness_complete=faithfulness_complete,
            small_cell_ci_suppressed=small_cell_ci_suppressed,
        )
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        logger.warning("public UI evidence unavailable: %s", type(exc).__name__)
        return None
```

Implement `render_public_evidence()` with fixed markup classes, escaped model-row values, `110+` as the conservative test baseline, and `公開證據暫時無法載入` when the evidence is `None`. Do not render a default `3`, `1,000`, method mapping, or completed check when validation failed.

- [ ] **Step 4: Add malformed, inconsistent, and safe-fallback tests**

Add parameterized mutations for:

```python
@pytest.mark.parametrize(
    "mutation",
    [
        lambda data: data["models"].pop("ebm"),
        lambda data: data["models"]["logistic"]["calibration"].update(
            selection_split="test"
        ),
        lambda data: data["models"]["lightgbm"]["explain"].update(
            method="linear_shap"
        ),
        lambda data: data["models"]["ebm"]["test_metrics"]["calibrated_ci"][
            "roc_auc"
        ].update(n_boot=999),
    ],
)
def test_load_public_evidence_fails_closed(tmp_path: Path, mutation) -> None:
    payload = _summary_payload()
    mutation(payload)
    path = tmp_path / "summary.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert load_public_evidence(path) is None
```

Also assert that `render_public_evidence(None)` contains the unavailable message and none of `1,000`, `Linear SHAP`, `EBM Native`, or `TreeSHAP`.

- [ ] **Step 5: Run the presenter tests**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio_presenter.py -v
```

Expected: all Task 1 tests pass.

- [ ] **Step 6: Commit the evidence presenter**

```powershell
git add app\gradio_presenter.py tests\test_gradio_presenter.py
git commit -m "feat: present verified public evidence"
```

---

### Task 2: Feature grouping and safe replay states

**Files:**
- Modify: `app/gradio_presenter.py`
- Modify: `tests/test_gradio_presenter.py`

**Interfaces:**
- Consumes: `FEATURES`, `PAY_FEATURES`, `BILL_FEATURES`, `PAY_AMT_FEATURES`, `DISCLAIMER`, `DEMO_SCOPE`, and a service implementing `explain(features: dict[str, int]) -> dict[str, Any]`.
- Produces: `FEATURE_GROUPS`, `feature_mapping(values: Sequence[object]) -> dict[str, int]`, `case_values(test_cases: pd.DataFrame | None, index: object) -> tuple[tuple[int, ...] | None, str]`, `render_empty_result() -> str`, and `analyze_values(service: ExplanationService | None, values: Sequence[object]) -> tuple[str, pd.DataFrame]`.

- [ ] **Step 1: Write failing feature-order and integer-validation tests**

```python
from app.gradio_presenter import FEATURE_GROUPS, feature_mapping
from credit_xai.constants import FEATURES


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


def test_feature_mapping_preserves_integer_values() -> None:
    values = list(range(len(FEATURES)))
    assert feature_mapping(values) == dict(zip(FEATURES, values, strict=True))


@pytest.mark.parametrize(
    "values",
    [[0] * 22, [0] * 22 + [None], [0] * 22 + [1.5]],
)
def test_feature_mapping_rejects_incomplete_or_fractional_input(values) -> None:
    with pytest.raises(ValueError, match="23 個整數欄位"):
        feature_mapping(values)
```

- [ ] **Step 2: Run those tests and confirm they fail because the interfaces are absent**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio_presenter.py -k "feature_groups or feature_mapping" -v
```

Expected: import errors for `FEATURE_GROUPS` and `feature_mapping`.

- [ ] **Step 3: Implement the exact feature groups and strict conversion**

```python
from collections.abc import Sequence
from typing import Protocol

import pandas as pd

from credit_xai.constants import (
    BILL_FEATURES,
    DEMO_SCOPE,
    DISCLAIMER,
    FEATURES,
    PAY_AMT_FEATURES,
    PAY_FEATURES,
    TARGET,
)

FEATURE_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("基本資料", ("LIMIT_BAL", "AGE", "SEX", "EDUCATION", "MARRIAGE")),
    ("還款狀態", tuple(PAY_FEATURES)),
    ("帳單金額", tuple(BILL_FEATURES)),
    ("繳款金額", tuple(PAY_AMT_FEATURES)),
)


class ExplanationService(Protocol):
    def explain(self, features: dict[str, int]) -> dict[str, Any]: ...


def feature_mapping(values: Sequence[object]) -> dict[str, int]:
    if len(values) != len(FEATURES):
        raise ValueError("必須提供 23 個整數欄位。")
    converted: list[int] = []
    for value in values:
        if value is None:
            raise ValueError("必須提供 23 個整數欄位。")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("必須提供 23 個整數欄位。") from exc
        if not number.is_integer():
            raise ValueError("必須提供 23 個整數欄位。")
        converted.append(int(number))
    return dict(zip(FEATURES, converted, strict=True))
```

- [ ] **Step 4: Write failing tests for case loading, no-model, success, and sanitized errors**

Use a fake service returning this exact payload:

```python
class _FakeService:
    def explain(self, features: dict[str, int]) -> dict[str, object]:
        return {
            "model": "lightgbm",
            "probability_calibrated": 0.184,
            "probability_uncalibrated": 0.201,
            "calibration_method": "isotonic",
            "method": "tree_shap",
            "top_attributions": [
                {"feature": "PAY_0", "attribution": 0.42},
                {"feature": "LIMIT_BAL", "attribution": -0.17},
            ],
        }
```

Assert:

- `case_values(None, 0)` returns `None` plus a Traditional Chinese message.
- a two-row frame uses modulo indexing and returns all 23 values plus the recorded `TARGET` outcome in its note;
- `analyze_values(None, values)` renders `尚未載入`, em dashes, and no raw load error;
- fake success renders `18.4%`, `20.1%`, `LightGBM`, `isotonic`, `TreeSHAP`, `DISCLAIMER`, and `DEMO_SCOPE`;
- the attribution frame columns are `特徵`, `影響值 (link scale)`, `方向`, with `增加` for positive and `降低` for negative values;
- a fake service raising `RuntimeError(str(Path.home() / "models" / "internal.joblib"))` returns `輸入資料無法完成審計` and does not contain the home path, `internal.joblib`, or the exception message.

- [ ] **Step 5: Implement safe result and case rendering**

Implement these behaviors:

```python
def case_values(
    test_cases: pd.DataFrame | None, index: object
) -> tuple[tuple[int, ...] | None, str]:
    if test_cases is None or test_cases.empty:
        return None, "目前沒有已處理的測試案例；仍可手動輸入 23 個欄位。"
    resolved = int(float(index)) % len(test_cases)
    row = test_cases.iloc[resolved]
    values = tuple(int(row[feature]) for feature in FEATURES)
    return values, f"已載入測試案例 {resolved}；歷史觀察結果：{int(row[TARGET])}。"


def render_empty_result() -> str:
    return _result_shell(
        state="尚未載入",
        title="公開版本不包含 model bundle",
        body="載入本機驗證模型後才顯示結果；此處不使用示意數值。",
    )


def analyze_values(
    service: ExplanationService | None, values: Sequence[object]
) -> tuple[str, pd.DataFrame]:
    if service is None:
        return render_empty_result(), _empty_attributions()
    try:
        result = service.explain(feature_mapping(values))
        return render_success_result(result), attribution_frame(result)
    except Exception as exc:
        logger.warning("Gradio audit failed (%s)", type(exc).__name__)
        return render_input_error(), _empty_attributions()
```

Use `html.escape()` for every service-supplied string. The shared `_result_shell()` always appends `DISCLAIMER` and `DEMO_SCOPE`; do not use the words `approval`, `eligibility`, `accept`, `reject`, `核准`, `資格`, `通過核貸`, or `拒絕` in result copy.

- [ ] **Step 6: Run the complete presenter suite and strict typing for the new module**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio_presenter.py -v
.\.venv\Scripts\python.exe -m mypy --strict app\gradio_presenter.py
```

Expected: both commands pass.

- [ ] **Step 7: Commit the interaction presenter**

```powershell
git add app\gradio_presenter.py tests\test_gradio_presenter.py
git commit -m "feat: format safe audit interactions"
```

---

### Task 3: Build the approved Gradio surface and CSS system

**Files:**
- Create: `app/gradio_theme.css`
- Modify: `app/gradio_ui.py`
- Modify: `tests/test_gradio.py`

**Interfaces:**
- Consumes: every Task 1/2 presenter interface, `Config.derived_results_dir`, `PredictionService`, and optional processed `test.parquet`.
- Produces: `build_ui(cfg: Config) -> gr.Blocks` with 23 individually labeled integer controls, four tabs, one case-loader event, one analyze event, a public-evidence section, and the approved responsive CSS.

- [ ] **Step 1: Replace the existing config-string test with failing structural tests**

Write tests that inspect `build_ui(test_config).get_config_file()`:

```python
from __future__ import annotations

import json
from pathlib import Path

from app.gradio_ui import build_ui
from credit_xai.constants import DEMO_SCOPE, FEATURES


def _config(test_config) -> tuple[dict, str]:
    config = build_ui(test_config).get_config_file()
    return config, json.dumps(config, ensure_ascii=False)


def test_gradio_uses_approved_zh_tw_historical_language(test_config) -> None:
    _, text = _config(test_config)
    for phrase in (
        "不只呈現模型預測，更檢驗解釋是否可信。",
        "執行審計",
        "公開驗證證據",
        "尚未載入",
        DEMO_SCOPE,
    ):
        assert phrase in text
    for forbidden in ("Predict + explain", "Run historical audit", "approval", "eligibility"):
        assert forbidden not in text


def test_gradio_exposes_each_feature_as_one_labeled_number(test_config) -> None:
    config, _ = _config(test_config)
    labels = [
        component["props"].get("label")
        for component in config["components"]
        if component["type"] == "number"
    ]
    for feature in FEATURES:
        assert labels.count(feature) == 1


def test_gradio_has_four_feature_tabs_and_wide_layout(test_config) -> None:
    config, text = _config(test_config)
    assert {"基本資料", "還款狀態", "帳單金額", "繳款金額"} <= {
        component["props"].get("label")
        for component in config["components"]
        if component["type"] == "tabitem"
    }
    assert config["fill_width"] is True
    assert "audit-workspace" in text
```

- [ ] **Step 2: Run the structural tests and confirm they fail against the current Dataframe UI**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py -v
```

Expected: failures for Traditional Chinese copy, missing individual feature labels, tabs, and layout classes.

- [ ] **Step 3: Create the square Editorial Audit Console CSS**

Start `app/gradio_theme.css` with the audited tokens and global constraints:

```css
:root {
  --audit-field: #f6f3ec;
  --audit-structure: #202d65;
  --audit-action: #283b86;
  --audit-amber: #c88725;
  --audit-amber-light: #e4ad4f;
  --audit-result: #f0f1f6;
  --audit-text: #202838;
  --audit-muted: #606777;
  --audit-rule: #bfc1c8;
  --audit-rule-warm: #c8c7c2;
}

.gradio-container {
  max-width: 1440px !important;
  margin-inline: auto !important;
  padding: 0 !important;
  background: var(--audit-field) !important;
  color: var(--audit-text) !important;
  font-family: system-ui, "Noto Sans TC", "Microsoft JhengHei", sans-serif !important;
}

.gradio-container button,
.gradio-container input,
.gradio-container .block,
.gradio-container .panel,
.gradio-container .form {
  border-radius: 0 !important;
}

.gradio-container :focus-visible {
  outline: 3px solid var(--audit-amber) !important;
  outline-offset: 2px !important;
}

.audit-workspace { border: 1px solid var(--audit-rule); border-top: 3px solid var(--audit-action); }
.audit-input-column { border-right: 1px solid var(--audit-rule); padding: 0.7rem 0.875rem !important; }
.audit-result-column { background: var(--audit-result); padding: 0.7rem 0.875rem !important; }
.audit-feature-row { align-items: stretch !important; gap: 0.5rem !important; }
.audit-number label { justify-content: center !important; font-size: 0.75rem !important; }
.audit-number input { text-align: center !important; font-size: 1rem !important; font-weight: 650 !important; }
.audit-tabs button { justify-content: center !important; min-height: 2.5rem !important; font-size: 0.875rem !important; }
.audit-primary { min-height: 3rem !important; background: var(--audit-action) !important; }

@media (max-width: 820px) {
  .audit-workspace { flex-direction: column !important; }
  .audit-input-column { border-right: 0; border-bottom: 1px solid var(--audit-rule); }
  .audit-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .audit-feature-row { flex-wrap: wrap !important; }
  .audit-number { min-width: calc(50% - 0.5rem) !important; }
}
```

Add the approved header, thesis, KPI, evidence-table, state, footer, and compact-width selectors. Every custom container uses `border-radius: 0`; there is no `box-shadow`, `linear-gradient`, or transition other than Gradio's unavoidable built-in behavior.

- [ ] **Step 4: Rebuild `build_ui()` around individual controls**

Use this assembly shape:

```python
from app.gradio_presenter import (
    FEATURE_GROUPS,
    analyze_values,
    case_values,
    load_public_evidence,
    render_empty_result,
    render_public_evidence,
)

_CSS_PATH = Path(__file__).with_name("gradio_theme.css")


def build_ui(cfg: Config) -> gr.Blocks:
    try:
        service: PredictionService | None = PredictionService(cfg)
    except Exception as exc:
        service = None
        logger.warning("Gradio UI model unavailable (%s)", type(exc).__name__)

    test_path = Path(cfg.data.processed_dir) / "test.parquet"
    test_cases = pd.read_parquet(test_path) if test_path.exists() else None
    evidence = load_public_evidence(cfg.derived_results_dir / "summary.json")

    with gr.Blocks(
        title="Credit XAI Audit",
        css_paths=_CSS_PATH,
        fill_width=True,
        theme=gr.themes.Base(),
    ) as demo:
        gr.HTML(_header_and_hero_html(evidence), elem_id="audit-header")
        controls: dict[str, gr.Number] = {}
        with gr.Row(elem_classes="audit-workspace"):
            with gr.Column(scale=8, elem_classes="audit-input-column"):
                gr.HTML(_input_heading_html())
                with gr.Row(elem_classes="audit-case-controls"):
                    case_index = gr.Number(
                        value=0,
                        precision=0,
                        label="案例編號",
                        elem_classes="audit-case-index",
                    )
                    load_btn = gr.Button("載入測試案例", elem_classes="audit-secondary")
                case_note = gr.Markdown(elem_classes="audit-case-note")
                with gr.Tabs(elem_classes="audit-tabs"):
                    for label, features in FEATURE_GROUPS:
                        with gr.Tab(label):
                            with gr.Row(elem_classes="audit-feature-row"):
                                for feature in features:
                                    controls[feature] = gr.Number(
                                        value=_EXAMPLE[feature],
                                        precision=0,
                                        label=feature,
                                        elem_classes="audit-number",
                                    )
                analyze_btn = gr.Button(
                    "執行審計", variant="primary", elem_classes="audit-primary"
                )
            with gr.Column(scale=4, elem_classes="audit-result-column"):
                result_html = gr.HTML(render_empty_result(), elem_id="audit-result")
                attribution_table = gr.Dataframe(
                    headers=["特徵", "影響值 (link scale)", "方向"],
                    datatype=["str", "number", "str"],
                    interactive=False,
                    label="Top attributions",
                    elem_classes="audit-attributions",
                )
        gr.HTML(render_public_evidence(evidence), elem_id="audit-evidence")
        gr.HTML(_footer_html(), elem_id="audit-footer")

        ordered_controls = [controls[feature] for feature in FEATURES]

        def analyze(*values: object) -> tuple[str, pd.DataFrame]:
            return analyze_values(service, values)

        def load_case(index: object) -> tuple[Any, ...]:
            values, note = case_values(test_cases, index)
            if values is None:
                return (*[gr.skip() for _ in FEATURES], note)
            return (*values, note)

        analyze_btn.click(
            analyze,
            inputs=ordered_controls,
            outputs=[result_html, attribution_table],
        )
        load_btn.click(
            load_case,
            inputs=[case_index],
            outputs=[*ordered_controls, case_note],
        )
    return cast(gr.Blocks, demo)
```

Static HTML helpers in `app/gradio_ui.py` contain only approved fixed copy. Values from `PublicEvidence` are rendered by the presenter. Remove the old `gr.Dataframe` input and the old English result Markdown.

- [ ] **Step 5: Add CSS and component contract tests**

Add tests that read `app/gradio_theme.css` and assert:

```python
def test_gradio_css_uses_approved_square_tokens() -> None:
    css = Path("app/gradio_theme.css").read_text(encoding="utf-8").lower()
    for token in ("#f6f3ec", "#202d65", "#283b86", "#c88725", "#e4ad4f"):
        assert token in css
    assert "max-width: 1440px" in css
    assert "@media (max-width: 820px)" in css
    assert "border-radius: 0" in css
    assert "box-shadow" not in css
    assert "linear-gradient" not in css
```

Also assert that the Gradio config contains exactly one `執行審計` button, the result/evidence element IDs, and no input `dataframe` component.

- [ ] **Step 6: Run focused UI tests, Ruff, and strict mypy**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -v
.\.venv\Scripts\python.exe -m ruff format --check app\gradio_ui.py app\gradio_presenter.py tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\python.exe -m ruff check app\gradio_ui.py app\gradio_presenter.py tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\python.exe -m mypy --strict app\gradio_ui.py app\gradio_presenter.py
```

Expected: all commands pass.

- [ ] **Step 7: Commit the approved UI surface**

```powershell
git add app\gradio_ui.py app\gradio_theme.css tests\test_gradio.py
git commit -m "feat: redesign gradio audit console"
```

---

### Task 4: Browser, synthetic-bundle, accessibility, and design-system gate

**Files:**
- Create: `DESIGN.md`
- Create: `.impeccable/design.json`
- Modify only when an observed defect has a failing focused test: `app/gradio_ui.py`, `app/gradio_presenter.py`, `app/gradio_theme.css`, `tests/test_gradio.py`, `tests/test_gradio_presenter.py`

**Interfaces:**
- Consumes: mounted `/ui`, `configs/smoke.yaml` model-absent state, `configs/ci.yaml` synthetic LightGBM state, and the approved design specification.
- Produces: verified desktop/compact renders and a post-build design-system record derived from shipped CSS.

- [ ] **Step 1: Start the model-absent UI on a free local port**

Run in a persistent terminal:

```powershell
$env:PYTHONPATH = "src;."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 7860
```

Expected: `/health` returns 200 with `model_loaded=false`, and `/ui/` loads without a raw exception or filesystem path.

- [ ] **Step 2: Inspect desktop and compact layouts in one bounded browser pass**

Use the Codex in-app browser against `http://127.0.0.1:7860/ui/`.

Desktop checks at approximately 1440×1000:

- the product/thesis/boundary is legible in the first viewport;
- status cells, four KPI cells, tabs, case controls, numeric values, and the action are centered;
- narrative and evidence rows remain left-aligned;
- there is no decorative rounded corner, shadow, horizontal page scroll, or unnecessary blank card;
- all 23 labels exist in the DOM;
- `尚未載入` and em-dash result fields are visible;
- public evidence comes from the committed summary and shows the three correct explainer mappings.

Compact checks at approximately 390×844:

- header/status, thesis/boundary, workspace, and evidence stack in reading order;
- KPI cells form a 2×2 grid;
- feature controls wrap without page-level horizontal scrolling;
- focus rings and text remain visible at 200% browser zoom.

Save screenshots only under ignored `tmp/ui-review/`; do not add screenshots or browser state to the repository.

- [ ] **Step 3: If inspection finds a material defect, prove it with one focused failing test before editing**

Examples of acceptable tests are an absent class/element in `get_config_file()`, a CSS token/breakpoint mismatch, a raw error string in presenter output, or an output ordering mismatch. Add the single failing test, confirm red, make the smallest edit, rerun focused tests, and then perform one final desktop/compact confirmation. Do not conduct open-ended visual polishing after that second pass.

- [ ] **Step 4: Produce a local synthetic LightGBM bundle without real data or network access**

Run:

```powershell
$env:PYTHONPATH = "src;."
$env:CUDA_VISIBLE_DEVICES = ""
$env:OMP_NUM_THREADS = "2"
$env:MKL_NUM_THREADS = "2"
.\.venv\Scripts\python.exe -m credit_xai.cli data prepare --config configs\ci.yaml --force
.\.venv\Scripts\python.exe -m credit_xai.cli train --model lightgbm --config configs\ci.yaml
.\.venv\Scripts\python.exe -m credit_xai.cli calibrate --model lightgbm --config configs\ci.yaml
.\.venv\Scripts\python.exe -m credit_xai.cli explain --model lightgbm --config configs\ci.yaml --force
```

Expected: all outputs remain under ignored `tmp/ci/`; the config source is `synthetic`; no UCI ZIP/XLS, network request, formal result, or committed model path is touched.

- [ ] **Step 5: Launch the synthetic-bundle UI and exercise the full interaction**

Run in a persistent terminal:

```powershell
$env:CREDIT_XAI_CONFIG = "configs/ci.yaml"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 7861
```

In the browser:

- confirm `/health` is 200 with `model_loaded=true`;
- open `/ui/`, leave the example values intact, and click `執行審計`;
- verify calibrated and uncalibrated probabilities appear only after the click;
- verify model is `LightGBM`, explanation is `TreeSHAP`, and attribution rows render with direction text;
- verify the historical disclaimer remains visible and no approval/eligibility/accept/reject language appears;
- verify browser console has no application error;
- stop both Uvicorn processes after the checks.

- [ ] **Step 6: Run the Impeccable detector once and close its mechanical findings**

```powershell
$impeccableSkill = Join-Path $env:USERPROFILE ".codex\skills\impeccable"
node (Join-Path $impeccableSkill "scripts\detect.mjs") --json app\gradio_ui.py app\gradio_theme.css
```

Record the output. Fix only objective findings that conflict with the approved spec, accessibility, or responsive behavior; do not run the detector a second time.

- [ ] **Step 7: Perform the finish review inline because subagents are prohibited**

Use `impeccable/reference/degraded/finish-reviewer.md` with:

- the original owner request and approved specification;
- desktop and compact screenshots from `tmp/ui-review/`;
- the rendered model-absent and synthetic-success states;
- the detector output;
- the direction contract: Traditional Chinese Editorial Audit Console, square geometry, warm/indigo/amber palette, evidence-first, 8/4 workspace.

The verdict must separately score thesis, own-world fidelity, story/flow, first viewport, responsive form, accessibility, and truth/privacy. Apply one bounded material-fix batch if required and capture one confirmation set. Stop after that second inspection round.

- [ ] **Step 8: Write `DESIGN.md` from the shipped CSS, not the prototype**

Use canonical headings in this order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts. The frontmatter must contain the exact shipped color, type, spacing, zero-radius, and primary-button tokens. State explicitly:

- Creative North Star: `The Editorial Audit Console`;
- flat depth with rules and tonal fields, no shadows;
- square corners (`0px`) as the normative shape;
- 1440 px desktop container and 820 px compact breakpoint;
- 14 px body minimum and 12 px compact metadata minimum;
- center-only-for-short-equal-weight rule;
- no rounded dashboard cards, pills, fabricated numbers, decision language, or decorative animation.

- [ ] **Step 9: Write `.impeccable/design.json` without duplicating token primitives**

Use `schemaVersion: 2`. Include:

- color metadata keyed to the `DESIGN.md` frontmatter names;
- breakpoint `{ "name": "compact", "value": "820px" }`;
- representative self-contained CSS/HTML for the square primary button, numeric field, status cell, KPI cell, and evidence row;
- narrative rules copied verbatim from `DESIGN.md`;
- no `generatedAt` value derived from the current clock; use the fixed release date `2026-08-12T00:00:00+08:00` so the public file remains deterministic.

- [ ] **Step 10: Verify and commit the design-system record**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -v
git diff --check
git add DESIGN.md .impeccable\design.json app tests
git commit -m "docs: record gradio design system"
```

Expected: focused tests pass; the commit includes `app` or `tests` only if the bounded finish review required a tested correction.

---

### Task 5: Release hardening, Docker rebuild, and renewed Feature Freeze

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Modify: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: final UI source, tests, CSS, `DESIGN.md`, `.impeccable/design.json`, release verifier, package builder, and Docker Compose API service.
- Produces: a clean, locally verified, unpublished `main` commit with renewed Feature Freeze evidence.

- [ ] **Step 1: Run the complete fresh source gate**

```powershell
.\.venv\Scripts\python.exe -m uv lock --check
.\.venv\Scripts\python.exe -m ruff format --check src app tests
.\.venv\Scripts\python.exe -m ruff check src app tests
.\.venv\Scripts\python.exe -m mypy --strict src app
.\.venv\Scripts\python.exe -m pytest
```

Expected: the full collected suite passes. Confirm the collected count is at least 110 before retaining the public `110+` claim; if it is below 110, remove that KPI and its spec claim rather than lowering or inventing a number.

- [ ] **Step 2: Rebuild and inspect package artifacts in an ignored output root**

```powershell
.\.venv\Scripts\python.exe -m build --outdir tmp\ui-release\dist
```

Inspect the sdist and wheel exactly as the existing release tests do. The sdist must contain `app/gradio_ui.py`, `app/gradio_presenter.py`, and `app/gradio_theme.css`. Neither artifact may contain `.env`, raw data, models, results, `.superpowers`, browser screenshots, private notes, or absolute paths. Install the wheel with `[serve]` in an isolated ignored environment and rerun package import plus FastAPI `/health`; preserve the existing API-only wheel boundary rather than changing packaging in this UI task.

- [ ] **Step 3: Rebuild the CPU-only API image and smoke the changed UI layer**

```powershell
docker compose config --quiet
Measure-Command { docker compose build api }
docker image inspect credit-xai-audit:latest --format '{{.Id}}|{{.Size}}|{{.Config.User}}'
docker compose up -d api
```

Verify:

- configured/runtime user is `appuser`/UID 1000;
- no GPU device request, CUDA visibility, or `/dev/nvidia0` exists;
- `/health` is 200 with `model_loaded=false`;
- `/ui/` is 200 and contains `不只呈現模型預測，更檢驗解釋是否可信。`;
- the image still contains no raw dataset, model bundle, `.env`, private notes, browser artifacts, or committed `results/` payload;
- the request does not write into the repository mounts.

Stop and remove the Compose container and network after the smoke; retain only the audited image and record its new ID, size, build time, and zero running containers.

- [ ] **Step 4: Update changelog and verification evidence**

In `CHANGELOG.md`, add an `Unreleased` entry describing:

- Traditional Chinese evidence-first Gradio redesign;
- grouped 23-feature inputs and responsive layout;
- safe model-absent and invalid-input states;
- no model, metric, API, or decision-scope change.

In `docs/release/VERIFICATION.md`, add a dated UI renewal subsection with:

- focused and full test counts;
- desktop/compact visual and accessibility results;
- model-absent and synthetic LightGBM success results;
- exact explainer mapping and non-decision language check;
- package contents and isolated smoke;
- Docker image ID/size/build time, CPU/non-root/privacy results, and cleanup;
- the statement that Feature Freeze is renewed after this owner-approved UI-only change.

Do not add local absolute paths, screenshots, synthetic prediction values, or sensitive logs.

- [ ] **Step 5: Regenerate the release manifest and run every release gate**

```powershell
.\.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; print(write_release_manifest('.'))"
.\.venv\Scripts\python.exe -m credit_xai.release.verify all
git diff --check
```

Expected: all release gates pass and the manifest contains `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`, presenter source, CSS, tests, plan/spec, and updated documentation with correct hashes.

- [ ] **Step 6: Audit the final diff and public boundary**

```powershell
git status --short
git diff --stat d6a943f..HEAD
git diff --name-status
git remote -v
git tag --list
```

Confirm that only UI/presentation tests, approved design-system files, minimal release docs, and the manifest changed. Confirm no formal `results/`, `assets/`, model, data, API schema, pipeline, config, Dockerfile, or dependency file changed unless a verified release gate proved it necessary; if such a file appears, stop and explain the expansion before committing.

- [ ] **Step 7: Commit the renewed release evidence**

```powershell
git add CHANGELOG.md docs\release\VERIFICATION.md manifests\release_manifest.json
git commit -m "docs: verify gradio release gate"
```

- [ ] **Step 8: Run immutable post-commit checks**

```powershell
.\.venv\Scripts\python.exe -m credit_xai.release.verify all
git status --short --branch
git log -1 '--format=%H%n%an <%ae>%n%cn <%ce>%n%B'
git log -1 '--format=%B' | Select-String -Pattern 'Co-authored-by|Signed-off-by|Reviewed-by' -CaseSensitive:$false
git remote -v
```

Expected:

- release gates pass post-commit;
- branch is `main` and worktree is clean;
- author and committer are `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`;
- contributor trailer search returns no match;
- no remote exists and no remote action occurred;
- candidate is again under Feature Freeze.

---

## Plan Self-Review

- **Spec coverage:** Tasks 1–5 cover evidence truth, all four input groups, empty/loading/success/error states, Traditional Chinese copy, square visual grammar, typography/density, centered short content, responsive behavior, accessibility, public-boundary constraints, local synthetic interaction, package/Docker gates, design-system persistence, and renewed Feature Freeze.
- **Scope:** This is one UI/presentation subsystem. It does not change models, pipeline, API schema, dependencies, formal artifacts, or deployment.
- **Type consistency:** `PublicEvidence`, `FEATURE_GROUPS`, `feature_mapping`, `case_values`, `render_empty_result`, `render_public_evidence`, and `analyze_values` have one definition and identical signatures wherever consumed.
- **Truth boundary:** UI evidence validates the committed summary and fails closed; case results come only from `PredictionService`; `110+` is a tested lower-bound release claim.
- **No unresolved implementation choice:** file ownership, component structure, labels, palette, geometry, breakpoints, copy, error handling, tests, browser states, package policy, Docker scope, and commit boundaries are fixed above.
