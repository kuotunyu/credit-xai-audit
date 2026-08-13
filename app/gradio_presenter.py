"""Pure presentation helpers for the public Gradio audit console."""

from __future__ import annotations

import html
import json
import logging
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from credit_xai.constants import (
    BILL_FEATURES,
    DEMO_SCOPE,
    DISCLAIMER,
    FEATURES,
    MODEL_NAMES,
    PAY_AMT_FEATURES,
    PAY_FEATURES,
    TARGET,
)
from credit_xai.data.schema import SchemaError
from credit_xai.serving.service import ServiceError

logger = logging.getLogger(__name__)

_MODEL_LABELS = {
    "logistic": "Logistic",
    "ebm": "EBM",
    "lightgbm": "LightGBM",
}
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

FEATURE_LABELS: dict[str, str] = {
    "LIMIT_BAL": "信用額度",
    "SEX": "性別",
    "EDUCATION": "教育程度",
    "MARRIAGE": "婚姻狀態",
    "AGE": "年齡",
    "PAY_0": "9 月還款狀態",
    "PAY_2": "8 月還款狀態",
    "PAY_3": "7 月還款狀態",
    "PAY_4": "6 月還款狀態",
    "PAY_5": "5 月還款狀態",
    "PAY_6": "4 月還款狀態",
    "BILL_AMT1": "9 月帳單金額",
    "BILL_AMT2": "8 月帳單金額",
    "BILL_AMT3": "7 月帳單金額",
    "BILL_AMT4": "6 月帳單金額",
    "BILL_AMT5": "5 月帳單金額",
    "BILL_AMT6": "4 月帳單金額",
    "PAY_AMT1": "9 月繳款金額",
    "PAY_AMT2": "8 月繳款金額",
    "PAY_AMT3": "7 月繳款金額",
    "PAY_AMT4": "6 月繳款金額",
    "PAY_AMT5": "5 月繳款金額",
    "PAY_AMT6": "4 月繳款金額",
}

FEATURE_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("基本資料", ("LIMIT_BAL", "AGE", "SEX", "EDUCATION", "MARRIAGE")),
    ("還款狀態", tuple(PAY_FEATURES)),
    ("帳單金額", tuple(BILL_FEATURES)),
    ("繳款金額", tuple(PAY_AMT_FEATURES)),
)
_ATTRIBUTION_COLUMNS = ["特徵", "影響值 (link scale)", "方向"]


@dataclass(frozen=True)
class EvidenceModelRow:
    """One verified model-to-explanation mapping for public display."""

    model: str
    calibration: str
    explanation: str


@dataclass(frozen=True)
class PublicEvidence:
    """Minimal verified release evidence used by the public UI."""

    model_count: int
    bootstrap_iterations: int
    explainer_count: int
    models: tuple[EvidenceModelRow, ...]
    stability_complete: bool
    faithfulness_complete: bool
    small_cell_ci_suppressed: bool


class ExplanationService(Protocol):
    """Serving boundary used by the pure presenter."""

    def explain(self, features: dict[str, int]) -> dict[str, Any]: ...


def feature_mapping(values: Sequence[object]) -> dict[str, int]:
    """Convert UI values into the canonical integer-only serving payload."""
    if len(values) != len(FEATURES):
        raise ValueError("必須提供 23 個整數欄位。")
    converted: list[int] = []
    for value in values:
        if value is None:
            raise ValueError("必須提供 23 個整數欄位。")
        try:
            number = float(str(value))
        except (TypeError, ValueError) as exc:
            raise ValueError("必須提供 23 個整數欄位。") from exc
        if not number.is_integer():
            raise ValueError("必須提供 23 個整數欄位。")
        converted.append(int(number))
    return dict(zip(FEATURES, converted, strict=True))


def case_values(
    test_cases: pd.DataFrame | None, index: object
) -> tuple[tuple[int, ...] | None, str]:
    """Return one processed case in canonical order without leaking raw errors."""
    if test_cases is None or test_cases.empty:
        return None, "目前沒有已處理的測試案例；仍可手動輸入 23 個欄位。"
    try:
        numeric = float(str(index))
    except (TypeError, ValueError, OverflowError):
        return None, "案例編號必須是有限整數。"
    if not math.isfinite(numeric) or not numeric.is_integer():
        return None, "案例編號必須是有限整數。"
    resolved = int(numeric)
    if not 0 <= resolved < len(test_cases):
        return None, f"案例編號必須介於 0 與 {len(test_cases) - 1} 之間。"
    try:
        row = test_cases.iloc[resolved]
        values = tuple(int(row[feature]) for feature in FEATURES)
        outcome = int(row[TARGET])
    except (KeyError, TypeError, ValueError, OverflowError):
        return None, "測試案例資料格式不完整；請改用手動輸入。"
    return values, f"已載入測試案例 {resolved}；歷史觀察結果：{outcome}。"


def _empty_attributions() -> pd.DataFrame:
    return pd.DataFrame(columns=_ATTRIBUTION_COLUMNS)


def _result_shell(
    *,
    state: str,
    title: str,
    body: str,
    calibrated: str = "—",
    uncalibrated: str = "—",
    model: str = "—",
    calibration: str = "—",
    explanation: str = "—",
) -> str:
    values = {
        "state": html.escape(state),
        "title": html.escape(title),
        "body": html.escape(body),
        "calibrated": html.escape(calibrated),
        "uncalibrated": html.escape(uncalibrated),
        "model": html.escape(model),
        "calibration": html.escape(calibration),
        "explanation": html.escape(explanation),
        "disclaimer": html.escape(DISCLAIMER),
        "scope": html.escape(DEMO_SCOPE),
    }
    return f"""
    <section class="audit-result-shell" aria-live="polite">
      <div class="audit-result-state">{values["state"]}</div>
      <h2>{values["title"]}</h2>
      <p class="audit-result-body">{values["body"]}</p>
      <div class="audit-probability">
        <span>Calibrated probability</span>
        <strong>{values["calibrated"]}</strong>
      </div>
      <dl class="audit-result-meta">
        <div><dt>Uncalibrated probability</dt><dd>{values["uncalibrated"]}</dd></div>
        <div><dt>模型</dt><dd>{values["model"]}</dd></div>
        <div><dt>Calibration</dt><dd>{values["calibration"]}</dd></div>
        <div><dt>解釋方法</dt><dd>{values["explanation"]}</dd></div>
      </dl>
      <div class="audit-result-boundary">
        <strong>僅供 2005 歷史資料教育審計</strong>
        <span>不是現實世界風險評估、金融建議或因果證明。</span>
        <small lang="en">{values["disclaimer"]} {values["scope"]}</small>
      </div>
    </section>
    """


def render_empty_result() -> str:
    """Render the honest public state when no local bundle is available."""
    return _result_shell(
        state="尚未載入",
        title="公開版本不包含 model bundle",
        body="載入本機驗證模型後才顯示結果；此處不使用示意數值。",
    )


def _render_input_error(detail: str = "輸入資料無法完成審計，請檢查欄位後再試。") -> str:
    return _result_shell(
        state="無法完成",
        title="輸入資料無法完成審計",
        body=detail,
    )


def _render_service_error() -> str:
    return _result_shell(
        state="暫時無法回應",
        title="分析服務暫時無法回應",
        body="目前無法完成本機歷史模型重播；請稍後再試。",
    )


def _validated_result(result: dict[str, Any]) -> tuple[float, float, str, str, str]:
    model = str(result["model"])
    method = str(result["method"])
    if model not in _MODEL_LABELS or method != _EXPECTED_EXPLANATIONS[model]:
        raise ValueError("model and explanation method do not match")
    if result.get("output_type") != "historical_model_replay":
        raise ValueError("unexpected serving output type")
    calibrated = float(result["probability_calibrated"])
    uncalibrated = float(result["probability_uncalibrated"])
    if not all(
        math.isfinite(value) and 0.0 <= value <= 1.0 for value in (calibrated, uncalibrated)
    ):
        raise ValueError("invalid probability")
    calibration = str(result["calibration_method"])
    return calibrated, uncalibrated, model, method, calibration


def _render_success_result(result: dict[str, Any]) -> str:
    calibrated, uncalibrated, model, method, calibration = _validated_result(result)
    return _result_shell(
        state="已完成",
        title="歷史模型重播結果",
        body="結果來自目前載入且通過完整性驗證的本機 bundle。",
        calibrated=f"{calibrated:.1%}",
        uncalibrated=f"{uncalibrated:.1%}",
        model=_MODEL_LABELS[model],
        calibration=calibration,
        explanation=_EXPLANATION_LABELS[method],
    )


def _attribution_frame(result: dict[str, Any]) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for raw in result["top_attributions"]:
        feature = html.escape(str(raw["feature"]))
        attribution = float(raw["attribution"])
        if not math.isfinite(attribution):
            raise ValueError("invalid attribution")
        direction = "增加" if attribution > 0 else "降低" if attribution < 0 else "中性"
        records.append(
            {
                "特徵": feature,
                "影響值 (link scale)": round(attribution, 4),
                "方向": direction,
            }
        )
    return pd.DataFrame.from_records(records, columns=_ATTRIBUTION_COLUMNS)


def analyze_values(
    service: ExplanationService | None, values: Sequence[object]
) -> tuple[str, pd.DataFrame]:
    """Run a local historical replay and return sanitized presentation values."""
    if service is None:
        return render_empty_result(), _empty_attributions()
    try:
        features = feature_mapping(values)
    except ValueError:
        return _render_input_error("必須提供 23 個整數欄位。"), _empty_attributions()
    try:
        result = service.explain(features)
    except (SchemaError, ServiceError) as exc:
        logger.info("Gradio input rejected (%s)", type(exc).__name__)
        return _render_input_error(), _empty_attributions()
    except Exception as exc:
        logger.warning("Gradio audit failed (%s)", type(exc).__name__)
        return _render_service_error(), _empty_attributions()
    try:
        return _render_success_result(result), _attribution_frame(result)
    except Exception as exc:
        logger.warning("Gradio result rejected (%s)", type(exc).__name__)
        return _render_service_error(), _empty_attributions()


def load_public_evidence(path: Path) -> PublicEvidence | None:
    """Validate committed summary evidence and fail closed on any mismatch."""
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
            bootstraps.add(int(model["test_metrics"]["calibrated_ci"]["roc_auc"]["n_boot"]))
            rank = model["explain"]["rank_stability"]
            stability_complete &= (
                int(rank["refit"]["n_iterations"]) == 20
                and int(rank["resample"]["n_iterations"]) == 200
            )
            faithfulness_complete &= int(model["explain"]["faithfulness"]["n_instances"]) == 2000
            small_groups = [
                group for group in model["groups"]["by_group"].values() if group["small_cell"]
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

        if bootstraps != {1000} or not all(
            (
                stability_complete,
                faithfulness_complete,
                small_cell_ci_suppressed,
            )
        ):
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


def render_public_evidence(evidence: PublicEvidence | None) -> str:
    """Render verified evidence without inventing values for a failed contract."""
    if evidence is None:
        return """
        <section class="audit-evidence-section" aria-labelledby="evidence-title">
          <div class="audit-section-heading">
            <p class="audit-section-index">公開證據</p>
            <h2 id="evidence-title">公開驗證證據</h2>
          </div>
          <div class="audit-evidence-unavailable" role="status">
            <strong>公開證據暫時無法載入</strong>
            <span>頁面不會以預設值替代缺失或不一致的 release evidence。</span>
          </div>
        </section>
        """

    rows = "".join(
        "<tr>"
        f'<th scope="row">{html.escape(row.model)}</th>'
        f"<td>{html.escape(row.calibration)}</td>"
        f"<td>{html.escape(row.explanation)}</td>"
        '<td><span class="audit-verified-mark" aria-hidden="true">✓</span> 已驗證</td>'
        "</tr>"
        for row in evidence.models
    )
    return f"""
    <section class="audit-evidence-section" aria-labelledby="evidence-title">
      <div class="audit-section-heading">
        <p class="audit-section-index">公開證據</p>
        <h2 id="evidence-title">公開驗證證據</h2>
        <p>每一項展示都能回到 committed artifact；不是裝飾性宣稱。</p>
      </div>
      <div class="audit-evidence-grid">
        <div class="audit-evidence-table-wrap">
          <table class="audit-evidence-table">
            <caption>模型、Calibration 與 explanation method 對應</caption>
            <thead>
              <tr>
                <th>模型</th><th>Calibration 選擇</th><th>解釋方法</th><th>狀態</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <div class="audit-evidence-checks" aria-label="驗證範圍">
          <h3>驗證範圍</h3>
          <ul>
            <li>
              <span aria-hidden="true">✓</span>
              {evidence.bootstrap_iterations:,} 次 stratified Bootstrap CI
            </li>
            <li>
              <span aria-hidden="true">✓</span>
              Explanation Stability：20 次 refit、200 次 resample
            </li>
            <li>
              <span aria-hidden="true">✓</span>
              Faithfulness perturbation：2,000 筆；不作 causal proof
            </li>
            <li><span aria-hidden="true">✓</span> Group metrics 小樣本 CI suppression</li>
            <li>
              <span aria-hidden="true">✓</span>
              CPU-only Docker synthetic smoke，證據見 VERIFICATION
            </li>
          </ul>
        </div>
      </div>
      <p class="audit-evidence-links">
        證據索引：<code>README.md</code> · <code>MODEL_CARD.md</code> ·
        <code>DATA_CARD.md</code> · <code>docs/release/VERIFICATION.md</code>
      </p>
    </section>
    """
