# Gradio Reading Density Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Increase supporting-text legibility and use more of a wide browser while reducing low-information vertical space without changing product behavior or the approved Editorial Audit Console identity.

**Architecture:** Keep the Gradio component tree and all callbacks unchanged. Express the correction entirely through the existing CSS tokens and layout rules, verify it with a temporary real-browser contract, and persist only the CSS, design documentation, release evidence, and deterministic release-manifest hash changes.

**Tech Stack:** Gradio 5, CSS, Playwright/Chromium, pytest, Ruff, strict Mypy, Docker, Python packaging.

## Global Constraints

- Traditional Chinese remains primary; technical terms remain in English.
- Preserve square geometry, the current palette, the 7/5 workspace, and the shared-rule field ledger.
- Do not change models, XAI methods, API schemas, accepted metrics, datasets, dependencies, or factual claims.
- Do not add a remote, push, tag, release, deploy, or contributor trailer.
- Commit only as `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not use GPU, CUDA, a paid API, real UCI data, or a writable host model/result mount.

---

### Task 1: Browser density contract and CSS correction

**Files:**
- Create temporarily: `tmp/reading-density-contract.js`
- Modify: `app/gradio_theme.css`
- Test: `tests/test_gradio.py`
- Test: `tests/test_gradio_presenter.py`

**Interfaces:**
- Consumes: the current Gradio DOM classes and the model-absent preview at `/ui/`.
- Produces: the same DOM and callbacks with a 1,600px desktop stage, larger support tokens, and tighter low-information rhythm.

- [ ] **Step 1: Write the failing real-browser contract**

Create a Playwright script that renders 1,908px and 390px viewports and asserts:

```javascript
expect(desktop.stageWidth).toBeGreaterThanOrEqual(1580);
expect(desktop.stageWidth).toBeLessThanOrEqual(1600);
expect(desktop.supportPx).toBeGreaterThanOrEqual(16);
expect(desktop.labelPx).toBeGreaterThanOrEqual(15);
expect(desktop.metaPx).toBeGreaterThanOrEqual(15);
expect(desktop.valuePx).toBeGreaterThanOrEqual(19);
expect(desktop.workspaceEvidenceGap).toBeLessThanOrEqual(24);
expect(desktop.inputTail).toBeLessThanOrEqual(10);
expect(desktop.overflow).toBe(0);
expect(phone.overflow).toBe(0);
expect(phone.heroPx).toBeLessThanOrEqual(33);
expect(phone.actionWidth).toBeCloseTo(phone.formWidth, 1);
```

The script must also assert equal visible field widths within 0.1px, at least
44px targets, left-aligned labels and values, and zero `pageerror`/console
errors.

- [ ] **Step 2: Run the contract and verify RED**

Run:

```powershell
node tmp/reading-density-contract.js
```

Expected: FAIL because the current stage is 1,440px, support text is 15.04px,
metadata/labels are 14.0–14.56px, and the workspace/evidence gap is 32px.

- [ ] **Step 3: Implement the minimal CSS correction**

In `app/gradio_theme.css`:

```css
:root {
  --audit-type-body: 1.0625rem;
  --audit-type-support: 1rem;
  --audit-type-label: 0.96875rem;
  --audit-type-meta: 0.9375rem;
  --audit-type-value: 1.1875rem;
}

.gradio-container { max-width: 1600px !important; }
```

Reduce only low-information padding/margins in the hero, input plane, feature
row, result field, evidence transition, and footer. Preserve 44px targets,
responsive columns, and all component classes.

- [ ] **Step 4: Run the contract and focused tests for GREEN**

Run:

```powershell
node tmp/reading-density-contract.js
.venv\Scripts\python.exe -m pytest tests/test_gradio.py tests/test_gradio_presenter.py -q
.venv\Scripts\ruff.exe format --check app tests
.venv\Scripts\ruff.exe check app tests
.venv\Scripts\mypy.exe --strict app/main.py app/gradio_ui.py app/gradio_presenter.py
```

Expected: browser contract and all 36 focused tests pass; Ruff and Mypy pass.

- [ ] **Step 5: Commit the CSS correction**

```powershell
git add app/gradio_theme.css
git commit -m "style: improve gradio reading density"
```

### Task 2: Bounded visual, release, and package confirmation

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Modify: `manifests/release_manifest.json`
- Delete: `tmp/reading-density-contract.js`
- Delete: `tmp/layout-assessment.js`

**Interfaces:**
- Consumes: Task 1 CSS and existing model-absent/synthetic smoke profiles.
- Produces: durable design/release evidence and a clean unpublished candidate.

- [ ] **Step 1: Inspect one desktop/mobile screenshot batch**

Capture 1,908px and 390px screenshots together. Check thesis hierarchy,
support-copy legibility, section rhythm, field alignment, result-state truth,
evidence-table readability, overflow, and source order. Apply at most one
batched correction if a material defect is visible, then run one confirmation
batch and stop polishing.

- [ ] **Step 2: Run the final layout detector and focused gates**

Run the installed Impeccable layout detector from its configured skill root,
then run:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_gradio.py tests/test_gradio_presenter.py -q
.venv\Scripts\ruff.exe format --check .
.venv\Scripts\ruff.exe check .
.venv\Scripts\mypy.exe --strict src app
```

Expected: detector returns `[]`; all focused and static gates pass.

- [ ] **Step 3: Verify synthetic success and current Docker image**

Rebuild the API image, then use only `configs/ci.yaml` synthetic artifacts in
an isolated temporary output. Confirm LightGBM, `isotonic`, `TreeSHAP`, visible
attributions, no financial action field, CPU-only operation, non-root runtime,
and no writable repository mount. Remove temporary containers, networks, and
volumes; retain the tested image.

- [ ] **Step 4: Update durable documentation and release manifest**

Record exact RED/GREEN browser measurements, the bounded visual result, and
fresh verification evidence in the listed design/release files. Regenerate:

```powershell
.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; write_release_manifest('.')"
```

- [ ] **Step 5: Run complete release gates**

Run non-editable setup, `uv lock --check`, Ruff, strict Mypy, all 145 tests,
release verifier, wheel/sdist build, isolated wheel import/API health, archive
privacy inspection, owner identity/trailer audit, and source-archive read-only
status. Restore the model-absent preview at `http://127.0.0.1:7860/ui/`.

- [ ] **Step 6: Commit evidence and confirm Feature Freeze**

```powershell
git add .impeccable/design.json CHANGELOG.md DESIGN.md docs/release/VERIFICATION.md manifests/release_manifest.json
git commit -m "docs: record verified reading density gate"
```

Expected final state: clean `main`, no remote or tag, owner-only identity, zero
contributor trailers, unchanged private source archive, and no remote action.
