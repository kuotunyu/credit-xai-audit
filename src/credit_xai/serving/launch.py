"""The `serve` step: uvicorn wrapper mounting the Gradio UI at /ui."""

from __future__ import annotations

import logging

from credit_xai.config import Config

logger = logging.getLogger(__name__)


def run(cfg: Config, host: str | None = None, port: int | None = None) -> None:
    import uvicorn

    from credit_xai.serving.api import create_app

    app = create_app(cfg)
    try:
        import gradio as gr
        from app.gradio_ui import build_ui

        app = gr.mount_gradio_app(app, build_ui(cfg), path="/ui")
        logger.info("Gradio UI mounted at /ui")
    except Exception as exc:
        logger.warning(
            "Gradio UI not mounted (%s: %s); API still available", type(exc).__name__, exc
        )

    uvicorn.run(
        app,
        host=host or cfg.serve.host,
        port=port or cfg.serve.port,
        log_level="info",
    )
