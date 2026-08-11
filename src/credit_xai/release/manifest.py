"""Build and verify the deterministic public release manifest."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml

from credit_xai.utils.io import atomic_write_json, read_json, sha256_file

SOURCE_SNAPSHOT = "58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61"
RELEASE_MANIFEST_PATH = Path("manifests/release_manifest.json")
PUBLIC_EXCLUSIONS = [
    ".git history from private archive",
    "environments and caches",
    "private progress, handoff, and agent notes",
    "raw UCI dataset rows and archives",
    "serialized model bundles",
    "platform-specific notebooks",
]
_LOCAL_ONLY_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "tmp",
}


def _tracked_paths(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return sorted(
        path
        for path in completed.stdout.decode("utf-8").split("\0")
        if path and path != RELEASE_MANIFEST_PATH.as_posix()
    )


def _actual_public_paths(root: Path) -> set[str]:
    paths: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in _LOCAL_ONLY_PARTS or part.startswith(".venv") for part in relative.parts):
            continue
        if path.is_file() and relative != RELEASE_MANIFEST_PATH:
            paths.add(relative.as_posix())
    return paths


def build_release_manifest(root: str | Path) -> dict[str, Any]:
    root = Path(root).resolve()
    with (root / "configs" / "full.yaml").open("r", encoding="utf-8") as handle:
        full = yaml.safe_load(handle)
    files = []
    for relative in _tracked_paths(root):
        path = root / relative
        files.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": 1,
        "candidate_state": "unpublished",
        "source": {
            "kind": "audited committed snapshot from private archive",
            "commit": SOURCE_SNAPSHOT,
            "history_copied": False,
        },
        "models": ["logistic", "ebm", "lightgbm"],
        "evidence_budgets": {
            "bootstrap_iterations_per_model": full["evaluation"]["bootstrap"]["n_iterations"],
            "explanation_refits_per_model": full["explain"]["rank_stability"]["n_refits"],
            "explanation_resamples_per_model": full["explain"]["rank_stability"]["n_resamples"],
            "faithfulness_instances_per_model": full["explain"]["faithfulness"]["n_instances"],
            "explained_test_rows_per_model": full["explain"]["shap"]["test_sample_size"],
        },
        "public_exclusions": PUBLIC_EXCLUSIONS,
        "files": files,
    }


def write_release_manifest(root: str | Path) -> Path:
    root = Path(root).resolve()
    path = root / RELEASE_MANIFEST_PATH
    atomic_write_json(path, build_release_manifest(root))
    return path


def verify_release_manifest(root: str | Path) -> list[str]:
    root = Path(root).resolve()
    path = root / RELEASE_MANIFEST_PATH
    errors: list[str] = []
    try:
        manifest = read_json(path)
        if manifest.get("candidate_state") != "unpublished":
            errors.append("release manifest: candidate_state must be unpublished")
        if manifest.get("source", {}).get("commit") != SOURCE_SNAPSHOT:
            errors.append("release manifest: source snapshot is incorrect")
        if manifest.get("public_exclusions") != PUBLIC_EXCLUSIONS:
            errors.append("release manifest: public exclusions are incorrect")
        entries = manifest["files"]
        listed_paths = [str(entry["path"]) for entry in entries]
        if len(listed_paths) != len(set(listed_paths)):
            errors.append("release manifest: duplicate file paths")
        actual_paths = _actual_public_paths(root)
        if set(listed_paths) != actual_paths:
            missing = sorted(set(listed_paths) - actual_paths)
            unlisted = sorted(actual_paths - set(listed_paths))
            errors.append(
                "release manifest: public file set differs "
                f"(missing={missing[:5]}, unlisted={unlisted[:5]})"
            )
        for entry in entries:
            relative = Path(entry["path"])
            if relative.is_absolute() or ".." in relative.parts:
                errors.append(f"{entry['path']}: unsafe path in release manifest")
                continue
            artifact = root / relative
            if not artifact.is_file():
                errors.append(f"{relative.as_posix()}: file listed in release manifest is missing")
                continue
            if artifact.stat().st_size != entry["bytes"]:
                errors.append(f"{relative.as_posix()}: size differs from release manifest")
            if sha256_file(artifact) != entry["sha256"]:
                errors.append(f"{relative.as_posix()}: sha256 differs from release manifest")
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"{RELEASE_MANIFEST_PATH.as_posix()}: cannot verify: {exc}")
    return errors
