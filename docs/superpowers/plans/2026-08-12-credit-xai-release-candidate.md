# Credit XAI Release Candidate Implementation Plan

> **For agentic workers:** Execute inline in this repository. The owner has
> explicitly prohibited subagents and additional tasks. Steps use checkbox
> (`- [ ]`) syntax for tracking.

**Goal:** Produce a clean, verifiable, unpublished portfolio release candidate
that preserves the accepted full-run evidence and passes local publication
gates without modifying the private archive.

**Architecture:** Start from an allowlisted copy of one audited committed
snapshot, then add small release-verification modules around the existing
pipeline. Accepted artifacts remain immutable inputs until independent
regeneration and comparison justify a later change. Reproduction, packaging,
and archives use separate ignored output roots.

**Tech Stack:** Python 3.11, uv, pytest, Ruff, strict mypy, hatchling/build,
scikit-learn, LightGBM, InterpretML EBM, SHAP, FastAPI, Gradio, Docker Compose.

## Global Constraints

- CPU only; CUDA and GPU execution are forbidden.
- No paid API and no unknown dataset mirror.
- Do not modify or rewrite the private source repository.
- Do not create a remote, push, pull request, tag, release, upload, or deploy.
- Target branch is `main`; every author and committer is exactly
  `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Commit messages are short English imperatives and contain no contributor
  trailers.
- README generated blocks come only from `results/derived/summary.json`.
- Full reproduction writes outside committed `results/`, then gets compared.

---

### Task 1: Import the audited public snapshot

**Files:**

- Create: all tracked source files except `PROGRESS.md` and `notebooks/**`
- Preserve: `results/raw/**`, `results/derived/**`, `assets/**`, `manifests/**`
- Exclude: source `.git`, environments, caches, raw data, and model bundles

**Interfaces:**

- Consumes: source commit `58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`
- Produces: a source-compatible target tree with no inherited history

- [ ] **Step 1: Copy only audited tracked paths**

Run a `git ls-files` loop against the source commit and copy each allowed path
with its directory structure. Reject the two excluded path classes before any
copy occurs.

- [ ] **Step 2: Prove the import matches the source snapshot**

For every imported source path, compare SHA-256 in source and target. Assert
that `.git`, `PROGRESS.md`, `notebooks`, `.venv`, `data`, and model payloads did
not cross the boundary.

- [ ] **Step 3: Run syntax and existing fast tests in a target-only environment**

Run:

```powershell
uv sync --all-extras --group dev
uv run python -m compileall -q src app tests
uv run pytest
```

Expected: dependency resolution succeeds and the inherited suite reports zero
failures.

- [ ] **Step 4: Commit the imported snapshot**

```powershell
git add --all
git commit -m "chore: import audited public snapshot"
```

### Task 2: Make reporting deterministic and claims executable

**Files:**

- Modify: `src/credit_xai/reporting/aggregate.py`
- Modify: `src/credit_xai/reporting/run.py`
- Create: `src/credit_xai/release/__init__.py`
- Create: `src/credit_xai/release/claims.py`
- Create: `tests/test_release_claims.py`
- Modify: `tests/test_reporting.py`

**Interfaces:**

- Consumes: full config, raw artifacts, checkpoint metadata, committed summary
- Produces: `verify_claims(root: Path) -> list[str]`, where an empty list means
  every evidence-backed claim is consistent

- [ ] **Step 1: Write failing tests for deterministic summary metadata**

Build the same synthetic summary twice while patching wall-clock time and the
current host package list. Assert the serialized summaries are identical and
derive run metadata from immutable raw artifacts.

- [ ] **Step 2: Verify the deterministic-report test fails for time/environment drift**

```powershell
uv run pytest tests/test_reporting.py -k deterministic -vv
```

Expected: failure because `generated_at` and host environment currently change.

- [ ] **Step 3: Implement stable report metadata**

Use timestamps and package versions recorded by pipeline artifacts. Keep all
metric, calibration, explanation, and group values derived from raw evidence.

- [ ] **Step 4: Write failing behavioral claim-verifier tests**

Copy fixture artifacts into a temporary root, mutate one invariant at a time,
and assert detection of: split overlap/count mismatch, non-validation
calibration selection, non-1000 full bootstrap stores, incomplete checkpoint
metadata, wrong model/explainer mapping, causal faithfulness wording,
unsuppressed small-cell intervals, altered README generated blocks, and changed
committed figure/table hashes.

- [ ] **Step 5: Verify each mutation test fails because the verifier is absent**

```powershell
uv run pytest tests/test_release_claims.py -vv
```

Expected: import or assertion failure naming the missing verifier behavior.

- [ ] **Step 6: Implement the minimal claim verifier**

Parse JSON and Markdown structurally, recompute split hashes and checkpoint
line counts, compare autogen blocks to rendered summary tables, and return
path-qualified errors without changing any artifact.

- [ ] **Step 7: Run focused and reporting tests**

```powershell
uv run pytest tests/test_release_claims.py tests/test_reporting.py -vv
```

Expected: zero failures.

- [ ] **Step 8: Commit the claim and determinism gates**

```powershell
git add src/credit_xai/release src/credit_xai/reporting tests
git commit -m "feat: verify release claims"
```

### Task 3: Harden provenance, checkpoints, paths, and privacy

**Files:**

- Modify: `src/credit_xai/data/download.py`
- Modify: `src/credit_xai/data/prepare.py`
- Modify: `src/credit_xai/config.py`
- Modify: `src/credit_xai/utils/checkpoints.py`
- Create: `src/credit_xai/release/privacy.py`
- Create: `tests/test_release_privacy.py`
- Modify: `tests/test_prepare.py`
- Modify: `tests/test_checkpoints.py`
- Modify: `tests/test_config.py`

**Interfaces:**

- Produces: `verify_public_tree(root: Path) -> list[str]`
- Preserves: current checkpoint file names and deterministic iteration records

- [ ] **Step 1: Write failing tests for checksum and checkpoint edge cases**

Tests use local byte fixtures to assert a cached/downloaded ZIP with the wrong
SHA-256 is rejected, duplicate/out-of-range checkpoint iteration IDs cannot be
completed, and `require_complete` rejects a store whose record count differs
from metadata.

- [ ] **Step 2: Run the focused tests and confirm expected failures**

```powershell
uv run pytest tests/test_prepare.py tests/test_checkpoints.py -vv
```

- [ ] **Step 3: Implement checksum and checkpoint validation**

Read the expected URL and ZIP digest from the committed dataset fingerprint.
Validate existing and new downloads before extraction. Enforce exactly one
record for every iteration in a complete checkpoint.

- [ ] **Step 4: Write failing portability/privacy tests**

Create a temporary repository under a Unicode path. Assert config-relative
paths resolve from the config file or an explicit project root, never the
caller account's working directory. Seed fixtures with forbidden credentials,
home paths, raw data, model pickles, private notes, and oversized files, and
assert the public-tree verifier reports each category without echoing secret
values.

- [ ] **Step 5: Implement portable path resolution and fail-closed privacy scan**

Keep config serialization stable by separating stored relative paths from
runtime resolution. Scan only public-candidate files, redact matches, and use
an explicit allowlist for compact evidence file types and size ceilings.

- [ ] **Step 6: Run focused tests**

```powershell
uv run pytest tests/test_prepare.py tests/test_checkpoints.py tests/test_config.py tests/test_release_privacy.py -vv
```

- [ ] **Step 7: Commit provenance and privacy hardening**

```powershell
git add src/credit_xai/data src/credit_xai/config.py src/credit_xai/utils/checkpoints.py src/credit_xai/release tests
git commit -m "fix: harden provenance and privacy"
```

### Task 4: Harden the educational serving boundary

**Files:**

- Modify: `src/credit_xai/constants.py`
- Modify: `src/credit_xai/serving/service.py`
- Modify: `src/credit_xai/serving/api.py`
- Modify: `app/gradio_ui.py`
- Modify: `tests/test_api.py`
- Create: `tests/test_gradio.py`

**Interfaces:**

- Produces: prediction/explanation payloads explicitly labeled as historical
  educational model output, never a recommendation or eligibility decision

- [ ] **Step 1: Write failing API and UI language tests**

Assert `/predict`, `/explain`, OpenAPI metadata, and Gradio output include the
historical-audit scope; assert forbidden decision fields and words such as
approval, eligibility, accept, and reject are absent from response keys and UI
actions.

- [ ] **Step 2: Run tests and confirm they fail on current generic output**

```powershell
uv run pytest tests/test_api.py tests/test_gradio.py -vv
```

- [ ] **Step 3: Implement minimal labels and untrusted-bundle warning**

Keep probabilities and attributions for demo value, add explicit scope fields,
rename UI actions to historical audit language, and document that a hash next
to a pickle proves integrity but not publisher authenticity.

- [ ] **Step 4: Run FastAPI and Gradio focused smoke tests**

```powershell
uv run pytest tests/test_api.py tests/test_gradio.py -vv
```

- [ ] **Step 5: Commit serving hardening**

```powershell
git add src/credit_xai/constants.py src/credit_xai/serving app tests
git commit -m "fix: label educational demo outputs"
```

### Task 5: Add release metadata, manifest, and documentation

**Files:**

- Create: `CITATION.cff`
- Create: `CHANGELOG.md`
- Create: `SECURITY.md`
- Create: `docs/release/PUBLIC_BOUNDARY.md`
- Create: `docs/release/OWNER_ACTIONS.md`
- Create: `docs/release/VERIFICATION.md`
- Create: `manifests/release_manifest.json`
- Modify: `README.md`
- Modify: `README_zh-TW.md`
- Modify: `MODEL_CARD.md`
- Modify: `DATA_CARD.md`
- Modify: `FAILURES.md`
- Modify: `configs/full.yaml`
- Create: `tests/test_release_manifest.py`

**Interfaces:**

- Produces: `build_release_manifest(root: Path) -> dict[str, object]`
- Excludes: the release manifest itself from its content-hash closure

- [ ] **Step 1: Write failing manifest tests**

Assert stable sorted paths, SHA-256 for every tracked public artifact, declared
exclusions, source snapshot provenance, evidence budgets, and self-exclusion.

- [ ] **Step 2: Run the manifest test and confirm the builder is missing**

```powershell
uv run pytest tests/test_release_manifest.py -vv
```

- [ ] **Step 3: Implement and generate the release manifest**

Generate JSON mechanically from the Git index and accepted artifact metadata.
No result value is entered by hand.

- [ ] **Step 4: Align all narrative claims**

Correct the full-run duration to the measured approximately 4.5 hours, state
the 2005/historical/non-causal/non-discrimination boundaries in both languages,
distinguish test point estimates from bootstrap means, clarify LightGBM's
recorded TreeSHAP fallback, document group suppression, and add code/data
licenses and citation metadata. Do not edit autogen numeric blocks.

- [ ] **Step 5: Regenerate summary, tables, READMEs, and figures twice**

Run the report command against copied accepted raw artifacts in two separate
temporary roots, compare every output byte, then update the committed artifacts
only from one verified run.

- [ ] **Step 6: Run claim, manifest, and documentation gates**

```powershell
uv run pytest tests/test_release_claims.py tests/test_release_manifest.py tests/test_reporting.py -vv
uv run python -m credit_xai.release.verify claims .
```

- [ ] **Step 7: Commit release metadata and verified generated artifacts**

```powershell
git add CITATION.cff CHANGELOG.md SECURITY.md docs manifests README.md README_zh-TW.md MODEL_CARD.md DATA_CARD.md FAILURES.md configs results assets tests src
git commit -m "docs: add release evidence"
```

### Task 6: Enforce quality, packaging, CI, and Docker gates

**Files:**

- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Modify: `.github/workflows/ci.yml`
- Modify: `Dockerfile`
- Modify: `docker-compose.yml`
- Create: `tests/test_package.py`

**Interfaces:**

- Produces: buildable wheel/sdist and CI commands matching local release gates

- [ ] **Step 1: Write a failing installed-package smoke test**

Build a wheel, install it into an empty virtual environment, import
`credit_xai`, load configs by absolute and Unicode paths, construct the API
without a model, and verify `/health` plus the 503 demo boundary.

- [ ] **Step 2: Add strict typing and build dependencies**

Configure mypy with `strict = true`, explicit third-party import overrides only
where libraries publish no typing, and add `mypy`, `types-PyYAML`, `build`, and
the existing test/runtime tools to the development group.

- [ ] **Step 3: Run Ruff, strict mypy, and the full suite**

```powershell
uv run ruff format --check
uv run ruff check
uv run mypy --strict src app
uv run pytest
```

- [ ] **Step 4: Build and test package artifacts**

```powershell
uv run python -m build
```

Inspect wheel and sdist contents, install the wheel into an empty environment,
and run the package/API smoke test with no repository import path.

- [ ] **Step 5: Build and health-check Docker when available**

```powershell
docker version
docker compose build api
docker compose --profile smoke run --rm smoke
docker compose up -d api
```

Poll `/health`, verify CPU-only configuration, record status, then stop only the
candidate's Compose project. If no daemon is available, record that exact
environment limitation instead of claiming a pass.

- [ ] **Step 6: Make CI run the same gates**

Add strict mypy, release verification, package build/content inspection, and
Docker health checks while keeping the network-free synthetic pipeline.

- [ ] **Step 7: Commit build and CI gates**

```powershell
git add pyproject.toml uv.lock .github/workflows/ci.yml Dockerfile docker-compose.yml tests
git commit -m "build: enforce publication gates"
```

### Task 7: Run isolated reproduction and final candidate audit

**Files:**

- Update: `docs/release/VERIFICATION.md`
- Update: `docs/release/OWNER_ACTIONS.md`
- Regenerate: `manifests/release_manifest.json`

**Interfaces:**

- Consumes: clean committed candidate and official UCI archive
- Produces: an evidence report distinguishing verified, compared, unavailable,
  and owner-only actions

- [ ] **Step 1: Run the full pipeline into an isolated output root**

Create a full config overlay whose results, models, manifests, data, and
checkpoints live under one ignored reproduction directory inside this target.
Use `--resume` for all checkpointed commands. Do not change accepted artifacts.

- [ ] **Step 2: Compare reproduction to accepted evidence**

Compare provenance and split hashes exactly. Compare deterministic predictions,
calibration choices, bootstrap records, explanation method metadata, and all
derived metrics with explicitly justified tolerances. A partial run is labeled
partial; approximate agreement is never labeled full reproduction.

- [ ] **Step 3: Build and inspect a clean Git archive**

Use `git archive HEAD`, extract under a fresh temporary path, verify archive
contents and privacy, perform a clean install there, and rerun quality, tests,
claims, report determinism, package, and app smoke gates.

- [ ] **Step 4: Audit Git identity and publication state**

Assert `main`, clean status, no remote, no tags, only the owner author/committer,
no `Co-authored-by` or contributor trailers, no secrets/absolute paths/private
files, and no oversized tracked objects.

- [ ] **Step 5: Record reproducible evidence and owner actions**

Write exact commands, UTC times, versions, exit codes, counts, hashes, Docker
status, reproduction comparison status, remaining limitations, suggested
GitHub description/topics, and publication steps that the owner may perform
tomorrow.

- [ ] **Step 6: Regenerate the release manifest and run every gate fresh**

```powershell
uv run ruff format --check
uv run ruff check
uv run mypy --strict src app
uv run pytest
uv run python -m credit_xai.release.verify all .
git diff --check
git status --short
```

- [ ] **Step 7: Commit verification evidence**

```powershell
git add docs/release manifests/release_manifest.json
git commit -m "docs: record candidate verification"
```

- [ ] **Step 8: Re-run final immutable-state checks**

Verify the final `HEAD`, repeat full tests and release audits, ensure the target
worktree is empty, then compare source `HEAD`, status, refs, and tracked-tree
hash to the initial audit. Do not invoke any network publication command.
