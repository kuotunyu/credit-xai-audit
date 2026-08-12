# Gradio Audit Worksheet Implementation Plan

**Goal:** Replace the fragmented tabbed case-input plane with one complete,
orderly 23-field audit worksheet while preserving behavior and release scope.

**Architecture:** Keep presenters, callbacks, outputs, API behavior, and the
right result plane unchanged. Recompose only the Gradio input component tree
and its CSS into a toolbar, four canonical feature-group ledgers, and one
footer. Prove the structure with component-config tests and rendered-browser
RED/GREEN contracts before renewing release evidence.

**Tech Stack:** Python 3.11, Gradio 5, CSS Grid, pytest, Ruff, strict Mypy,
in-app Chromium, Docker.

## Global constraints

- Traditional Chinese remains primary; source-schema and established ML/XAI
  terms remain English.
- Use square geometry and the approved Editorial Audit Console palette.
- Do not change models, metrics, result artifacts, API schemas, dependencies,
  Docker policy, or product claims.
- Use CPU only and synthetic data only for runtime smoke.
- Do not create a remote, push, PR, tag, Release, upload, or deployment.
- Commit only as `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` with
  no contributor trailer.

## Task 1: RED structural contracts

**Files:** `tests/test_gradio.py`, rendered local `/ui/`.

- Replace tab-specific implementation assertions with component-tree
  contracts: no tab items; four feature-group rows in canonical order; each
  row contains the expected number labels; one input footer owns the case note
  and primary action.
- Render a desktop RED contract that requires all four groups visible, 23
  visible numeric controls, equal field widths per group, a consistent label
  rail, no tabs, action-tail blank space at most 12px, and zero positive
  horizontal overflow.
- Confirm failure against the incumbent tabbed interface before production
  edits.

## Task 2: Minimal worksheet implementation

**Files:** `app/gradio_ui.py`, `app/gradio_theme.css`.

- Read Impeccable craft-floor guidance immediately before editing.
- Replace the tab tree with four canonical `audit-feature-group` rows. Each row
  contains one semantic group heading and the existing `gr.Number` controls in
  canonical order.
- Move the case note and primary action into one `audit-input-footer`.
- Delete obsolete tab, grid-area, detached-action, and conditional-tab CSS.
- Add explicit 5/6 desktop, 3 compact, and 2 phone field tracks; use shared
  rules rather than boxes.
- Preserve `ordered_controls`, callbacks, values, labels, queueing, and all
  output components.
- Run focused Gradio/presenter tests, Ruff format/check, and strict Mypy.

## Task 3: Rendered GREEN and bounded refinement

**Files:** local preview; production CSS only if a measured defect remains.

- Reload the local preview and run the desktop contract at 1,908px and 1,280px.
- Run responsive geometry at 768px and 390px: 3/2 tracks, complete labels,
  canonical order, 44px targets, and no overflow/errors.
- Inspect one desktop and one phone screenshot as a batch. Make at most one
  measured correction batch and one confirmation pass.
- Verify model-absent state and an isolated synthetic-bundle success state,
  including model/calibration/explanation-method agreement and attribution
  output.

## Task 4: Durable evidence

**Files:** `DESIGN.md`, `.impeccable/design.json`, `CHANGELOG.md`,
`docs/release/VERIFICATION.md`, `manifests/release_manifest.json`.

- Replace stale tab-ledger language with the complete worksheet contract.
- Record only verified responsive, interaction, and source-test evidence; do
  not include local paths, case-level probabilities, or sensitive logs.
- Regenerate the release manifest and run the release verifier.

## Task 5: Final release gates

- Rebuild and inspect the CPU-only API image.
- Run isolated synthetic pipeline plus API/UI smoke in disposable runtime
  storage; verify no raw dataset, model bundle, `.env`, private notes, or
  committed-result pollution.
- Remove temporary containers, network, and volume; retain only the test image.
- Run non-editable package setup/import verification, Ruff format/check,
  strict Mypy, full pytest, release verifier, package build, isolated wheel
  import/API health, privacy/claim/manifest audit, and Git identity/trailer
  audit.
- Commit small English changes, leave `main` clean, and keep the local
  model-absent preview available for owner review.
