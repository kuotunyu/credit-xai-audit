"""Model bundle persistence: joblib payloads + a manifest with content hashes.

Bundles live under the gitignored ``models/<name>/`` directory::

    models/<name>/model.joblib        fitted estimator (pipeline for logistic)
    models/<name>/calibrator.joblib   written by the calibrate step
    models/<name>/manifest.json       hashes, versions, config_hash, adapter info

Pickled artifacts are only ever loaded from this local, hash-verified directory.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np
import sklearn

from credit_xai.config import Config
from credit_xai.models.base import ModelAdapter
from credit_xai.utils.io import atomic_write_json, ensure_dir, read_json, sha256_file

logger = logging.getLogger(__name__)

MODEL_FILE = "model.joblib"
CALIBRATOR_FILE = "calibrator.joblib"
MANIFEST_FILE = "manifest.json"


class PersistenceError(RuntimeError):
    pass


def model_dir(cfg: Config, model_name: str) -> Path:
    return Path(cfg.run.models_dir) / model_name


def _package_versions() -> dict[str, str]:
    versions = {"numpy": np.__version__, "scikit-learn": sklearn.__version__}
    for pkg in ("lightgbm", "interpret", "shap"):
        try:
            versions[pkg] = __import__(pkg).__version__
        except ImportError:
            pass
    return versions


def save_model(
    cfg: Config, adapter: ModelAdapter, estimator: Any, extra: dict[str, Any] | None = None
) -> Path:
    directory = ensure_dir(model_dir(cfg, adapter.name))
    payload_path = directory / MODEL_FILE
    joblib.dump(estimator, payload_path)
    manifest = {
        "model_name": adapter.name,
        "estimator_class": adapter.estimator_class(estimator),
        "explainer_kind": adapter.explainer_kind,
        "is_fallback": adapter.is_fallback,
        "created_at": datetime.now(UTC).isoformat(),
        "config_hash": cfg.config_hash,
        "run_name": cfg.run.name,
        "seed": cfg.run.seed,
        "package_versions": _package_versions(),
        "files": {MODEL_FILE: sha256_file(payload_path)},
        **(extra or {}),
    }
    atomic_write_json(directory / MANIFEST_FILE, manifest)
    logger.info("saved %s bundle to %s", adapter.name, directory)
    return directory


def save_aux_parquet(cfg: Config, model_name: str, filename: str, frame: Any) -> Path:
    """Attach a parquet artifact (e.g. the SHAP background sample) to a bundle,
    recording its hash in the manifest."""
    directory = model_dir(cfg, model_name)
    manifest_path = directory / MANIFEST_FILE
    if not manifest_path.exists():
        raise PersistenceError(f"no trained bundle for {model_name!r}; run train first")
    path = directory / filename
    frame.to_parquet(path, index=False)
    manifest = read_json(manifest_path)
    manifest["files"][filename] = sha256_file(path)
    atomic_write_json(manifest_path, manifest)
    return path


def load_aux_parquet(cfg: Config, model_name: str, filename: str) -> Any:
    import pandas as pd

    manifest = load_manifest(cfg, model_name)
    if filename not in manifest["files"]:
        raise PersistenceError(f"bundle for {model_name!r} has no artifact {filename!r}")
    path = model_dir(cfg, model_name) / filename
    if not path.exists():
        raise PersistenceError(f"missing artifact {path}")
    actual = sha256_file(path)
    if actual != manifest["files"][filename]:
        raise PersistenceError(f"{path}: sha256 mismatch; artifact corrupted or tampered")
    return pd.read_parquet(path)


def save_calibrator(cfg: Config, model_name: str, calibrator: Any) -> Path:
    directory = model_dir(cfg, model_name)
    manifest_path = directory / MANIFEST_FILE
    if not manifest_path.exists():
        raise PersistenceError(f"no trained bundle for {model_name!r}; run train first")
    payload_path = directory / CALIBRATOR_FILE
    joblib.dump(calibrator, payload_path)
    manifest = read_json(manifest_path)
    manifest["files"][CALIBRATOR_FILE] = sha256_file(payload_path)
    atomic_write_json(manifest_path, manifest)
    return payload_path


def load_manifest(cfg: Config, model_name: str) -> dict[str, Any]:
    manifest_path = model_dir(cfg, model_name) / MANIFEST_FILE
    if not manifest_path.exists():
        raise PersistenceError(
            f"model bundle for {model_name!r} not found at {manifest_path.parent}; "
            "run `train` first"
        )
    return cast(dict[str, Any], read_json(manifest_path))


def load_model(cfg: Config, model_name: str, expect_config_hash: bool = True) -> Any:
    manifest = load_manifest(cfg, model_name)
    if expect_config_hash and manifest["config_hash"] != cfg.config_hash:
        raise PersistenceError(
            f"bundle for {model_name!r} was trained under a different config "
            f"({manifest['config_hash'][:12]}... != {cfg.config_hash[:12]}...); retrain "
            "or use the matching config file"
        )
    return _load_verified(cfg, model_name, MODEL_FILE, manifest)


def load_calibrator(cfg: Config, model_name: str) -> Any:
    manifest = load_manifest(cfg, model_name)
    if CALIBRATOR_FILE not in manifest["files"]:
        raise PersistenceError(f"no calibrator saved for {model_name!r}; run `calibrate` first")
    return _load_verified(cfg, model_name, CALIBRATOR_FILE, manifest)


def _load_verified(cfg: Config, model_name: str, filename: str, manifest: dict[str, Any]) -> Any:
    path = model_dir(cfg, model_name) / filename
    if not path.exists():
        raise PersistenceError(f"missing artifact {path}")
    actual = sha256_file(path)
    expected = manifest["files"].get(filename)
    if actual != expected:
        raise PersistenceError(
            f"{path}: sha256 mismatch (file {actual[:12]}... != manifest "
            f"{str(expected)[:12]}...); artifact corrupted or tampered"
        )
    return joblib.load(path)
