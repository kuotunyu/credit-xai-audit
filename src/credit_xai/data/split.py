"""Fixed stratified train/val/test split, frozen as a committed manifest.

The split is computed once at prepare time and stored as explicit positional
indices into the canonical cleaned frame. Downstream steps always load the
manifest — they never re-split — so sklearn behavior drift is caught by the
manifest-verification test instead of silently absorbed.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split

from credit_xai.config import Config, canonical_json
from credit_xai.constants import STEP_LOCAL_CASES, STEP_SPLIT
from credit_xai.utils.io import atomic_write_json, read_json, sha256_text
from credit_xai.utils.seeding import rng, seed_int

logger = logging.getLogger(__name__)

SPLIT_NAMES = ("train", "val", "test")


class SplitError(ValueError):
    pass


def compute_split(y: pd.Series, cfg: Config) -> dict[str, np.ndarray]:
    """Two-stage stratified split on the target; returns positional indices."""
    fractions = cfg.data.split
    seed = seed_int(cfg.run.seed, STEP_SPLIT)
    idx = np.arange(len(y))
    idx_trainval, idx_test = train_test_split(
        idx, test_size=fractions.test, stratify=y, random_state=seed
    )
    rel_val = fractions.val / (fractions.train + fractions.val)
    idx_train, idx_val = train_test_split(
        idx_trainval, test_size=rel_val, stratify=y.iloc[idx_trainval], random_state=seed
    )
    return {
        "train": np.sort(idx_train),
        "val": np.sort(idx_val),
        "test": np.sort(idx_test),
    }


def build_split_manifest(y: pd.Series, cfg: Config, dataset_content_sha256: str) -> dict[str, Any]:
    indices = compute_split(y, cfg)
    _check_partition(indices, len(y))
    manifest: dict[str, Any] = {
        "seed": cfg.run.seed,
        "derived_split_seed": seed_int(cfg.run.seed, STEP_SPLIT),
        "fractions": cfg.data.split.model_dump(),
        "sklearn_version": sklearn.__version__,
        "dataset_content_sha256": dataset_content_sha256,
        "n_rows": int(len(y)),
        "class_counts": {
            name: {
                "n": int(len(ix)),
                "positives": int(y.iloc[ix].sum()),
            }
            for name, ix in indices.items()
        },
        "indices": {name: ix.tolist() for name, ix in indices.items()},
    }
    manifest["indices_sha256"] = _indices_hash(manifest["indices"])
    return manifest


def write_split_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(path, manifest, indent=None)  # compact: ~30k indices
    logger.info(
        "split manifest written: %s (%s)",
        path,
        {k: v["n"] for k, v in manifest["class_counts"].items()},
    )


def load_split_manifest(path: str | Path) -> dict[str, Any]:
    manifest = read_json(path)
    if _indices_hash(manifest["indices"]) != manifest["indices_sha256"]:
        raise SplitError(f"{path}: indices_sha256 does not match indices (manifest edited?)")
    return manifest


def verify_split_manifest(manifest: dict[str, Any], y: pd.Series, content_sha256: str) -> None:
    """Cheap invariants checked every time downstream code loads the split."""
    if manifest["dataset_content_sha256"] != content_sha256:
        raise SplitError(
            "split manifest was built for a different dataset "
            f"({manifest['dataset_content_sha256'][:12]}... != {content_sha256[:12]}...)"
        )
    if manifest["n_rows"] != len(y):
        raise SplitError(f"manifest n_rows {manifest['n_rows']} != data rows {len(y)}")
    indices = {name: np.asarray(ix) for name, ix in manifest["indices"].items()}
    _check_partition(indices, len(y))
    for name, ix in indices.items():
        expected = manifest["class_counts"][name]["positives"]
        actual = int(y.iloc[ix].sum())
        if actual != expected:
            raise SplitError(f"{name}: positive count {actual} != manifest {expected}")


def select_local_cases(y_val: pd.Series, cfg: Config) -> dict[str, Any]:
    """Model-independent fixed cases for local-explanation reporting: an equal
    number per target class, drawn deterministically from the VALIDATION split.
    y_val is indexed by positional indices into the canonical frame."""
    g = rng(cfg.run.seed, STEP_LOCAL_CASES)
    n_per_class = cfg.data.local_cases_per_class
    chosen: dict[str, list[int]] = {}
    for label in (0, 1):
        pool = y_val.index[y_val == label].to_numpy()
        if len(pool) < n_per_class:
            raise SplitError(
                f"validation split has only {len(pool)} rows of class {label}, "
                f"need {n_per_class} local cases"
            )
        picked = g.choice(pool, size=n_per_class, replace=False)
        chosen[str(label)] = sorted(int(i) for i in picked)
    return {
        "selection_rule": (
            "deterministic label-stratified draw from the validation split; "
            f"{n_per_class} cases per class; seed derived from (seed, '{STEP_LOCAL_CASES}')"
        ),
        "split": "val",
        "indices_by_class": chosen,
    }


def _indices_hash(indices: dict[str, list[int]]) -> str:
    return sha256_text(canonical_json({k: list(map(int, v)) for k, v in indices.items()}))


def _check_partition(indices: dict[str, np.ndarray], n_rows: int) -> None:
    all_idx = np.concatenate([indices[name] for name in SPLIT_NAMES])
    if len(all_idx) != n_rows or len(np.unique(all_idx)) != n_rows:
        raise SplitError("split indices do not form a partition of the dataset rows")
