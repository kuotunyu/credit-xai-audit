from __future__ import annotations

import json

from app.gradio_ui import build_ui

from credit_xai.constants import DEMO_SCOPE


def test_gradio_config_uses_historical_audit_language(test_config) -> None:
    config_text = json.dumps(build_ui(test_config).get_config_file())

    assert DEMO_SCOPE in config_text
    assert "Run historical audit" in config_text
    assert "Historical model replay" in config_text
    assert "Predict + explain" not in config_text
