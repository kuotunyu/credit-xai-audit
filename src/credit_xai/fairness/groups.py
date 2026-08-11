"""Predeclared group definitions for the descriptive group-metric snapshot.

Groups: SEX (UCI coding reported verbatim: 1 = male, 2 = female) and the
predeclared AGE bins from the config. Bin edges are committed configuration and
are never tuned against results.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from credit_xai.config import Config

SEX_LABELS = {1: "sex=1_male", 2: "sex=2_female"}


def age_bin_label(lo: int, hi: int | None) -> str:
    return f"age={lo}-{hi}" if hi is not None else f"age={lo}+"


def group_masks(frame: pd.DataFrame, cfg: Config) -> dict[str, np.ndarray]:
    """Ordered mapping group_id -> boolean mask over the frame's rows."""
    masks: dict[str, np.ndarray] = {}
    sex = frame[cfg.fairness.sex_column].to_numpy()
    for code, label in SEX_LABELS.items():
        masks[label] = sex == code
    age = frame["AGE"].to_numpy()
    for lo, hi in cfg.fairness.age_bins:
        mask = (age >= lo) & (age <= hi) if hi is not None else age >= lo
        masks[age_bin_label(lo, hi)] = mask
    return masks
