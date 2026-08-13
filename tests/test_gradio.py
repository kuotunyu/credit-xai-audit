from __future__ import annotations

import json
import warnings
from pathlib import Path

from app.gradio_presenter import FEATURE_GROUPS, FEATURE_LABELS
from app.gradio_ui import _theme, build_ui

from credit_xai.constants import DEMO_SCOPE, FEATURES


def _config(test_config) -> tuple[dict, str]:
    config = build_ui(test_config).get_config_file()
    return config, json.dumps(config, ensure_ascii=False)


def test_gradio_build_avoids_gradio6_moved_parameter_warnings(test_config) -> None:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "error",
            message="The parameters have been moved from the Blocks constructor.*",
            category=UserWarning,
        )
        build_ui(test_config)


def test_mounted_gradio_keeps_the_audit_stylesheet(test_config) -> None:
    from app.gradio_ui import mount_ui

    from credit_xai.serving.api import create_app

    app = mount_ui(create_app(test_config), test_config, path="/ui")
    mounted_ui = next(route.app for route in app.routes if getattr(route, "path", None) == "/ui")
    config = mounted_ui.get_blocks().config

    assert "--audit-field: #f6f3ec" in config["css"].lower()


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
        "DESIGN.md",
        "approval",
        "eligibility",
    ):
        assert forbidden not in text


def test_gradio_pairs_readable_labels_with_canonical_feature_codes(test_config) -> None:
    config, _ = _config(test_config)
    numbers = [
        component
        for component in config["components"]
        if component["type"] == "number"
        and "audit-number" in component.get("props", {}).get("elem_classes", [])
    ]

    assert len(numbers) == len(FEATURES) == 23
    assert {
        component["props"].get("info"): component["props"].get("label") for component in numbers
    } == {feature: FEATURE_LABELS[feature] for feature in FEATURES}


def test_gradio_exposes_four_complete_feature_group_ledgers(test_config) -> None:
    config, text = _config(test_config)
    components = {component["id"]: component for component in config["components"]}
    layout_nodes = [config["layout"]]
    for node in layout_nodes:
        layout_nodes.extend(node.get("children", []))

    groups = [
        component
        for component in config["components"]
        if "audit-feature-group" in component.get("props", {}).get("elem_classes", [])
    ]

    assert not [component for component in config["components"] if component["type"] == "tabitem"]
    assert len(groups) == len(FEATURE_GROUPS) == 4
    for group, (label, features) in zip(groups, FEATURE_GROUPS, strict=True):
        group_node = next(node for node in layout_nodes if node["id"] == group["id"])
        descendants = list(group_node.get("children", []))
        for node in descendants:
            descendants.extend(node.get("children", []))
        child_components = [components[node["id"]] for node in descendants]
        heading = next(component for component in child_components if component["type"] == "html")
        number_components = [
            component for component in child_components if component["type"] == "number"
        ]

        assert label in heading["props"]["value"]
        assert f"{len(features)} 欄" in heading["props"]["value"]
        assert [component["props"].get("info") for component in number_components] == list(features)
        assert [component["props"].get("label") for component in number_components] == [
            FEATURE_LABELS[feature] for feature in features
        ]

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


def test_gradio_groups_heading_and_case_actions_in_one_toolbar(test_config) -> None:
    config, _ = _config(test_config)
    components = {component["id"]: component for component in config["components"]}

    toolbar = next(
        component
        for component in config["components"]
        if "audit-input-toolbar" in component.get("props", {}).get("elem_classes", [])
    )
    layout_nodes = [config["layout"]]
    for node in layout_nodes:
        layout_nodes.extend(node.get("children", []))
    toolbar_node = next(node for node in layout_nodes if node["id"] == toolbar["id"])
    child_components = [components[child["id"]] for child in toolbar_node["children"]]

    assert [component["type"] for component in child_components] == ["html", "row"]
    assert "audit-input-heading-block" in child_components[0]["props"]["elem_classes"]
    assert "audit-case-controls" in child_components[1]["props"]["elem_classes"]


def test_gradio_groups_case_context_and_primary_action_in_one_footer(
    test_config,
) -> None:
    config, _ = _config(test_config)
    components = {component["id"]: component for component in config["components"]}
    layout_nodes = [config["layout"]]
    for node in layout_nodes:
        layout_nodes.extend(node.get("children", []))

    footer = next(
        component
        for component in config["components"]
        if "audit-input-footer" in component.get("props", {}).get("elem_classes", [])
    )
    footer_node = next(node for node in layout_nodes if node["id"] == footer["id"])
    descendants = list(footer_node.get("children", []))
    for node in descendants:
        descendants.extend(node.get("children", []))
    child_components = [components[node["id"]] for node in descendants]

    assert [component["type"] for component in child_components] == ["markdown", "button"]
    assert "audit-case-note" in child_components[0]["props"]["elem_classes"]
    assert "audit-primary" in child_components[1]["props"]["elem_classes"]


def test_gradio_places_attributions_after_workspace_and_hides_them_initially(
    test_config,
) -> None:
    config, _ = _config(test_config)
    workspace = next(
        component
        for component in config["components"]
        if "audit-workspace" in component.get("props", {}).get("elem_classes", [])
    )
    attributions = next(
        component
        for component in config["components"]
        if "audit-attributions" in component.get("props", {}).get("elem_classes", [])
    )
    layout_nodes = [config["layout"]]
    for node in layout_nodes:
        layout_nodes.extend(node.get("children", []))
    workspace_node = next(node for node in layout_nodes if node["id"] == workspace["id"])
    workspace_descendants = list(workspace_node.get("children", []))
    for node in workspace_descendants:
        workspace_descendants.extend(node.get("children", []))

    assert attributions["id"] not in {node["id"] for node in workspace_descendants}
    assert attributions["props"]["visible"] is False


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
    assert "max-width: 1600px" in css
    for token in (
        "--audit-type-body: 1.0625rem",
        "--audit-type-support: 1rem",
        "--audit-type-label: 0.96875rem",
        "--audit-type-meta: 0.9375rem",
        "--audit-type-value: 1.1875rem",
    ):
        assert token in css
    assert "@media (max-width: 820px)" in css
    assert "border-radius: 0" in css
    assert "box-shadow" not in css
    assert "linear-gradient" not in css


def test_gradio_theme_keeps_the_approved_light_palette_in_dark_preference() -> None:
    tokens = _theme().to_dict()["theme"]

    assert tokens["body_background_fill_dark"] == "#F6F3EC"
    assert tokens["body_text_color_dark"] == "#202838"
    assert tokens["block_background_fill_dark"] == "#FFFDF8"
    assert tokens["input_background_fill_dark"] == "#FFFDF8"
    assert tokens["button_secondary_background_fill_dark"] == "#FFFDF8"
    assert tokens["button_secondary_text_color_dark"] == "#283B86"
    assert tokens["shadow_drop"] == "none"
    assert tokens["shadow_drop_lg"] == "none"
    assert tokens["button_transition"] == "none"


def test_gradio_css_uses_complete_responsive_open_sections() -> None:
    css = Path("app/gradio_theme.css").read_text(encoding="utf-8").lower()

    assert (
        "color: var(--audit-white)"
        in css.split(".audit-product-lockup strong", maxsplit=1)[1].split("}", maxsplit=1)[0]
    )
    assert ".audit-tabs" not in css
    five_track_rule = css.split(".audit-feature-count-5 .audit-feature-row > .form", maxsplit=1)[
        1
    ].split("}", maxsplit=1)[0]
    six_track_rule = css.split(".audit-feature-count-6 .audit-feature-row > .form", maxsplit=1)[
        1
    ].split("}", maxsplit=1)[0]
    assert "grid-template-columns: repeat(6, minmax(0, 1fr))" in five_track_rule
    assert "grid-template-columns: repeat(6, minmax(0, 1fr))" in six_track_rule
    first_field_rule = css.split(".audit-feature-count-5 .audit-number:first-child", maxsplit=1)[
        1
    ].split("}", maxsplit=1)[0]
    assert "grid-column: span 2" in first_field_rule
    compact = css.split("@media (max-width: 820px)", maxsplit=1)[1].split(
        "@media (max-width: 520px)", maxsplit=1
    )[0]
    phone = css.split("@media (max-width: 520px)", maxsplit=1)[1]
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in compact
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in phone
    assert "min-width: 0" in phone

    workspace_rule = css.split(".audit-workspace {", maxsplit=1)[1].split("}", maxsplit=1)[0]
    group_rule = css.split(".audit-feature-group {", maxsplit=1)[1].split("}", maxsplit=1)[0]
    heading_rule = css.split(".audit-group-heading-block {", maxsplit=1)[1].split("}", maxsplit=1)[
        0
    ]
    number_rule = css.split(".audit-number {", maxsplit=1)[1].split("}", maxsplit=1)[0]
    input_rule = css.split(".audit-number input {", maxsplit=1)[1].split("}", maxsplit=1)[0]
    toolbar_rule = css.split(".audit-input-toolbar {", maxsplit=1)[1].split("}", maxsplit=1)[0]
    footer_rule = css.split(".audit-input-footer {", maxsplit=1)[1].split("}", maxsplit=1)[0]

    assert "align-items: flex-start" in workspace_rule
    assert "display: block" in group_rule
    assert "grid-template-columns" not in group_rule
    assert "width: 100%" in heading_rule
    assert "border-right: 0" in heading_rule
    assert "border-left: 0" in number_rule
    assert "border-bottom: 1px solid var(--audit-rule)" in input_rule
    assert "padding-inline: 0.75rem" in toolbar_rule
    assert "padding-inline: 0.75rem" in footer_rule
    assert ".audit-number + .audit-number" not in css


def test_gradio_css_removes_framework_gutters_and_keeps_labels_readable() -> None:
    css = Path("app/gradio_theme.css").read_text(encoding="utf-8").lower()

    app_rule = css.split(".gradio-container main.app", maxsplit=1)[1].split("}", maxsplit=1)[0]
    assert "padding: 0" in app_rule
    assert "max-width: 100%" in app_rule
    label_rule = css.split('.audit-number [data-testid="block-info"]', maxsplit=1)[1].split(
        "}", maxsplit=1
    )[0]
    assert "color: var(--audit-muted)" in label_rule
