# Gradio Desktop Density Correction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the shipped Gradio desktop type scale, whitespace, and case-control layout while preserving the approved Editorial Audit Console, all interactions, and every evidence boundary.

**Architecture:** Keep the existing presenter and Gradio callback graph unchanged. Make one semantic composition change by grouping the existing input heading and case controls inside `audit-input-toolbar`, then recalibrate the incumbent CSS tokens/selectors. Verify the source contract first, then render model-absent and synthetic-success states before refreshing deterministic release evidence.

**Tech Stack:** Python 3.11, Gradio 5, CSS, pytest, Ruff, strict mypy, browser rendering, Docker/release verifier.

## Global Constraints

- Work inline on `main`; do not create a worktree, subagent, remote, PR, tag, release, or deployment.
- Use CPU only; do not download UCI data or modify accepted metrics, models, pipeline code, API schemas, dependencies, or Docker policy.
- Preserve Traditional Chinese-first copy, original ML/XAI terms, warm/indigo/amber palette, square `0px` geometry, flat depth, and the 8/4 desktop workspace.
- Desktop thesis must use `clamp(2.35rem, 2.7vw, 3rem)`; desktop KPI values must not exceed approximately 37px.
- Operational labels and metadata must use a coherent 13–14px range; compact disclaimer/footer text must be at least 12.5px.
- The scope boundary must size to content rather than stretch to the thesis height.
- Interactive targets remain at least 44px high and retain the existing visible 3px focus outline.
- No factual copy, numerical evidence, model/explainer mapping, privacy boundary, or non-decision language may change.
- The owner authorized autonomous execution; do not stop for intermediate aesthetic approval.

---

### Task 1: Rebalance desktop hierarchy and case-toolbar composition

**Files:**
- Modify: `tests/test_gradio.py`
- Modify: `app/gradio_ui.py`
- Modify: `app/gradio_theme.css`

**Interfaces:**
- Consumes: `_input_heading_html()`, existing `case_index`, `load_btn`, `case_note`, `FEATURE_GROUPS`, and Gradio callbacks.
- Produces: the `audit-input-toolbar` layout class and a CSS contract with the approved desktop scale; callback signatures and component values remain identical.

- [ ] **Step 1: Write the failing Gradio composition test**

Append a focused test that exercises the real Gradio config tree and proves the
heading plus case controls share one toolbar parent:

```python
def test_gradio_groups_heading_and_case_actions_in_one_toolbar(test_config) -> None:
    config, _ = _config(test_config)
    components = {component["id"]: component for component in config["components"]}

    toolbar = next(
        component
        for component in config["components"]
        if "audit-input-toolbar" in component.get("props", {}).get("elem_classes", [])
    )
    layout_nodes = [config["layout"]]
    for node in layout_nodes:
        layout_nodes.extend(node.get("children", []))
    toolbar_node = next(node for node in layout_nodes if node["id"] == toolbar["id"])
    child_components = [components[child["id"]] for child in toolbar_node["children"]]

    assert [component["type"] for component in child_components] == ["html", "row"]
    assert "audit-input-heading-block" in child_components[0]["props"]["elem_classes"]
    assert "audit-case-controls" in child_components[1]["props"]["elem_classes"]
```

- [ ] **Step 2: Run the focused test and confirm RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py::test_gradio_groups_heading_and_case_actions_in_one_toolbar -v
```

Expected: fail because no `audit-input-toolbar` component exists.

- [ ] **Step 3: Record a rendered RED measurement before editing CSS**

Use the already-running mounted page and evaluate real computed layout. The old
page must fail at least the thesis and boundary assertions:

```javascript
const h1 = document.querySelector(".audit-hero h1").getBoundingClientRect();
const boundary = document.querySelector(".audit-boundary").getBoundingClientRect();
const resultMeta = parseFloat(
  getComputedStyle(document.querySelector(".audit-result-meta dt")).fontSize
);
if (!(h1.height < 120 && boundary.height < h1.height && resultMeta >= 13.5)) {
  throw new Error("desktop density contract not met");
}
```

Capture the measured values with the expected failure; this is the behavioral
RED for the CSS correction rather than a brittle source-string assertion.

- [ ] **Step 4: Group the existing heading and case controls**

In `build_ui`, replace the two sibling blocks with the same controls inside one row:

```python
with gr.Row(elem_classes="audit-input-toolbar"):
    gr.HTML(
        _input_heading_html(),
        padding=False,
        elem_classes="audit-input-heading-block",
    )
    with gr.Row(elem_classes="audit-case-controls"):
        case_index = gr.Number(...)
        load_btn = gr.Button(...)
```

Do not change component labels, values, precision, step, element classes, outputs, or callback wiring.

- [ ] **Step 5: Apply the minimal density CSS**

Use these exact structural values in `app/gradio_theme.css`:

```css
.audit-hero {
  grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.65fr);
  gap: clamp(1.5rem, 3vw, 3rem);
  padding: clamp(1rem, 1.7vw, 1.5rem) 1rem 0.85rem;
}

.audit-hero h1 {
  font-size: clamp(2.35rem, 2.7vw, 3rem);
}

.audit-boundary {
  align-self: center;
  padding: 0.35rem 0 0.35rem 1rem;
}

.audit-kpi { min-height: 70px; }
.audit-kpi strong { font-size: clamp(1.75rem, 2.2vw, 2.3rem); }
.audit-kpi span { font-size: 0.88rem; }

.audit-input-column { gap: 0.45rem !important; }
.audit-input-toolbar {
  align-items: center !important;
  gap: 0.75rem !important;
}
.audit-input-heading-block {
  flex: 1 1 300px !important;
  min-width: 260px !important;
}
.audit-case-controls {
  flex: 0 1 390px !important;
  min-width: 340px !important;
  margin: 0 0 0 auto !important;
}
```

Also set the method/scope copy to 0.98–1rem, result title to `clamp(1.3rem, 1.7vw, 1.55rem)`, result body to 0.95rem, result metadata to 0.86rem, result-boundary text to 0.8–0.84rem, and evidence/footer compact copy to at least 0.78rem. Remove the old `.audit-case-controls > .form { margin-left: auto }` behavior and add a 1080px toolbar-wrap rule. Reduce the existing 820px and 520px thesis maxima without lowering interactive target sizes.

- [ ] **Step 6: Run focused tests and static checks**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -q
.\.venv\Scripts\python.exe -m ruff format app tests
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m mypy --strict app
```

Expected: all focused tests and static checks pass with no functional callback change.

- [ ] **Step 7: Commit the tested correction**

```powershell
git add app/gradio_ui.py app/gradio_theme.css tests/test_gradio.py
git commit -m "fix: rebalance gradio desktop density"
```

---

### Task 2: Render and close the visual defect

**Files:**
- Modify only if rendered evidence requires one bounded correction: `app/gradio_theme.css`, `tests/test_gradio.py`
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`

**Interfaces:**
- Consumes: mounted `/ui/`, the user-provided 1,900-by-975 baseline, model-absent state, ignored synthetic LightGBM bundle, and the shipped design system.
- Produces: desktop/compact render evidence and synchronized durable type/layout rules.

- [ ] **Step 1: Refresh the mounted UI and inspect representative states**

Render the model-absent page at 1,900-by-975 and a compact viewport. Record computed headline, body, metadata, KPI, hero, toolbar, and first-feature positions plus document `clientWidth`/`scrollWidth`. Confirm the title no longer dominates, the scope boundary is content-sized, the toolbar uses both sides of its row, and no horizontal overflow exists.

- [ ] **Step 2: Verify the synthetic result state**

Use only the existing ignored synthetic bundle. Confirm LightGBM/TreeSHAP, calibrated and uncalibrated fields, readable result metadata, stable geometry, and absence of approval/eligibility/decision language. Do not copy a synthetic probability into public documentation.

- [ ] **Step 3: Run the layout detector and make at most one bounded fix batch**

```powershell
node "$env:USERPROFILE\.codex\skills\impeccable\scripts\detect.mjs" --json --scope layout app\gradio_ui.py app\gradio_theme.css
```

Combine any detector finding with the rendered assessment. If a material defect remains, first extend the focused source test so it fails, apply one CSS-only correction batch, rerun focused tests, and capture one final confirmation render. Do not begin an open-ended polish loop.

- [ ] **Step 4: Synchronize the design-system record**

Update `DESIGN.md` frontmatter and Typography/Layout prose with the exact 38–48px desktop thesis, 13–16px supporting scale, content-sized boundary, 70px KPI minimum, and combined responsive case toolbar. Update only corresponding metadata/narrative fields in `.impeccable/design.json`; preserve deterministic `generatedAt`.

- [ ] **Step 5: Verify and commit**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -q
git diff --check
git add DESIGN.md .impeccable\design.json app tests
git commit -m "docs: record balanced console density"
```

---

### Task 3: Renew release evidence and Feature Freeze

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Modify: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: final UI/CSS/tests/design records and existing release tooling.
- Produces: a clean, unpublished `main` candidate with renewed manifest hashes and Feature Freeze evidence.

- [ ] **Step 1: Run the complete source gate**

```powershell
uv lock --check
.\.venv\Scripts\python.exe -m ruff format --check src app tests
.\.venv\Scripts\python.exe -m ruff check src app tests
.\.venv\Scripts\python.exe -m mypy --strict src app
.\.venv\Scripts\python.exe -m pytest
```

- [ ] **Step 2: Update release documentation**

Add a concise `Unreleased` changelog entry and a dated density-correction subsection to `docs/release/VERIFICATION.md`. Record focused/full counts, desktop/compact geometry, synthetic model/explainer smoke, and the fact that no model, metric, API, pipeline, dependency, Docker policy, or decision scope changed. Do not add local paths or synthetic prediction values.

- [ ] **Step 3: Refresh manifest and run release gates**

```powershell
.\.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; print(write_release_manifest('.'))"
.\.venv\Scripts\python.exe -m credit_xai.release.verify all
git diff --check
```

- [ ] **Step 4: Audit and commit the final evidence**

Confirm the diff contains only approved UI, tests, design/spec/plan, release docs, and manifest changes. Then:

```powershell
git add CHANGELOG.md docs\release\VERIFICATION.md manifests\release_manifest.json
git commit -m "docs: verify gradio density gate"
```

- [ ] **Step 5: Run immutable post-commit verification**

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m credit_xai.release.verify all
git status --short --branch
git log -1 '--format=%H%n%an <%ae>%n%cn <%ce>%n%B'
git log --format='%B' | Select-String -Pattern 'Co-authored-by|Signed-off-by|Reviewed-by' -CaseSensitive:$false
git remote -v
```

Expected: full suite and release gates pass, `main` is clean, identity is the owner account, contributor trailers are zero, no remote exists, and the candidate returns to Feature Freeze.

---

## Plan Self-Review

- **Spec coverage:** Type scale, hero stretch, case-toolbar composition, KPI density, result readability, responsive behavior, accessibility, browser evidence, synthetic truth boundary, design persistence, manifest renewal, and Feature Freeze are each assigned to a task.
- **Scope:** One Gradio presentation subsystem; no model, evidence, API, pipeline, dependency, Docker, or publication work is introduced.
- **Interface consistency:** Existing controls and callbacks retain their names and values; only their layout parent changes. `audit-input-toolbar` is the sole new presentation interface.
- **TDD:** The old separate-row config and the old rendered 60px/stretch behavior
  must each produce RED before any production edit. Any rendered follow-up
  correction also requires a failing behavioral assertion first.
- **No placeholders:** All values, files, commands, commit messages, and verification outcomes are specified.
