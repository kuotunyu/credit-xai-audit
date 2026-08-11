from __future__ import annotations

import json
import shutil
from pathlib import Path

from credit_xai.release.claims import verify_claims

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _candidate_copy(tmp_path: Path) -> Path:
    root = tmp_path / "candidate"
    root.mkdir()
    for directory in ("configs", "manifests", "results"):
        shutil.copytree(PROJECT_ROOT / directory, root / directory)
    for filename in ("README.md", "README_zh-TW.md"):
        shutil.copy2(PROJECT_ROOT / filename, root / filename)
    return root


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def test_claim_verifier_accepts_committed_evidence(tmp_path: Path) -> None:
    assert verify_claims(_candidate_copy(tmp_path)) == []


def test_claim_verifier_rejects_overlapping_split_indices(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    manifest_path = root / "manifests" / "split_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["indices"]["val"][0] = manifest["indices"]["train"][0]
    _write_json(manifest_path, manifest)

    errors = verify_claims(root)

    assert any("split" in error and "partition" in error for error in errors)


def test_claim_verifier_rejects_test_selected_calibration(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    calibration_path = root / "results" / "raw" / "logistic" / "calibration.json"
    calibration = _read_json(calibration_path)
    calibration["selection_split"] = "test"
    _write_json(calibration_path, calibration)

    errors = verify_claims(root)

    assert any("calibration" in error and "validation" in error for error in errors)


def test_claim_verifier_rejects_incomplete_bootstrap_records(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    records_path = root / "results" / "raw" / "ebm" / "eval" / "bootstrap_metrics.jsonl"
    lines = records_path.read_text(encoding="utf-8").splitlines()
    records_path.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    errors = verify_claims(root)

    assert any("bootstrap_metrics" in error and "1000" in error for error in errors)


def test_claim_verifier_rejects_wrong_model_explainer_mapping(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    summary_path = root / "results" / "derived" / "summary.json"
    summary = _read_json(summary_path)
    summary["models"]["lightgbm"]["explain"]["method"] = "linear_shap"
    _write_json(summary_path, summary)

    errors = verify_claims(root)

    assert any("lightgbm" in error and "tree_shap" in error for error in errors)


def test_claim_verifier_rejects_small_cell_confidence_interval(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    summary_path = root / "results" / "derived" / "summary.json"
    summary = _read_json(summary_path)
    group = summary["models"]["ebm"]["groups"]["by_group"]["age=60+"]
    assert group["small_cell"] is True
    group["ci"] = {"auc": {"ci_low": 0.1, "ci_high": 0.9, "n_boot": 1000}}
    _write_json(summary_path, summary)

    errors = verify_claims(root)

    assert any("small cell" in error and "CI" in error for error in errors)


def test_claim_verifier_rejects_causal_faithfulness_claim(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    summary_path = root / "results" / "derived" / "summary.json"
    summary = _read_json(summary_path)
    summary["models"]["logistic"]["explain"]["faithfulness"]["hypothesis"] = (
        "The perturbation proves the feature causes the outcome."
    )
    _write_json(summary_path, summary)

    errors = verify_claims(root)

    assert any("faithfulness" in error and "causal" in error for error in errors)


def test_claim_verifier_rejects_modified_readme_autogen_block(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    readme_path = root / "README.md"
    text = readme_path.read_text(encoding="utf-8")
    readme_path.write_text(text.replace("ROC-AUC | 0.726", "ROC-AUC | 0.999", 1), encoding="utf-8")

    errors = verify_claims(root)

    assert any("README.md" in error and "AUTOGEN" in error for error in errors)


def test_claim_verifier_rejects_modified_derived_table(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    table_path = root / "results" / "derived" / "tables" / "metrics.md"
    table_path.write_text("altered\n", encoding="utf-8")

    errors = verify_claims(root)

    assert any("tables/metrics.md" in error and "summary" in error for error in errors)


def test_claim_verifier_rejects_raw_artifact_hash_drift(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    artifact_path = root / "results" / "raw" / "logistic" / "eval" / "point_metrics.json"
    artifact_path.write_text(artifact_path.read_text(encoding="utf-8") + " ", encoding="utf-8")

    errors = verify_claims(root)

    assert any("point_metrics.json" in error and "sha256" in error for error in errors)


def test_claim_verifier_rejects_stale_split_index_hash(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    manifest_path = root / "manifests" / "split_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["indices"]["val"][0], manifest["indices"]["val"][1] = (
        manifest["indices"]["val"][1],
        manifest["indices"]["val"][0],
    )
    _write_json(manifest_path, manifest)

    errors = verify_claims(root)

    assert any("indices_sha256" in error for error in errors)


def test_claim_verifier_rejects_dataset_fingerprint_drift(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    fingerprint_path = root / "manifests" / "dataset_fingerprint.json"
    fingerprint = _read_json(fingerprint_path)
    fingerprint["content_sha256"] = "0" * 64
    _write_json(fingerprint_path, fingerprint)

    errors = verify_claims(root)

    assert any("dataset fingerprint" in error for error in errors)


def test_claim_verifier_rejects_summary_calibration_boundary_drift(tmp_path: Path) -> None:
    root = _candidate_copy(tmp_path)
    summary_path = root / "results" / "derived" / "summary.json"
    summary = _read_json(summary_path)
    summary["models"]["ebm"]["calibration"]["selection_split"] = "test"
    _write_json(summary_path, summary)

    errors = verify_claims(root)

    assert any("summary" in error and "validation" in error for error in errors)
