# Gradio Visual Chrome Distillation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the boxed spreadsheet-like chrome with a borderless editorial console while preserving square geometry, accessibility, evidence, and behavior.

**Architecture:** Keep the existing Gradio component tree and all Python callbacks unchanged. Refine `app/gradio_theme.css` so semantic grouping comes from typography, proximity, tonal fields, and selective horizontal rules; use rendered Playwright style/geometry assertions for the CSS red-green cycle because this is a visual behavior rather than a Python API contract.

**Tech Stack:** Gradio 5, CSS, bundled Chromium/Playwright, Python 3.11, pytest.

## Global Constraints

- Keep Traditional Chinese primary and retain Logistic, EBM, LightGBM, Calibration, Bootstrap, SHAP, Faithfulness, Stability, and attribution terminology in English.
- Preserve square corners; do not replace rectangles with rounded cards or pills.
- Do not change model artifacts, accepted metrics, public claims, callbacks, API schema, dependencies, or explanation mappings.
- Keep exactly one solid primary action; use amber only for scope and runtime state.
- Maintain 44px minimum interactive targets, visible focus, and no page-level horizontal overflow.
- Do not publish, add a remote, or add contributor trailers.

---

### Task 1: Distill visual chrome

**Files:**
- Modify: `app/gradio_theme.css`

**Interfaces:**
- Consumes: existing semantic classes emitted by `app/gradio_ui.py`.
- Produces: unchanged Gradio configuration and event outputs with a new borderless rendered treatment.

- [ ] **Step 1: Capture the failing rendered contract**

Run a Playwright computed-style audit against the current 1280px model-absent page. Assert that these unwanted conditions are absent: status cell left borders, KPI cell right borders, workspace outer side borders, tab right borders, numeric field side borders, outlined secondary action, and a primary action wider than 260px. Confirm the assertions fail on the boxed design.

- [ ] **Step 2: Implement the minimal CSS transformation**

Change only the incumbent classes:

- render `.audit-statuses` as an inline cluster and remove status cell borders/background blocks;
- remove KPI cell dividers and retain one quiet row transition;
- remove workspace outer and column split borders, making the input background transparent;
- use underline-only case and numeric inputs;
- remove tab boxes and retain only the active underline;
- make the secondary action text-led and the desktop primary action compact/right-aligned;
- remove attribution/evidence outer borders while retaining horizontal row rules and the result tonal plane;
- keep compact layouts wrapping without recreating card grids, with the primary action full width only below 520px.

- [ ] **Step 3: Run focused source gates**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -q
.\.venv\Scripts\ruff.exe format --check app tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\ruff.exe check app tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\mypy.exe --strict app
```

Expected: 36 tests pass and all static checks pass.

- [ ] **Step 4: Verify rendered GREEN behavior**

Repeat the computed-style audit and require all seven chrome assertions to pass. Capture model-absent screenshots at 1900px, 1280px, 768px, and 390px; assert committed KPIs, hidden initial attribution band, no overflow, and no page errors. Then exercise the ignored synthetic LightGBM bundle and assert `TreeSHAP`, the conditional attribution band, no decision language, and the same responsive constraints.

- [ ] **Step 5: Commit**

```powershell
git add app/gradio_theme.css
git commit -m "style: distill gradio visual chrome"
```

### Task 2: Release evidence and final gates

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Modify: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: the verified model-absent and synthetic browser measurements.
- Produces: deterministic unpublished release evidence matching the implemented visual system.

- [ ] **Step 1: Record the borderless design rule**

Document that lines mark transitions rather than containers, inputs are underline-only, the primary action is the only solid control, and the result plane is the only major content surface.

- [ ] **Step 2: Refresh and verify the release manifest**

Run:

```powershell
.\.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; write_release_manifest('.')"
.\.venv\Scripts\python.exe -m credit_xai.release.verify all
```

Expected: `release gates passed: all`.

- [ ] **Step 3: Run complete release gates**

Run `uv lock --check`, Ruff format/check, strict Mypy, all tests, `python -m build`, archive privacy inspection, and the release verifier. Record exact test count and browser evidence.

- [ ] **Step 4: Commit and restore public preview**

```powershell
git add DESIGN.md .impeccable/design.json CHANGELOG.md docs/release/VERIFICATION.md manifests/release_manifest.json
git commit -m "docs: verify borderless audit console"
```

Restore `http://127.0.0.1:7860/ui/` to the committed-evidence model-absent configuration. Confirm `main`, clean status, owner-only identity, zero contributor trailers, no remotes, unchanged source archive, and no remote action before renewing Feature Freeze.
