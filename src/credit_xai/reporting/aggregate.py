"""Aggregate results/raw/** into results/derived/summary.json — the single
source of truth for every number that appears in the READMEs, tables, and
figures. Refuses to aggregate incomplete checkpoint stores (no partial numbers
can ever be published)."""

from __future__ import annotations

import logging
import platform
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from credit_xai import __version__
from credit_xai.config import Config
from credit_xai.constants import FEATURES, MODEL_NAMES
from credit_xai.metrics.bootstrap import percentile_ci, summarize_records
from credit_xai.utils.checkpoints import require_complete
from credit_xai.utils.io import read_json, sha256_file
from credit_xai.utils.seeding import rng

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1
METRIC_KEYS = ("roc_auc", "pr_auc", "log_loss", "brier", "ece")
RATE_KEYS = ("selection_rate", "fpr", "fnr")
STEP_FAITHFULNESS_CI = "report/faithfulness_ci"


class AggregationError(RuntimeError):
    pass


def build_summary(cfg: Config) -> dict[str, Any]:
    raw = Path(cfg.raw_results_dir)
    provenance: list[dict[str, str]] = []
    artifact_timestamps: list[str] = []

    def load(path: Path) -> Any:
        if not path.exists():
            raise AggregationError(f"missing raw artifact: {path} — run the pipeline first")
        provenance.append({"path": path.as_posix(), "sha256": sha256_file(path)})
        if path.suffix != ".json":
            return path
        artifact = read_json(path)
        generated_at = artifact.get("generated_at") if isinstance(artifact, dict) else None
        if isinstance(generated_at, str):
            artifact_timestamps.append(generated_at)
        return artifact

    prepare_meta = load(raw / "data" / "prepare_meta.json")
    ci_level = cfg.evaluation.bootstrap.ci_level

    models: dict[str, Any] = {}
    for name in MODEL_NAMES:
        model_raw = raw / name
        train_meta = load(model_raw / "train_meta.json")
        calibration = load(model_raw / "calibration.json")
        point = load(model_raw / "eval" / "point_metrics.json")
        groups_point = load(model_raw / "eval" / "group_metrics.json")
        gi = load(model_raw / "explain" / "global_importance.json")
        local_cases = load(model_raw / "explain" / "local_cases.json")

        for artifact in (train_meta, calibration, point, groups_point, gi, local_cases):
            if artifact["config_hash"] != cfg.config_hash:
                raise AggregationError(
                    f"{name}: artifact config_hash mismatch — rerun the pipeline "
                    "under the current config before reporting"
                )

        metric_records = require_complete(model_raw / "eval", "bootstrap_metrics")
        group_records = require_complete(model_raw / "eval", "group_bootstrap")
        stability_records = require_complete(model_raw / "explain", "stability")
        faith_records = require_complete(model_raw / "explain", "faithfulness")
        for extra in (
            model_raw / "eval" / "bootstrap_metrics.jsonl",
            model_raw / "eval" / "group_bootstrap.jsonl",
            model_raw / "explain" / "stability.jsonl",
            model_raw / "explain" / "faithfulness.jsonl",
        ):
            provenance.append({"path": extra.as_posix(), "sha256": sha256_file(extra)})

        cal_summary = summarize_records(metric_records, [f"cal_{k}" for k in METRIC_KEYS], ci_level)
        unc_summary = summarize_records(metric_records, [f"unc_{k}" for k in METRIC_KEYS], ci_level)
        rate_summary = summarize_records(metric_records, [f"cal_{k}" for k in RATE_KEYS], ci_level)

        models[name] = {
            "train": {
                "estimator_class": train_meta["estimator_class"],
                "is_fallback": train_meta["is_fallback"],
                "fit_seconds": train_meta["fit_seconds"],
                "n_train_rows": train_meta["n_train_rows"],
            },
            "calibration": {
                "selected_method": calibration["selected_method"],
                "selection_metric": calibration["selection_metric"],
                "selection_split": calibration["selection_split"],
                "per_method_val_log_loss": {
                    method: calibration["per_method_val"][method]["log_loss"]
                    for method in calibration["per_method_val"]
                },
                "per_method_val_ece": {
                    method: calibration["per_method_val"][method]["ece"]
                    for method in calibration["per_method_val"]
                },
                "threshold": calibration["threshold"],
                "threshold_policy": calibration["threshold_policy"],
                "val_base_rate": calibration["val_base_rate"],
            },
            "test_metrics": {
                "n_test_rows": point["n_test_rows"],
                "point_uncalibrated": point["uncalibrated"],
                "point_calibrated": point["calibrated"],
                "rates_at_threshold_point": point["rates_at_threshold"],
                "calibrated_ci": {k: cal_summary[f"cal_{k}"] for k in METRIC_KEYS},
                "uncalibrated_ci": {k: unc_summary[f"unc_{k}"] for k in METRIC_KEYS},
                "rates_ci": {k: rate_summary[f"cal_{k}"] for k in RATE_KEYS},
                "latency": point["latency"],
            },
            "groups": _aggregate_groups(groups_point, group_records, ci_level),
            "explain": {
                "method": gi["method"],
                "method_detail": gi["method_detail"],
                "n_explained": gi["n_explained"],
                "importance": gi["importance"],
                "top_k": gi["top_k"],
                "rank_stability": _aggregate_rank_stability(stability_records, ci_level),
                "local_stability": _aggregate_local_stability(local_cases, stability_records),
                "faithfulness": _aggregate_faithfulness(faith_records, cfg, ci_level),
            },
        }

    summary = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": max(artifact_timestamps),
        "disclaimer": (
            "Historical 2005 educational audit. Not for lending decisions. Not financial advice."
        ),
        "run": {
            "name": cfg.run.name,
            "config_hash": cfg.config_hash,
            "seed": cfg.run.seed,
            "bootstrap_iterations": cfg.evaluation.bootstrap.n_iterations,
            "ci_level": ci_level,
        },
        "dataset": {
            "source": prepare_meta["acquisition"]["source"],
            "content_sha256": prepare_meta["dataset_content_sha256"],
            "n_rows": prepare_meta["cleaning"]["n_rows"],
            "cleaning": prepare_meta["cleaning"],
            "splits": prepare_meta["splits"],
        },
        "environment": {
            "python": platform.python_version(),
            "credit_xai_version": __version__,
            "packages": _package_versions(),
        },
        "models": models,
        "provenance": provenance,
    }
    return summary


def _package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for pkg in ("numpy", "pandas", "sklearn", "shap", "lightgbm", "interpret"):
        try:
            out[pkg] = __import__(pkg).__version__
        except ImportError:
            pass
    return out


def _aggregate_groups(
    groups_point: dict[str, Any], group_records: list[dict[str, Any]], ci_level: float
) -> dict[str, Any]:
    out: dict[str, Any] = {"note": groups_point["note"], "by_group": {}}
    for group_id, point in groups_point["groups"].items():
        entry: dict[str, Any] = dict(point)
        if point["small_cell"]:
            entry["ci"] = None
            entry["ci_note"] = "suppressed: small cell (unstable)"
        else:
            cis: dict[str, Any] = {}
            for key in ("auc", "fpr", "fnr", "selection_rate"):
                values = [
                    r[group_id][key]
                    for r in group_records
                    if r.get(group_id, {}).get(key) is not None
                ]
                if values:
                    low, high = percentile_ci(np.asarray(values), ci_level)
                    cis[key] = {"ci_low": low, "ci_high": high, "n_boot": len(values)}
                else:
                    cis[key] = None
            entry["ci"] = cis
        out["by_group"][group_id] = entry
    return out


def _aggregate_rank_stability(records: list[dict[str, Any]], ci_level: float) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for kind in ("refit", "resample"):
        subset = [r for r in records if r["kind"] == kind]
        if not subset:
            out[kind] = None
            continue
        summary = summarize_records(
            subset, ["jaccard_vs_reference", "kendall_tau_vs_reference"], ci_level
        )
        out[kind] = {
            "n_iterations": len(subset),
            "jaccard_topk": summary["jaccard_vs_reference"],
            "kendall_tau": summary["kendall_tau_vs_reference"],
        }
    return out


def _aggregate_local_stability(
    local_cases: dict[str, Any], stability_records: list[dict[str, Any]]
) -> dict[str, Any]:
    """Sign consistency (majority-sign frequency over the case's top-5 reference
    features) and Spearman rank correlation of |attributions| vs the reference,
    across refit iterations."""
    refits = [r for r in stability_records if r["kind"] == "refit"]
    if not refits:
        return {"note": "no refit iterations configured", "per_case": []}
    cases = local_cases["cases"]
    per_case: list[dict[str, Any]] = []
    for c_idx, case in enumerate(cases):
        ref = np.array([case["attributions_link_scale"][f] for f in FEATURES])
        top5 = np.argsort(-np.abs(ref))[:5]
        boot = np.array([r["local_attributions"][c_idx] for r in refits])  # (B, 23)
        sign_rates = []
        for f in top5:
            signs = np.sign(boot[:, f])
            pos = float((signs > 0).mean())
            neg = float((signs < 0).mean())
            sign_rates.append(max(pos, neg))
        rhos = [
            float(spearmanr(np.abs(ref), np.abs(boot[b])).statistic) for b in range(len(refits))
        ]
        per_case.append(
            {
                "canonical_position": case["canonical_position"],
                "label": case["label"],
                "sign_consistency_top5": float(np.mean(sign_rates)),
                "spearman_abs_rank_mean": float(np.mean(rhos)),
            }
        )
    return {
        "n_refits": len(refits),
        "per_case": per_case,
        "aggregate": {
            "sign_consistency_top5_mean": float(
                np.mean([c["sign_consistency_top5"] for c in per_case])
            ),
            "spearman_abs_rank_mean": float(
                np.mean([c["spearman_abs_rank_mean"] for c in per_case])
            ),
        },
    }


def _aggregate_faithfulness(
    records: list[dict[str, Any]], cfg: Config, ci_level: float
) -> dict[str, Any]:
    delta_top = np.array([r["delta_top"] for r in records])
    delta_rand = np.array([r["delta_random"] for r in records])
    ratio = float(delta_top.mean() / delta_rand.mean()) if delta_rand.mean() > 0 else None

    # paired bootstrap over instances for the ratio CI (deterministic)
    g = rng(cfg.run.seed, STEP_FAITHFULNESS_CI)
    ratios = []
    for _ in range(1000):
        idx = g.integers(0, len(records), size=len(records))
        denom = delta_rand[idx].mean()
        if denom > 0:
            ratios.append(delta_top[idx].mean() / denom)
    ci = percentile_ci(np.asarray(ratios), ci_level) if ratios else (None, None)
    return {
        "hypothesis": (
            "If attributions are faithful, replacing the top-attributed feature "
            "shifts predictions more than replacing a matched-random feature. "
            "Sanity check on the explainer-model pair; not causal evidence."
        ),
        "n_instances": len(records),
        "n_draws_per_instance": cfg.explain.faithfulness.n_draws,
        "delta_top_mean": float(delta_top.mean()),
        "delta_top_median": float(np.median(delta_top)),
        "delta_random_mean": float(delta_rand.mean()),
        "delta_random_median": float(np.median(delta_rand)),
        "ratio_top_vs_random": ratio,
        "ratio_ci": {"ci_low": ci[0], "ci_high": ci[1], "n_boot": len(ratios)},
        "top_feature_counts": _count([r["top_feature"] for r in records]),
    }


def _count(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))
