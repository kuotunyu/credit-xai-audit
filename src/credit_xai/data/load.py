"""Parsing the raw UCI artifact into the canonical raw frame (ID + 23 features + target)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from credit_xai.constants import FEATURES, ID_COLUMN, RAW_TARGET, TARGET

logger = logging.getLogger(__name__)

_EXPECTED_RAW_COLUMNS = [ID_COLUMN, *FEATURES, RAW_TARGET]
# ucimlrepo serves this dataset with X1..X23 / Y variable names, in the same
# positional order as the documented schema.
_UCI_POSITIONAL = {f"X{i + 1}": name for i, name in enumerate(FEATURES)}
_UCI_POSITIONAL["Y"] = TARGET


class RawDataError(ValueError):
    """Raised when the raw artifact does not look like the documented dataset."""


def load_xls(path: str | Path) -> pd.DataFrame:
    """Read the legacy .xls: row 0 is an X1..X23 placeholder header, row 1 the real one."""
    frame = pd.read_excel(path, header=1, engine="xlrd")
    if list(frame.columns) != _EXPECTED_RAW_COLUMNS:
        raise RawDataError(
            f"unexpected columns in {path}: got {list(frame.columns)[:5]}..., "
            f"expected {_EXPECTED_RAW_COLUMNS[:5]}..."
        )
    frame = frame.rename(columns={RAW_TARGET: TARGET})
    return _finalize(frame)


def from_ucimlrepo_frames(features: pd.DataFrame, targets: pd.DataFrame, ids: Any) -> pd.DataFrame:
    """Assemble the canonical raw frame from ucimlrepo's fetch result parts."""
    frame = features.copy()
    frame[targets.columns[0]] = targets.iloc[:, 0]
    if set(frame.columns) >= set(_UCI_POSITIONAL):
        frame = frame.rename(columns=_UCI_POSITIONAL)
    elif RAW_TARGET in frame.columns:
        frame = frame.rename(columns={RAW_TARGET: TARGET})
    if TARGET not in frame.columns:
        raise RawDataError(f"could not identify target column among {list(frame.columns)}")
    if ID_COLUMN not in frame.columns:
        if ids is not None:
            frame.insert(0, ID_COLUMN, np.asarray(ids).ravel())
        else:
            frame.insert(0, ID_COLUMN, np.arange(1, len(frame) + 1))
    missing = [c for c in [ID_COLUMN, *FEATURES, TARGET] if c not in frame.columns]
    if missing:
        raise RawDataError(f"ucimlrepo frame is missing columns: {missing}")
    return _finalize(frame[[ID_COLUMN, *FEATURES, TARGET]])


def _finalize(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame[[ID_COLUMN, *FEATURES, TARGET]].copy()
    if frame.isna().any().any():
        bad = frame.columns[frame.isna().any()].tolist()
        raise RawDataError(f"raw data contains missing values in columns: {bad}")
    frame = frame.astype(np.int64)
    if not frame[TARGET].isin([0, 1]).all():
        raise RawDataError("target column is not binary 0/1")
    frame = frame.sort_values(ID_COLUMN).reset_index(drop=True)
    logger.info("raw frame loaded: %d rows, %d columns", len(frame), frame.shape[1])
    return frame


def canonical_content_hash(frame: pd.DataFrame) -> str:
    """Source-independent fingerprint: fixed column order, int64, canonical CSV."""
    from credit_xai.utils.io import sha256_text

    canonical = frame[[ID_COLUMN, *FEATURES, TARGET]].astype(np.int64)
    text = canonical.to_csv(index=False, lineterminator="\n")
    return sha256_text(text)
