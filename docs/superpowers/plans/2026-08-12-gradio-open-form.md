# Gradio Open Form Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the uncomfortable spreadsheet-like case worksheet with four
open form sections and a content-height result plane without changing behavior.

**Architecture:** Preserve the Gradio component tree, canonical feature order,
callbacks, and presenter output. Change only structural CSS plus durable design
and release evidence. Prove the presentation through a rendered-browser
RED/GREEN contract before renewing Docker and package gates.

**Tech Stack:** Python 3.11, Gradio 5, CSS Grid/Flexbox, pytest, Ruff, strict
Mypy, in-app Chromium, Docker.

## Global Constraints

- Keep all 23 inputs visible and in canonical source/focus order.
- Traditional Chinese remains primary; dataset and ML/XAI terms stay in their
  established English forms.
- Preserve square geometry, the existing palette, callbacks, feature schema,
  result semantics, API behavior, and historical educational-audit boundary.
- Do not change models, calibration, thresholds, metrics, formal results,
  dependencies, Docker policy, or publication state.
- Use CPU only and synthetic data only for runtime smoke.
- Do not create a remote, push, PR, tag, Release, upload, or deployment.
- Commit only as `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` with
  no contributor trailer.

---

### Task 1: Rendered RED contract

**Files:**
- Test: live `http://127.0.0.1:7860/ui/`
- Inspect: `app/gradio_theme.css`

**Interfaces:**
- Consumes: incumbent `.audit-feature-group`, `.audit-group-heading-block`,
  `.audit-number`, `.audit-result-column`, and `.audit-workspace` elements.
- Produces: measured evidence that the old worksheet violates the open-form
  contract.

- [ ] **Step 1: Measure the incumbent desktop structure**

At 1,908px and 1,280px, collect the group and result rectangles plus computed
border sides. Require:

```text
group heading width == feature row width
vertical separator count == 0
field input border-bottom == 1px
result height < input height
visible numeric controls == 23
page horizontal overflow == 0px
```

- [ ] **Step 2: Verify RED**

Expected: FAIL because the heading is a 128px side rail, 19 vertical separators
are visible across feature rows, field inputs have no underline, and the result
plane stretches to the input height.

### Task 2: Open-section CSS

**Files:**
- Modify: `app/gradio_theme.css`
- Test: `tests/test_gradio.py`

**Interfaces:**
- Consumes: the existing Gradio component classes; no component or callback
  change.
- Produces: full-width group headings, open equal-track field rows, input-heavy
  desktop proportions, and a content-height result plane.

- [ ] **Step 1: Write the failing structural test**

Replace the ledger-specific CSS contract with a behavior-level contract whose
rendered counterpart requires open sections, 5/6 desktop tracks, 3 compact
tracks, and 2 phone tracks. The break it catches is reintroducing a side rail,
vertical separators, or stretching the result panel.

- [ ] **Step 2: Run focused tests and confirm RED**

Run:

```powershell
.venv\Scripts\pytest.exe tests/test_gradio.py -q
```

Expected: the new open-section contract fails against the incumbent CSS.

- [ ] **Step 3: Load the craft floor and implement minimal CSS**

Apply these behavior rules:

```css
.audit-workspace { align-items: flex-start !important; }
.audit-input-column { flex-grow: 8 !important; }
.audit-result-column { flex-grow: 4 !important; align-self: flex-start; }
.audit-feature-group { display: block !important; }
.audit-group-heading-block { width: 100% !important; border: 0 !important; }
.audit-feature-row > .form { gap: 1rem !important; }
.audit-number + .audit-number { border-left: 0 !important; }
.audit-number input { border-bottom: 1px solid var(--audit-rule) !important; }
```

Make group headings horizontal, use section spacing and one bottom rule rather
than a closed grid, retain equal 5/6/3/2 tracks, and preserve 44px targets.

- [ ] **Step 4: Run focused GREEN gates**

```powershell
.venv\Scripts\pytest.exe tests/test_gradio.py tests/test_gradio_presenter.py -q
.venv\Scripts\ruff.exe format --check app tests
.venv\Scripts\ruff.exe check app tests
.venv\Scripts\mypy.exe --strict app
```

- [ ] **Step 5: Commit the UI change**

```powershell
git add app/gradio_theme.css tests/test_gradio.py
git commit -m "style: open gradio case form"
```

### Task 3: Bounded browser verification

**Files:**
- Modify only if the batched inspection finds a measured defect:
  `app/gradio_theme.css`
- Test: live model-absent and isolated synthetic previews.

**Interfaces:**
- Consumes: Task 2 CSS and existing synthetic `configs/ci.yaml` artifacts in
  disposable storage.
- Produces: responsive visual and interaction evidence.

- [ ] **Step 1: Run the GREEN geometry batch**

At 1,908px, 1,280px, 768px, and 390px assert: 23 visible controls, 4 full-width
group headings, no vertical cell separators, equal field widths within one
pixel, 5/6/3/2 tracks, 44px targets, no clipped labels, content-height result,
zero page overflow, and zero browser logs.

- [ ] **Step 2: Inspect desktop and phone together**

Confirm the squint test shows the case task first, four natural form groups
second, and the supporting empty result third. Confirm the form no longer reads
as a spreadsheet and the result no longer creates a large empty cool block.

- [ ] **Step 3: Apply at most one measured correction batch**

If the combined inspection exposes a defect, fix all measured defects in one
CSS edit and run one confirmation batch. Do not continue open-ended polishing.

- [ ] **Step 4: Verify model-absent and synthetic success states**

The public preview must remain `model_loaded=false`. The isolated synthetic UI
must show LightGBM, `isotonic`, TreeSHAP, and the attribution table at desktop
and phone widths without overflow, browser errors, or financial-action copy.

### Task 4: Durable evidence and final gates

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: verified geometry and runtime evidence.
- Produces: a traceable, clean, unpublished release candidate.

- [ ] **Step 1: Update durable design language**

Replace the side-rail/continuous-cell-ledger description with full-width group
headings, open field rows, field underlines, and content-height result behavior.

- [ ] **Step 2: Rebuild and run isolated Docker smoke**

Run Compose config/build, inspect non-root/CPU/privacy boundaries, execute the
network-disabled full synthetic pipeline in a disposable volume, mount only the
synthetic volume read-only into the API, and verify health/predict/explain/UI.
Remove all temporary containers, network, and volume; retain only the image.

- [ ] **Step 3: Record verified evidence and regenerate manifest**

Do not record local absolute paths or case-level probabilities. Run:

```powershell
.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; write_release_manifest('.')"
.venv\Scripts\python.exe -m credit_xai.release.verify all
git diff --check
```

- [ ] **Step 4: Run final source and package gates**

Run non-editable setup/import, `uv lock --check`, Ruff format/check, strict
Mypy, full pytest, release verifier, wheel/sdist build, archive privacy scan,
isolated wheel import/API health, Git identity/trailer audit, target clean
status, and source-archive read-only status.

- [ ] **Step 5: Commit evidence and restore the preview**

```powershell
git add DESIGN.md .impeccable/design.json CHANGELOG.md docs/release/VERIFICATION.md manifests/release_manifest.json
git commit -m "docs: verify open form release gate"
```

Restore the model-absent preview at `http://127.0.0.1:7860/ui/`, keep the
browser at its normal viewport, and leave `main` clean with no remote action.
