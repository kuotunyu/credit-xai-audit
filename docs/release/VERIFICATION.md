# Local Release-Candidate Verification

Verification date: 2026-08-12 (Asia/Taipei)

Candidate state: **unpublished**. No remote, push, pull request, tag, release,
deployment, or model upload was created.

## Environment

- Windows 11 10.0.26200, Intel Core i7-13700, CPU only
- Python 3.11.15; uv 0.11.18; Git 2.41.0.windows.1
- `CUDA_VISIBLE_DEVICES` was empty; long-run thread counts were capped at 2
- Source snapshot: `58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`

## Static, test, and evidence gates

The final source-level run completed with:

- `uv lock --check`: pass (92 locked packages)
- `ruff check src app tests`: pass
- `ruff format --check src app tests`: pass (88 files)
- `mypy --strict src app`: pass (64 source files)
- `pytest`: 109 passed, 5 third-party deprecation warnings
- `credit_xai.release.verify claims`: pass
- `credit_xai.release.verify privacy`: pass

The warnings are three SHAP/Matplotlib pending deprecations and two Gradio 5
`row_count` deprecations. They do not change outputs; the Gradio dependency is
bounded below version 6 for this candidate.

The non-editable clean setup command, `python scripts/setup_environment.py`,
completed and imported the package successfully from the non-ASCII checkout.

## Dataset provenance

The official UCI static archive was downloaded from the URL pinned in
`manifests/dataset_fingerprint.json` and verified before extraction:

- archive bytes: 5,539,494
- archive SHA-256:
  `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`
- canonical content SHA-256:
  `f6c131c25f5ea6716c1439d986550832a5ba1ed218fbbfc3013bb92bb78dcee2`

Checksum mismatch handling was also covered by the test suite and fails closed.

## Report determinism

Two isolated report runs rebuilt the candidate from the same committed raw
artifacts. All 13 outputs were byte-identical between runs: `summary.json`, four
derived Markdown tables, six PNG figures, and both README files. The accepted
summary was rebuilt rather than manually edited. The six PNGs were also checked
at the pixel level against the prior rendering: zero changed pixels.

## Full CPU reproduction

One isolated full run completed from the verified UCI archive without writing to
the candidate's committed `results/`, `assets/`, `data/`, or `models/` paths.
Elapsed wall time was approximately 12 minutes 34 seconds on the environment
above. Every checkpoint ended with `status=complete` and its exact declared IDs:

| Model | Metric bootstrap | Group bootstrap | Stability | Faithfulness |
|---|---:|---:|---:|---:|
| logistic | 1,000 | 1,000 | 220 | 2,000 |
| EBM | 1,000 | 1,000 | 220 | 2,000 |
| LightGBM | 1,000 | 1,000 | 220 | 2,000 |

The isolated claim verifier passed. Comparison against the accepted summary,
excluding time, platform, and latency metadata, covered 1,109 fields:

- dataset hash and config hash: exact match
- categorical differences: 0
- numeric differences: 60 floating-point tail differences
- maximum absolute numeric difference: `2.2151169787321123e-12`
- calibration methods, explainer methods, and all three top-10 feature rankings:
  exact match

The reproduction therefore supports numerical reproducibility on this Windows
CPU environment, but it is not described as byte-identical. Its outputs remain
isolated and were not adopted over the committed evidence. LightGBM used the
recorded path-dependent `pred_contrib` TreeSHAP fallback, as declared in
`FAILURES.md` and the accepted artifacts.

## API, UI, package, and container gates

- FastAPI and Gradio without a model: health 200, `model_loaded=false`, 11 UI
  components, and the historical-replay decision boundary was present.
- FastAPI and Gradio with the isolated hash-verified LightGBM bundle: health,
  predict, and explain all returned 200; explanation method was `tree_shap`.
- sdist: 226,994 bytes, 84 files; wheel: 85,013 bytes, 67 files.
- Archive inspection found no environment, raw dataset, model, result, or scratch
  payload in either distribution.
- The wheel was installed in an isolated environment outside the repository;
  package import and FastAPI health passed.
- `docker compose config --quiet`: pass.
- Docker CLI/buildx were present, but the Docker Desktop Linux daemon was not
  running. Docker build and container health were **not executed and are not
  claimed as passed**. They remain an owner action before publication.

## Interpretation boundary

This is an educational audit of a 2005 historical dataset. It is not a lending
system, financial advice, causal research, or evidence about modern credit-market
fairness. Group metrics are descriptive model-behavior snapshots; small-cell
confidence intervals are suppressed. Faithfulness perturbations are model sanity
checks, not causal proof.
