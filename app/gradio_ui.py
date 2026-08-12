"""Evidence-first Gradio console for local historical model replay."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, cast

import gradio as gr
import pandas as pd
from app.gradio_presenter import (
    FEATURE_GROUPS,
    PublicEvidence,
    analyze_values,
    case_values,
    load_public_evidence,
    render_empty_result,
    render_public_evidence,
)

from credit_xai.config import Config
from credit_xai.constants import FEATURES
from credit_xai.serving.service import PredictionService

logger = logging.getLogger(__name__)

_CSS_PATH = Path(__file__).with_name("gradio_theme.css")
_ATTRIBUTION_COLUMNS = ["特徵", "影響值 (link scale)", "方向"]
_FINISH_CONTRACT = (
    "unreviewed and undocumented is unfinished; this build ends with the finish "
    "review, the verdict, and DESIGN.md"
)
_EXAMPLE = {
    "LIMIT_BAL": 200000,
    "SEX": 2,
    "EDUCATION": 2,
    "MARRIAGE": 1,
    "AGE": 35,
    "PAY_0": 0,
    "PAY_2": 0,
    "PAY_3": 0,
    "PAY_4": 0,
    "PAY_5": 0,
    "PAY_6": 0,
    "BILL_AMT1": 50000,
    "BILL_AMT2": 48000,
    "BILL_AMT3": 46000,
    "BILL_AMT4": 44000,
    "BILL_AMT5": 42000,
    "BILL_AMT6": 40000,
    "PAY_AMT1": 2000,
    "PAY_AMT2": 2000,
    "PAY_AMT3": 2000,
    "PAY_AMT4": 2000,
    "PAY_AMT5": 2000,
    "PAY_AMT6": 2000,
}


def _header_and_hero_html(evidence: PublicEvidence | None) -> str:
    model_count = str(evidence.model_count) if evidence is not None else "—"
    bootstrap = f"{evidence.bootstrap_iterations:,}" if evidence is not None else "—"
    explainer_count = str(evidence.explainer_count) if evidence is not None else "—"
    return f"""
    <!--
    THESIS: Evidence leads; this refuses the generic centered model-demo card.
    OWN-WORLD: Warm paper, structural indigo, amber signals, square rules, no ornament.
    STORY: Recognize audit depth, enter a historical case, inspect bounded evidence.
    FIRST VIEWPORT: Masthead, thesis and boundary, four evidence cells, then an 8/4 console.
    FORM: Owner-pinned Editorial Audit Console; seed owner-approved-editorial-audit-console.
    FINISH: {_FINISH_CONTRACT}
    -->
    <header class="audit-masthead">
      <div class="audit-product-lockup">
        <strong>Credit XAI Audit</strong>
        <span>Trustworthy AI 作品集</span>
      </div>
      <div class="audit-statuses" aria-label="Release 狀態">
        <div class="audit-status">僅使用<br>CPU</div>
        <div class="audit-status">可重現</div>
        <div class="audit-status">功能凍結</div>
      </div>
    </header>
    <section class="audit-hero" aria-labelledby="audit-title">
      <div class="audit-hero-copy">
        <p class="audit-eyebrow">2005 歷史資料教育審計</p>
        <h1 id="audit-title">不只呈現模型預測，更檢驗解釋是否可信。</h1>
        <p class="audit-method-line">
          Logistic · EBM · LightGBM　／　Calibration · Bootstrap · SHAP ·
          Faithfulness · Stability
        </p>
      </div>
      <aside class="audit-boundary" aria-label="使用範圍">
        <strong>使用範圍</strong>
        <span>
          僅供歷史模型重播與作品集展示；不適用於核貸決策、金融建議或因果推論。
        </span>
      </aside>
    </section>
    <section class="audit-kpis" aria-label="Release evidence 摘要">
      <div class="audit-kpi"><strong>{model_count}</strong><span>比較模型</span></div>
      <div class="audit-kpi"><strong>{bootstrap}</strong><span>Bootstrap 重抽樣</span></div>
      <div class="audit-kpi"><strong>{explainer_count}</strong><span>模型對應解釋方法</span></div>
      <div class="audit-kpi"><strong>110+</strong><span>測試通過</span></div>
    </section>
    """


def _input_heading_html() -> str:
    return """
    <div class="audit-input-heading">
      <span>01　案例輸入</span>
      <h2>建立歷史案例</h2>
      <p>23 個欄位 · integer-only · 僅在本機處理</p>
    </div>
    """


def _footer_html() -> str:
    return """
    <footer class="audit-footer">
      <span><strong>Credit XAI Audit</strong> · 2005 UCI historical educational audit</span>
      <span>不是 lending system · 不是金融建議 · 不是 causal study</span>
    </footer>
    """


def _theme() -> gr.Theme:
    return gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="amber",
        neutral_hue="slate",
        text_size="md",
        spacing_size="sm",
        radius_size="none",
        font=(
            "Noto Sans TC",
            "Microsoft JhengHei",
            "PingFang TC",
            "system-ui",
            "sans-serif",
        ),
    ).set(
        body_background_fill="#F6F3EC",
        body_background_fill_dark="#F6F3EC",
        body_text_color="#202838",
        body_text_color_dark="#202838",
        body_text_color_subdued="#606777",
        body_text_color_subdued_dark="#606777",
        body_text_size="15px",
        background_fill_primary="#FFFDF8",
        background_fill_primary_dark="#FFFDF8",
        background_fill_secondary="#F0F1F6",
        background_fill_secondary_dark="#F0F1F6",
        border_color_primary="#BFC1C8",
        border_color_primary_dark="#BFC1C8",
        block_background_fill="#FFFDF8",
        block_background_fill_dark="#FFFDF8",
        block_label_background_fill="#FFFDF8",
        block_label_background_fill_dark="#FFFDF8",
        block_label_text_color="#606777",
        block_label_text_color_dark="#606777",
        block_border_width="0px",
        block_radius="0px",
        block_shadow="none",
        block_shadow_dark="none",
        container_radius="0px",
        panel_background_fill="#F0F1F6",
        panel_background_fill_dark="#F0F1F6",
        shadow_drop="none",
        shadow_drop_lg="none",
        shadow_inset="none",
        input_background_fill="#FFFDF8",
        input_background_fill_dark="#FFFDF8",
        input_background_fill_focus="#FFFDF8",
        input_background_fill_focus_dark="#FFFDF8",
        input_background_fill_hover="#FFFDF8",
        input_background_fill_hover_dark="#FFFDF8",
        input_border_color="#BFC1C8",
        input_border_color_dark="#BFC1C8",
        input_border_width="1px",
        input_radius="0px",
        input_shadow="none",
        input_shadow_dark="none",
        input_shadow_focus="none",
        input_shadow_focus_dark="none",
        button_large_radius="0px",
        button_medium_radius="0px",
        button_small_radius="0px",
        button_primary_background_fill="#283B86",
        button_primary_background_fill_dark="#283B86",
        button_primary_background_fill_hover="#202D65",
        button_primary_background_fill_hover_dark="#202D65",
        button_primary_border_color="#283B86",
        button_primary_border_color_dark="#283B86",
        button_primary_text_color="#FFFDF8",
        button_primary_text_color_dark="#FFFDF8",
        button_primary_shadow="none",
        button_primary_shadow_hover="none",
        button_primary_shadow_active="none",
        button_primary_shadow_dark="none",
        button_primary_shadow_hover_dark="none",
        button_primary_shadow_active_dark="none",
        button_secondary_background_fill="#FFFDF8",
        button_secondary_background_fill_dark="#FFFDF8",
        button_secondary_background_fill_hover="#F0F1F6",
        button_secondary_background_fill_hover_dark="#F0F1F6",
        button_secondary_border_color="#283B86",
        button_secondary_border_color_dark="#283B86",
        button_secondary_text_color="#283B86",
        button_secondary_text_color_dark="#283B86",
        button_secondary_shadow="none",
        button_secondary_shadow_hover="none",
        button_secondary_shadow_active="none",
        button_secondary_shadow_dark="none",
        button_secondary_shadow_hover_dark="none",
        button_secondary_shadow_active_dark="none",
        button_transition="none",
        table_border_color="#BFC1C8",
        table_border_color_dark="#BFC1C8",
        table_even_background_fill="#FFFDF8",
        table_even_background_fill_dark="#FFFDF8",
        table_odd_background_fill="#F6F3EC",
        table_odd_background_fill_dark="#F6F3EC",
        table_text_color="#202838",
        table_text_color_dark="#202838",
        table_radius="0px",
    )


def _load_test_cases(cfg: Config) -> pd.DataFrame | None:
    test_path = Path(cfg.data.processed_dir) / "test.parquet"
    if not test_path.exists():
        return None
    try:
        return pd.read_parquet(test_path)
    except Exception as exc:
        logger.warning("Gradio test cases unavailable (%s)", type(exc).__name__)
        return None


def build_ui(cfg: Config) -> gr.Blocks:
    """Build the mounted Editorial Audit Console without changing serving logic."""
    try:
        service: PredictionService | None = PredictionService(cfg)
    except Exception as exc:
        service = None
        logger.warning("Gradio UI model unavailable (%s)", type(exc).__name__)

    test_cases = _load_test_cases(cfg)
    evidence = load_public_evidence(cfg.derived_results_dir / "summary.json")
    initial_case_note = case_values(test_cases, 0)[1]

    with gr.Blocks(
        title="Credit XAI Audit",
        css_paths=_CSS_PATH,
        fill_width=True,
        theme=_theme(),
    ) as demo:
        gr.HTML(
            _header_and_hero_html(evidence),
            elem_id="audit-header",
            padding=False,
        )
        controls: dict[str, gr.Number] = {}
        with gr.Row(elem_classes="audit-workspace"):
            with gr.Column(scale=8, min_width=560, elem_classes="audit-input-column"):
                with gr.Row(elem_classes="audit-input-toolbar"):
                    gr.HTML(
                        _input_heading_html(),
                        padding=False,
                        elem_classes="audit-input-heading-block",
                    )
                    with gr.Row(elem_classes="audit-case-controls"):
                        case_index = gr.Number(
                            value=0,
                            precision=0,
                            step=1,
                            label="案例編號",
                            elem_classes="audit-case-index",
                        )
                        load_btn = gr.Button(
                            "載入測試案例",
                            elem_classes="audit-secondary",
                        )
                case_note = gr.Markdown(
                    initial_case_note,
                    container=False,
                    elem_classes="audit-case-note",
                )
                with gr.Tabs(elem_classes="audit-tabs"):
                    for label, features in FEATURE_GROUPS:
                        with gr.Tab(label):
                            with gr.Row(elem_classes="audit-feature-row"):
                                for feature in features:
                                    controls[feature] = gr.Number(
                                        value=_EXAMPLE[feature],
                                        precision=0,
                                        step=1,
                                        label=feature,
                                        elem_classes="audit-number",
                                    )
                analyze_btn = gr.Button(
                    "執行審計",
                    variant="primary",
                    elem_classes="audit-primary",
                )
            with gr.Column(scale=4, min_width=300, elem_classes="audit-result-column"):
                result_html = gr.HTML(
                    render_empty_result(),
                    elem_id="audit-result",
                    padding=False,
                )
        attribution_table = gr.Dataframe(
            value=pd.DataFrame(columns=_ATTRIBUTION_COLUMNS),
            headers=_ATTRIBUTION_COLUMNS,
            datatype=["str", "number", "str"],
            interactive=False,
            wrap=True,
            max_height=300,
            visible=False,
            label="主要 attributions（link scale）",
            elem_classes="audit-attributions",
        )
        gr.HTML(
            render_public_evidence(evidence),
            elem_id="audit-evidence",
            padding=False,
        )
        gr.HTML(_footer_html(), elem_id="audit-footer", padding=False)

        ordered_controls = [controls[feature] for feature in FEATURES]

        def analyze(*values: object) -> tuple[str, gr.Dataframe]:
            html_result, frame = analyze_values(service, values)
            return html_result, gr.Dataframe(value=frame, visible=not frame.empty)

        def load_case(index: object) -> tuple[Any, ...]:
            values, note = case_values(test_cases, index)
            if values is None:
                return (*[gr.skip() for _ in FEATURES], note)
            return (*values, note)

        analyze_btn.click(
            analyze,
            inputs=ordered_controls,
            outputs=[result_html, attribution_table],
            show_progress="minimal",
        )
        load_btn.click(
            load_case,
            inputs=[case_index],
            outputs=[*ordered_controls, case_note],
            show_progress="minimal",
        )
    return cast(gr.Blocks, demo)
