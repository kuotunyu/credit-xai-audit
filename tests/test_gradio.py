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
    for forbidden in (
        "Predict + explain",
        "Run historical audit",
        "approval",
        "eligibility",
    ):
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
    tab_labels = {
        component["props"].get("label")
        for component in config["components"]
        if component["type"] == "tabitem"
    }

    assert {"基本資料", "還款狀態", "帳單金額", "繳款金額"} <= tab_labels
    assert config["fill_width"] is True
    assert "audit-workspace" in text


def test_gradio_has_one_primary_audit_action_and_named_regions(test_config) -> None:
    config, text = _config(test_config)
    audit_buttons = [
        component
        for component in config["components"]
        if component["type"] == "button" and component["props"].get("value") == "執行審計"
    ]

    assert len(audit_buttons) == 1
    assert '"elem_id": "audit-result"' in text
    assert '"elem_id": "audit-evidence"' in text


def test_gradio_uses_output_only_attribution_table(test_config) -> None:
    config, _ = _config(test_config)
    dataframes = [
        component for component in config["components"] if component["type"] == "dataframe"
    ]

    assert len(dataframes) == 1
    assert dataframes[0]["props"]["interactive"] is False


def test_gradio_css_uses_approved_square_tokens() -> None:
    css = Path("app/gradio_theme.css").read_text(encoding="utf-8").lower()

    for token in ("#f6f3ec", "#202d65", "#283b86", "#c88725", "#e4ad4f"):
        assert token in css
    assert "max-width: 1440px" in css
    assert "@media (max-width: 820px)" in css
    assert "border-radius: 0" in css
    assert "box-shadow" not in css
    assert "linear-gradient" not in css
