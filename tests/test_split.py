from __future__ import annotations

import numpy as np
import pytest

from credit_xai.constants import TARGET
from credit_xai.data.clean import clean
from credit_xai.data.split import (
    SplitError,
    build_split_manifest,
    load_split_manifest,
    select_local_cases,
    verify_split_manifest,
    write_split_manifest,
)
from credit_xai.data.synthetic import generate_synthetic

CONTENT_SHA = "c" * 64


@pytest.fixture(scope="module")
def cleaned():
    frame, _ = clean(generate_synthetic(3000, seed=11))
    return frame


def test_split_is_deterministic(cleaned, test_config) -> None:
    m1 = build_split_manifest(cleaned[TARGET], test_config, CONTENT_SHA)
    m2 = build_split_manifest(cleaned[TARGET], test_config, CONTENT_SHA)
    assert m1["indices"] == m2["indices"]
    assert m1["indices_sha256"] == m2["indices_sha256"]


def test_split_partition_and_fractions(cleaned, test_config) -> None:
    manifest = build_split_manifest(cleaned[TARGET], test_config, CONTENT_SHA)
    idx = {k: np.asarray(v) for k, v in manifest["indices"].items()}
    n = len(cleaned)
    combined = np.concatenate(list(idx.values()))
    assert len(combined) == n and len(np.unique(combined)) == n
    assert abs(len(idx["train"]) / n - 0.70) < 0.01
    assert abs(len(idx["val"]) / n - 0.15) < 0.01
    assert abs(len(idx["test"]) / n - 0.15) < 0.01


def test_split_is_stratified(cleaned, test_config) -> None:
    manifest = build_split_manifest(cleaned[TARGET], test_config, CONTENT_SHA)
    overall = cleaned[TARGET].mean()
    for name, ix in manifest["indices"].items():
        share = cleaned[TARGET].iloc[ix].mean()
        assert abs(share - overall) < 0.02, f"{name} positive share drifted"


def test_manifest_roundtrip_and_tamper_detection(cleaned, test_config, tmp_path) -> None:
    manifest = build_split_manifest(cleaned[TARGET], test_config, CONTENT_SHA)
    path = tmp_path / "split_manifest.json"
    write_split_manifest(path, manifest)
    loaded = load_split_manifest(path)
    verify_split_manifest(loaded, cleaned[TARGET], CONTENT_SHA)

    with pytest.raises(SplitError, match="different dataset"):
        verify_split_manifest(loaded, cleaned[TARGET], "d" * 64)

    tampered = dict(manifest)
    tampered["indices"] = {
        k: ([v[1], v[0]] + list(v[2:]) if k == "train" else list(v))
        for k, v in manifest["indices"].items()
    }
    # reordering does not change the set but does change the canonical hash
    write_split_manifest(path, tampered)
    with pytest.raises(SplitError, match="indices_sha256"):
        load_split_manifest(path)


def test_local_cases_from_validation_only(cleaned, test_config) -> None:
    manifest = build_split_manifest(cleaned[TARGET], test_config, CONTENT_SHA)
    y_val = cleaned[TARGET].iloc[manifest["indices"]["val"]]
    cases = select_local_cases(y_val, test_config)
    per_class = test_config.data.local_cases_per_class
    val_set = set(manifest["indices"]["val"])
    for label in ("0", "1"):
        picked = cases["indices_by_class"][label]
        assert len(picked) == per_class
        assert set(picked) <= val_set
        for i in picked:
            assert cleaned[TARGET].iloc[i] == int(label)
    # determinism
    again = select_local_cases(y_val, test_config)
    assert again["indices_by_class"] == cases["indices_by_class"]
