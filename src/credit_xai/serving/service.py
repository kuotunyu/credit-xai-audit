"""PredictionService: hash-verified bundle loading, schema-validated inputs,
calibrated predictions, and local explanations. Used by the FastAPI app and the
Gradio UI; never touches the raw dataset."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import FEATURES
from credit_xai.data.schema import load_schema, validate_frame
from credit_xai.explain.explainers import Attributor, build_attributor
from credit_xai.models.persistence import (
    load_aux_parquet,
    load_calibrator,
    load_manifest,
    load_model,
)
from credit_xai.models.registry import get_adapter

logger = logging.getLogger(__name__)


class ServiceError(RuntimeError):
    pass


class PredictionService:
    def __init__(self, cfg: Config, model_name: str | None = None):
        self.cfg = cfg
        self.model_name = model_name or cfg.serve.model
        self.adapter = get_adapter(self.model_name, cfg)
        # Serving accepts bundles trained under a different budget config
        # (expect_config_hash=False); the manifest still hash-verifies payloads.
        self.estimator = load_model(cfg, self.model_name, expect_config_hash=False)
        self.calibrator = load_calibrator(cfg, self.model_name)
        self.manifest = load_manifest(cfg, self.model_name)
        background = load_aux_parquet(cfg, self.model_name, "background.parquet")
        self.attributor: Attributor = build_attributor(self.adapter, self.estimator, background)
        schema_path = Path(cfg.run.manifests_dir) / "feature_schema.json"
        self.schema = load_schema(schema_path) if schema_path.exists() else None
        logger.info(
            "serving %s (%s, calibrator loaded, explainer=%s)",
            self.model_name,
            self.manifest["estimator_class"],
            self.attributor.method,
        )

    # -- helpers ---------------------------------------------------------------
    def frame_from_features(self, features: dict[str, Any]) -> pd.DataFrame:
        missing = [f for f in FEATURES if f not in features]
        if missing:
            raise ServiceError(f"missing features: {missing}")
        extra = [k for k in features if k not in FEATURES]
        if extra:
            raise ServiceError(f"unknown features: {extra}")
        try:
            row = {f: int(features[f]) for f in FEATURES}
        except (TypeError, ValueError) as exc:
            raise ServiceError(f"all features must be integers: {exc}") from exc
        frame = pd.DataFrame([row], columns=FEATURES).astype(np.int64)
        if self.schema is not None:
            validate_frame(frame, self.schema, require_target=False)
        return frame

    def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        frame = self.frame_from_features(features)
        p_unc = float(self.adapter.predict_proba(self.estimator, frame)[0])
        p_cal = float(self.calibrator.predict(np.array([p_unc]))[0])
        return {
            "model": self.model_name,
            "probability_calibrated": p_cal,
            "probability_uncalibrated": p_unc,
            "calibration_method": getattr(self.calibrator, "method", "unknown"),
        }

    def explain(self, features: dict[str, Any], top_k: int = 10) -> dict[str, Any]:
        frame = self.frame_from_features(features)
        prediction = self.predict(features)
        phi = self.attributor.attributions(frame)[0]
        order = np.argsort(-np.abs(phi))
        return {
            **prediction,
            "method": self.attributor.method,
            "base_value_link_scale": self.attributor.base_value,
            "attributions_link_scale": {f: float(phi[i]) for i, f in enumerate(FEATURES)},
            "top_attributions": [
                {"feature": FEATURES[i], "attribution": float(phi[i])} for i in order[:top_k]
            ],
        }
