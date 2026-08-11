# Credit XAI Release Candidate Design

## Status and authority

This design records the owner-approved implementation brief for an unpublished
portfolio release candidate. It does not authorize a remote, push, tag,
release, deployment, model upload, or other publication action.

The private archive remains read-only. The public candidate is a new repository
with new history, built from audited files at source commit
`58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`; source Git metadata is never
copied.

## Purpose and claims

The project is a reproducible Machine Learning / Trustworthy AI portfolio audit
of the 2005 UCI Default of Credit Card Clients dataset. It retains logistic
regression, Explainable Boosting Machine, and LightGBM evidence for calibration,
1,000-replicate stratified bootstrap intervals, explanation stability,
faithfulness perturbation, SHAP/EBM attribution, and descriptive group metrics.

It is not a lending system, financial advice, causal research, or evidence of
discrimination in present-day credit markets. API and Gradio output is an
educational replay of a historical model only. Faithfulness perturbations are
model-behavior sanity checks, and group slices are descriptive diagnostics with
small-cell confidence-interval suppression.

## Chosen release architecture

The selected approach is an allowlisted clean export plus evidence-preserving
hardening:

1. Import committed code, configs, tests, public documentation, manifests,
   compact raw/derived evidence, and generated figures.
2. Exclude source history, environments, caches, raw data, serialized models,
   private progress/handoff material, and platform-specific notebooks.
3. Add executable release gates that independently verify claims, artifact
   completeness and hashes, generated-document consistency, privacy, Git
   identity, packaging, API behavior, and archive contents.
4. Reproduce into a separate output root. Never overwrite accepted artifacts
   until an explicit comparison supports replacement.

Two alternatives were rejected. Copying the old repository and rewriting its
history risks retaining contributor metadata and private objects. Publishing
only `summary.json` and figures would be smaller, but would discard the raw
bootstrap, stability, faithfulness, and attribution evidence required to audit
the claims.

## Data and evaluation boundaries

- The official UCI static archive is the primary source. Its URL, ZIP SHA-256,
  canonical content SHA-256, cleaning recodes, and row counts are pinned.
- The frozen 70/15/15 split is a complete, disjoint partition of 30,000 rows:
  21,000 train, 4,500 validation, and 4,500 test.
- Training uses train; LightGBM may use validation for early stopping.
- Calibration fit, calibration-method selection, fixed local cases, and the
  reporting threshold use validation only.
- Test is used only for final metrics, bootstrap intervals, group snapshots,
  and explanations. It never selects a calibrator or threshold.
- Bootstrap iteration seeds derive deterministically from the root seed, step,
  and iteration. Checkpoints reject incompatible configs and incomplete stores.

## Explanation and group-metric boundaries

- Logistic regression uses analytic linear SHAP in transformed space, summed
  back to the 23 parent features.
- LightGBM uses TreeSHAP; the recorded full-run fallback is tree-path-dependent
  `pred_contrib`, not an interventional explainer.
- EBM uses native additive term contributions; interaction terms are divided
  equally among parents as a declared reporting convention.
- Faithfulness donor replacement breaks feature dependence and cannot support
  causal interpretation.
- A group is unstable when either outcome class has fewer than the configured
  minimum. Point estimates may remain visible, but confidence intervals must be
  suppressed and marked unstable.

## Components and public boundary

- `src/credit_xai/`: pipeline, validation, serving, and release-verification
  logic.
- `tests/`: fast deterministic and integration tests, including release gates.
- `configs/`: CPU-only CI, smoke, and full configurations.
- `manifests/`: dataset, schema, fixed-case, split, and release manifests.
- `results/raw/`: compact machine-produced evidence needed to recompute the
  accepted summary and figures; no raw UCI rows or model bundles.
- `results/derived/`: `summary.json` and generated tables.
- `assets/`: figures generated from accepted artifacts.
- `docs/release/`: verification record, public artifact boundary, and owner
  actions.

Excluded from the candidate are `.git` from the archive, `.venv`, cache and
build directories, source `PROGRESS.md`, notebooks containing handoff/runtime
paths, raw dataset files, model pickles, credentials, and machine-specific
paths.

## Release gates

The candidate is ready only when all of the following have fresh evidence:

- clean, isolated dependency installation on CPU;
- official UCI URL and checksum verification;
- Ruff formatting/checking and strict mypy;
- full pytest suite;
- deterministic report regeneration and committed README/table/figure checks;
- isolated full reproduction when feasible, with explicit comparison status;
- FastAPI and Gradio smoke checks;
- Docker build and health smoke when a daemon is available;
- wheel/sdist build and isolated wheel import/API smoke;
- secret, privacy, path, large-file, archive-content, Git identity, and trailer
  audits;
- clean `main` worktree with no remote configured.

Environmental inability to run Docker or a long reproduction is reported as a
limitation, never converted into a passing claim. Owner-only publication steps
remain in an action report and are not executed.

## Error handling and testing strategy

Existing behavior is characterized before changes. Each release blocker gets a
failing behavioral test, the smallest corrective implementation, and a green
focused test before broader verification. Release scripts fail closed on
missing, incomplete, inconsistent, private, or unverifiable artifacts. Output
roots are explicit and repository-relative by default, which keeps Windows and
non-ASCII workspace paths portable without account-specific workarounds.
