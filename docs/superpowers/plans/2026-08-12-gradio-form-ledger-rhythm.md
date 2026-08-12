# Gradio Form Ledger Rhythm Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the visually conflicting four-tab/five-field rhythm with a compact tab index and one orderly editorial field ledger.

**Architecture:** Preserve the existing Gradio component tree, callbacks, and feature groups. Change only presentation CSS, its durable design description, and release evidence; prove the correction with a rendered-browser RED/GREEN contract and responsive synthetic smoke.

**Tech Stack:** Python 3.11, Gradio 5, CSS Grid, Playwright/Chromium from the bundled workspace runtime, pytest, Ruff, Mypy, Docker.

## Global Constraints

- Traditional Chinese remains primary; established Machine Learning and XAI terms remain English.
- Keep square geometry, the approved palette, and the existing Editorial Audit Console identity.
- Do not change features, callbacks, API schemas, models, metrics, results, dependencies, or Docker policy.
- Use CPU only; synthetic data only for runtime smoke; do not access the UCI dataset.
- Do not create a remote, push, PR, tag, Release, upload, or deployment.
- Commit only as `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` with no contributor trailer.

---

### Task 1: Rendered alignment contract

**Files:**
- Inspect: `app/gradio_theme.css`
- Inspect: `app/gradio_ui.py`
- Test: ephemeral Playwright script executed against `http://127.0.0.1:7860/ui/`

**Interfaces:**
- Consumes: rendered `.audit-tabs`, `.audit-feature-row`, `.audit-number`, and `.audit-primary` elements.
- Produces: measured RED evidence that fails until the tab index and field ledger have distinct, orderly rhythms.

- [ ] **Step 1: Run a desktop RED contract**

At 1,908px, measure the input plane, tab list, visible field cells, field labels,
inputs, and action. Require all of the following:

```text
tablist_width / input_column_width <= 0.80
visible field width spread <= 1px
field label justify-content == flex-start
field input text-align == left
field form top and bottom borders == 1px
all internal visible cells have a 1px left separator
input bottom border == 0px
page horizontal overflow == 0px
```

Expected before implementation: FAIL because the tab list occupies 100%,
labels/values are centered, the form has no shared ledger borders, cells have no
separators, and each input owns a separate bottom border.

- [ ] **Step 2: Record the single root-cause hypothesis**

```text
The interface looks crooked because a full-width four-column navigation grid
and a full-width five-column data grid compete for the same visual plane, while
centered text and disconnected underlines make both grids appear as floating
objects. Making navigation content-sized and fields one shared ledger removes
the competing rhythm at its source.
```

### Task 2: Minimal ledger implementation

**Files:**
- Modify: `app/gradio_theme.css`
- Test: `tests/test_gradio.py`

**Interfaces:**
- Consumes: the existing Gradio DOM and CSS classes; no component-tree change.
- Produces: compact tab index, shared-rule field ledger, left-aligned field content, and responsive 5/3/2 field tracks.

- [ ] **Step 1: Load incumbent design guidance before editing**

Run Impeccable context once for `app/gradio_theme.css`, read
`reference/layout.md`, then read `reference/craft-floor.md` immediately before
the edit.

- [ ] **Step 2: Implement the minimal CSS change**

Apply these behavior-level rules:

```css
.audit-tabs [role="tablist"] {
  width: min(100%, 34rem);
}

.audit-tabs button[role="tab"] {
  justify-content: flex-start;
}

.audit-feature-row > .form {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(0, 1fr);
  gap: 0;
  border-block: 1px solid var(--audit-rule);
}

.audit-number + .audit-number {
  border-left: 1px solid var(--audit-rule-warm);
}
```

Remove each input's bottom border, give every field the same inset, align labels
and values left, and align the non-phone primary action to one visible ledger
track. In the existing `820px` and `520px` queries, preserve three/two field
columns and add row-aware separator resets without creating boxes.

- [ ] **Step 3: Run the GREEN desktop contract**

Expected: every Task 1 assertion passes, with zero browser errors.

- [ ] **Step 4: Run focused source tests**

Run:

```powershell
.venv\Scripts\pytest.exe tests/test_gradio.py tests/test_gradio_presenter.py -q
.venv\Scripts\ruff.exe format --check app tests
.venv\Scripts\ruff.exe check app tests
.venv\Scripts\mypy.exe --strict app
```

Expected: 36 tests pass; Ruff and Mypy pass.

- [ ] **Step 5: Commit the UI correction**

```powershell
git add app/gradio_theme.css
git commit -m "style: order gradio form ledger"
```

### Task 3: Bounded browser inspection

**Files:**
- Modify only if the first batched inspection finds a contract defect: `app/gradio_theme.css`
- Test: ephemeral Playwright scripts against model-absent and synthetic-bundle previews.

**Interfaces:**
- Consumes: Task 2 CSS and existing synthetic `configs/ci.yaml` artifacts in an isolated temporary output.
- Produces: desktop/mobile visual evidence and one optional batch correction followed by one confirmation pass.

- [ ] **Step 1: Run one responsive geometry batch**

At 1,714px, 1,280px, 768px, and 390px assert: no horizontal overflow, no
browser errors, complete labels, tab targets at least 44px, input targets at
least 46px, equal visible field widths, a compact desktop tab index, and
5/5/3/2 basic-data columns.

- [ ] **Step 2: Inspect desktop and phone screenshots together**

Confirm that the tab rail reads as navigation, the visible fields read as one
ledger, label/value insets match, separators are continuous, and no unnecessary
card, radius, shadow, or empty band was introduced.

- [ ] **Step 3: Batch-fix only measured defects and confirm once**

If Step 2 finds defects, make one CSS batch correction and rerun the geometry
batch once. Stop polishing after the confirmation pass.

- [ ] **Step 4: Run synthetic success-state interaction**

Using CPU-only `configs/ci.yaml` artifacts outside committed paths, click the
primary action at 1,714px and 390px. Assert LightGBM, `isotonic`, `TreeSHAP`,
and at least ten attribution rows are visible; assert no financial-action text,
page overflow, or browser exception.

### Task 4: Durable design and release evidence

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: verified geometry and synthetic evidence from Task 3.
- Produces: durable ledger rules and traceable release evidence without screenshots, local paths, or synthetic prediction values.

- [ ] **Step 1: Update durable design language**

Replace the four-equal-tab/full-width-field wording with the compact group-index
and shared-rule ledger behavior. Mirror the same rule in the Impeccable sidecar.

- [ ] **Step 2: Record only verified evidence**

Add the RED/GREEN measurements, responsive widths, synthetic success boundary,
and focused gate counts. Do not record local absolute paths or case-level
probabilities.

- [ ] **Step 3: Regenerate and verify the manifest**

```powershell
.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; write_release_manifest('.')"
.venv\Scripts\python.exe -m credit_xai.release.verify all
git diff --check
```

- [ ] **Step 4: Commit documentation**

```powershell
git add DESIGN.md .impeccable/design.json CHANGELOG.md docs/release/VERIFICATION.md manifests/release_manifest.json
git commit -m "docs: record orderly form gate"
```

### Task 5: Container and final release gates

**Files:**
- Modify after verified runtime only: `docs/release/VERIFICATION.md`
- Regenerate after evidence: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: committed UI and documentation.
- Produces: clean unpublished `main` candidate with renewed CPU-only Docker and package evidence.

- [ ] **Step 1: Rebuild and inspect the API image**

Run `docker compose config --quiet` and `docker compose build api`. Record image
ID, bytes, build time, non-root UID, CPU/GPU boundary, and absence of raw data,
bundles, results, `.env`, and private notes.

- [ ] **Step 2: Run isolated synthetic pipeline and API/UI smoke**

Use `network=none`, two CPUs, two GB, and a disposable volume. Run preparation,
all three training paths, calibration, evaluation, explanation, and report.
Mount the result volume read-only into a temporary API container and verify
health, predict, explain, and the desktop/phone UI ledger. Remove containers,
network, and volume; retain only the test image.

- [ ] **Step 3: Record Docker evidence and refresh the manifest**

Commit only verified evidence and manifest hashes as:

```powershell
git commit -m "docs: record verified ledger container gate"
```

- [ ] **Step 4: Run final source and package verification**

Run non-editable setup/import hash, `uv lock --check`, Ruff format/check, strict
Mypy, full pytest, release verifier, `python -m build`, isolated wheel import/API
health, archive privacy inspection, Git identity/trailer audit, target clean
status, and source-archive read-only status.

- [ ] **Step 5: Restore the local model-absent preview**

Start the CPU-only preview at `http://127.0.0.1:7860/ui/` and verify `/health`
200 with `model_loaded=false` and `/ui/` 200.
