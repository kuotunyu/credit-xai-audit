"""Figures generated from raw artifacts (predictions, reliability bins, shapes)
and summary.json — never from live models. Matplotlib Agg backend only."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import precision_recall_curve, roc_curve  # noqa: E402

from credit_xai.config import Config  # noqa: E402
from credit_xai.constants import DISCLAIMER, MODEL_NAMES  # noqa: E402
from credit_xai.utils.io import ensure_dir, read_json  # noqa: E402

logger = logging.getLogger(__name__)

_COLORS = {"logistic": "#4477AA", "ebm": "#EE6677", "lightgbm": "#228833"}


def _finish(fig: plt.Figure, path: Path) -> None:
    fig.text(0.5, 0.005, DISCLAIMER, ha="center", fontsize=7, color="0.4")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("wrote %s", path)


def roc_pr_curves(cfg: Config, assets_dir: Path) -> None:
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(10, 4.2))
    for name in MODEL_NAMES:
        pred = pd.read_parquet(cfg.raw_results_dir / name / "eval" / "predictions.parquet")
        y, p = pred["y"], pred["p_calibrated"]
        fpr, tpr, _ = roc_curve(y, p)
        ax_roc.plot(fpr, tpr, label=name, color=_COLORS[name], lw=1.5)
        precision, recall, _ = precision_recall_curve(y, p)
        ax_pr.plot(recall, precision, label=name, color=_COLORS[name], lw=1.5)
    ax_roc.plot([0, 1], [0, 1], ls="--", color="0.6", lw=1)
    ax_roc.set(xlabel="False positive rate", ylabel="True positive rate", title="ROC (test)")
    ax_pr.set(xlabel="Recall", ylabel="Precision", title="Precision-Recall (test)")
    for ax in (ax_roc, ax_pr):
        ax.legend()
        ax.grid(alpha=0.25)
    _finish(fig, assets_dir / "roc_pr_curves.png")


def reliability_diagram(cfg: Config, summary: dict[str, Any], assets_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    for name in MODEL_NAMES:
        bins = read_json(cfg.raw_results_dir / name / "eval" / "reliability_bins.json")
        conf = [b["mean_predicted"] for b in bins["bins"]]
        acc = [b["observed_rate"] for b in bins["bins"]]
        ece = summary["models"][name]["test_metrics"]["point_calibrated"]["ece"]
        ax.plot(
            conf,
            acc,
            marker="o",
            ms=3.5,
            lw=1.2,
            color=_COLORS[name],
            label=f"{name} (ECE {ece:.3f})",
        )
    ax.plot([0, 1], [0, 1], ls="--", color="0.6", lw=1)
    lim = max(0.05, ax.get_xlim()[1], ax.get_ylim()[1])
    ax.set(
        xlabel="Mean predicted probability (bin)",
        ylabel="Observed default rate (bin)",
        title="Reliability diagram (test, calibrated)",
        xlim=(0, lim),
        ylim=(0, lim),
    )
    ax.legend()
    ax.grid(alpha=0.25)
    _finish(fig, assets_dir / "reliability_diagram.png")


def global_importance_bars(summary: dict[str, Any], assets_dir: Path) -> None:
    fig, axes = plt.subplots(1, len(MODEL_NAMES), figsize=(12.5, 4.2), sharey=False)
    for ax, name in zip(axes, MODEL_NAMES, strict=True):
        ex = summary["models"][name]["explain"]
        top = ex["top_k"][:8][::-1]
        values = [ex["importance"][f] for f in top]
        ax.barh(top, values, color=_COLORS[name])
        ax.set_title(f"{name} ({ex['method']})", fontsize=10)
        ax.tick_params(labelsize=8)
        ax.set_xlabel("mean |attribution| (link scale)", fontsize=8)
    fig.suptitle("Global feature importance (explained test sample)", fontsize=11)
    _finish(fig, assets_dir / "global_importance.png")


def ebm_shape_grid(cfg: Config, assets_dir: Path, n_terms: int = 6) -> None:
    shapes = read_json(cfg.raw_results_dir / "ebm" / "explain" / "ebm_shapes.json")
    importances = shapes["term_importances_mean_abs"]
    continuous = [t for t in shapes["terms"] if t["kind"] == "continuous"]
    continuous.sort(key=lambda t: -importances.get(t["name"], 0.0))
    chosen = continuous[:n_terms]
    if not chosen:
        logger.warning("no continuous EBM terms to plot")
        return
    ncols = 3
    nrows = int(np.ceil(len(chosen) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12.5, 3.4 * nrows), squeeze=False)
    for slot, term in enumerate(chosen):
        ax = axes[slot // ncols][slot % ncols]
        cuts = np.asarray(term["cut_points"], dtype=float)
        # slice off missing (first) and unknown (last) slots
        scores = np.asarray(term["scores"], dtype=float)[1:-1]
        sds = np.asarray(term["score_standard_deviations"], dtype=float)[1:-1]
        edges = np.concatenate(
            [
                [cuts[0] - (cuts[-1] - cuts[0]) * 0.05 - 1],
                cuts,
                [cuts[-1] + (cuts[-1] - cuts[0]) * 0.05 + 1],
            ]
        )
        ax.stairs(scores, edges, color=_COLORS["ebm"], lw=1.4)
        ax.stairs(
            scores + sds, edges, baseline=scores - sds, fill=True, alpha=0.18, color=_COLORS["ebm"]
        )
        ax.axhline(0, color="0.6", lw=0.8, ls="--")
        ax.set_title(term["name"], fontsize=9)
        ax.tick_params(labelsize=8)
        ax.set_ylabel("log-odds contribution", fontsize=8)
    for slot in range(len(chosen), nrows * ncols):
        axes[slot // ncols][slot % ncols].axis("off")
    fig.suptitle("EBM shape functions (top continuous terms, ±1 SD across bags)", fontsize=11)
    _finish(fig, assets_dir / "ebm_shapes_top.png")


def faithfulness_bars(summary: dict[str, Any], assets_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    width = 0.35
    xs = np.arange(len(MODEL_NAMES))
    tops = [summary["models"][m]["explain"]["faithfulness"]["delta_top_mean"] for m in MODEL_NAMES]
    rands = [
        summary["models"][m]["explain"]["faithfulness"]["delta_random_mean"] for m in MODEL_NAMES
    ]
    ax.bar(xs - width / 2, tops, width, label="top-attributed feature replaced", color="#CC3311")
    ax.bar(xs + width / 2, rands, width, label="matched-random feature replaced", color="#88CCEE")
    for i, m in enumerate(MODEL_NAMES):
        f = summary["models"][m]["explain"]["faithfulness"]
        if f["ratio_top_vs_random"] is not None:
            ax.text(
                i,
                max(tops[i], rands[i]) * 1.04,
                f"×{f['ratio_top_vs_random']:.1f}",
                ha="center",
                fontsize=9,
            )
    ax.set_xticks(xs, MODEL_NAMES)
    ax.set_ylabel("mean |Δ predicted probability|")
    ax.set_title("Faithfulness perturbation (test sample)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    _finish(fig, assets_dir / "faithfulness.png")


def group_auc_plot(summary: dict[str, Any], assets_dir: Path) -> None:
    group_ids = list(summary["models"][MODEL_NAMES[0]]["groups"]["by_group"])
    xs = np.arange(len(group_ids))
    width = 0.26
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    for k, name in enumerate(MODEL_NAMES):
        by_group = summary["models"][name]["groups"]["by_group"]
        vals, err_lo, err_hi, flagged = [], [], [], []
        for gid in group_ids:
            g = by_group[gid]
            auc = g.get("auc")
            vals.append(np.nan if auc is None else auc)
            ci = (g.get("ci") or {}).get("auc") if g.get("ci") else None
            if ci and auc is not None:
                err_lo.append(auc - ci["ci_low"])
                err_hi.append(ci["ci_high"] - auc)
            else:
                err_lo.append(0.0)
                err_hi.append(0.0)
                flagged.append(gid)
        ax.bar(
            xs + (k - 1) * width,
            vals,
            width,
            label=name,
            color=_COLORS[name],
            yerr=[err_lo, err_hi],
            capsize=2,
            error_kw={"lw": 0.8},
        )
    ax.set_xticks(xs, [g.replace("=", "\n") for g in group_ids], fontsize=8)
    ax.set_ylim(0.5, 1.0)
    ax.set_ylabel("ROC-AUC (test)")
    ax.set_title("Group snapshot: AUC by predeclared group (bars without whiskers = small cell)")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    _finish(fig, assets_dir / "group_auc.png")


def render_all(cfg: Config, summary: dict[str, Any], assets_dir: str | Path) -> list[str]:
    assets_dir = ensure_dir(assets_dir)
    roc_pr_curves(cfg, assets_dir)
    reliability_diagram(cfg, summary, assets_dir)
    global_importance_bars(summary, assets_dir)
    ebm_shape_grid(cfg, assets_dir)
    faithfulness_bars(summary, assets_dir)
    group_auc_plot(summary, assets_dir)
    return [p.name for p in sorted(Path(assets_dir).glob("*.png"))]
