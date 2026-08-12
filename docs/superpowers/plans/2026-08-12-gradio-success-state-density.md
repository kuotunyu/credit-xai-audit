# Gradio Success-State Density Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the desktop success-state dead space by presenting verified attributions in a conditional full-width band below the existing input/result workspace.

**Architecture:** Keep `analyze_values` as the presentation boundary that returns sanitized HTML and a DataFrame. Adapt only the Gradio UI wrapper so a non-empty frame returns a visible Dataframe component update, while empty/error frames keep it hidden; place the component after the workspace and style it as a flat evidence band.

**Tech Stack:** Python 3.11, Gradio 5, pandas, pytest, CSS, Playwright browser verification.

## Global Constraints

- Use CPU only and the existing ignored synthetic LightGBM bundle for runtime verification.
- Do not change models, accepted metrics, public claims, API schemas, dependencies, or explanation mappings.
- Keep Traditional Chinese primary, square corners, flat editorial structure, and the historical non-decision boundary.
- Do not publish, add a remote, or add contributor trailers.

---

### Task 1: Conditional full-width attribution band

**Files:**
- Modify: `tests/test_gradio.py`
- Modify: `app/gradio_ui.py`
- Modify: `app/gradio_theme.css`

**Interfaces:**
- Consumes: `analyze_values(service, values) -> tuple[str, pd.DataFrame]`
- Produces: the existing Gradio `/analyze` output contract, with the Dataframe component initially hidden and shown only for a non-empty verified frame.

- [ ] **Step 1: Write the failing configuration test**

Add a test that builds the real Gradio config, locates `audit-workspace` and `audit-attributions`, and asserts the attribution component is not a descendant of the workspace and has `visible is False` initially.

- [ ] **Step 2: Run the test to verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py::test_gradio_places_attributions_after_workspace_and_hides_them_initially -q
```

Expected: FAIL because the existing attribution component is inside the result column and visible.

- [ ] **Step 3: Implement the minimal layout and visibility update**

Move the `gr.Dataframe` construction immediately after the workspace and set `visible=False`. Update the local `analyze` wrapper to return the existing HTML plus `gr.Dataframe(value=frame, visible=not frame.empty)`. Add `.audit-attributions` spacing and structural rules without rounded corners, shadow, or decorative effects.

- [ ] **Step 4: Run focused GREEN checks**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -q
.\.venv\Scripts\ruff.exe format --check app tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\ruff.exe check app tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\mypy.exe --strict app
```

Expected: 35 tests pass and all static checks pass.

- [ ] **Step 5: Verify the real success state**

Use the ignored `configs/ci.yaml` bundle and Playwright at 1900px, 768px, and 390px. Assert `LightGBM`, `TreeSHAP`, ten attribution data rows, no decision language, no page-level horizontal overflow, no page errors, and a visible attribution band after `/analyze`.

- [ ] **Step 6: Commit**

```powershell
git add app/gradio_ui.py app/gradio_theme.css tests/test_gradio.py
git commit -m "fix: compact gradio success evidence"
```

### Task 2: Release evidence and final gates

**Files:**
- Modify: `DESIGN.md`
- Modify: `.impeccable/design.json`
- Modify: `CHANGELOG.md`
- Modify: `docs/release/VERIFICATION.md`
- Modify: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: the verified success-state browser measurements and committed UI behavior.
- Produces: deterministic release evidence with `candidate_state=unpublished`.

- [ ] **Step 1: Record the layout invariant**

Document that attribution evidence becomes a full-width conditional band and that empty/error states reserve no table space. Keep the incumbent Editorial Audit Console tokens unchanged.

- [ ] **Step 2: Refresh and verify the release manifest**

Run:

```powershell
.\.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; write_release_manifest('.')"
.\.venv\Scripts\python.exe -m credit_xai.release.verify all
```

Expected: `release gates passed: all`.

- [ ] **Step 3: Run final source and package gates**

Run `uv lock --check`, Ruff format/check, strict Mypy, all 144 tests, `python -m build`, archive privacy inspection, and the release verifier. Confirm all pass.

- [ ] **Step 4: Commit and audit Git state**

```powershell
git add DESIGN.md .impeccable/design.json CHANGELOG.md docs/release/VERIFICATION.md manifests/release_manifest.json
git commit -m "docs: verify compact success evidence"
```

Confirm `main`, clean status, owner-only author/committer identity, zero contributor trailers, no remotes, unchanged source archive, and no remote action. Restore the public preview to the committed-evidence model-absent configuration and renew Feature Freeze.
