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
- `ruff format --check src app tests`: pass (90 files)
- `mypy --strict src app`: pass (65 source files)
- `pytest`: 144 passed, 18 third-party deprecation warnings
- `credit_xai.release.verify claims`: pass
- `credit_xai.release.verify privacy`: pass

The warnings are three SHAP/Matplotlib pending deprecations and 15 Gradio 5
constructor/`row_count` deprecation reports emitted across five UI-construction
tests. They do not change outputs; the Gradio dependency is bounded below
version 6 for this candidate.

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

- FastAPI and Gradio without a model: health 200, `model_loaded=false`, all 23
  labeled integer inputs, and the historical-replay decision boundary present.
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

The owner-approved UI renewal reran the Docker release gate on the Docker Desktop
Linux daemon with the following fresh evidence:

- `docker compose build api`: pass in 121.191 seconds. Runtime validation was
  still performed even though reusable build layers were available.
- Image: `credit-xai-audit:latest`, ID
  `sha256:a15fdf1bbb176f9146bf36e955e1de50d767a327031549f93290363d26ef9e55`.
  `docker image inspect` reported 814,558,270 bytes.
- Runtime identity and compute boundary: configured user `appuser`, UID 1000,
  Linux/amd64, two-CPU/two-GB smoke limits, empty `CUDA_VISIBLE_DEVICES`,
  `NVIDIA_VISIBLE_DEVICES=void`, no GPU device requests, and no `/dev/nvidia0`.
- Image content audit: `/app/data` and `/app/results` had no payloads, while
  `/app/models` contained only the public `.gitkeep`; no joblib bundle, `.env`,
  raw UCI payload, private progress/handoff/agent note, or committed result
  payload was present.
- The existing synthetic CI command set passed in 20.767 seconds inside a
  two-CPU/two-GB container with `network=none`. It generated 2,000 synthetic
  rows; trained logistic, EBM, and LightGBM; calibrated on validation; evaluated
  and explained all three models; and regenerated the smoke report without
  touching the accepted public evidence.
- Synthetic artifact audit: source fingerprint `synthetic`, no ZIP/XLS, three
  bundle hash manifests valid, exact checkpoint IDs and `status=complete` for
  50 metric bootstraps, 50 group bootstraps, 12 stability iterations, and 50
  faithfulness instances per model. Explainers were `linear_shap`, `ebm_native`,
  and `tree_shap` respectively.
- Model-absent Compose API: container healthy; container-internal `/health` 200
  with `model_loaded=false`; Gradio `/ui/` and `/ui/config` returned 200 and
  contained the shipped Traditional Chinese thesis, model set, and honest
  no-bundle state. Container-internal checks were authoritative because another
  local process already occupied the host loopback port; that unrelated process
  was left untouched.
- Read-only synthetic LightGBM bundle: container healthy; `/health`, `/predict`,
  `/explain`, Gradio `/ui`, and OpenAPI all returned 200. The explanation method
  was `tree_shap`; responses retained the historical replay disclaimer/scope and
  exposed no approval, eligibility, accept, reject, or decision fields.
- The API had no writable repository mount. Its synthetic bundle volume was
  read-only, so requests and responses could not alter the public repository.
- Cleanup audit: release-gate containers, project network, and temporary volume
  were removed. The audited `credit-xai-audit:latest` image was intentionally
  retained; it had zero running containers after cleanup.

## Owner-approved UI renewal gate

- Focused presenter/Gradio suite: 35 passed. Full suite: 144 passed.
- Desktop and compact browser inspection confirmed the approved 8/4 editorial
  workspace, readable type, visible keyboard focus, square controls, stable
  empty/result geometry, and no page-level horizontal overflow at 390px.
- The model-absent screen showed no illustrative probability. A separate,
  ignored synthetic LightGBM bundle produced successful calibrated prediction
  and explanation views without exposing the synthetic prediction value in
  public evidence.
- API `/health`, `/predict`, and `/explain` returned 200 with the synthetic
  bundle; Gradio `/analyze` also succeeded. The model/explainer pair was exactly
  `LightGBM`/`TreeSHAP`, and approval, eligibility, accept, reject, and lending
  decision fields or language were absent.
- Synthetic artifacts used source `synthetic`, the verified deterministic
  checksum, and split counts 1,400/300/300. All three bundle manifests and file
  hashes passed; explainer mappings were `linear_shap`, `ebm_native`, and
  `tree_shap`. Metric/group checkpoints were complete at 50/50, stability at
  12, and faithfulness at 50 per model. No network or UCI archive was used.
- `python -m build` produced the sdist and API-only wheel. The sdist contained
  `app/gradio_ui.py`, `app/gradio_presenter.py`, and `app/gradio_theme.css`;
  archive inspection found no environment, raw-data payload, model bundle,
  result payload, browser artifact, scratch file, or absolute archive path.
  An isolated wheel install imported from its own site-packages and passed the
  FastAPI model-absent health smoke from the extracted sdist application layer.
- The design review reached `ship`: hierarchy, editorial-world fidelity,
  first-viewport story, responsive form, accessibility, and truth/privacy all
  matched the approved specification. The one mechanical detector notice was
  the approved amber scope-boundary rule, not a decorative card accent.

Feature Freeze is renewed after this owner-approved, UI-only change. It changed
no model, formal metric, accepted result, API schema, pipeline, dependency,
Docker policy, or decision scope.

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
