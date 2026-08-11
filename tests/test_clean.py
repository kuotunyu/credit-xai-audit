from __future__ import annotations

import pandas as pd
import pytest

from credit_xai.constants import FEATURES, ID_COLUMN, TARGET
from credit_xai.data.clean import CleaningError, clean
from credit_xai.data.schema import SchemaError, build_schema, validate_frame
from credit_xai.data.synthetic import generate_synthetic


def _tiny_raw() -> pd.DataFrame:
    n = 8
    frame = pd.DataFrame({ID_COLUMN: range(1, n + 1)})
    for col in FEATURES:
        frame[col] = 1
    frame["SEX"] = [1, 2, 1, 2, 1, 2, 1, 2]
    frame["EDUCATION"] = [0, 5, 6, 1, 2, 3, 4, 2]
    frame["MARRIAGE"] = [0, 1, 2, 3, 1, 2, 1, 3]
    frame["AGE"] = [21, 30, 45, 60, 35, 50, 28, 70]
    frame[TARGET] = [0, 1, 0, 1, 0, 1, 0, 1]
    return frame.astype("int64")


def test_recodes_and_id_drop() -> None:
    cleaned, meta = clean(_tiny_raw())
    assert ID_COLUMN not in cleaned.columns
    assert len(cleaned) == 8
    assert cleaned["EDUCATION"].tolist() == [4, 4, 4, 1, 2, 3, 4, 2]
    assert cleaned["MARRIAGE"].tolist() == [3, 1, 2, 3, 1, 2, 1, 3]
    assert meta["education_recoded"] == {0: 1, 5: 1, 6: 1}
    assert meta["marriage_recoded"] == {0: 1}
    assert meta["n_rows"] == 8


def test_clean_on_synthetic_preserves_rows_and_domains() -> None:
    raw = generate_synthetic(2000, seed=3)
    cleaned, meta = clean(raw)
    assert len(cleaned) == 2000
    assert set(cleaned["EDUCATION"].unique()) <= {1, 2, 3, 4}
    assert set(cleaned["MARRIAGE"].unique()) <= {1, 2, 3}
    # synthetic generator injects undocumented codes, so some recoding must occur
    assert sum(meta["education_recoded"].values()) > 0
    assert sum(meta["marriage_recoded"].values()) > 0


def test_invalid_sex_rejected() -> None:
    raw = _tiny_raw()
    raw.loc[0, "SEX"] = 9
    with pytest.raises(CleaningError, match="SEX"):
        clean(raw)


def test_missing_column_rejected() -> None:
    raw = _tiny_raw().drop(columns=["LIMIT_BAL"])
    with pytest.raises(CleaningError, match="LIMIT_BAL"):
        clean(raw)


def test_schema_roundtrip_and_validation() -> None:
    cleaned, _ = clean(generate_synthetic(1000, seed=5))
    schema = build_schema(cleaned)
    validate_frame(cleaned, schema, require_target=True)

    bad = cleaned.copy()
    bad.loc[bad.index[0], "MARRIAGE"] = 7
    with pytest.raises(SchemaError, match="MARRIAGE"):
        validate_frame(bad, schema, require_target=True)

    floaty = cleaned.copy()
    floaty["AGE"] = floaty["AGE"].astype(float)
    with pytest.raises(SchemaError, match="AGE"):
        validate_frame(floaty, schema, require_target=True)
