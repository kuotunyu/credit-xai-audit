"""The `data prepare` step: acquire -> fingerprint -> clean -> schema -> split ->
manifests -> processed parquet files; plus the loader used by every later step."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from credit_xai.config import Config
from credit_xai.constants import TARGET, UCI_DATASET_ID
from credit_xai.data.clean import clean
from credit_xai.data.download import fetch_real_dataset
from credit_xai.data.load import canonical_content_hash
from credit_xai.data.schema import build_schema, load_schema, validate_frame, write_schema
from credit_xai.data.split import (
    SPLIT_NAMES,
    SplitError,
    build_split_manifest,
    load_split_manifest,
    select_local_cases,
    verify_split_manifest,
    write_split_manifest,
)
from credit_xai.data.synthetic import generate_synthetic
from credit_xai.utils.io import atomic_write_json, ensure_dir, read_json

logger = logging.getLogger(__name__)

FINGERPRINT_NAME = "dataset_fingerprint.json"
SPLIT_MANIFEST_NAME = "split_manifest.json"
SCHEMA_NAME = "feature_schema.json"
LOCAL_CASES_NAME = "local_cases.json"
CLEANED_PARQUET = "cleaned.parquet"


class PrepareError(RuntimeError):
    pass


def run(cfg: Config, force: bool = False) -> None:
    manifests_dir = ensure_dir(cfg.run.manifests_dir)
    processed_dir = ensure_dir(cfg.data.processed_dir)
    raw_results_dir = ensure_dir(cfg.raw_results_dir / "data")

    fingerprint_path = manifests_dir / FINGERPRINT_NAME
    expected_zip_sha256 = None
    if cfg.data.source == "uci_static" and fingerprint_path.exists():
        expected_zip_sha256 = read_json(fingerprint_path).get("zip_sha256")

    # 1. Acquire the raw frame.
    if cfg.data.source == "synthetic":
        raw = generate_synthetic(cfg.data.synthetic_rows, cfg.run.seed)
        source_meta: dict[str, Any] = {"source": "synthetic", "n_rows": len(raw)}
    else:
        raw, source_meta = fetch_real_dataset(
            cfg.data.source, cfg.data.cache_dir, expected_zip_sha256
        )

    # 2. Fingerprint (pin on first run, verify afterwards).
    content_sha = canonical_content_hash(raw)
    _pin_or_verify_fingerprint(fingerprint_path, content_sha, source_meta, force)

    # 3. Clean.
    cleaned, clean_meta = clean(raw)

    # 4. Schema.
    schema = build_schema(cleaned)
    validate_frame(cleaned, schema, require_target=True)
    write_schema(manifests_dir / SCHEMA_NAME, schema)

    # 5. Split manifest + fixed local cases.
    manifest = build_split_manifest(cleaned[TARGET], cfg, content_sha)
    write_split_manifest(manifests_dir / SPLIT_MANIFEST_NAME, manifest)
    val_idx = manifest["indices"]["val"]
    local_cases = select_local_cases(cleaned[TARGET].iloc[val_idx], cfg)
    atomic_write_json(manifests_dir / LOCAL_CASES_NAME, local_cases)

    # 6. Processed parquet files (canonical + per split).
    cleaned.to_parquet(processed_dir / CLEANED_PARQUET, index=False)
    for name in SPLIT_NAMES:
        part = cleaned.iloc[manifest["indices"][name]]
        part.to_parquet(processed_dir / f"{name}.parquet", index=False)

    # 7. Step metadata for the audit trail.
    prepare_meta = {
        "generated_at": datetime.now(UTC).isoformat(),
        "config_hash": cfg.config_hash,
        "run_name": cfg.run.name,
        "uci_dataset_id": UCI_DATASET_ID if cfg.data.source != "synthetic" else None,
        "acquisition": source_meta,
        "dataset_content_sha256": content_sha,
        "cleaning": clean_meta,
        "splits": manifest["class_counts"],
        "local_cases": local_cases["indices_by_class"],
    }
    atomic_write_json(raw_results_dir / "prepare_meta.json", prepare_meta)
    logger.info(
        "data prepare complete: %s rows, splits %s",
        clean_meta["n_rows"],
        {k: v["n"] for k, v in manifest["class_counts"].items()},
    )


def load_processed(cfg: Config) -> dict[str, pd.DataFrame]:
    """Load the three split frames, verifying manifest consistency every time."""
    processed_dir = Path(cfg.data.processed_dir)
    manifests_dir = Path(cfg.run.manifests_dir)
    cleaned_path = processed_dir / CLEANED_PARQUET
    if not cleaned_path.exists():
        raise PrepareError(f"processed data not found at {cleaned_path}; run `data prepare` first")
    cleaned = pd.read_parquet(cleaned_path)
    schema = load_schema(manifests_dir / SCHEMA_NAME)
    validate_frame(cleaned, schema, require_target=True)
    manifest = load_split_manifest(manifests_dir / SPLIT_MANIFEST_NAME)
    verify_split_manifest(manifest, cleaned[TARGET], canonical_content_hash_cleaned(cfg))
    splits: dict[str, pd.DataFrame] = {}
    for name in SPLIT_NAMES:
        part = pd.read_parquet(processed_dir / f"{name}.parquet")
        expected_n = manifest["class_counts"][name]["n"]
        if len(part) != expected_n:
            raise SplitError(f"{name}.parquet has {len(part)} rows, manifest says {expected_n}")
        splits[name] = part
    return splits


def canonical_content_hash_cleaned(cfg: Config) -> str:
    """The fingerprint the split manifest was built against (raw content hash)."""
    fingerprint = read_json(Path(cfg.run.manifests_dir) / FINGERPRINT_NAME)
    return fingerprint["content_sha256"]


def load_local_cases(cfg: Config) -> dict[str, Any]:
    return read_json(Path(cfg.run.manifests_dir) / LOCAL_CASES_NAME)


def _pin_or_verify_fingerprint(
    path: Path, content_sha: str, source_meta: dict[str, Any], force: bool
) -> None:
    record = {
        "content_sha256": content_sha,
        "pinned_at": datetime.now(UTC).isoformat(),
        **source_meta,
    }
    if not path.exists() or force:
        atomic_write_json(path, record)
        logger.info("dataset fingerprint pinned: %s (content %s...)", path, content_sha[:12])
        return
    existing = read_json(path)
    if existing.get("content_sha256") != content_sha:
        raise PrepareError(
            f"dataset content hash mismatch: manifest {path} has "
            f"{existing.get('content_sha256', '?')[:12]}..., freshly loaded data has "
            f"{content_sha[:12]}... — the upstream file changed or the source is "
            "inconsistent. Use --force only if you intend to re-pin."
        )
    logger.info("dataset fingerprint verified (%s...)", content_sha[:12])
