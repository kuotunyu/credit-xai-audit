"""Shared constants: disclaimer, column names, cleaning maps, model names."""

from __future__ import annotations

DISCLAIMER = "Historical 2005 educational audit. Not for lending decisions. Not financial advice."

# Raw UCI column names (after the header=1 quirk is handled in data.load).
ID_COLUMN = "ID"
RAW_TARGET = "default payment next month"
TARGET = "default"  # internal canonical target name; original name recorded in the schema

CATEGORICAL_FEATURES = ["SEX", "EDUCATION", "MARRIAGE"]
PAY_FEATURES = ["PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"]
BILL_FEATURES = [f"BILL_AMT{i}" for i in range(1, 7)]
PAY_AMT_FEATURES = [f"PAY_AMT{i}" for i in range(1, 7)]

FEATURES: list[str] = [
    "LIMIT_BAL",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "AGE",
    *PAY_FEATURES,
    *BILL_FEATURES,
    *PAY_AMT_FEATURES,
]
NUMERIC_FEATURES: list[str] = [c for c in FEATURES if c not in CATEGORICAL_FEATURES]

# Cleaning policy (documented in DATA_CARD.md): undocumented codes collapse into
# the documented catch-all "others" category. This is a labeling convention only.
EDUCATION_RECODE: dict[int, int] = {0: 4, 5: 4, 6: 4}
MARRIAGE_RECODE: dict[int, int] = {0: 3}

MODEL_NAMES = ("logistic", "ebm", "lightgbm")

# UCI provenance
UCI_DATASET_ID = 350
UCI_STATIC_ZIP_URL = (
    "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
)
UCI_XLS_NAME = "default of credit card clients.xls"

# Step-name conventions for seed derivation and checkpoints.
STEP_SPLIT = "split"
STEP_SYNTHETIC = "synthetic"
STEP_LOCAL_CASES = "local_cases"


def step_train(model: str) -> str:
    return f"train/{model}"


def step_eval_bootstrap(model: str) -> str:
    return f"eval/bootstrap/{model}"


def step_group_bootstrap(model: str) -> str:
    return f"eval/groups/{model}"


def step_shap_background(model: str) -> str:
    return f"explain/background/{model}"


def step_rank_stability(model: str) -> str:
    return f"explain/rank_stability/{model}"


def step_faithfulness(model: str) -> str:
    return f"explain/faithfulness/{model}"
