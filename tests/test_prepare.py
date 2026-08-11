from __future__ import annotations

import hashlib

import pytest

from credit_xai.data.download import ZIP_FILENAME, download_zip
from credit_xai.data.load import RawDataError
from credit_xai.data.prepare import (
    FINGERPRINT_NAME,
    LOCAL_CASES_NAME,
    SCHEMA_NAME,
    SPLIT_MANIFEST_NAME,
    PrepareError,
    load_local_cases,
    load_processed,
    run,
)
from credit_xai.utils.io import atomic_write_json, read_json


def test_prepare_end_to_end_synthetic(test_config) -> None:
    run(test_config)

    manifests = test_config.run.manifests_dir
    for name in (FINGERPRINT_NAME, SPLIT_MANIFEST_NAME, SCHEMA_NAME, LOCAL_CASES_NAME):
        assert (manifests / name).exists(), name

    meta = read_json(test_config.raw_results_dir / "data" / "prepare_meta.json")
    assert meta["config_hash"] == test_config.config_hash
    assert meta["acquisition"]["source"] == "synthetic"
    assert meta["cleaning"]["n_rows"] == test_config.data.synthetic_rows

    splits = load_processed(test_config)
    assert set(splits) == {"train", "val", "test"}
    total = sum(len(v) for v in splits.values())
    assert total == test_config.data.synthetic_rows

    cases = load_local_cases(test_config)
    assert set(cases["indices_by_class"]) == {"0", "1"}


def test_prepare_is_idempotent_and_verifies_fingerprint(test_config) -> None:
    run(test_config)
    run(test_config)  # second run must verify, not re-pin

    fp_path = test_config.run.manifests_dir / FINGERPRINT_NAME
    record = read_json(fp_path)
    record["content_sha256"] = "0" * 64
    atomic_write_json(fp_path, record)
    with pytest.raises(PrepareError, match="mismatch"):
        run(test_config)
    # --force re-pins
    run(test_config, force=True)
    assert read_json(fp_path)["content_sha256"] != "0" * 64


def test_load_processed_without_prepare_raises(test_config) -> None:
    with pytest.raises(PrepareError, match="data prepare"):
        load_processed(test_config)


def test_cached_uci_zip_must_match_pinned_checksum(tmp_path) -> None:
    payload = b"official archive fixture"
    zip_path = tmp_path / ZIP_FILENAME
    zip_path.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest()

    assert download_zip(tmp_path, expected_sha256=expected) == zip_path
    with pytest.raises(RawDataError, match="sha256"):
        download_zip(tmp_path, expected_sha256="0" * 64)
