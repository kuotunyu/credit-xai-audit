# FAILURES — compatibility issues, fallbacks, and honest negative results

> **Historical 2005 educational audit. Not for lending decisions. Not financial advice.**

Living log. Every entry is a real event from building or running this
repository; "not triggered" entries are recorded so the absence of a fallback
is auditable too.

## 1. shap interventional TreeExplainer × LightGBM categoricals — FALLBACK TRIGGERED

- **Environment**: shap 0.48.0, lightgbm 4.6.0, numpy 2.2.6, Windows 11/10, Python 3.11.
- **Symptom**: constructing `shap.TreeExplainer(model, data=background,
  feature_perturbation="interventional")` for an `LGBMClassifier` trained with
  native pandas categoricals fails at the probe call with
  `AttributeError: 'TreeEnsemble' object has no attribute 'values'`.
- **Action**: automatic, designed fallback to LightGBM's built-in
  `pred_contrib=True` (path-dependent TreeSHAP). The mode actually used is
  recorded in every explain artifact under `method_detail.feature_perturbation`
  (current smoke run: `tree_path_dependent(pred_contrib)`).
- **Impact**: attributions remain exact TreeSHAP values, but expectations are
  path-dependent (split-cover weighted) rather than interventional against an
  explicit background. Documented in MODEL_CARD.md. Time spent: ~15 min (well
  under the 2 h stop-loss).

## 2. Unanchored `.gitignore` patterns silently excluded source code — FIXED

- **Symptom**: the pattern `data/` (unanchored) also matched
  `src/credit_xai/data/` and `results/raw/data/`, so the entire data-pipeline
  package was untracked while the working tree looked clean; `models/*` had the
  same latent problem for `src/credit_xai/models/`.
- **Detection**: `git ls-files src/credit_xai/data` returned empty during a
  post-commit audit.
- **Fix**: root-anchored patterns (`/data/`, `/models/*`) in commit `cfb94d5`.
  Lesson: verify with `git ls-files` after the first commit of any new package.

## 3. EBM (interpret) install on Windows — NOT TRIGGERED

- interpret-core 0.7.8 wheels installed cleanly via uv on Windows/Python 3.11
  and inside the Linux Docker image. The 2 h stop-loss fallback (EBM as
  optional dependency) remains available but was never needed. The lazy-import
  guard with an install hint is still in `models/registry.py` for environments
  without the extra.

## 4. LightGBM install — NOT TRIGGERED

- lightgbm 4.6.0 wheels installed cleanly on both platforms. The
  `HistGradientBoostingClassifier` fallback in `models/lgbm.py` is tested but
  was never activated in the recorded runs (`train_meta.json:is_fallback` is
  `false` everywhere).

## 5. First `uv sync` failed: hatchling requires README.md — FIXED

- `pyproject.toml` declared `readme = "README.md"` before the file existed;
  the editable build failed with `OSError: Readme file does not exist`.
  Fixed by creating the README skeleton before the first sync. Trivial (<5 min).

## 6. `uv run pytest` import error: `tests` not a package — FIXED

- `from tests.conftest import ...` failed under pytest's default import mode
  until `tests/__init__.py` was added. Trivial (<5 min).

## 7. Docker engine not running on first build attempt — OPERATIONAL NOTE

- `docker compose build` failed with the named-pipe error
  (`dockerDesktopLinuxEngine: The system cannot find the file specified`)
  because Docker Desktop was not started. Resolved by starting Docker Desktop;
  no repo change needed.

## 8. Dockerfile layer-cache anti-pattern: README.md coupled to the dependency-install layer — FIXED

- **Symptom**: `COPY pyproject.toml uv.lock README.md LICENSE ./` put a
  frequently-changing file (README.md, rewritten by every `report` run) in the
  same layer as the rarely-changing dependency manifests. Any byte of drift in
  README.md invalidated that layer *and* the subsequent `RUN uv sync
  --no-install-project` (installs numpy/pandas/sklearn/shap/lightgbm/
  interpret-core/gradio — several minutes), even though no dependency had
  changed. Confirmed empirically: a build with zero changes took ~1m43s (all
  layers `CACHED`); appending one blank line to README.md and rebuilding forced
  a ~5 minute full dependency reinstall.
- **Root cause, part 2**: separately, the project's own `credit_xai` package
  was `uv sync --no-editable`-installed *into* the same venv as every
  third-party dependency. Any change under `src/` (even a one-line comment)
  invalidated that install step, which invalidated the venv layer, which
  forced `COPY --from=builder /app/.venv /app/.venv` to re-copy the entire
  venv (measured: 1.2 GB, 23,166 files) across the build-stage boundary —
  costly even when the dependency-install step itself stayed cached, and
  especially slow on Windows/WSL2 filesystem I/O.
- **Fix**: (1) builder stage now copies only `pyproject.toml`, `uv.lock`, and
  `LICENSE`, and writes a content-stable placeholder `README.md` via `RUN echo`
  purely to satisfy hatchling's `readme = "README.md"` existence check before
  `uv sync --no-install-project` — the real README's churn no longer touches
  this layer at all. (2) the project's own package is no longer installed into
  the venv; the builder stops after installing third-party dependencies only,
  and the runtime stage adds `COPY src ./src` plus `ENV PYTHONPATH=/app/src` so
  `python -m credit_xai.cli` resolves the package from raw source instead.
  Verified after the fix: a source-only change leaves `COPY pyproject.toml
  uv.lock LICENSE` and `uv sync --no-install-project` both `CACHED`; a clean
  from-scratch build succeeds (`docker builder prune -af` then rebuild, exit
  0); `credit_xai.__file__` resolves to `/app/src/credit_xai/__init__.py`
  (confirms PYTHONPATH resolution, not a site-packages install); all four API
  endpoints and the containerized synthetic smoke pipeline were re-verified
  end-to-end after the change.

## 9. Colab's `MPLBACKEND` breaks lightgbm and shap imports in subprocesses — FIXED

- **Environment**: Google Colab, Python 3.11 via uv, project venv at
  `/content/venv` (VM-local, outside Drive).
- **Symptom**: `uv run python -c "import lightgbm, shap"` from a notebook cell
  fails with `ValueError: Key backend:
  'module://matplotlib_inline.backend_inline' is not a valid value for
  backend`. `credit_xai`, `interpret`, and `sklearn` import fine — only the
  packages that pull in matplotlib at import time are affected.
- **Cause**: Colab exports `MPLBACKEND=module://matplotlib_inline.backend_inline`
  for its own inline plotting. Subprocesses inherit the variable, but the
  project venv does not contain `matplotlib_inline` (it is not a dependency),
  so matplotlib rejects the backend during rcParams initialisation and the
  import chain dies.
- **Fix**: set `os.environ["MPLBACKEND"] = "Agg"` in the notebook's environment
  cell, before any subprocess runs. `Agg` is headless and is exactly what
  `reporting/figures.py` selects anyway, so nothing else changes. Reproduced
  and verified locally: `MPLBACKEND="module://matplotlib_inline.backend_inline"
  uv run python -c "import lightgbm, shap"` raises the identical error, while
  `MPLBACKEND=Agg` imports both cleanly (lightgbm 4.6.0, shap 0.48.0, backend
  `Agg`).
- **Note**: this is a Colab-vs-subprocess environment issue, not a package
  incompatibility; no dependency pin changed and no fallback was needed.

## 10. Windows non-ASCII checkout × editable `.pth` decoding — FIXED

- **Environment**: Windows, Python 3.11, Traditional Chinese system locale,
  repository path containing non-ASCII characters.
- **Symptom**: the default editable `uv sync` succeeds, but Python then fails
  during `site` initialization with `UnicodeDecodeError` before project code can
  run. The editable `.pth` contains a UTF-8 source path while Python 3.11 reads
  it with the active legacy locale codec.
- **Fix**: `scripts/setup_environment.py` performs a pinned non-editable wheel
  install (`uv sync --frozen --no-editable`) and verifies import. The release
  test copies the project to a Unicode checkout, confirms no source-path `.pth`
  exists, and imports the installed package from outside the repository.
- **Scope**: no user name, drive, or machine path is hard-coded. Development
  commands use `uv run --no-sync`; source-tree tests explicitly set a relative
  `PYTHONPATH=src`, while isolated wheel tests exercise the installed artifact.

## Residual nondeterminism notes

- LightGBM runs with `deterministic=true, force_row_wise=true` and a fixed
  thread count; sklearn and EBM get derived `random_state` values; every
  bootstrap iteration derives its own seed. Reproducibility is claimed **given
  the committed uv.lock and the same platform/BLAS**, not bitwise across
  operating systems.
- Latency numbers depend on the host CPU and thread environment; the
  measurement records platform details and is not comparable across machines.
