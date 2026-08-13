# Public artifact boundary

## Repository lineage

This public candidate was rebuilt from the audited committed snapshot
`58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`. Its Git history was intentionally
not copied. Later donor development is not part of that snapshot; any useful
change from it must be reviewed and reconciled selectively under this
repository's own tests, evidence, and release boundary.

## Included

- Pipeline source, configs, tests, API/Gradio demo, and CPU-only Docker files.
- Dataset fingerprint, feature schema, frozen split indices, and fixed local
  cases.
- Compact machine-produced raw evidence for calibration, 1,000-replicate
  bootstraps, predictions, SHAP/EBM attributions, stability, faithfulness, and
  descriptive group metrics.
- Derived `summary.json`, Markdown tables, six figures, model/data cards,
  failures log, license, citation, changelog, and release-verification records.

## Excluded

- The private archive's `.git` directory, refs, objects, authorship history,
  contributor trailers, progress log, and handoff material.
- Virtual environments, caches, build outputs, temporary reproduction outputs,
  credentials, account paths, and editor/OS metadata.
- Raw UCI ZIP/XLS/Parquet rows and serialized model/calibrator/background
  bundles.
- Platform-specific notebooks from the private working archive.

## Why raw evidence remains public

The JSONL and compact Parquet files are the evidence behind reported
uncertainty and explanation claims. Removing them would make the 1,000
bootstrap intervals, stability estimates, faithfulness comparison, ROC/PR
figures, and group snapshot difficult to audit. Each retained file is small,
hashable, derived from a public dataset, and covered by the release manifest.

## Interpretation boundary

The files describe model behavior on one Taiwanese bank's 2005 data. They do
not establish causes, discrimination, present-day market behavior, individual
creditworthiness, or suitability for any real decision.
