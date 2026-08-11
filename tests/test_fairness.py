from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from credit_xai.fairness.groups import age_bin_label, group_masks
from credit_xai.fairness.metrics import group_snapshot


def test_group_masks_cover_sex_and_age(test_config) -> None:
    frame = pd.DataFrame(
        {
            "SEX": [1, 1, 2, 2, 2],
            "AGE": [22, 35, 41, 39, 70],
        }
    )
    masks = group_masks(frame, test_config)  # age bins: [21,39], [40,None]
    assert masks["sex=1_male"].tolist() == [True, True, False, False, False]
    assert masks["sex=2_female"].tolist() == [False, False, True, True, True]
    assert masks[age_bin_label(21, 39)].tolist() == [True, True, False, True, False]
    assert masks[age_bin_label(40, None)].tolist() == [False, False, True, False, True]


def test_group_snapshot_point_estimates() -> None:
    y = np.array([0, 0, 1, 1, 0, 1])
    p = np.array([0.1, 0.2, 0.8, 0.9, 0.3, 0.7])
    y_hat = p >= 0.5
    masks = {"g_all": np.ones(6, dtype=bool), "g_first4": np.array([1, 1, 1, 1, 0, 0], bool)}
    snap = group_snapshot(y, p, y_hat, masks, small_cell_min=2)
    assert snap["g_all"]["n"] == 6
    assert snap["g_all"]["auc"] == pytest.approx(1.0)
    assert snap["g_all"]["fpr"] == pytest.approx(0.0)
    assert snap["g_all"]["fnr"] == pytest.approx(0.0)
    assert snap["g_all"]["selection_rate"] == pytest.approx(0.5)
    assert snap["g_first4"]["n"] == 4
    assert snap["g_first4"]["prevalence"] == pytest.approx(0.5)


def test_group_snapshot_flags_small_cells_and_single_class() -> None:
    y = np.array([0, 0, 0, 1])
    p = np.array([0.2, 0.1, 0.3, 0.9])
    y_hat = p >= 0.5
    masks = {"tiny": np.array([1, 1, 0, 0], bool), "ok": np.ones(4, bool)}
    snap = group_snapshot(y, p, y_hat, masks, small_cell_min=1)
    assert snap["tiny"]["auc"] is None  # single-class slice
    assert snap["tiny"]["fnr"] is None
    assert snap["tiny"]["small_cell"] is True
    assert snap["ok"]["small_cell"] is False
