"""Markdown tables generated from summary.json (never from live models)."""

from __future__ import annotations

from typing import Any

from credit_xai.constants import MODEL_NAMES

_METRIC_LABELS = {
    "roc_auc": "ROC-AUC",
    "pr_auc": "PR-AUC",
    "log_loss": "Log loss",
    "brier": "Brier",
    "ece": "ECE",
}


def _fmt(value: float | None, digits: int = 3) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def _fmt_ci(entry: dict[str, Any] | None, digits: int = 3) -> str:
    if not entry or entry.get("mean") is None:
        return "—"
    return (
        f"{entry['mean']:.{digits}f} [{entry['ci_low']:.{digits}f}, {entry['ci_high']:.{digits}f}]"
    )


def metrics_table(summary: dict[str, Any]) -> str:
    run = summary["run"]
    lines = [
        f"Test-set metrics, calibrated model (mean and {int(run['ci_level'] * 100)}% "
        f"bootstrap CI over {run['bootstrap_iterations']} stratified replicates; "
        f"run: `{run['name']}`).",
        "",
        "| Metric | " + " | ".join(MODEL_NAMES) + " |",
        "|---|" + "---|" * len(MODEL_NAMES),
    ]
    for key, label in _METRIC_LABELS.items():
        cells = [
            _fmt_ci(summary["models"][m]["test_metrics"]["calibrated_ci"][key]) for m in MODEL_NAMES
        ]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lat_cells = []
    for m in MODEL_NAMES:
        lat = summary["models"][m]["test_metrics"]["latency"]
        lat_cells.append(
            f"{lat['per_row_ms']['median']:.2f} ms/row · "
            f"{lat['batch_ms_per_1k_rows']['median']:.1f} ms/1k"
        )
    lines.append("| Latency (median) | " + " | ".join(lat_cells) + " |")
    return "\n".join(lines)


def calibration_table(summary: dict[str, Any]) -> str:
    lines = [
        "Calibration method selected on validation log loss only; the test set "
        "never participates in selection.",
        "",
        "| Model | Val log loss (sigmoid) | Val log loss (isotonic) | Selected "
        "| Test ECE uncal → cal | Threshold* |",
        "|---|---|---|---|---|---|",
    ]
    for m in MODEL_NAMES:
        cal = summary["models"][m]["calibration"]
        tm = summary["models"][m]["test_metrics"]
        sig = cal["per_method_val_log_loss"].get("sigmoid")
        iso = cal["per_method_val_log_loss"].get("isotonic")
        lines.append(
            f"| {m} | {_fmt(sig, 4)} | {_fmt(iso, 4)} | **{cal['selected_method']}** | "
            f"{tm['point_uncalibrated']['ece']:.4f} → {tm['point_calibrated']['ece']:.4f} | "
            f"{cal['threshold']:.3f} |"
        )
    lines.append(
        "\n\\* Threshold = validation-quantile at (1 − validation base rate), frozen "
        "before test evaluation."
    )
    return "\n".join(lines)


def xai_table(summary: dict[str, Any]) -> str:
    lines = ["**Global top-5 features** (mean |attribution| on the explained test sample):", ""]
    lines.append("| Rank | " + " | ".join(MODEL_NAMES) + " |")
    lines.append("|---|" + "---|" * len(MODEL_NAMES))
    for rank in range(5):
        cells = [summary["models"][m]["explain"]["top_k"][rank] for m in MODEL_NAMES]
        lines.append(f"| {rank + 1} | " + " | ".join(cells) + " |")

    lines += [
        "",
        "**Explanation stability** (top-k Jaccard vs the full-data reference; "
        "`refit` = model refit on bootstrap resamples of train, `resample` = "
        "explanation-sample resampling only):",
        "",
        "| Model | Method | Jaccard (refit) | Kendall τ (refit) | Jaccard (resample) "
        "| Sign consistency (local, top-5) | Spearman ρ (local) |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in MODEL_NAMES:
        ex = summary["models"][m]["explain"]
        refit = ex["rank_stability"].get("refit") or {}
        resample = ex["rank_stability"].get("resample") or {}
        local = ex["local_stability"].get("aggregate", {})
        lines.append(
            f"| {m} | {ex['method']} | "
            f"{_fmt_ci(refit.get('jaccard_topk'))} | "
            f"{_fmt_ci(refit.get('kendall_tau'))} | "
            f"{_fmt_ci(resample.get('jaccard_topk'))} | "
            f"{_fmt(local.get('sign_consistency_top5_mean'))} | "
            f"{_fmt(local.get('spearman_abs_rank_mean'))} |"
        )

    lines += [
        "",
        "**Faithfulness perturbation** (mean |Δ probability| when replacing the "
        "top-attributed vs a matched-random feature with validation donor values; "
        "ratio > 1 supports faithfulness; sanity check, not causal evidence):",
        "",
        "| Model | Δ top | Δ random | Ratio [CI] | n |",
        "|---|---|---|---|---|",
    ]
    for m in MODEL_NAMES:
        f = summary["models"][m]["explain"]["faithfulness"]
        ci = f["ratio_ci"]
        ratio = (
            f"{f['ratio_top_vs_random']:.2f} [{ci['ci_low']:.2f}, {ci['ci_high']:.2f}]"
            if f["ratio_top_vs_random"] is not None and ci["ci_low"] is not None
            else "—"
        )
        lines.append(
            f"| {m} | {f['delta_top_mean']:.4f} | {f['delta_random_mean']:.4f} | "
            f"{ratio} | {f['n_instances']} |"
        )
    return "\n".join(lines)


def groups_table(summary: dict[str, Any]) -> str:
    lines = [
        "Descriptive snapshot of model behavior on 2005 historical data, by SEX "
        "(UCI coding: 1 = male, 2 = female) and predeclared age bins, at the frozen "
        "base-rate threshold. These numbers support no conclusions about "
        "individuals or lending practices. CIs are suppressed for small cells.",
        "",
    ]
    for m in MODEL_NAMES:
        groups = summary["models"][m]["groups"]["by_group"]
        lines += [
            f"**{m}**",
            "",
            "| Group | n | AUC | FPR | FNR | Selection rate |",
            "|---|---|---|---|---|---|",
        ]
        for gid, g in groups.items():

            def cell(key: str, g: dict[str, Any] = g) -> str:
                point = g.get(key)
                if point is None:
                    return "—"
                ci = (g.get("ci") or {}).get(key) if g.get("ci") else None
                if ci:
                    return f"{point:.3f} [{ci['ci_low']:.3f}, {ci['ci_high']:.3f}]"
                return f"{point:.3f} (small cell)"

            lines.append(
                f"| {gid} | {g['n']} | {cell('auc')} | {cell('fpr')} | "
                f"{cell('fnr')} | {cell('selection_rate')} |"
            )
        lines.append("")
    return "\n".join(lines)


def all_tables(summary: dict[str, Any]) -> dict[str, str]:
    return {
        "metrics": metrics_table(summary),
        "calibration": calibration_table(summary),
        "xai": xai_table(summary),
        "groups": groups_table(summary),
    }
