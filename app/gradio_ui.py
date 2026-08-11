"""Gradio UI: browse dataset cases or enter features manually; shows the
calibrated probability and the model's local explanation. Mounted at /ui."""

from __future__ import annotations

import logging
from pathlib import Path

import gradio as gr
import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import DEMO_SCOPE, DISCLAIMER, FEATURES, TARGET
from credit_xai.serving.service import PredictionService

logger = logging.getLogger(__name__)

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


def build_ui(cfg: Config) -> gr.Blocks:
    try:
        service: PredictionService | None = PredictionService(cfg)
        load_error = None
    except Exception as exc:
        service = None
        load_error = f"{type(exc).__name__}: {exc}"
        logger.warning("Gradio UI: model not loaded (%s)", load_error)

    test_path = Path(cfg.data.processed_dir) / "test.parquet"
    test_cases = pd.read_parquet(test_path) if test_path.exists() else None

    def _frame(values: pd.DataFrame) -> dict[str, int]:
        row = values.iloc[0]
        return {f: int(row[f]) for f in FEATURES}

    def analyze(values: pd.DataFrame):
        if service is None:
            return f"**Model not loaded.** {load_error}", pd.DataFrame()
        try:
            result = service.explain(_frame(values))
        except Exception as exc:
            return f"**Input error:** {exc}", pd.DataFrame()
        prob = result["probability_calibrated"]
        text = (
            f"### Historical model replay probability: **{prob:.1%}**\n"
            f"(uncalibrated {result['probability_uncalibrated']:.1%}; model "
            f"`{result['model']}`, calibration `{result['calibration_method']}`, "
            f"explainer `{result['method']}`)\n\n> {DISCLAIMER} {DEMO_SCOPE}"
        )
        table = pd.DataFrame(result["top_attributions"]).round(4)
        return text, table

    def load_case(index: int):
        if test_cases is None:
            return gr.skip(), "No processed dataset available (run `data prepare`)."
        index = int(index) % len(test_cases)
        row = test_cases.iloc[index]
        values = pd.DataFrame([[int(row[f]) for f in FEATURES]], columns=FEATURES)
        return values, f"Loaded test case {index} (recorded outcome: {int(row[TARGET])})."

    with gr.Blocks(title="credit-xai-audit") as demo:
        gr.Markdown(f"# credit-xai-audit\n> **{DISCLAIMER}**\n\n{DEMO_SCOPE}")
        with gr.Row():
            case_index = gr.Number(value=0, precision=0, label="Test case index")
            load_btn = gr.Button("Browse dataset case")
        case_note = gr.Markdown()
        grid = gr.Dataframe(
            value=pd.DataFrame([_EXAMPLE], columns=FEATURES),
            headers=list(FEATURES),
            datatype=["number"] * len(FEATURES),
            row_count=(1, "fixed"),
            label="Features (edit manually or load a dataset case)",
        )
        analyze_btn = gr.Button("Run historical audit", variant="primary")
        result_md = gr.Markdown()
        attribution_table = gr.Dataframe(label="Top attributions (link scale)")

        load_btn.click(load_case, inputs=[case_index], outputs=[grid, case_note])
        analyze_btn.click(analyze, inputs=[grid], outputs=[result_md, attribution_table])
        gr.Markdown(f"---\n{DISCLAIMER} {DEMO_SCOPE}")
    return demo
