# Local Release-Candidate Verification

Verification date: 2026-08-12 (Asia/Taipei)

Candidate state: **unpublished**. No remote, push, pull request, tag, release,
deployment, or model upload was created.

## Environment

- Windows 11 10.0.26200, Intel Core i7-13700, CPU only
- Python 3.11.15; uv 0.11.18; Git 2.41.0.windows.1
- Docker Engine 29.6.1; Docker Compose 5.3.0; Linux/amd64 daemon with 24 CPUs
- `CUDA_VISIBLE_DEVICES` was empty; long-run thread counts were capped at 2
- Source snapshot: `58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`

## Static, test, and evidence gates

The final source-level run completed with:

- `uv lock --check`: pass (92 locked packages)
- `ruff check src app tests`: pass
- `ruff format --check src app tests`: pass (88 files)
- `mypy --strict src app`: pass (64 source files)
- `pytest`: 110 passed, 5 third-party deprecation warnings
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
- `python -m build`: pass; both sdist and wheel were produced. Exact compressed
  bytes are recorded in the release-gate report rather than treated as a stable
  claim, because refreshing the embedded release manifest changes gzip output.
- Archive inspection found no environment, raw dataset, model, result, or scratch
  payload in either distribution.
- The wheel was installed in an isolated environment outside the repository;
  package import and FastAPI health passed.
- `docker compose config --quiet`: pass.

The final Docker release gate used the Docker Desktop Linux daemon and completed
with the following fresh evidence:

- `docker compose build api`: pass in 200.092 seconds. The build pulled and
  installed Linux CPU dependencies rather than relying solely on cached runtime
  validation.
- Image: `credit-xai-audit:latest`, ID
  `sha256:907aa52bcf84e2f65cb0623cecc369bb25059b5d39c9f640b0a0ed30536877b4`.
  `docker image inspect` reported 814,540,128 bytes; Docker Desktop reported
  3.51 GB in its unpacked local image store (3.399 GB unique).
- Runtime identity and compute boundary: configured user `appuser`, UID 1000,
  Linux/amd64, two-CPU/two-GB smoke limits, empty `CUDA_VISIBLE_DEVICES`,
  `NVIDIA_VISIBLE_DEVICES=void`, no GPU device requests, and no `/dev/nvidia0`.
- Image content audit: `/app/data`, `/app/models`, and `/app/results` were empty;
  no joblib bundle, `.env`, raw UCI payload, private progress/handoff/agent note,
  or committed result payload was present.
- Existing Compose synthetic profile: pass in 19.635 seconds with
  `network_mode=none`. It generated 2,000 synthetic rows; trained logistic,
  EBM, and LightGBM; calibrated on validation; evaluated and explained all three
  models; and regenerated the smoke report without touching the accepted public
  evidence.
- Synthetic artifact audit: source fingerprint `synthetic`, no ZIP/XLS, three
  bundle hash manifests valid, exact checkpoint IDs and `status=complete` for
  50 metric bootstraps, 50 group bootstraps, 12 stability iterations, and 50
  faithfulness instances per model. Explainers were `linear_shap`, `ebm_native`,
  and `tree_shap` respectively.
- Model-absent Compose API: container healthy; `/health` 200 with
  `model_loaded=false`; `/predict` 503; Gradio `/ui` 200.
- Read-only synthetic LightGBM bundle: container healthy; `/health`, `/predict`,
  `/explain`, Gradio `/ui`, and OpenAPI all returned 200. The explanation method
  was `tree_shap`; responses retained the historical replay disclaimer/scope and
  exposed no approval, eligibility, accept, reject, or decision fields.
- The API had no writable repository mount. Its synthetic bundle volume was
  read-only, so requests and responses could not alter the public repository.
- Cleanup audit: release-gate containers, project network, and temporary volume
  were removed. The audited `credit-xai-audit:latest` image was intentionally
  retained; it had zero running containers after cleanup.

With these Docker gates and the final source/package gates recorded below, the
unpublished candidate is under **Feature Freeze**. Only evidence corrections,
security fixes, or owner-approved publication metadata may change it before
release.

## Interpretation boundary

This is an educational audit of a 2005 historical dataset. It is not a lending
system, financial advice, causal research, or evidence about modern credit-market
fairness. Group metrics are descriptive model-behavior snapshots; small-cell
confidence intervals are suppressed. Faithfulness perturbations are model sanity
checks, not causal proof.
