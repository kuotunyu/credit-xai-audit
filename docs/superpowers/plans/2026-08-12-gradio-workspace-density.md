# Gradio Workspace Density Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the desktop input-column void by compressing the existing result content into a responsive facts band without adding content or changing behavior.

**Architecture:** Keep the existing presenter HTML and Gradio component tree. Use CSS grid on the result shell so probability and metadata share one desktop row, while a narrow-phone override restores source-order stacking. Validate rendered geometry rather than exact CSS tokens.

**Tech Stack:** Gradio 5, CSS Grid, Playwright browser contracts, pytest, Ruff, Mypy, Docker.

## Global Constraints

- Traditional Chinese remains primary; established ML/XAI terms remain in English.
- Preserve all result and interpretation copy, square geometry, typography, palette, and visible focus.
- Do not alter models, accepted metrics, API schemas, pipelines, explanations, or product features.
- Use CPU only, no UCI download, no remote action, and no runtime write into committed paths.

---

### Task 1: Rendered workspace contract

**Files:**
- Inspect: `app/gradio_theme.css`
- Test output: ignored browser measurements only

**Interfaces:**
- Consumes: model-absent UI at `http://127.0.0.1:7860/ui/`.
- Produces: baseline and acceptance geometry at 1,734px.

- [ ] **Step 1: Define the RED contract**

  Measure input/result height, action-to-column-bottom space, result shell height, horizontal overflow, and the probability/metadata row positions. Require at most 32px below the action and shared probability/metadata vertical position.

- [ ] **Step 2: Verify RED**

  Run against committed CSS. Expected: 113px remains below the action and probability ends before metadata begins.

### Task 2: Responsive result facts band

**Files:**
- Modify: `app/gradio_theme.css`

**Interfaces:**
- Consumes: the existing `.audit-result-shell`, `.audit-probability`, `.audit-result-meta`, and `.audit-result-boundary` DOM.
- Produces: a two-column facts row above 520px and source-order stacking at 520px or below.

- [ ] **Step 1: Apply the minimum CSS change**

  Make the result shell a two-column grid, span state/title/body/boundary across both columns, place probability and metadata in the same grid row, remove the empty reserved body line, and tighten only non-interactive vertical rhythm. Add a 520px override that restores one column and automatic rows.

- [ ] **Step 2: Verify GREEN**

  Restart the preview and rerun the exact Task 1 contract. Expected: no more than 32px below the action, input/result height difference no more than 4px, facts share one row, and no overflow.

- [ ] **Step 3: Run focused gates and commit**

  Run the 36 Gradio/presenter tests, Ruff format/check, strict Mypy for `app`, layout detector, and `git diff --check`. Commit as `style: compact gradio result facts`.

### Task 3: State and responsive verification

**Files:**
- Verify: current UI and ignored synthetic CI bundle

**Interfaces:**
- Consumes: model-absent and synthetic LightGBM UI states.
- Produces: geometry evidence at 1,734px, 1,280px, 768px, and 390px.

- [ ] **Step 1: Batch-inspect model-absent widths**

  Check grouping, wrapping, action visibility, 44px targets, full boundary copy, em dashes, and page overflow at all four widths.

- [ ] **Step 2: Verify synthetic success**

  Execute one case with the ignored CPU-only bundle and assert LightGBM, `isotonic`, TreeSHAP, visible attributions, no decision language, and no overflow.

### Task 4: Release evidence and final gates

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: verified browser and container measurements.
- Produces: a clean unpublished local release candidate under renewed Feature Freeze.

- [ ] **Step 1: Record the verified spatial rule**

  Update durable design language and release evidence without screenshots, absolute paths, or synthetic prediction values; regenerate the release manifest.

- [ ] **Step 2: Run full source/package gates**

  Run non-editable setup, uv lock check, Ruff, strict Mypy, all tests, release verifier, build, isolated wheel health, and archive privacy inspection.

- [ ] **Step 3: Rebuild and smoke Docker**

  Build the current CPU-only image, run the network-disabled synthetic pipeline and model-absent/synthetic API/UI smokes, then remove temporary containers, networks, and volumes while retaining the tested image.

- [ ] **Step 4: Commit evidence and audit Git**

  Commit as `docs: record workspace density gate`, confirm clean `main`, owner-only identity, zero trailers/remotes, unchanged source archive, restore the model-absent preview, and renew Feature Freeze.
