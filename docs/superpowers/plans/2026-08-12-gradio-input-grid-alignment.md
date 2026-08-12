# Gradio Input Grid Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the unrelated left-workspace flex rows with one orderly, responsive alignment grid without changing content, behavior, or model evidence.

**Architecture:** Keep the existing Gradio DOM and focus order. Flatten only the toolbar layout wrapper with CSS, assign its children and the existing direct siblings to a desktop input-column grid, and target Gradio's real `[role="tablist"]` element for equal tab tracks. Restore a source-order single-column grid at compact widths.

**Tech Stack:** Gradio 5, CSS Grid, Playwright geometry contracts, pytest, Ruff, Mypy, Docker.

## Global Constraints

- Traditional Chinese remains primary and established ML/XAI terms remain English.
- Preserve the approved palette, typography, square geometry, copy, API schema, models, metrics, explanations, and decision boundary.
- Use CPU only, synthetic data only for smoke, no UCI download, and no runtime write into committed paths.
- Do not create a remote, push, tag, release, deploy, or add a contributor trailer.

---

### Task 1: Rendered alignment contract

**Files:**
- Inspect: `app/gradio_theme.css`
- Test output: ephemeral Playwright measurements only

**Interfaces:**
- Consumes: model-absent UI at `http://127.0.0.1:7860/ui/`.
- Produces: a RED/GREEN geometry contract at 1,714px.

- [ ] **Step 1: Write the failing browser contract**

Measure `.audit-input-column`, `.audit-case-controls`, `.audit-case-note`,
`.audit-tabs [role="tablist"]`, all four tab buttons, `.audit-feature-row`, and
`.audit-primary`. Require:

```javascript
const equalTabs = Math.max(...tabWidths) - Math.min(...tabWidths) <= 1;
const tabsFill = Math.abs(tablist.width - input.width) <= 1;
const utilityAligned = Math.abs(caseNoteCenterY - caseControlsCenterY) <= 8;
const rightEdgesAligned = Math.abs(caseControls.right - input.right) <= 1
  && Math.abs(action.right - input.right) <= 1;
const pageFits = document.documentElement.scrollWidth
  === document.documentElement.clientWidth;
```

- [ ] **Step 2: Run the contract and verify RED**

Expected: the contract fails because the note is below the controls and the
tablist uses content-width buttons rather than four equal tracks.

### Task 2: Single input-column grid

**Files:**
- Modify: `app/gradio_theme.css`

**Interfaces:**
- Consumes: the existing Gradio toolbar, case note, tabs, and action DOM.
- Produces: one desktop layout grid with unchanged source and focus order.

- [ ] **Step 1: Implement the minimum desktop CSS**

Use the existing semantic classes with the following topology:

```css
.audit-input-column {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) 390px;
  grid-template-areas:
    "heading heading"
    "note controls"
    "tabs tabs"
    "action action";
}

.audit-input-toolbar { display: contents !important; }
.audit-input-heading-block { grid-area: heading; }
.audit-case-note { grid-area: note; align-self: end; }
.audit-case-controls { grid-area: controls; align-self: end; }
.audit-tabs { grid-area: tabs; }
.audit-primary { grid-area: action; justify-self: end; }

.audit-tabs [role="tablist"] {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
```

Remove only flex declarations made obsolete by this grid. Keep current control
heights, feature-field equality, result-plane layout, colors, and copy.

- [ ] **Step 2: Restore compact source-order layout**

At 820px and below, use one grid column and the areas `heading`, `controls`,
`note`, `tabs`, `action`. At 520px and below, set the tablist to two equal
columns; keep the full-width phone action.

- [ ] **Step 3: Run the exact browser contract and verify GREEN**

Expected: utility centers differ by no more than 8px, the four desktop tabs are
equal and fill the input width, both control/action right edges align, and page
overflow is zero.

- [ ] **Step 4: Run focused gates and commit**

Run the 36 Gradio/presenter tests, Ruff format/check, strict Mypy for `app`, the
Impeccable layout detector, and `git diff --check`. Commit as
`style: align gradio input workspace`.

### Task 3: Responsive states and release evidence

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: the committed CSS and existing ignored synthetic CI bundle.
- Produces: a clean local release candidate under renewed Feature Freeze.

- [ ] **Step 1: Batch-inspect responsive and dynamic states**

At 1,714px, 1,280px, 768px, and 390px, assert zero overflow, consistent visual
and DOM order, visible focus, 44px minimum controls, and no clipped labels.
Verify model-absent and CPU-only synthetic LightGBM success states without
publishing a synthetic prediction value.

- [ ] **Step 2: Record the verified alignment rule**

Update durable design language and release evidence with measured geometry,
without screenshots, absolute paths, or synthetic prediction values. Regenerate
`manifests/release_manifest.json` and run the release verifier.

- [ ] **Step 3: Run full source/package gates**

Run non-editable setup and source hash, `uv lock --check`, Ruff, strict Mypy,
all 145 tests, release verifier, wheel/sdist build, isolated wheel API health,
and archive privacy inspection.

- [ ] **Step 4: Rebuild and smoke Docker**

Run Compose config/build, inspect non-root/CPU/privacy boundaries, execute the
network-disabled synthetic pipeline in a disposable volume, verify model-absent
and read-only synthetic API/UI paths, and remove all temporary runtime resources
while retaining the tested image.

- [ ] **Step 5: Commit evidence and audit Git**

Commit evidence as `docs: record aligned workspace gate`; confirm clean `main`,
owner-only identity, zero contributor trailers/remotes/tags, unchanged source
archive, and a restored model-absent preview at port 7860.
