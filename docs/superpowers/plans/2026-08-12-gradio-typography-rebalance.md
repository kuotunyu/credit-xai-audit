# Gradio Typography Rebalance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebalance the Gradio interface so the thesis no longer overwhelms the page and all operational text is comfortably readable at real browser sizes.

**Architecture:** Keep the existing HTML, interactions, product language, and Editorial Audit Console identity. Change only the CSS role scale and the minimum layout adjustments required by that scale, then update the durable design and release evidence generated from the verified render.

**Tech Stack:** Gradio 5, CSS, Playwright/Chromium browser contracts, pytest, Ruff, Mypy, Docker.

## Global Constraints

- 正體中文 remains primary; established ML/XAI terms remain in English.
- Keep square geometry, the existing palette, local system fonts, and the single tonal result plane.
- Do not alter models, accepted metrics, API schemas, pipelines, explanations, product features, or safety copy.
- Do not add network fonts, dependencies, raw data, bundles, or runtime writes to the public tree.
- Use no GPU and no real UCI download; success-state verification uses the existing ignored synthetic bundle.
- Do not create a remote, push, tag, release, deploy, or add contributor trailers.

---

### Task 1: Browser typography contract

**Files:**
- Inspect: `app/gradio_theme.css`
- Inspect: `app/gradio_ui.py`
- Evidence output: ignored `tmp/ui-type-rebalance/`

**Interfaces:**
- Consumes: the running model-absent UI at `http://127.0.0.1:7860/ui/`.
- Produces: measured baseline and acceptance values for named rendered roles.

- [ ] **Step 1: Define the failing browser contract**

  At a 1,656px viewport, query computed styles for the thesis, status, section marker, form metadata, number label/value, result boundary, table cell, and footer. Assert thesis is at most 40px; ordinary roles are at least 15px; operational labels are at least 14px; numeric values are at least 18px.

- [ ] **Step 2: Run the contract and verify RED**

  Run the Playwright contract against the committed UI. Expected: failure reports the 44.71px thesis plus the 12.16–13.76px roles. This is a one-off rendered-behavior test, not a permanent exact-token test.

### Task 2: Apply the role scale

**Files:**
- Modify: `app/gradio_theme.css`

**Interfaces:**
- Consumes: the thresholds from Task 1 and existing selectors.
- Produces: one coherent responsive type ramp without HTML or behavior changes.

- [ ] **Step 1: Implement the minimum CSS change**

  Set the container body role to 16px; cap the desktop thesis at 40px; raise status, marker, metadata, tab, field label, result metadata, evidence, and footer roles to their specified floors; set values/actions to 18px/16px; rebalance the workspace to 7/5; tighten hero/KPI/workspace spacing only where the new scale requires it.

- [ ] **Step 2: Restart the preview and verify GREEN**

  Re-run the exact Task 1 browser contract. Expected: every role clears its independent threshold, the thesis is within 36–40px, and the 1,656px page has no horizontal overflow or page errors.

- [ ] **Step 3: Run focused source gates**

  Run `pytest tests/test_gradio.py tests/test_gradio_presenter.py -q`, Ruff format/check for `app` and those tests, strict Mypy for `app`, and `git diff --check`.

- [ ] **Step 4: Commit the production change**

  Commit `app/gradio_theme.css` as `style: rebalance gradio typography` using the configured owner identity and no trailers.

### Task 3: Responsive and success-state verification

**Files:**
- Evidence output: ignored `tmp/ui-type-rebalance/`

**Interfaces:**
- Consumes: model-absent default config and existing ignored `configs/ci.yaml` synthetic bundle.
- Produces: screenshots and computed-style reports at 1,656px, 1,280px, 768px, and 390px.

- [ ] **Step 1: Inspect all model-absent widths in one batch**

  Capture full-page screenshots and role measurements at all four widths. Check real copy wrapping, no page overflow, touch targets of at least 44px, visible focus, stable empty-result geometry, and the absence of fabricated values.

- [ ] **Step 2: Make at most one consolidated correction**

  If the first batch exposes a material hierarchy, wrapping, or density defect, correct all observed defects in one CSS patch and rerun one confirmation batch. Do not enter an open-ended polish loop.

- [ ] **Step 3: Verify the synthetic success state**

  Start the existing CPU-only CI configuration, execute one case, and assert `LightGBM`, `isotonic`, `TreeSHAP`, calibrated/uncalibrated probability labels, visible attributions, no decision language, and no overflow at desktop and phone widths.

### Task 4: Durable design and release evidence

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: verified computed values and screenshots from Tasks 2–3.
- Produces: consistent human-readable design rules and manifest hashes.

- [ ] **Step 1: Update the design system**

  Replace the obsolete 38–48px thesis range and 12px metadata floor with the verified balanced ramp. Update the component CSS snippets in `.impeccable/design.json` to match the shipped numeric field, status, KPI, and primary-action roles.

- [ ] **Step 2: Record evidence without local paths or prediction values**

  Add baseline/green role measurements, responsive outcomes, and synthetic model/method agreement to `VERIFICATION.md`. Add one concise typography-rebalance entry to `CHANGELOG.md`.

- [ ] **Step 3: Regenerate and verify the manifest**

  Run `write_release_manifest('.')`, `credit_xai.release.verify all`, JSON parsing for `.impeccable/design.json`, and `git diff --check`.

- [ ] **Step 4: Commit evidence**

  Commit the design, changelog, verification, and manifest files as `docs: record typography release gate`.

### Task 5: Final release verification

**Files:**
- Verify only: complete committed tree and built archives.

**Interfaces:**
- Consumes: final committed source and evidence.
- Produces: a clean unpublished local release candidate and restored preview.

- [ ] **Step 1: Run complete source/package gates**

  Run non-editable setup, `uv lock --check`, Ruff format/check, strict Mypy, all 145 tests, release verifier, `python -m build`, isolated wheel import/API health, and archive privacy/content inspection.

- [ ] **Step 2: Rebuild and smoke the current Docker image**

  Run Compose config/build, inspect non-root/CPU/privacy boundaries, execute the network-disabled synthetic pipeline, verify container health and the exact browser typography contract on the image, and remove all temporary runtime resources while retaining the tested image.

- [ ] **Step 3: Audit Git and restore preview**

  Confirm `main`, clean status, no remote, owner-only author/committer identities, zero contributor trailers, unchanged source archive, and no remote actions. Restore the model-absent preview at `http://127.0.0.1:7860/ui/` and renew Feature Freeze.
