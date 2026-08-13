"""Thin ASGI entry point: `uvicorn app.main:app` from the repo root.

Config path comes from the CREDIT_XAI_CONFIG env var (default configs/smoke.yaml).
All logic lives in credit_xai.serving.
"""

from __future__ import annotations

import os

from credit_xai.config import load_config
from credit_xai.serving.api import create_app
from credit_xai.utils.logging import setup_logging

setup_logging(os.environ.get("CREDIT_XAI_LOG_LEVEL", "INFO"))
_cfg = load_config(os.environ.get("CREDIT_XAI_CONFIG", "configs/smoke.yaml"))
app = create_app(_cfg)

try:  # optional UI; the API works without gradio installed
    from app.gradio_ui import mount_ui

    app = mount_ui(app, _cfg, path="/ui")
except Exception:  # pragma: no cover - UI is best-effort here
    pass
