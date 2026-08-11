"""The `report` step: aggregate -> summary.json -> tables -> figures -> README injection."""

from __future__ import annotations

import logging
from pathlib import Path

from credit_xai.config import Config
from credit_xai.reporting.aggregate import build_summary
from credit_xai.reporting.figures import render_all
from credit_xai.reporting.render import inject
from credit_xai.reporting.tables import all_tables
from credit_xai.utils.io import atomic_write_json, ensure_dir

logger = logging.getLogger(__name__)

README_FILES = ("README.md", "README_zh-TW.md")


def run(cfg: Config, readme_dir: str | Path = ".", assets_dir: str | Path = "assets") -> None:
    summary = build_summary(cfg)
    derived = ensure_dir(cfg.derived_results_dir)
    atomic_write_json(derived / "summary.json", summary)
    logger.info("summary.json written (%d models)", len(summary["models"]))

    tables = all_tables(summary)
    tables_dir = ensure_dir(derived / "tables")
    for name, content in tables.items():
        (tables_dir / f"{name}.md").write_text(content + "\n", encoding="utf-8", newline="\n")

    figures = render_all(cfg, summary, assets_dir)
    logger.info("figures: %s", ", ".join(figures))

    run_label = f"{summary['run']['name']} / config {summary['run']['config_hash'][:12]}"
    for readme in README_FILES:
        readme_path = Path(readme_dir) / readme
        if readme_path.exists():
            inject(readme_path, tables, run_label)
        else:
            logger.warning("%s not found; skipping injection", readme_path)
    logger.info("report complete")
