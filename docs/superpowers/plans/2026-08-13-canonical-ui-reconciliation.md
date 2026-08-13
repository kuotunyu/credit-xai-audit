# Canonical UI Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile the useful post-snapshot UI work from `3_ML_xAI` into the clean `credit-xai-audit` public candidate, then make the canonical/archived repository roles difficult to confuse.

**Architecture:** Keep `app/gradio_ui.py`, `app/gradio_presenter.py`, `app/gradio_theme.css`, and `src/credit_xai/release/` authoritative. Reimplement only verified UX gaps through the canonical presenter and component contracts, preserve all scientific artifacts, and finish by moving the donor into the existing recoverable archive only when no process uses it.

**Tech Stack:** Python 3.11, Gradio 5, pandas, FastAPI, pytest, Ruff, strict Mypy, Hatch/build, Docker Compose, Codex in-app browser.

## Global Constraints

- Canonical repository: `credit-xai-audit`; `3_ML_xAI` is a read-only donor after source HEAD is recorded.
- Source snapshot provenance remains `58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`; source history is never copied.
- Do not change training, calibration, evaluation, model selection, explanation algorithms, API schemas, committed experiment results, or dataset/model payload boundaries.
- Do not add low/medium/high risk bands, lending guidance, approval language, fabricated predictions, raw data, or model bundles.
- English remains the default `README.md`; `README_zh-TW.md` remains the full Traditional Chinese version.
- New tracked UI imagery must come from canonical code, show an honest public-safe state, and remain below 5 MiB.
- All production behavior changes use red-green-refactor; every commit uses `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` with no contributor trailer.
- Do not push, create a remote, tag, release, publish, deploy, or sync Hugging Face.
- Never move the donor while a Codex, Python, terminal, editor, or server process uses its path.

---

## File structure

- Create `AGENTS.md`: stable public canonical-repository policy; no local absolute path or private handoff.
- Create `tests/test_repository_identity.py`: executable canonical-policy and machine-portability contract.
- Modify `docs/release/PUBLIC_BOUNDARY.md`: distinguish the immutable audited source snapshot from later donor development.
- Modify `app/gradio_presenter.py`: feature labels, strict case indices, and sanitized result-state separation.
- Modify `tests/test_gradio_presenter.py`: presenter red-green contracts.
- Modify `app/gradio_ui.py`: show a human label and retain the original feature code as component info.
- Modify `tests/test_gradio.py`: Gradio component contract for the label/code pairing.
- Create `tests/test_readme_contract.py`: recruiter opening and tracked image contract.
- Create `assets/ui_audit_console.png`: canonical model-absent desktop screenshot.
- Modify `README.md` and `README_zh-TW.md`: recruiter-first opening without touching generated evidence bodies.
- Modify `CHANGELOG.md`, `DESIGN.md`, and `docs/release/VERIFICATION.md`: verified reconciliation evidence only.
- Regenerate `manifests/release_manifest.json`: final tracked file list, sizes, and hashes.
- Create or update workspace-only `XAI/PROJECT_MAP.md`: exact active/archive locations outside the public candidate.
- Update archive-only `_archive/superseded-20260813/ARCHIVE_MANIFEST.md`: recoverable donor move and exact SHA.

### Task 1: Establish the canonical repository contract

**Files:**
- Create: `tests/test_repository_identity.py`
- Create: `AGENTS.md`
- Modify: `docs/release/PUBLIC_BOUNDARY.md`

**Interfaces:**
- Consumes: the fixed source snapshot in `src/credit_xai/release/manifest.py`.
- Produces: public, machine-portable policy text used by future agents and release reviewers.

- [ ] **Step 1: Write the failing repository-identity test**

```python
from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_canonical_repository_policy_is_public_and_machine_portable() -> None:
    policy = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "canonical public candidate" in policy
    assert "read-only donor" in policy
    assert "Do not merge unrelated history" in policy
    assert not re.search(r"(?i)[A-Z]:[\\/]Users[\\/]", policy)


def test_public_boundary_names_the_immutable_source_snapshot() -> None:
    boundary = (PROJECT_ROOT / "docs" / "release" / "PUBLIC_BOUNDARY.md").read_text(
        encoding="utf-8"
    )

    assert "58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61" in boundary
    assert "later donor development is not part of that snapshot" in boundary
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_repository_identity.py -v
```

Expected: FAIL because `AGENTS.md` does not exist and the boundary wording is absent.

- [ ] **Step 3: Add the minimal public policy**

Create `AGENTS.md` with this stable content:

```markdown
# Canonical repository policy

This repository is the canonical public candidate for Credit XAI Audit.

- Treat any unrelated-history source repository as a read-only donor.
- Do not merge unrelated history or bulk-copy a donor tree into this repository.
- Preserve the public privacy, evidence, packaging, and release-verification boundaries.
- Do not add raw data, model payloads, local paths, private notes, fabricated evidence, or financial-decision language.
- Do not push, publish, deploy, tag, release, or change remotes without explicit owner authorization.
```

Add a `Source lineage` section to `docs/release/PUBLIC_BOUNDARY.md` stating that
the public candidate was built from the immutable audited snapshot at the exact
SHA and that later donor development is not part of that snapshot.

- [ ] **Step 4: Verify GREEN and privacy safety**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_repository_identity.py -v
.\.venv\Scripts\python.exe -c "from credit_xai.release.privacy import verify_public_tree; errors=verify_public_tree('.'); print('\n'.join(errors)); raise SystemExit(bool(errors))"
```

Expected: the focused tests pass and the privacy scan returns no errors.

- [ ] **Step 5: Commit the canonical contract**

```powershell
git add AGENTS.md docs/release/PUBLIC_BOUNDARY.md tests/test_repository_identity.py
git commit -m "docs: mark canonical public repository"
```

### Task 2: Reconcile presenter validation and failure states

**Files:**
- Modify: `tests/test_gradio_presenter.py`
- Modify: `app/gradio_presenter.py`

**Interfaces:**
- Produces: `FEATURE_LABELS: dict[str, str]` covering all 23 canonical features.
- Preserves: `case_values(...) -> tuple[tuple[int, ...] | None, str]` and `analyze_values(...) -> tuple[str, pd.DataFrame]`.

- [ ] **Step 1: Add failing label, case-index, and result-state tests**

Add these contracts to `tests/test_gradio_presenter.py`:

```python
from app.gradio_presenter import FEATURE_LABELS
from credit_xai.serving.service import ServiceError


def test_feature_labels_cover_every_canonical_feature() -> None:
    assert set(FEATURE_LABELS) == set(FEATURES)
    assert FEATURE_LABELS["LIMIT_BAL"] == "信用額度"
    assert FEATURE_LABELS["PAY_0"] == "9 月還款狀態"
    assert FEATURE_LABELS["BILL_AMT1"] == "9 月帳單金額"
    assert FEATURE_LABELS["PAY_AMT1"] == "9 月繳款金額"


@pytest.mark.parametrize("index", [None, "abc", 1.5, float("nan"), float("inf")])
def test_case_values_rejects_non_integer_index(index: object) -> None:
    cases = pd.DataFrame([{**dict.fromkeys(FEATURES, 0), TARGET: 0}])
    values, note = case_values(cases, index)
    assert values is None
    assert note == "案例編號必須是有限整數。"


@pytest.mark.parametrize("index", [-1, 2])
def test_case_values_rejects_out_of_range_index(index: int) -> None:
    cases = pd.DataFrame(
        [{**dict.fromkeys(FEATURES, 0), TARGET: 0} for _ in range(2)]
    )
    values, note = case_values(cases, index)
    assert values is None
    assert note == "案例編號必須介於 0 與 1 之間。"


class _RejectedService:
    def explain(self, features: dict[str, int]) -> dict[str, Any]:
        raise ServiceError("private detail")


def test_analyze_values_distinguishes_input_rejection_from_runtime_failure() -> None:
    rejected, rejected_frame = analyze_values(_RejectedService(), list(range(23)))
    failed, failed_frame = analyze_values(_ExplodingService(), list(range(23)))

    assert "輸入資料無法完成審計" in rejected
    assert "分析服務暫時無法回應" in failed
    assert "private detail" not in rejected
    assert str(Path.home()) not in failed
    assert rejected_frame.empty and failed_frame.empty
```

Replace the modulo test with a direct in-range case test; the loaded case must
remain in canonical feature order and include the historical observation.

- [ ] **Step 2: Run focused tests and verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio_presenter.py -k "feature_labels or case_values or distinguishes" -v
```

Expected: missing `FEATURE_LABELS`, fractional indices are truncated, out-of-range indices wrap, and runtime failures use the input-error state.

- [ ] **Step 3: Implement the minimal canonical presenter changes**

Add a 23-entry `FEATURE_LABELS` mapping. Implement strict indices as:

```python
try:
    numeric = float(str(index))
except (TypeError, ValueError, OverflowError):
    return None, "案例編號必須是有限整數。"
if not math.isfinite(numeric) or not numeric.is_integer():
    return None, "案例編號必須是有限整數。"
resolved = int(numeric)
if not 0 <= resolved < len(test_cases):
    return None, f"案例編號必須介於 0 與 {len(test_cases) - 1} 之間。"
```

Import `SchemaError` and `ServiceError`. Add a sanitized service renderer:

```python
def _render_service_error() -> str:
    return _result_shell(
        state="暫時無法回應",
        title="分析服務暫時無法回應",
        body="目前無法完成本機歷史模型重播；請稍後再試。",
    )
```

Split `analyze_values` into service execution and result rendering:

```python
try:
    result = service.explain(features)
except (SchemaError, ServiceError) as exc:
    logger.info("Gradio input rejected (%s)", type(exc).__name__)
    return _render_input_error(), _empty_attributions()
except Exception as exc:
    logger.warning("Gradio audit failed (%s)", type(exc).__name__)
    return _render_service_error(), _empty_attributions()
try:
    return _render_success_result(result), _attribution_frame(result)
except Exception as exc:
    logger.warning("Gradio result rejected (%s)", type(exc).__name__)
    return _render_service_error(), _empty_attributions()
```

- [ ] **Step 4: Verify GREEN and presenter quality**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio_presenter.py -v
.\.venv\Scripts\ruff.exe format --check app\gradio_presenter.py tests\test_gradio_presenter.py
.\.venv\Scripts\ruff.exe check app\gradio_presenter.py tests\test_gradio_presenter.py
.\.venv\Scripts\mypy.exe --strict app\gradio_presenter.py
```

- [ ] **Step 5: Commit presenter reconciliation**

```powershell
git add app/gradio_presenter.py tests/test_gradio_presenter.py
git commit -m "feat(ui): clarify audit inputs and failure states"
```

### Task 3: Present readable labels without losing feature codes

**Files:**
- Modify: `tests/test_gradio.py`
- Modify: `app/gradio_ui.py`
- Modify only if browser evidence requires it: `app/gradio_theme.css`

**Interfaces:**
- Consumes: `FEATURE_LABELS` from Task 2.
- Produces: 23 Gradio numbers with a Traditional Chinese label and canonical code in `info`.

- [ ] **Step 1: Replace the raw-label test with a failing label/code contract**

```python
from app.gradio_presenter import FEATURE_GROUPS, FEATURE_LABELS


def test_gradio_pairs_readable_labels_with_canonical_feature_codes(test_config) -> None:
    config, _ = _config(test_config)
    numbers = [
        component
        for component in config["components"]
        if component["type"] == "number"
        and "audit-number" in component.get("props", {}).get("elem_classes", [])
    ]

    assert len(numbers) == len(FEATURES) == 23
    assert {
        component["props"].get("info"): component["props"].get("label")
        for component in numbers
    } == {feature: FEATURE_LABELS[feature] for feature in FEATURES}
```

Update the feature-group test to assert `info` equals the ordered canonical
feature list and `label` equals the ordered human-label list.

- [ ] **Step 2: Run and verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py -k "labels or feature_group" -v
```

Expected: raw feature codes are still used as labels and `info` is absent.

- [ ] **Step 3: Implement the minimal component change**

Import `FEATURE_LABELS` and build each number with:

```python
controls[feature] = gr.Number(
    value=_EXAMPLE[feature],
    precision=0,
    step=1,
    label=FEATURE_LABELS[feature],
    info=feature,
    elem_classes="audit-number",
)
```

- [ ] **Step 4: Verify GREEN, format, and type safety**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_gradio.py tests\test_gradio_presenter.py -v
.\.venv\Scripts\ruff.exe format --check app tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\ruff.exe check app tests\test_gradio.py tests\test_gradio_presenter.py
.\.venv\Scripts\mypy.exe --strict app
```

- [ ] **Step 5: Commit the component contract**

```powershell
git add app/gradio_ui.py app/gradio_theme.css tests/test_gradio.py
git commit -m "feat(ui): pair readable labels with feature codes"
```

Do not stage `app/gradio_theme.css` if browser geometry does not require a CSS
change.

### Task 4: Add a recruiter-first README opening and canonical screenshot

**Files:**
- Create: `tests/test_readme_contract.py`
- Create: `assets/ui_audit_console.png`
- Modify: `README.md`
- Modify: `README_zh-TW.md`

**Interfaces:**
- Preserves: all `AUTOGEN:*:START/END` blocks and committed scientific values.
- Produces: the same screenshot link and capability categories in both languages.

- [ ] **Step 1: Write the failing README/image contract**

```python
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE = PROJECT_ROOT / "assets" / "ui_audit_console.png"


def test_readmes_open_with_recruiter_summary_and_canonical_ui_image() -> None:
    english = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (PROJECT_ROOT / "README_zh-TW.md").read_text(encoding="utf-8")

    assert "## 30-second portfolio summary" in english
    assert "## 30 秒作品摘要" in chinese
    for text in (english, chinese):
        assert "assets/ui_audit_console.png" in text
        for capability in ("Model comparison", "Probability quality", "Explainability", "Delivery"):
            assert capability in text
        for marker in ("AUTOGEN:METRICS:START", "AUTOGEN:METRICS:END"):
            assert text.count(marker) == 1


def test_canonical_ui_image_is_small_valid_png() -> None:
    payload = IMAGE.read_bytes()
    assert payload.startswith(b"\x89PNG\r\n\x1a\n")
    assert 50_000 < len(payload) < 5 * 1024 * 1024
```

- [ ] **Step 2: Run and verify RED**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_readme_contract.py -v
```

Expected: the summary headings and canonical screenshot are absent.

- [ ] **Step 3: Add the recruiter-first opening without editing evidence blocks**

Immediately after each title/disclaimer, add:

- one sentence explaining that the repository audits whether probability and
  explanations are trustworthy rather than merely showing a prediction;
- the language-switch link;
- `![Credit XAI Audit canonical model-absent console](assets/ui_audit_console.png)`;
- a four-row 30-second table with exactly `Model comparison`, `Probability quality`,
  `Explainability`, and `Delivery` as the capability labels;
- direct links to methodology, limitations, and `docs/release/VERIFICATION.md`;
- an exact caption stating that the public candidate excludes model bundles and
  the screenshot contains no fabricated prediction.

Do not replace, reformat, or manually update any generated evidence block.

- [ ] **Step 4: Capture the canonical public-safe desktop state**

Start the worktree UI without a model bundle on a free loopback port. Use the
in-app browser at a 1440 by 1000 viewport, wait for the Gradio page to settle,
verify the title and explicit model-absent state, confirm no horizontal
overflow or browser console error, and save one viewport PNG to
`assets/ui_audit_console.png`. Do not use the donor screenshot.

- [ ] **Step 5: Verify the README/image contract and claims**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_readme_contract.py tests\test_release_claims.py -v
.\.venv\Scripts\python.exe -m credit_xai.release.verify claims .
```

- [ ] **Step 6: Commit the portfolio opening**

```powershell
git add README.md README_zh-TW.md assets/ui_audit_console.png tests/test_readme_contract.py
git commit -m "docs: add recruiter-first audit overview"
```

### Task 5: Run the complete publication gate and record evidence

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `DESIGN.md`
- Modify: `docs/release/VERIFICATION.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**
- Consumes: final tracked public tree and all Task 1–4 tests.
- Produces: final deterministic release manifest and factual verification record.

- [ ] **Step 1: Run focused and complete static/test gates**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_repository_identity.py tests\test_gradio_presenter.py tests\test_gradio.py tests\test_readme_contract.py -v
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe --strict src app
.\.venv\Scripts\python.exe -m pytest
uv lock --check
```

Record exact pass counts and warnings. Do not claim a gate that did not run.

- [ ] **Step 2: Build and inspect distributions outside the tracked tree**

```powershell
.\.venv\Scripts\python.exe -m build --outdir tmp\canonical-ui-release\dist
.\.venv\Scripts\python.exe -m credit_xai.release.verify privacy .
```

Inspect wheel/sdist members for private notes, absolute paths, raw data, model
payloads, and the donor-only UI modules. Install the wheel into a disposable
environment and import `credit_xai`; record the hashes and cleanup location.

- [ ] **Step 3: Rebuild and smoke the CPU-only Docker image**

Run Compose config/build, confirm the non-root/CPU/no-GPU boundary, start the
model-absent API, and verify `/health`, `/ui/`, and expected `/predict` failure.
When a disposable verified synthetic bundle is available, mount only that
volume read-only and verify `/health`, `/predict`, `/explain`, and `/ui/` without
changing committed results. Remove containers, network, and temporary volume;
retain only the audited image.

- [ ] **Step 4: Update durable evidence using only observed results**

Add one changelog entry, update the shipped design record, and append a dated
verification section containing exact test counts, browser widths, screenshot
state/hash/bytes, distribution hashes, Docker identity, endpoints, limitations,
and cleanup. State that the donor source was not copied wholesale and that no
remote action occurred.

- [ ] **Step 5: Regenerate the manifest and run all release gates**

```powershell
.\.venv\Scripts\python.exe -c "from credit_xai.release.manifest import write_release_manifest; print(write_release_manifest('.'))"
.\.venv\Scripts\python.exe -m credit_xai.release.verify all .
git diff --check
```

- [ ] **Step 6: Commit verified release evidence**

```powershell
git add CHANGELOG.md DESIGN.md docs/release/VERIFICATION.md manifests/release_manifest.json
git commit -m "docs: verify canonical UI reconciliation"
```

- [ ] **Step 7: Re-run the final gates from committed state**

```powershell
.\.venv\Scripts\ruff.exe format --check .
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\mypy.exe --strict src app
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m credit_xai.release.verify all .
git status --short --branch
```

Expected: all commands exit zero and the integration branch is clean.

### Task 6: Integrate locally and remove the ambiguous active source path

**Files:**
- Create or modify outside the public repository: `XAI/PROJECT_MAP.md`
- Modify in archive: `_archive/superseded-20260813/ARCHIVE_MANIFEST.md`
- Move if and only if safe: `XAI/3_ML_xAI` to
  `_archive/superseded-20260813/XAI/3_ML_xAI`

**Interfaces:**
- Consumes: clean verified integration branch, clean donor HEAD, and process audit.
- Produces: canonical `main`, one recoverable donor archive, and no ambiguous active `3_ML_xAI` directory.

- [ ] **Step 1: Finish the integration branch**

Use the finishing-development-branch workflow. Verify the original canonical
checkout is still clean and unchanged except for the design/plan commits, then
fast-forward local `main` to the verified branch. Do not push. Retain the branch
until the archive and final audit succeed.

- [ ] **Step 2: Resolve and validate exact archive paths**

Resolve the source and destination with `Resolve-Path`; verify both remain
under the intended workspace/archive roots and verify the destination does not
exist. Record donor `HEAD`, branch, status, remotes, and untracked files.

- [ ] **Step 3: Audit live processes before moving**

Use `Get-CimInstance Win32_Process` and listening-port ownership to find every
command line or working directory referencing `3_ML_xAI`. If any process uses
the donor, do not stop it and do not move the directory. Mark archival as
deferred with the process IDs and leave `XAI/PROJECT_MAP.md` warning that the
path is a donor only.

- [ ] **Step 4: Move the donor only when the audit is empty**

When the source worktree is clean and no process uses it, use one PowerShell
`Move-Item -LiteralPath` operation from the validated source to the validated
archive destination. Do not delete or rewrite Git history.

- [ ] **Step 5: Write the workspace and recovery maps**

`XAI/PROJECT_MAP.md` must name `credit-xai-audit` as the only active canonical
repository and the archive path as non-active. `ARCHIVE_MANIFEST.md` must record
former path, archived path, canonical replacement, donor SHA, canonical SHA,
move timestamp, clean status, no-remote state, and exact recovery instruction.

- [ ] **Step 6: Perform final filesystem and Git audit**

Confirm:

- canonical `main` is clean and points to the verified reconciliation SHA;
- no active `XAI/3_ML_xAI` directory remains if the move was allowed;
- the archived repository resolves to the recorded donor SHA and remains clean;
- neither repository has a configured remote or newly added contributor;
- no push, tag, release, deployment, or publication occurred.
