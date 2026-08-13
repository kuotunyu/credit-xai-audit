# Engineering fallbacks and negative results

> Historical 2005 educational audit. Not for lending decisions or financial
> advice.

This is a curated record of failures that changed the implementation or define
how its evidence must be interpreted. Routine setup mistakes and resolved UI
iteration notes are intentionally omitted.

## TreeSHAP interventional mode was incompatible with native categoricals

With SHAP 0.48.0 and LightGBM 4.6.0, probing an interventional
`TreeExplainer` against an `LGBMClassifier` trained with native pandas
categoricals raised `AttributeError: 'TreeEnsemble' object has no attribute
values`.

The implementation falls back automatically to LightGBM
`pred_contrib=True`, which provides exact path-dependent TreeSHAP values. Every
explanation artifact records the actual mode under
`method_detail.feature_perturbation`; the accepted run reports
`tree_path_dependent(pred_contrib)`. These attributions describe model behavior
under split-cover weighting, not interventional effects or real-world causes.

## Unanchored ignore rules hid source packages

An early `data/` pattern also matched `src/credit_xai/data/` and
`results/raw/data/`; `models/*` created the same risk for
`src/credit_xai/models/`. The working tree appeared clean while source files
were absent from Git.

The rules are now root-anchored as `/data/` and `/models/*`. Release tests and
the generated manifest verify the actual tracked tree rather than trusting
`git status` alone.

## Windows Unicode paths broke editable installs

On Python 3.11 with a legacy Windows locale, an editable `.pth` containing a
UTF-8 checkout path could fail during Python `site` initialization before
project code loaded.

`scripts/setup_environment.py` therefore performs a frozen, non-editable wheel
install. The portability test copies the project to a Unicode path, verifies
that no source-path `.pth` is installed, and imports the package from outside
the checkout. No account name, drive, or machine-specific path is hard-coded.

## Colab leaked an invalid plotting backend into subprocesses

Colab exports `MPLBACKEND=module://matplotlib_inline.backend_inline`. A project
subprocess without `matplotlib_inline` then failed while importing LightGBM or
SHAP. Notebook setup overrides the inherited value with the headless `Agg`
backend before invoking subprocesses. No dependency pin or model behavior
changed.

## Docker smoke orchestration exposed volume and filesystem assumptions

Fresh named volumes were initially created as root-owned and could not be
written by the non-root application user. A later manual probe also applied an
API-style read-only root filesystem to the report command, even though report
generation intentionally writes disposable figures and README blocks.

The accepted orchestration initializes only the explicitly named temporary
volume for the non-root UID, runs the synthetic pipeline with networking and
GPU visibility disabled, and uses read-only filesystems only for API
containers. Disposable containers, networks, and volumes are removed after the
gate. No host dataset, model, request, response, or repository path is mounted
writable during the smoke run.

## Reproducibility boundary

- LightGBM uses deterministic row-wise execution and fixed thread counts;
  sklearn, EBM, bootstrap iterations, refits, and resamples receive derived
  seeds.
- Reproducibility is claimed for the committed lockfile and equivalent
  platform/BLAS behavior, not bitwise identity across operating systems.
- Latency is host- and thread-dependent and must not be compared across
  machines without matching the recorded environment.
- Faithfulness perturbations are model sanity checks, not causal evidence.
