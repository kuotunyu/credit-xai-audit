"""Dataset acquisition: UCI static zip (primary) or ucimlrepo (fallback).

The raw payload is cached under the gitignored cache dir and verified against the
committed fingerprint manifest. The dataset itself is never committed.
"""

from __future__ import annotations

import logging
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from credit_xai.constants import UCI_STATIC_ZIP_URL, UCI_XLS_NAME
from credit_xai.data.load import RawDataError, from_ucimlrepo_frames, load_xls
from credit_xai.utils.io import ensure_dir, sha256_file

logger = logging.getLogger(__name__)

ZIP_FILENAME = "default_of_credit_card_clients.zip"
_UA = {"User-Agent": "credit-xai-audit/0.1 (educational research; requests)"}


class DatasetChecksumError(RawDataError):
    """The official archive bytes do not match the committed fingerprint."""


def _verify_zip_checksum(path: Path, expected_sha256: str | None) -> None:
    if expected_sha256 is None:
        return
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise DatasetChecksumError(
            f"{path}: sha256 mismatch ({actual[:12]}... != {expected_sha256[:12]}...)"
        )


def download_zip(
    cache_dir: str | Path,
    url: str = UCI_STATIC_ZIP_URL,
    timeout: int = 120,
    expected_sha256: str | None = None,
) -> Path:
    """Download the static zip to the cache (skipped if already present)."""
    cache_path = ensure_dir(cache_dir)
    zip_path = cache_path / ZIP_FILENAME
    if zip_path.exists() and zip_path.stat().st_size > 0:
        _verify_zip_checksum(zip_path, expected_sha256)
        logger.info("using cached dataset zip: %s", zip_path)
        return zip_path
    logger.info("downloading %s", url)
    with requests.get(url, headers=_UA, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        fd, tmp_name = tempfile.mkstemp(dir=cache_path, suffix=".part")
        try:
            with os.fdopen(fd, "wb") as fh:
                for chunk in resp.iter_content(chunk_size=1 << 20):
                    fh.write(chunk)
            _verify_zip_checksum(Path(tmp_name), expected_sha256)
            os.replace(tmp_name, zip_path)
        except BaseException:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
    logger.info("downloaded %s (%.1f MiB)", zip_path, zip_path.stat().st_size / 2**20)
    return zip_path


def extract_xls(zip_path: str | Path, cache_dir: str | Path) -> Path:
    cache_path = ensure_dir(cache_dir)
    xls_path = cache_path / UCI_XLS_NAME
    if xls_path.exists():
        return xls_path
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".xls")]
        if not names:
            raise RawDataError(f"no .xls member found in {zip_path}: {zf.namelist()}")
        member = names[0]
        with zf.open(member) as src, xls_path.open("wb") as dst:
            dst.write(src.read())
    logger.info("extracted %s", xls_path)
    return xls_path


def fetch_uci_static(
    cache_dir: str | Path, expected_zip_sha256: str | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    zip_path = download_zip(cache_dir, expected_sha256=expected_zip_sha256)
    xls_path = extract_xls(zip_path, cache_dir)
    frame = load_xls(xls_path)
    meta = {
        "source": "uci_static",
        "url": UCI_STATIC_ZIP_URL,
        "zip_sha256": sha256_file(zip_path),
    }
    return frame, meta


def fetch_ucimlrepo(dataset_id: int = 350) -> tuple[pd.DataFrame, dict[str, Any]]:
    from ucimlrepo import fetch_ucirepo

    logger.info("fetching dataset id=%d via ucimlrepo", dataset_id)
    result = fetch_ucirepo(id=dataset_id)
    ids = getattr(result.data, "ids", None)
    frame = from_ucimlrepo_frames(result.data.features, result.data.targets, ids)
    meta = {"source": "ucimlrepo", "dataset_id": dataset_id, "zip_sha256": None}
    return frame, meta


def fetch_real_dataset(
    source: str, cache_dir: str | Path, expected_zip_sha256: str | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Primary/fallback chain for the two real sources."""
    if source == "uci_static":
        try:
            return fetch_uci_static(cache_dir, expected_zip_sha256)
        except DatasetChecksumError:
            raise
        except (requests.RequestException, zipfile.BadZipFile, RawDataError) as exc:
            logger.warning("uci_static failed (%s); falling back to ucimlrepo", exc)
            return fetch_ucimlrepo()
    if source == "ucimlrepo":
        return fetch_ucimlrepo()
    raise ValueError(f"unknown real data source: {source!r}")
