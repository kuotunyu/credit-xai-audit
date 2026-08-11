"""Cleaning policy (documented in DATA_CARD.md).

- Drop the ID column.
- EDUCATION: undocumented codes {0, 5, 6} -> 4 ("others").
- MARRIAGE: undocumented code {0} -> 3 ("others").

This is a fixed, fit-free value mapping — it uses no statistics of the data, so
applying it before the train/val/test split cannot leak information. Recode
counts are recorded so the mapping is auditable.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from credit_xai.constants import (
    EDUCATION_RECODE,
    FEATURES,
    ID_COLUMN,
    MARRIAGE_RECODE,
    TARGET,
)

logger = logging.getLogger(__name__)


class CleaningError(ValueError):
    pass


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return (cleaned frame without ID, recode metadata)."""
    expected = [ID_COLUMN, *FEATURES, TARGET]
    missing = [c for c in expected if c not in raw.columns]
    if missing:
        raise CleaningError(f"raw frame is missing columns: {missing}")

    n_rows = len(raw)
    frame = raw[expected].copy()

    education_counts = {
        int(code): int((frame["EDUCATION"] == code).sum()) for code in sorted(EDUCATION_RECODE)
    }
    marriage_counts = {
        int(code): int((frame["MARRIAGE"] == code).sum()) for code in sorted(MARRIAGE_RECODE)
    }
    frame["EDUCATION"] = frame["EDUCATION"].replace(EDUCATION_RECODE)
    frame["MARRIAGE"] = frame["MARRIAGE"].replace(MARRIAGE_RECODE)

    if not frame["EDUCATION"].isin([1, 2, 3, 4]).all():
        bad = sorted(frame.loc[~frame["EDUCATION"].isin([1, 2, 3, 4]), "EDUCATION"].unique())
        raise CleaningError(f"EDUCATION contains unexpected codes after recode: {bad}")
    if not frame["MARRIAGE"].isin([1, 2, 3]).all():
        bad = sorted(frame.loc[~frame["MARRIAGE"].isin([1, 2, 3]), "MARRIAGE"].unique())
        raise CleaningError(f"MARRIAGE contains unexpected codes after recode: {bad}")
    if not frame["SEX"].isin([1, 2]).all():
        bad = sorted(frame.loc[~frame["SEX"].isin([1, 2]), "SEX"].unique())
        raise CleaningError(f"SEX contains unexpected codes: {bad}")

    frame = frame.drop(columns=[ID_COLUMN])
    if len(frame) != n_rows:
        raise CleaningError(f"row count changed during cleaning: {n_rows} -> {len(frame)}")

    meta = {
        "n_rows": n_rows,
        "dropped_columns": [ID_COLUMN],
        "education_recoded": education_counts,
        "education_recode_map": {str(k): v for k, v in EDUCATION_RECODE.items()},
        "marriage_recoded": marriage_counts,
        "marriage_recode_map": {str(k): v for k, v in MARRIAGE_RECODE.items()},
    }
    logger.info(
        "cleaning: %d rows; EDUCATION recodes %s; MARRIAGE recodes %s",
        n_rows,
        education_counts,
        marriage_counts,
    )
    return frame, meta
