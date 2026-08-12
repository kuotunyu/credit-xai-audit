"""Pure presentation helpers for the public Gradio audit console."""

from __future__ import annotations

import html
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from credit_xai.constants import MODEL_NAMES

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
