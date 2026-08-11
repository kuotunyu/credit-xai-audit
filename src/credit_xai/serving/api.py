"""FastAPI app factory. Endpoints: GET /health, POST /predict, POST /explain,
GET /model-card. Every response that carries a prediction or explanation also
carries the fixed disclaimer."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from credit_xai import __version__
from credit_xai.config import Config
from credit_xai.constants import DISCLAIMER, FEATURES
from credit_xai.data.schema import SchemaError
from credit_xai.serving.service import PredictionService, ServiceError

logger = logging.getLogger(__name__)

_EXAMPLE_FEATURES = {
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


class FeaturesPayload(BaseModel):
    features: dict[str, int] = Field(
        description=f"all 23 features: {', '.join(FEATURES)}",
        examples=[_EXAMPLE_FEATURES],
    )


def create_app(cfg: Config, model_name: str | None = None) -> FastAPI:
    app = FastAPI(
        title="credit-xai-audit API",
        version=__version__,
        description=DISCLAIMER,
    )
    state: dict[str, Any] = {"service": None, "error": None}
    try:
        state["service"] = PredictionService(cfg, model_name)
    except Exception as exc:  # keep /health alive; surface the reason on use
        state["error"] = f"{type(exc).__name__}: {exc}"
        logger.warning("model not loaded: %s", state["error"])

    def _service() -> PredictionService:
        if state["service"] is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "model not loaded — train and calibrate first, or mount a "
                    f"models/ directory. Reason: {state['error']}"
                ),
            )
        return state["service"]

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "model_loaded": state["service"] is not None,
            "model": cfg.serve.model if model_name is None else model_name,
            "load_error": state["error"],
            "disclaimer": DISCLAIMER,
        }

    @app.post("/predict")
    def predict(payload: FeaturesPayload) -> dict[str, Any]:
        try:
            result = _service().predict(payload.features)
        except (ServiceError, SchemaError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {**result, "disclaimer": DISCLAIMER}

    @app.post("/explain")
    def explain(payload: FeaturesPayload) -> dict[str, Any]:
        try:
            result = _service().explain(payload.features)
        except (ServiceError, SchemaError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {**result, "disclaimer": DISCLAIMER}

    @app.get("/model-card", response_class=PlainTextResponse)
    def model_card() -> str:
        path = Path("MODEL_CARD.md")
        if not path.exists():
            raise HTTPException(status_code=404, detail="MODEL_CARD.md not found")
        return path.read_text(encoding="utf-8")

    return app
