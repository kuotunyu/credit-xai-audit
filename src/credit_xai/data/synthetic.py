"""Deterministic synthetic dataset with the same schema as the raw UCI data.

Used by tests, CI, and the Docker smoke profile so that no environment ever
depends on downloading the real dataset. The generator injects genuine signal
(PAY_* and LIMIT_BAL drive the target) so models learn something and the
faithfulness test has a real effect to detect. Values are arbitrary — this is
NOT a simulation of the 2005 population.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from credit_xai.constants import (
    BILL_FEATURES,
    FEATURES,
    ID_COLUMN,
    PAY_AMT_FEATURES,
    PAY_FEATURES,
    STEP_SYNTHETIC,
    TARGET,
)
from credit_xai.utils.seeding import rng


def generate_synthetic(n_rows: int, seed: int) -> pd.DataFrame:
    """Raw-shaped frame: ID + 23 features + target, including undocumented
    EDUCATION/MARRIAGE codes so the cleaning path is exercised."""
    g = rng(seed, STEP_SYNTHETIC)

    limit_bal = g.integers(1, 81, n_rows) * 10_000
    sex = g.integers(1, 3, n_rows)
    education = g.choice(
        [0, 1, 2, 3, 4, 5, 6],
        size=n_rows,
        p=[0.004, 0.35, 0.45, 0.15, 0.03, 0.012, 0.004],
    )
    marriage = g.choice([0, 1, 2, 3], size=n_rows, p=[0.004, 0.45, 0.52, 0.026])
    age = g.integers(21, 80, n_rows)

    pay = np.empty((n_rows, 6), dtype=np.int64)
    pay[:, 0] = g.choice([-2, -1, 0, 1, 2, 3], size=n_rows, p=[0.25, 0.2, 0.35, 0.12, 0.06, 0.02])
    for j in range(1, 6):
        drift = g.integers(-1, 2, n_rows)
        pay[:, j] = np.clip(pay[:, j - 1] + drift, -2, 8)

    bill = g.integers(-20_000, 300_000, (n_rows, 6))
    pay_amt = g.integers(0, 50_000, (n_rows, 6))

    # Target: mostly repayment-status driven, mildly credit-limit driven.
    z = (
        0.8 * pay[:, 0]
        + 0.3 * pay[:, 1]
        + 0.15 * pay[:, 2]
        - limit_bal / 250_000
        + g.normal(0, 0.7, n_rows)
    )
    prob = 1.0 / (1.0 + np.exp(-(z - 0.6)))
    y = (g.random(n_rows) < prob).astype(np.int64)

    frame = pd.DataFrame({ID_COLUMN: np.arange(1, n_rows + 1, dtype=np.int64)})
    frame["LIMIT_BAL"] = limit_bal
    frame["SEX"] = sex
    frame["EDUCATION"] = education
    frame["MARRIAGE"] = marriage
    frame["AGE"] = age
    for j, col in enumerate(PAY_FEATURES):
        frame[col] = pay[:, j]
    for j, col in enumerate(BILL_FEATURES):
        frame[col] = bill[:, j]
    for j, col in enumerate(PAY_AMT_FEATURES):
        frame[col] = pay_amt[:, j]
    frame[TARGET] = y

    frame = frame[[ID_COLUMN, *FEATURES, TARGET]].astype(np.int64)
    return frame
