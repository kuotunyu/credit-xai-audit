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
        from app.gradio_ui import mount_ui

        app = mount_ui(app, cfg, path="/ui")
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
