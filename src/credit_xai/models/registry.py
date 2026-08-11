"""Adapter registry with optional-dependency detection and documented fallbacks."""

from __future__ import annotations

import logging

from credit_xai.config import Config
from credit_xai.constants import MODEL_NAMES
from credit_xai.models.base import ModelAdapter, ModelUnavailableError
from credit_xai.models.logistic import LogisticAdapter

logger = logging.getLogger(__name__)


def get_adapter(model_name: str, cfg: Config) -> ModelAdapter:
    if model_name not in MODEL_NAMES:
        raise ValueError(f"unknown model {model_name!r}; expected one of {MODEL_NAMES}")

    if model_name == "logistic":
        return LogisticAdapter()

    if model_name == "ebm":
        try:
            import interpret.glassbox  # noqa: F401
        except ImportError as exc:
            raise ModelUnavailableError(
                "The EBM model requires the optional 'interpret-core' dependency. "
                "Install it with: uv sync --extra ebm  (or: pip install "
                "'credit-xai-audit[ebm]'). Other models work without it."
            ) from exc
        from credit_xai.models.ebm import EbmAdapter

        return EbmAdapter()

    # lightgbm with automatic HistGradientBoosting fallback
    try:
        import lightgbm  # noqa: F401
    except ImportError:
        logger.warning(
            "lightgbm is not installed; falling back to sklearn "
            "HistGradientBoostingClassifier (recorded in train_meta.json / FAILURES.md)"
        )
        from credit_xai.models.lgbm import HistGradientBoostingAdapter

        return HistGradientBoostingAdapter()
    from credit_xai.models.lgbm import LightGBMAdapter

    return LightGBMAdapter.from_config(cfg)
