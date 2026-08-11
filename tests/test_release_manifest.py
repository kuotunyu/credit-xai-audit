from __future__ import annotations

import shutil
from pathlib import Path

from credit_xai.release.manifest import SOURCE_SNAPSHOT, build_release_manifest
from credit_xai.utils.io import sha256_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_release_manifest_is_sorted_complete_and_self_excluding() -> None:
    manifest = build_release_manifest(PROJECT_ROOT)
    paths = [entry["path"] for entry in manifest["files"]]

    assert paths == sorted(paths)
    assert "manifests/release_manifest.json" not in paths
    assert manifest["source"]["commit"] == SOURCE_SNAPSHOT
    assert manifest["evidence_budgets"] == {
        "bootstrap_iterations_per_model": 1000,
        "explanation_refits_per_model": 20,
        "explanation_resamples_per_model": 200,
        "faithfulness_instances_per_model": 2000,
        "explained_test_rows_per_model": 4500,
    }
    assert manifest["public_exclusions"] == [
        ".git history from private archive",
        "environments and caches",
        "private progress, handoff, and agent notes",
        "raw UCI dataset rows and archives",
        "serialized model bundles",
        "platform-specific notebooks",
    ]
    readme = next(entry for entry in manifest["files"] if entry["path"] == "README.md")
    assert readme["sha256"] == sha256_file(PROJECT_ROOT / "README.md")
    assert readme["bytes"] == (PROJECT_ROOT / "README.md").stat().st_size


def test_release_manifest_contains_no_excluded_paths() -> None:
    paths = [entry["path"].lower() for entry in build_release_manifest(PROJECT_ROOT)["files"]]

    assert not any("progress" in path or path.startswith("notebooks/") for path in paths)
    assert not any(path.startswith("data/") for path in paths)
    assert not any(path.startswith("models/") and path != "models/.gitkeep" for path in paths)


def test_release_manifest_builds_without_git_metadata(tmp_path: Path) -> None:
    configs = tmp_path / "configs"
    configs.mkdir()
    shutil.copyfile(PROJECT_ROOT / "configs" / "full.yaml", configs / "full.yaml")
    (tmp_path / "README.md").write_text("public candidate\n", encoding="utf-8")

    manifest = build_release_manifest(tmp_path)

    assert [entry["path"] for entry in manifest["files"]] == [
        "README.md",
        "configs/full.yaml",
    ]
