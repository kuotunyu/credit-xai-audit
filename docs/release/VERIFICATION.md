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
- `pytest`: 145 passed, 24 third-party deprecation warnings
- `credit_xai.release.verify claims`: pass
- `credit_xai.release.verify privacy`: pass

The warnings are three SHAP/Matplotlib pending deprecations and 21 Gradio 5
constructor/`row_count` deprecation reports emitted across seven UI-construction
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

- Focused presenter/Gradio suite: 36 passed. Full suite: 145 passed.
- Desktop and compact browser inspection at 1900px, 1280px, 768px, and 390px
  confirmed the approved 8/4 editorial workspace, readable type, visible
  keyboard focus, square controls, stable empty/result geometry, and no
  page-level horizontal overflow. The desktop thesis measured 38px at 1280px
  and capped at 48px at 1900px; compact metadata measured at least 13.76px.
- The scope boundary now sizes to its content instead of stretching to the hero.
  Case heading, metadata, index, and load action share one 85px desktop toolbar;
  the first feature row begins about 36px earlier than the superseded layout.
- A real synthetic success state moved the ten verified attribution rows into a
  conditional full-width band. At 1900px the workspace height fell from about
  855px to 497px, its input and result columns differed by about 3px, and the
  attribution band matched the 1,440px workspace width. The band was absent
  before analysis and remained overflow-free at 768px and 390px.
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

### Borderless visual distillation

- A browser-rendered RED contract at 1280px reproduced the excessive chrome:
  status, KPI, tab, numeric input, and secondary-action borders measured 1px,
  while the primary action stretched to 814.30px.
- The GREEN contract passed at 1900px, 1280px, 768px, and 390px. Those redundant
  border sides all measured 0px; Gradio's feature-form and case-index backgrounds
  were transparent; page width equalled viewport width; and no browser exception
  occurred. Desktop primary-action widths were 220.00px, 196.47px, and 184.31px;
  only the 390px phone layout intentionally used a full-width action.
- The same viewport set confirmed inline masthead statuses, unboxed KPI pairs,
  underline tabs and fields, and the result region as the only major tonal
  content plane. The evidence matrix remains a table because its row/column
  relationships require a grid.
- A fresh synthetic-bundle UI smoke returned health 200 with
  `model_loaded=true`, `LightGBM`, `isotonic`, and `TreeSHAP`. The result
  displayed calibrated and uncalibrated probabilities plus 11 attribution rows.
  Desktop and 390px success states had no horizontal overflow; the mobile
  attribution band and primary action both matched the viewport width.
- The smoke used the existing CPU-only `configs/ci.yaml` bundle under ignored
  `tmp/ci`; it did not download UCI data, use the network, alter accepted
  metrics, or write runtime data into the public tree. The focused Gradio and
  presenter suite passed all 36 tests, and the layout detector returned no
  findings.
- The current visual-code state was rebuilt as `credit-xai-audit:latest` in
  168.164 seconds. Image ID
  `sha256:a52605f19a33f2283ce33d912050b4b3968b863625f1cc688828d30b00fd5d349`
  measured 814,560,518 bytes and ran as `appuser`/UID 1000 on Linux/amd64.
  Its non-third-party `/app` content scan covered 79 files and found no raw-data
  payload, model bundle, result payload, `.env`, private note, or credential.
- The refreshed image passed a second CPU-only synthetic full pipeline in
  22.014 seconds with `network=none`, two CPUs, two GB of memory, empty
  `CUDA_VISIBLE_DEVICES`, and `NVIDIA_VISIBLE_DEVICES=void`. It regenerated all
  three training, validation-only calibration, evaluation, explanation, and
  report paths entirely inside the disposable container; the accepted public
  artifacts were not mounted or changed.
- The refreshed image's model-absent API was healthy with `/health` 200 and
  `model_loaded=false`. Because the pre-existing host service still owned port
  8000, a separately named disposable container exposed the same image on
  127.0.0.1:18080 for the browser gate. At 1280px and 390px, `/ui/` returned
  200, all six targeted redundant border sides measured 0px, the feature form
  was transparent, the honest no-bundle state was present, and neither overflow
  nor browser exceptions occurred. The unrelated port-8000 process was left
  untouched.
- All refreshed-gate containers and the Compose project network were removed;
  no project volume remained and no container referenced the image. The tested
  image was intentionally retained. The subsequent evidence/manifest commit
  changes no runtime source.

### Typography rebalance

- A real-browser RED contract at 1,656px measured the thesis at 44.712px while
  40 visible roles used 13.12px and another 18 used 13.44px. Named failures
  included the 12.16px section marker, 12.80px decision-boundary note, 13.12px
  field labels, 13.44px evidence cells, 14.72px primary action, and 16.64px
  numeric values.
- The exact GREEN contract measured the thesis at 38.916px, ordinary result
  copy and actions at 16px, supporting copy at 15.04px, labels at 14.56px,
  compact metadata at 14px, and numeric values at 18px. All named roles cleared
  their independent thresholds.
- Browser confirmation at 1,656px, 1,280px, 768px, and 390px measured thesis
  sizes of 38.916px, 36px, 36px, and 30px respectively. Every width had zero
  page-level horizontal overflow; case-number and primary-action controls were
  at least 44px and 50px high. The desktop workspace now uses a verified 7/5
  split, and the case heading/metadata and case controls occupy two stable rows.
- A CPU-only synthetic LightGBM UI run displayed `isotonic`, `TreeSHAP`, and
  the attribution table with 14–16px operational copy and no overflow. It used
  the existing ignored CI bundle, changed no accepted artifact, disclosed no
  prediction in this evidence, and exposed no approval, rejection, eligibility,
  or recommendation language.
- The focused Gradio/presenter suite passed all 36 tests after the change. Ruff
  format/check, strict Mypy for `app`, and `git diff --check` also passed.

The committed typography code was then rebuilt and exercised in Docker:

- `docker compose config --quiet` passed against Docker Engine 29.6.1 and
  Compose 5.3.0. `docker compose build api` completed in 190.781 seconds and
  produced `credit-xai-audit:latest`, ID
  `sha256:7ee5bb1fa09fb8c0718eada458ea21b3bc497553bced2cf16a1b1ce2cff7b459`,
  measuring 814,560,778 bytes.
- The image ran as `appuser`/UID 1000 on Linux/amd64 with two CPUs, two GB of
  memory, empty `CUDA_VISIBLE_DEVICES`, `NVIDIA_VISIBLE_DEVICES=void`, and no
  NVIDIA device. Its application content contained no raw data, result payload,
  model bundle, `.env`, private note, credential, or runtime scratch payload.
- The network-disabled synthetic pipeline completed cleanly in 21.869 seconds.
  It generated 2,000 synthetic rows, trained/calibrated/evaluated/explained all
  three models, and rendered its report inside a disposable Docker volume.
  Calibration used validation only; methods were `linear_shap`, `ebm_native`,
  and `tree_shap`; metric/group bootstrap counts were 50, stability resamples
  were 10, faithfulness counts were 50, and all bundle file hashes passed.
- A model-absent container became healthy with `/health` 200 and
  `model_loaded=false`. Its real browser render at 1,656px/390px reproduced the
  verified 38.916px/30px thesis, 16px body, 15.04px supporting copy, 14.56px
  labels, and 18px values with no overflow or fabricated prediction.
- A second container mounted only the disposable synthetic volume read-only.
  `/health`, `/predict`, and `/explain` returned 200; `model_loaded=true` and the
  method was `tree_shap`. Its Gradio success state displayed LightGBM,
  `isotonic`, TreeSHAP, and attributions without decision language or overflow.
- Both temporary containers and the synthetic volume were removed. No Compose
  network was created; no container references the retained tested image. The
  following evidence/manifest-only commit changes no runtime source.

### Workspace density

- A real-browser RED contract at 1,734px measured both workspace columns at
  509px high, with 113px of unused space below the primary action. Probability
  and the five-row model metadata table were sequential, making the result
  plane dictate the input column's height.
- The exact GREEN contract measured both columns at 405px, 9px below the
  primary action, and a zero-pixel column-height difference. Probability and
  model metadata now share one facts row, so the evidence section arrives
  104px earlier without adding content or moving form controls apart.
- Real-browser checks at 1,734px and 1,280px measured 9px and 7px below the
  action respectively. At 768px the input and result planes stack, and at
  390px the facts return to source-order stacking. All four widths had zero
  page-level horizontal overflow.
- A CPU-only synthetic LightGBM run displayed `isotonic`, `TreeSHAP`, and the
  attribution table in the compact layout. It used the ignored CI bundle,
  changed no accepted artifact, and exposed no approval, rejection,
  eligibility, recommendation, or financial-decision language.
- The focused Gradio/presenter suite passed all 36 tests. Ruff format/check,
  strict Mypy for `app`, the layout detector, and `git diff --check` also
  passed.

The committed workspace-density code was then rebuilt and exercised in Docker:

- `docker compose config --quiet` passed against Docker Engine 29.6.1 and
  Compose 5.3.0. `docker compose build api` completed in 158.153 seconds and
  produced `credit-xai-audit:latest`, ID
  `sha256:686e06bd303c32e794643c8982a40d7906163a99480f5129611daf02f223e70e`,
  measuring 814,561,428 bytes.
- The Linux/amd64 image defaults to non-root `appuser`/UID 1000. Runtime
  inspection used two CPUs, two GB of memory, empty `CUDA_VISIBLE_DEVICES`,
  `NVIDIA_VISIBLE_DEVICES=void`, and no device request. Its application layer
  contained no raw dataset, result payload, model/joblib bundle, `.env`,
  credential, private note, or runtime scratch payload.
- The existing synthetic CI pipeline completed in 22.681 seconds with
  `network=none`. It generated 2,000 rows and ran preparation, all three model
  paths, validation-only calibration, evaluation, explanation, and report
  rendering entirely inside a disposable volume; no accepted artifact was
  mounted or changed.
- The synthetic audit verified disjoint 1,400/300/300 splits, source
  `synthetic`, three valid bundle manifests and file hashes, `status=complete`
  for 50 metric bootstraps, 50 group bootstraps, 12 stability iterations, and
  50 faithfulness iterations per model. Explainers were `linear_shap`,
  `ebm_native`, and `tree_shap`; no ZIP/XLS payload existed.
- The model-absent container was healthy with `/health` 200,
  `model_loaded=false`, `/predict` 503, and `/ui/` 200. A second container
  mounted only the synthetic volume read-only; `/health`, `/predict`,
  `/explain`, and `/ui/` returned 200, with LightGBM and `tree_shap`, 23
  attributions, and no decision field or advisory language.
- Playwright rendered the actual model-absent Docker UI at 1,734px, 1,280px,
  768px, and 390px with zero page overflow and zero browser exceptions. The
  measured workspace values matched the source browser gate: 405px/9.08px at
  1,734px and 403px/7.19px at 1,280px; compact and phone layouts stacked in the
  intended order without fabricated prediction content.
- Both temporary containers and the synthetic volume were removed. No project
  network remained, no container references the image, and the tested image is
  intentionally retained. The following evidence/manifest-only commit changes
  no runtime source.

### Input-grid alignment

- A 1,714px real-browser RED contract measured a 67.36px center-line
  difference between case status and controls. The four tabs were only 84.17px
  wide inside an 809.67px input plane instead of dividing the available width.
- The exact GREEN contract measured a zero-pixel utility-row center difference,
  a 0.20px case-input/load-action bottom difference, zero-pixel right-edge
  differences, and four equal 202.41–202.42px tab tracks. Input-plane height
  remained about 405px and post-action space remained 7.19px.
- Browser checks at 1,714px, 1,280px, 768px, and 390px had zero page overflow,
  no browser exceptions, equal visible field widths, complete labels, and 44px
  minimum targets. Desktop used five field columns, compact used three, and
  phone used two; compact layouts retained DOM/source reading order.
- The CPU-only synthetic LightGBM UI succeeded at 1,714px and 390px with
  `isotonic`, `TreeSHAP`, and the attribution table visible below the workspace.
  It changed no accepted artifact and exposed no approval, rejection,
  eligibility, recommendation, or financial-action language.
- The focused Gradio/presenter suite passed all 36 tests. Ruff format/check,
  strict Mypy for `app`, the Impeccable layout detector, and `git diff --check`
  also passed.

The committed input-grid change was then rebuilt and exercised through the
actual container boundary:

- `docker compose config --quiet` passed. A fresh API image build completed in
  178.992 seconds and produced `credit-xai-audit:latest`, ID
  `sha256:269ef2ac69c4f09a214a6acef10abdc144b669b3548b3e6089408850cf39678c`,
  measuring 814,561,991 bytes.
- The Linux/amd64 image defaults to non-root `appuser`/UID 1000. It contained no
  raw dataset, model/joblib bundle, result payload, `.env`, private note, or
  runtime scratch file. Both API containers used a read-only root filesystem,
  two CPUs, two GB of memory, empty `CUDA_VISIBLE_DEVICES`,
  `NVIDIA_VISIBLE_DEVICES=void`, and no GPU device request.
- The full synthetic pipeline completed in 22.263 seconds with `network=none`
  and an isolated disposable volume. It produced 2,000 synthetic rows, disjoint
  1,400/300/300 splits, validation-only calibration, three hash-valid bundles,
  and complete metric/group bootstrap, stability, and faithfulness checkpoints.
  Explainers matched their bundles: `linear_shap`, `ebm_native`, and
  `tree_shap`.
- The model-absent API returned `/health` 200 with `model_loaded=false`,
  `/predict` 503, and `/ui/` 200. With the synthetic volume mounted read-only,
  `/health`, `/predict`, `/explain`, and `/ui/` returned 200; `/explain` used
  `tree_shap` with 23 attributions and neither response exposed a financial
  action or decision field.
- Playwright rendered the Docker UI at 1,714px, 1,280px, 768px, and 390px with
  zero horizontal overflow and zero browser exceptions. Tabs were equal,
  labels were complete, targets were at least 44px, and feature inputs formed
  five, five, three, and two columns respectively. Desktop utility centers and
  right edges matched within one pixel; compact layouts retained source order.
  A real synthetic UI action at 1,714px and 390px displayed LightGBM,
  `isotonic`, `TreeSHAP`, and the attribution table without financial-action
  language.
- Both temporary containers, the dedicated network, and the synthetic volume
  were removed. No container references the retained test image, and no
  committed result, model, dataset, request, or response was changed.

### Field-ledger rhythm

- A 1,908px real-browser RED contract measured the mismatch directly: the four
  full-width group tabs consumed 100% of the input plane while five active
  fields used a different center rhythm. Field labels and values were centered,
  the group had no shared top or bottom rule, its cells had no separators, and
  each input instead carried a disconnected bottom line.
- The exact GREEN contract reduced the group index to 68.8% of the input-plane
  width, kept the five active-cell widths within 0.02px, left-aligned labels and
  values, and established one-pixel shared boundaries and internal hairlines.
  The basic-group action matched its 158.19px ledger track.
- Real-browser checks covered all four groups at 1,714px, 1,280px, 768px, and
  390px. Desktop groups used five or six equal cells, compact layouts used
  three, and phones used two. The action matched one active desktop or compact
  track and became full width only on phones. There was no page overflow,
  clipped label, or browser exception.
- The CPU-only synthetic LightGBM UI succeeded at desktop and phone widths with
  `isotonic`, `TreeSHAP`, and 11 visible attribution rows. It exposed no
  financial-action language and changed no accepted artifact.
- The focused Gradio/presenter suite passed all 36 tests. Ruff format/check,
  strict Mypy for `app`, the Impeccable layout detector, and `git diff --check`
  also passed.

The committed field-ledger code was then rebuilt and exercised through the
actual container boundary:

- Docker Engine 29.6.1 and Compose 5.3.0 reported a Linux/amd64 daemon with 24
  CPUs. `docker compose config --quiet` passed. The API image build completed
  in 96.181 seconds and produced `credit-xai-audit:latest`, ID
  `sha256:7961ebcef91cd13ed3865a6c6424f781c40fc8d85338aa5c7c29004cfc8a9701`,
  measuring 814,562,510 bytes.
- The image defaults to non-root `appuser`/UID 1000 and resolves project code
  from `/app/src`. Its project layer contained zero raw-data, model, result, or
  temporary payload files and no `.env`, private note, credential, or model
  bundle. Runtime checks used two CPUs, two GB of memory, empty
  `CUDA_VISIBLE_DEVICES`, and `NVIDIA_VISIBLE_DEVICES=void`.
- The accepted synthetic pipeline ran as non-root with `network=none` in
  19.587 seconds. It used a clean disposable volume for `tmp/ci` and a
  disposable writable container layer for report-owned README/figure outputs,
  matching the existing smoke profile boundary. It produced 2,000 synthetic
  rows, disjoint 1,400/300/300 splits, validation-only calibration, three
  hash-declared bundles, and complete 50/50/12/50 evaluation, group,
  stability, and faithfulness checkpoints. Explainers were `linear_shap`,
  `ebm_native`, and `tree_shap` for Logistic, EBM, and LightGBM respectively.
- Earlier harness probes were rejected rather than counted as passes: a login
  shell resolved system Python instead of the image venv; read-only report
  probes correctly blocked `/app/assets` and generated README writes; and the
  first assets tmpfs was root-owned. The accepted command explicitly used the
  image venv and the disposable writable container layer. Neither accepted
  artifacts nor repository files were mounted writable.
- The model-absent API container used a read-only root filesystem and became
  healthy with `/health` 200, `model_loaded=false`, `/predict` 503, and `/ui/`
  200. The synthetic API mounted only the disposable volume read-only and
  returned 200 from `/health`, `/predict`, `/explain`, and `/ui/`; it reported
  LightGBM, `tree_shap`, 23 link-scale attributions, and no financial-action
  response field.
- Playwright executed the real synthetic UI action at 1,714px and 390px. Both
  layouts had zero overflow and zero browser exceptions, displayed LightGBM,
  `isotonic`, `TreeSHAP`, and the attribution table, and contained no approval
  or rejection term in the result. Desktop field widths differed by only
  0.016px and the 158.19px action matched one field track; the phone retained
  its two-column ledger and full-width action.
- Both healthy API containers, the dedicated network, and every temporary
  synthetic volume from this gate were removed. No container references the
  image. The tested `credit-xai-audit:latest` image is intentionally retained
  at 814,562,510 bytes; no host result, model, dataset, request, or response was
  created or changed.

### Reading-density refinement

- The real-browser RED contract at 1,908px measured a 1,440px stage, 15.04px
  support copy, 14.56px labels and metadata, 18px field values, and a 32px
  workspace-to-evidence transition. The exact GREEN contract measured a
  1,600px stage, 16px support copy, 15.5px labels and metadata, 19px values,
  and a 22px transition. The thesis remained 40px on desktop and 30px on a
  390px phone.
- A single bounded desktop/phone visual batch confirmed the larger reading
  scale, equal field ledger, 4.8px input tail, two-column phone fields, and
  full-width phone action. Both widths had zero page-level overflow and zero
  browser exceptions. The Impeccable layout detector returned no finding, and
  the focused Gradio/presenter suite passed all 36 tests.
- Docker Engine 29.6.1 and Compose 5.3.0 accepted the Compose configuration.
  The API image build completed in 111.96 seconds and produced
  `credit-xai-audit:latest`, ID
  `sha256:b0322baf8ad212e599b4d952f1b1a6a61887b8b9ad8dbbcabdc64c485628d4ff`,
  measuring 814,562,586 bytes. The Linux/amd64 image defaults to non-root
  `appuser`/UID 1000 and contained no raw data, committed results, model/joblib
  bundle, `.env`, private note, credential, or Git history.
- The accepted network-disabled synthetic pipeline used the image venv, two
  CPUs, two GB, and a disposable volume. It completed in 22.10 seconds with
  2,000 synthetic rows, disjoint 1,400/300/300 splits, validation-only
  `isotonic` calibration for all three models, twelve complete checkpoint
  records, three hash-valid bundles, and the expected `linear_shap`,
  `ebm_native`, and `tree_shap` explainers. An earlier harness invocation using
  system Python stopped before producing data and was not counted as evidence.
- Read-only model-absent and synthetic API containers both returned `/health`
  and `/ui/` 200. The former reported `model_loaded=false`; the latter returned
  200 from `/predict` and `/explain`, reported `historical_model_replay`, and
  used `tree_shap` with ten top attributions. Playwright executed the real
  synthetic Gradio action at 1,908px and 390px: both displayed LightGBM,
  `isotonic`, TreeSHAP, and the attribution table using the verified type scale,
  with no overflow, browser exception, or financial-action language.
- The final non-editable setup imported `credit_xai` from the checkout's
  `.venv` site-packages, with `direct_url.json` confirming `editable=false`.
  `uv lock --check` resolved all 92 locked packages; Ruff format/check passed
  for 91 files; strict Mypy passed for 65 source files; and the full suite passed
  all 145 tests with the 24 already-declared third-party deprecation warnings.
  Claims, privacy, and manifest gates passed independently after removing one
  machine-specific detector path from the public implementation plan.
- The wheel and sdist built in isolated build environments and passed member,
  payload, absolute-path, model-bundle, raw-data, result, environment, and
  private-note inspection. The wheel was installed with its declared `serve`
  dependencies in a separate environment; import resolved from that
  environment's site-packages and the model-absent FastAPI `/health` smoke
  returned 200. A preliminary `--no-deps` API probe stopped at the intentionally
  absent FastAPI dependency and was not counted as evidence.
- Both API containers and the disposable synthetic volume were removed. No
  temporary network remained. The tested image is intentionally retained; no
  host result, model, dataset, request, or response was created or changed.

### Complete audit worksheet rebuild

- The rendered RED contract exposed the structural defect directly: zero
  feature-group rows, four tabs, and only five visible numeric controls. The
  replacement removes tabs and exposes all four canonical groups and all 23
  fields in source order. Desktop rows use 5/6/6/6 equal tracks with a 128px
  group rail; the 768px layout uses three tracks with a 112px rail; and the
  390px layout uses two tracks with horizontal group headings.
- At 1,908px and 1,280px, the rebuilt case toolbar measured 70px tall and each
  within-row field-width spread was at most 0.02px. At 390px the toolbar was
  119.61px, including the stacked heading and one-line loader. Every tested
  width kept 44px-or-larger inputs and buttons, zero clipped labels, a 3.19px
  post-action tail, zero page overflow, and zero browser logs.
- The real model-absent preview remained fail-closed. The real synthetic
  container UI succeeded at 1,280px and 390px, displaying LightGBM,
  `isotonic`, TreeSHAP, and the verified attribution table. It exposed no
  financial-action language or case-level value in public evidence.
- Docker Engine 29.6.1 and Compose 5.3.0 accepted the Compose configuration.
  The Linux/amd64 API image build completed in 194.95 seconds and produced
  `credit-xai-audit:latest`, ID
  `sha256:20bef1a8090594eefde95d272fd3b1ea6fcc25dc4cbc86c9b22d18046b1a22c2`,
  measuring 814,562,858 bytes. It defaults to non-root `appuser`/UID 1000 and
  contains no GPU package, raw data, model bundle, committed result, `.env`,
  Git history, or private progress/handoff file.
- The accepted network-disabled synthetic pipeline used the image venv, two
  CPUs, two GB, and a disposable volume. It completed in 22.55 seconds with
  2,000 synthetic rows, disjoint 1,400/300/300 splits, validation-only
  `isotonic` calibration for all three models, twelve complete checkpoint
  streams, three hash-valid bundles, and the expected `linear_shap`,
  `ebm_native`, and `tree_shap` explainers. A preliminary login-shell command
  resolved system Python and stopped before data generation; it was corrected
  with the explicit image venv and is not counted as evidence.
- The synthetic API ran healthy with a read-only root filesystem and a
  read-only synthetic volume. `/health`, `/predict`, `/explain`, `/ui/`, and
  OpenAPI returned 200; the service reported `historical_model_replay`, used
  `tree_shap`, and returned ten top attributions. The first default-config
  launch also correctly failed closed with `model_loaded=false` before the
  explicit synthetic config was supplied.
- Both temporary API containers, the dedicated network, and the synthetic
  volume were removed. The tested image is intentionally retained. The Docker
  gate wrote no dataset, model, result, request, or response into the public
  repository.
- Fresh non-editable setup resolved `credit_xai` from the checkout's `.venv`
  site-packages with `editable=false`. `uv lock --check` resolved 92 packages;
  Ruff format/check passed for 91 files; strict Mypy passed for 65 source
  files; the focused Gradio/presenter suite passed all 37 tests; and the full
  suite passed all 146 tests with 27 already-declared third-party deprecation
  warnings. Claims, privacy, manifest, and release-verifier gates passed after
  manifest regeneration.
- The wheel and sdist built in isolated environments. Archive inspection found
  no raw/model/result/environment/private payload or absolute path; the sdist
  retained the Gradio sources and the wheel retained the intentional API-only
  boundary. A separate wheel-plus-`serve` installation imported from its own
  site-packages and returned model-absent `/health` 200, after which the
  verified temporary environment was removed.

Feature Freeze is renewed after this owner-approved, UI-only rebuild. It
changed no model, formal metric, accepted result, API schema, pipeline,
dependency, Docker policy, or decision scope.

### Open form release gate

- A rendered RED contract at 1,908px measured each 884px feature group as a
  128px side rail plus a 756px field row. Nineteen vertical cell separators
  were visible, none of the 23 inputs had an editable underline, and the empty
  result plane was forced to the same 481px height as the form.
- The replacement keeps all 23 fields in canonical source and focus order but
  presents each canonical group as an open section. At 1,908px every group
  heading and field row measured the same 1,008px width; all 23 inputs exposed
  one-pixel underlines; vertical separators and page overflow both measured
  zero; and the empty result plane followed its 425px content height rather
  than the 636px form height.
- Browser verification covered 1,908px, 1,280px, 768px, and 390px. Desktop
  used one shared six-column mother grid, with `LIMIT_BAL` spanning two
  columns; the compact layout resolved it into three visual columns and the
  phone into two. Every width retained all 23 controls with zero horizontal
  overflow. The model-absent action remained fail-closed and displayed no
  fabricated probability or attribution.
- Docker Engine 29.6.1 and Compose 5.3.0 accepted the Compose configuration.
  The Linux/amd64 CPU-only image build completed in 145.01 seconds and produced
  `credit-xai-audit:latest`, ID
  `sha256:12379e9a03a41b0fb776391b45efe83f53e66893a93a2d967331028402959f16`,
  measuring 814,562,956 bytes. It defaults to non-root `appuser`/UID 1000 and
  contained no raw dataset, committed result, model/joblib bundle, `.env`, Git
  history, private progress/handoff file, or GPU framework.
- The accepted network-disabled synthetic pipeline used two CPUs, two GB, and
  an isolated disposable volume. It completed in 16.02 seconds with 2,000
  synthetic rows, disjoint 1,400/300/300 splits, validation-only `isotonic`
  calibration for Logistic, EBM, and LightGBM, twelve complete checkpoint
  streams, three hash-valid bundles, and the expected `linear_shap`,
  `ebm_native`, and `tree_shap` explainers. An initial run stopped at volume
  initialization with a permission error before data generation; the volume
  was assigned to the image's non-root UID and the accepted run then started
  from empty storage.
- The synthetic API ran healthy with a read-only root filesystem and the
  synthetic volume mounted read-only. `/health`, `/predict`, `/explain`,
  `/ui/`, and OpenAPI all returned 200; the output remained
  `historical_model_replay`, explanation used `tree_shap`, and ten top
  attributions were returned. Real-browser actions at 1,280px and 390px showed
  LightGBM, `isotonic`, TreeSHAP, and the attribution table with zero page
  overflow or browser error and no lending recommendation language.
- Both temporary containers, the dedicated network, and the synthetic volume
  were removed. The tested image is intentionally retained. No Docker gate
  wrote a dataset, model, result, request, or response into the public tree.
- Fresh non-editable setup resolved `credit_xai` from the checkout's `.venv`
  site-packages with `editable=false`. `uv lock --check` resolved all 92 locked
  packages; Ruff format/check passed for 91 files; strict Mypy passed for 65
  source files; the focused Gradio/presenter suite passed all 37 tests; and the
  full suite passed all 146 tests with the 27 already-declared third-party
  deprecation warnings.
- The wheel and sdist built in isolated environments and passed archive member
  inspection: neither archive contained raw data, models, committed results,
  environment files, private notes, or Git history. The sdist retained the
  Gradio source while the intentional API-only wheel did not. A separate
  wheel-plus-`serve` environment imported from its own site-packages and
  returned model-absent `/health` 200.

Feature Freeze is renewed after this owner-approved presentation correction.
It changed no component graph, callback, model, formal metric, accepted result,
API schema, pipeline, dependency, Docker policy, or decision scope.

### Shared alignment grid gate

- The rendered RED measurement at 1,908px found the first feature group on five
  equal tracks while the other groups used six. Corresponding field starts
  drifted by as much as 133.34px, and the toolbar/footer inset differed from the
  feature grid by 12px. This made consistent vertical alignment impossible.
- The corrected form uses one six-column mother grid for all 23 fields and
  reserves two columns for `LIMIT_BAL`. At 1,908px the toolbar, every group,
  the first field, and the footer shared the same 174.5px left anchor with
  0px spread. All four group rows measured 119.25px; label and input-baseline
  spreads were 0px. The same baseline spread remained 0px at 1,280px and
  768px. At 390px all anchors remained equal, all groups resolved into three
  orderly rows, and horizontal overflow remained 0px.
- The focused Gradio/presenter suite passed 37 tests. Ruff format/check passed
  for 91 files, strict Mypy passed for 65 source files, and the full suite
  passed all 146 tests with the same 27 declared third-party warnings.
- Docker Engine 29.6.1 and Compose 5.3.0 rebuilt the Linux/amd64 CPU-only image
  in 117.89 seconds. `credit-xai-audit:latest`, ID
  `sha256:3ed61dc137e6871e0f8f0aee3f2f8f774d1a2c643c9ecc3d98782b793d32877a`,
  measured 814,563,141 bytes and defaulted to non-root `appuser`.
- A network-disabled synthetic pipeline completed in 15.55 seconds with 2,000
  rows, disjoint 1,400/300/300 splits, Logistic, EBM, and LightGBM training,
  validation-only `isotonic` calibration, evaluation, and model-correct
  `linear_shap`, `ebm_native`, and `tree_shap` explanations. It wrote only to
  a disposable Docker volume.
- The synthetic API remained healthy with a read-only root filesystem and
  read-only bundle mount. `/health`, `/predict`, `/explain`, `/ui/`, and
  OpenAPI returned 200; browser actions at 1,280px and 390px confirmed
  LightGBM, `isotonic`, TreeSHAP, all 23 inputs, 0px horizontal overflow, no
  browser error, and no lending recommendation language.
- The two test containers, dedicated network, and disposable volume were
  removed. The tested image is retained. No dataset, model, result, request,
  response, environment file, or private note entered the public tree.
- A fresh wheel and sdist build passed member and content inspection with no
  raw data, model bundle, result payload, environment file, private note, Git
  history, or absolute path. The sdist retained the three intended Gradio
  sources while the wheel preserved the intentional API-only boundary. A new
  wheel-plus-`serve` environment imported exclusively from its own
  `site-packages` and returned model-absent `/health` 200; both verified
  temporary directories were then removed.

With these Docker gates and the final source/package gates recorded below, the
unpublished candidate is under **Feature Freeze**. Only evidence corrections,
security fixes, or owner-approved publication metadata may change it before
release.

### Canonical UI reconciliation — 2026-08-13

- The public candidate remains `credit-xai-audit`. Its clean-snapshot source is
  `58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`; unrelated donor history was not
  merged or copied. Later donor UI work was reviewed and selectively
  reimplemented under the canonical presenter, tests, and public boundary.
- All 23 inputs now pair a Traditional Chinese label with the canonical feature
  code. Case selection rejects fractional, non-finite, negative, and
  out-of-range indices. Missing-model, expected input rejection, and unexpected
  inference/result failures remain distinct, sanitized, fail-closed states.
- The focused presenter/Gradio/README contract passed 48 tests with 24 declared
  Gradio deprecation warnings. Ruff format and check passed for 92 files,
  strict Mypy passed for 65 source files, the full suite passed 157 tests with
  27 third-party deprecation warnings, and `uv lock --check` resolved all 92
  locked packages.
- The canonical public model-absent UI was rendered at 1,440 by 1,000 pixels.
  Document and body widths both equaled the 1,440px viewport, the browser
  reported no console or page error, and the explicit no-bundle state contained
  no fabricated prediction. `assets/ui_audit_console.png` is 142,289 bytes with
  SHA-256
  `5315485b94d7021fa31822cb1413cdeb4d0beca1b3dce8dee6ea169c59ea9667`.
- The fresh wheel is 85,477 bytes with SHA-256
  `9b6a1aeccd8cc01f57b2d4cfa468b7fac59c757509f64dfbbeff07e3d5667360`;
  the sdist is 251,373 bytes with SHA-256
  `74d3fdc4b8c3fc8e30de136882f54d08d66a2b2e06b78fb05d57f5b399d60612`.
  Archive inspection found no raw data, serialized model, committed result,
  private note, credential, machine path, or donor-only `ui_presenters.py`.
  The sdist retained the four intended `app` files while the wheel retained its
  intentional API-only boundary. A disposable wheel-plus-`serve` environment
  imported version 0.1.0 exclusively from its own `site-packages`; model-absent
  `/health` returned 200 with `model_loaded=false`.
- Docker Engine 29.6.1 and Compose 5.3.0 rebuilt the Linux/amd64 CPU-only image
  in 174.26 seconds. `credit-xai-audit:canonical-ui-c7688c7`, ID
  `sha256:63219f054eb1f64561503c4a5a00d87250a4c62933cf302d54afc5337298f1eb`,
  measures 814,565,523 bytes, defaults to non-root `appuser`, and contains zero
  files under its runtime data, model, result, and temporary payload roots.
- The model-absent container used a read-only root filesystem, two CPU and 2 GiB
  limits, no GPU device request, and became healthy. `/health` and `/ui/`
  returned 200, `model_loaded=false`, and `/predict` correctly returned 503.
- A network-disabled synthetic pipeline ran as non-root in 21.46 seconds and
  wrote only to a disposable Docker volume. It produced 2,000 rows with
  disjoint 1,400/300/300 splits, trained Logistic, EBM, and LightGBM, selected
  validation-only isotonic calibration, completed evaluation and the matching
  `linear_shap`, `ebm_native`, and `tree_shap` explainers. A second read-only
  API container returned 200 from `/health`, `/predict`, `/explain`, and
  `/ui/`; the response remained `historical_model_replay`, used LightGBM and
  TreeSHAP, and returned ten top attributions.
- Real-browser synthetic actions at 1,280px and 390px displayed LightGBM,
  isotonic calibration, TreeSHAP, and the attribution table. At both widths the
  document and body matched the viewport width, with no horizontal overflow,
  console error, or page exception.
- Both API containers, the synthetic pipeline container, dedicated network,
  and disposable volume were removed. The audited image is retained. Temporary
  package inspection environments are outside the tracked tree and are removed
  after evidence capture. No push, tag, release, deployment, or other remote
  action occurred.

This presentation reconciliation changes no dataset, training, calibration,
model selection, formal metric, accepted result, explanation algorithm, API
schema, dependency, or Docker policy. Feature Freeze remains appropriate.

## Interpretation boundary

This is an educational audit of a 2005 historical dataset. It is not a lending
system, financial advice, causal research, or evidence about modern credit-market
fairness. Group metrics are descriptive model-behavior snapshots; small-cell
confidence intervals are suppressed. Faithfulness perturbations are model sanity
checks, not causal proof.
