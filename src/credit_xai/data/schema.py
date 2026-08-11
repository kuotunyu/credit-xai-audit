"""Feature schema: built at prepare time, committed as a manifest, and used to
validate frames downstream (serving inputs, tests)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pandas as pd

from credit_xai.constants import (
    CATEGORICAL_FEATURES,
    FEATURES,
    RAW_TARGET,
    TARGET,
)
from credit_xai.utils.io import atomic_write_json, read_json

SCHEMA_VERSION = 1

# Post-cleaning categorical domains (documented UCI codes; undocumented codes
# have been collapsed into the catch-all "others" categories by data.clean).
CATEGORICAL_DOMAINS: dict[str, list[int]] = {
    "SEX": [1, 2],
    "EDUCATION": [1, 2, 3, 4],
    "MARRIAGE": [1, 2, 3],
}


class SchemaError(ValueError):
    pass


def build_schema(frame: pd.DataFrame) -> dict[str, Any]:
    """Schema for a CLEANED frame (23 features + target)."""
    _require_columns(frame)
    columns: dict[str, Any] = {}
    for col in FEATURES:
        info: dict[str, Any] = {
            "dtype": "int64",
            "kind": "categorical" if col in CATEGORICAL_FEATURES else "numeric",
            "observed_min": int(frame[col].min()),
            "observed_max": int(frame[col].max()),
        }
        if col in CATEGORICAL_FEATURES:
            info["allowed_values"] = CATEGORICAL_DOMAINS[col]
        columns[col] = info
    return {
        "schema_version": SCHEMA_VERSION,
        "features": columns,
        "target": {"name": TARGET, "original_name": RAW_TARGET, "values": [0, 1]},
    }


def validate_frame(frame: pd.DataFrame, schema: dict[str, Any], require_target: bool) -> None:
    """Strict categorical-domain and dtype validation; numeric ranges are not
    enforced (observed_min/max are reference only)."""
    _require_columns(frame, require_target=require_target)
    for col, info in schema["features"].items():
        if not pd.api.types.is_integer_dtype(frame[col]):
            raise SchemaError(f"column {col} must be integer, got {frame[col].dtype}")
        allowed = info.get("allowed_values")
        if allowed is not None and not frame[col].isin(allowed).all():
            bad = sorted(frame.loc[~frame[col].isin(allowed), col].unique().tolist())
            raise SchemaError(f"column {col} contains values outside {allowed}: {bad}")
    if require_target and not frame[TARGET].isin(schema["target"]["values"]).all():
        raise SchemaError("target column contains non-binary values")


def write_schema(path: str | Path, schema: dict[str, Any]) -> None:
    atomic_write_json(path, schema)


def load_schema(path: str | Path) -> dict[str, Any]:
    schema = cast(dict[str, Any], read_json(path))
    if schema.get("schema_version") != SCHEMA_VERSION:
        raise SchemaError(
            f"schema version mismatch: file has {schema.get('schema_version')}, "
            f"code expects {SCHEMA_VERSION}"
        )
    return schema


def _require_columns(frame: pd.DataFrame, require_target: bool = True) -> None:
    expected = [*FEATURES, TARGET] if require_target else list(FEATURES)
    missing = [c for c in expected if c not in frame.columns]
    if missing:
        raise SchemaError(f"frame is missing columns: {missing}")
