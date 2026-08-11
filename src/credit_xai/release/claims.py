"""Verify that public claims remain backed by committed evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from credit_xai.config import canonical_json
from credit_xai.constants import MODEL_NAMES, UCI_STATIC_ZIP_URL
from credit_xai.reporting.render import SECTIONS, _marker_pattern, render_block
from credit_xai.reporting.tables import all_tables


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON value must be an object")
    return value


def verify_claims(root: str | Path) -> list[str]:
    """Return release-claim violations without changing the candidate tree."""
    root = Path(root)
    errors: list[str] = []
    split_path = root / "manifests" / "split_manifest.json"
    try:
        split = _read_json(split_path)
        indices = split["indices"]
        names = ("train", "val", "test")
        flattened = [int(i) for name in names for i in indices[name]]
        n_rows = int(split["n_rows"])
        if len(flattened) != n_rows or set(flattened) != set(range(n_rows)):
            errors.append(
                "manifests/split_manifest.json: split indices do not form a complete partition"
            )
        canonical_indices = canonical_json(
            {name: [int(i) for i in indices[name]] for name in names}
        ).encode("utf-8")
        if hashlib.sha256(canonical_indices).hexdigest() != split.get("indices_sha256"):
            errors.append("manifests/split_manifest.json: indices_sha256 does not match indices")
        _verify_dataset_fingerprint(root, split, errors)
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"manifests/split_manifest.json: cannot verify split partition: {exc}")
    _verify_calibration(root, errors)
    _verify_checkpoints(root, errors)
    _verify_summary_boundaries(root, errors)
    _verify_generated_outputs(root, errors)
    return errors


def _verify_calibration(root: Path, errors: list[str]) -> None:
    for model in MODEL_NAMES:
        relative = Path("results") / "raw" / model / "calibration.json"
        try:
            calibration = _read_json(root / relative)
            if calibration.get("selection_split") != "val":
                errors.append(f"{relative.as_posix()}: calibration must be selected on validation")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{relative.as_posix()}: cannot verify calibration boundary: {exc}")


def _verify_checkpoints(root: Path, errors: list[str]) -> None:
    config_path = root / "configs" / "full.yaml"
    try:
        with config_path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle)
        expected = {
            Path("eval") / "bootstrap_metrics": int(
                config["evaluation"]["bootstrap"]["n_iterations"]
            ),
            Path("eval") / "group_bootstrap": int(
                config["evaluation"]["bootstrap"]["n_iterations"]
            ),
            Path("explain") / "stability": int(
                config["explain"]["rank_stability"]["n_refits"]
                + config["explain"]["rank_stability"]["n_resamples"]
            ),
            Path("explain") / "faithfulness": int(config["explain"]["faithfulness"]["n_instances"]),
        }
    except (FileNotFoundError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        errors.append(f"configs/full.yaml: cannot determine checkpoint budgets: {exc}")
        return

    for model in MODEL_NAMES:
        for checkpoint, expected_count in expected.items():
            base = Path("results") / "raw" / model / checkpoint
            jsonl_path = root / base.with_suffix(".jsonl")
            meta_path = root / base.with_suffix(".meta.json")
            try:
                meta = _read_json(meta_path)
                if meta.get("status") != "complete":
                    errors.append(f"{base.as_posix()}: checkpoint status is not complete")
                if int(meta.get("n_iterations", -1)) != expected_count:
                    errors.append(
                        f"{base.as_posix()}: checkpoint metadata must declare "
                        f"{expected_count} iterations"
                    )
                records = [
                    json.loads(line)
                    for line in jsonl_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                iterations = [int(record["iter"]) for record in records]
                if len(iterations) != expected_count or set(iterations) != set(
                    range(expected_count)
                ):
                    errors.append(
                        f"{base.as_posix()}: checkpoint must contain exactly "
                        f"{expected_count} unique iterations"
                    )
            except (
                FileNotFoundError,
                KeyError,
                TypeError,
                ValueError,
                json.JSONDecodeError,
            ) as exc:
                errors.append(f"{base.as_posix()}: cannot verify checkpoint: {exc}")


def _verify_summary_boundaries(root: Path, errors: list[str]) -> None:
    relative = Path("results") / "derived" / "summary.json"
    try:
        summary = _read_json(root / relative)
        expected_methods = {
            "logistic": "linear_shap",
            "ebm": "ebm_native",
            "lightgbm": "tree_shap",
        }
        if summary["run"]["name"] != "full" or summary["run"]["bootstrap_iterations"] != 1000:
            errors.append(
                f"{relative.as_posix()}: accepted release evidence must be the "
                "1000-bootstrap full run"
            )
        for model, expected_method in expected_methods.items():
            model_summary = summary["models"][model]
            raw_calibration = _read_json(root / "results" / "raw" / model / "calibration.json")
            summary_calibration = model_summary["calibration"]
            if summary_calibration.get("selection_split") != "val":
                errors.append(
                    f"{relative.as_posix()}: {model} summary calibration must use validation"
                )
            for key in ("selected_method", "selection_split", "threshold"):
                if summary_calibration.get(key) != raw_calibration.get(key):
                    errors.append(
                        f"{relative.as_posix()}: {model} calibration {key} differs "
                        "from raw evidence"
                    )
            actual_method = model_summary["explain"]["method"]
            raw_method = _read_json(
                root / "results" / "raw" / model / "explain" / "global_importance.json"
            )["method"]
            if actual_method != expected_method or raw_method != expected_method:
                errors.append(
                    f"{relative.as_posix()}: {model} explanations must use {expected_method}"
                )
            hypothesis = str(model_summary["explain"]["faithfulness"]["hypothesis"]).lower()
            if "not causal evidence" not in hypothesis:
                errors.append(
                    f"{relative.as_posix()}: {model} faithfulness claim must reject "
                    "causal interpretation"
                )
            for group_id, group in model_summary["groups"]["by_group"].items():
                if group.get("small_cell") and group.get("ci") is not None:
                    errors.append(
                        f"{relative.as_posix()}: {model} {group_id} small cell must "
                        "have CI suppressed"
                    )
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{relative.as_posix()}: cannot verify summary boundaries: {exc}")


def _verify_dataset_fingerprint(root: Path, split: dict[str, Any], errors: list[str]) -> None:
    try:
        fingerprint = _read_json(root / "manifests" / "dataset_fingerprint.json")
        prepare = _read_json(root / "results" / "raw" / "data" / "prepare_meta.json")
        summary = _read_json(root / "results" / "derived" / "summary.json")
        content_hashes = {
            fingerprint["content_sha256"],
            split["dataset_content_sha256"],
            prepare["dataset_content_sha256"],
            summary["dataset"]["content_sha256"],
        }
        zip_hashes = {fingerprint["zip_sha256"], prepare["acquisition"]["zip_sha256"]}
        urls = {fingerprint["url"], prepare["acquisition"]["url"], UCI_STATIC_ZIP_URL}
        if len(content_hashes) != 1 or len(zip_hashes) != 1 or len(urls) != 1:
            errors.append(
                "manifests/dataset_fingerprint.json: dataset fingerprint differs from evidence"
            )
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(
            f"manifests/dataset_fingerprint.json: cannot verify dataset fingerprint: {exc}"
        )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_generated_outputs(root: Path, errors: list[str]) -> None:
    summary_relative = Path("results") / "derived" / "summary.json"
    try:
        summary = _read_json(root / summary_relative)
        for record in summary["provenance"]:
            artifact_relative = Path(record["path"])
            artifact_path = root / artifact_relative
            actual = _sha256(artifact_path)
            if actual != record["sha256"]:
                errors.append(
                    f"{artifact_relative.as_posix()}: sha256 differs from summary provenance"
                )

        tables = all_tables(summary)
        for name, content in tables.items():
            table_relative = Path("results") / "derived" / "tables" / f"{name}.md"
            if (root / table_relative).read_text(encoding="utf-8") != content + "\n":
                errors.append(f"{table_relative.as_posix()}: content differs from summary")

        run_label = f"{summary['run']['name']} / config {summary['run']['config_hash'][:12]}"
        for readme_name in ("README.md", "README_zh-TW.md"):
            text = (root / readme_name).read_text(encoding="utf-8")
            for section in SECTIONS:
                match = _marker_pattern(section).search(text)
                expected = render_block(section, tables[section.lower()], run_label)
                if match is None or match.group(0) != expected:
                    errors.append(f"{readme_name}: AUTOGEN {section} differs from summary")
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{summary_relative.as_posix()}: cannot verify generated outputs: {exc}")
