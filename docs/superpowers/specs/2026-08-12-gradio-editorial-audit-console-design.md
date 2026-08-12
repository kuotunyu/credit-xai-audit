# Gradio Editorial Audit Console Design

**Status:** Approved by the owner on 2026-08-12

**Primary target:** `app/gradio_ui.py`

**Approved concept:** Editorial Audit Console, prototype V7

## 1. Job and audience

The first audience is a portfolio reviewer or recruiter arriving from GitHub.
Within five seconds they should understand that Credit XAI Audit is a serious,
reproducible Machine Learning / Trustworthy AI project rather than a generic
risk-score demo. After that persuasive opening, the surface becomes an
operational audit console for a local historical model replay.

The secondary audience is an ML/XAI practitioner who wants to confirm the model
set, calibration boundary, Bootstrap evidence, explanation mapping, stability,
faithfulness, and group-metric safeguards.

## 2. Outcome and proof

The page must make three facts legible without a serialized model bundle:

1. the project compares Logistic, EBM, and LightGBM;
2. its public evidence includes validation-only Calibration, 1,000-replicate
   Bootstrap uncertainty, model-matched explanations, stability,
   faithfulness, and descriptive group metrics;
3. it is a historical 2005 educational audit, not a lending system, financial
   advice, causal research, or evidence about current-market fairness.

When a hash-verified local bundle is available, a visitor can enter or load one
historical case and receive calibrated and uncalibrated probabilities plus the
bundle's actual explanation method and top attributions. When no bundle is
available, the result fields show em dashes and an honest explanation; they
never contain illustrative predictions.

## 3. Selected direction

The surface is a compact editorial research console: a warm reading field,
deep indigo structural bands, and restrained amber state accents. It rejects
the generic rounded-card dashboard. Hierarchy comes from scale, rules, aligned
columns, and full-width color fields.

The memorable first viewport is a 12-column composition:

- a large Traditional Chinese thesis and interpretation boundary;
- one centered evidence strip;
- a wide grouped input workspace on the left;
- an honest model/result state on the right.

The primary action is `執行審計`. It appears inside the input grid rather than
as a detached call-to-action. Public evidence continues below the workspace so
the clone-without-model state still demonstrates the project's depth.

## 4. Information architecture

### 4.1 Header

- Product name: `Credit XAI Audit`.
- Descriptor: `Trustworthy AI 作品集`.
- Three equal status cells: `僅使用 CPU`, `可重現`, `功能凍結`.
- Status cells are square, equal-height, and centered on both axes.

### 4.2 Thesis and boundary

- Eyebrow: `2005 歷史資料教育審計`.
- Headline: `不只呈現模型預測，更檢驗解釋是否可信。`
- Model and audit terms remain in English where precision benefits:
  `Logistic`, `EBM`, `LightGBM`, `Calibration`, `Bootstrap`, `SHAP`,
  `Faithfulness`, and `Stability`.
- The adjacent boundary states that the page is only for historical replay and
  portfolio demonstration, and not for lending decisions, financial advice, or
  causal inference.

### 4.3 Evidence strip

Four equal-width cells use centered number/label pairs:

- `3` / `比較模型`;
- `1,000` / `Bootstrap 重抽樣`;
- `3` / `模型對應解釋方法`;
- `110+` / `測試通過`.

The first three values are derived or validated from committed
`results/derived/summary.json`. `110+` is a conservative verified release
baseline, not an exact live count; a test must prove the collected suite remains
at or above that bound. The UI must not copy model-performance numbers into
source code.

### 4.4 Case input

The existing 23 features are preserved and divided by the committed feature
constants:

- `基本資料`: `LIMIT_BAL`, `AGE`, `SEX`, `EDUCATION`, `MARRIAGE`;
- `還款狀態`: `PAY_0`, `PAY_2` through `PAY_6`;
- `帳單金額`: `BILL_AMT1` through `BILL_AMT6`;
- `繳款金額`: `PAY_AMT1` through `PAY_AMT6`.

Each group is a Gradio tab. Short labels and numeric values share one centered
axis inside equal-width fields. Values remain integer inputs and are assembled
into the same `FEATURES`-ordered mapping used by `PredictionService`; the
redesign does not change validation or model input semantics.

`案例編號` and `載入測試案例` remain available when processed test data
exists. Loading a case populates all 23 controls and reports the recorded
historical outcome without turning it into a recommendation. With no processed
dataset, the controls remain usable and the load action returns a concise
Traditional Chinese availability message.

### 4.5 Model replay result

The right column always exposes a clear state:

- **No bundle:** `尚未載入`; probability and model metadata display `—`; copy
  explains that the public repository intentionally excludes model bundles.
- **Loading:** the primary action is disabled and reports progress without
  moving the page layout.
- **Success:** title changes to `歷史模型重播結果`; calibrated probability is
  primary, uncalibrated probability is secondary; model, Calibration method,
  explainer, and top attributions come directly from the service response.
- **Invalid input:** an inline Traditional Chinese message identifies the
  input problem; no partial result remains visible.
- **Bundle error:** state remains available and honest; raw filesystem paths or
  sensitive exception detail are not rendered.

Every successful result repeats the historical educational-audit boundary.
Faithfulness or attribution output must never be described as causal proof.

### 4.6 Public verification evidence

Below the workspace, a full-width evidence section contains:

- a compact table mapping each model to validation-only Calibration selection
  and its correct explanation method (`Linear SHAP`, `EBM Native`,
  `TreeSHAP`);
- a checklist for 1,000-replicate stratified Bootstrap CI, explanation
  stability, faithfulness perturbation, group-metric small-cell suppression,
  and CPU-only Docker synthetic smoke;
- links or plain references to `README`, `MODEL_CARD`, `DATA_CARD`, and
  `VERIFICATION`.

The section reads from committed public evidence. If `summary.json` is absent,
malformed, or inconsistent, it fails closed to `公開證據暫時無法載入` rather
than displaying default numbers. It does not invoke training, download data, or
write into the repository.

## 5. Visual system

### Color

Use a restrained 80/15/5 distribution:

- warm reading field: `#F6F3EC`;
- deep indigo structure: `#202D65` and action `#283B86`;
- low-saturation amber state accent: `#C88725` / `#E4AD4F`;
- result field: `#F0F1F6`;
- primary text: `#202838`;
- secondary text: `#606777`;
- rules: `#BFC1C8` and `#C8C7C2`.

Color never carries state alone: every amber or indigo state also has text.

### Geometry

- No decorative rounded cards, pill badges, or rounded buttons.
- Components use square corners, one-pixel rules, and occasional three- or
  four-pixel structural accents.
- Circular geometry is reserved for controls whose semantics are genuinely
  circular; none is required in this surface.
- Avoid nested card shells. The input/result workspace is one continuous field.

### Typography and density

- Stack: system UI, `Noto Sans TC`, `Microsoft JhengHei`, sans-serif.
- Main headline: approximately 31–36 px desktop.
- Section titles: 19–22 px.
- Ordinary copy: minimum 14 px.
- Compact metadata: minimum 12 px.
- Input values: 15–17 px.
- Desktop content width: approximately 1440 px maximum.
- Reduce the current Gradio vertical padding by roughly 15–20% while keeping
  distinct reading groups.

### Alignment

Center both axes for short, equal-weight content: header status cells, KPI
number/label pairs, tab labels, compact case controls, short numeric values, and
the primary action. Keep thesis copy, explanatory paragraphs, form groups,
model metadata, attribution output, and evidence rows left-aligned.

## 6. Responsive behavior

- At wide desktop widths, use an 8/4 input-to-result split.
- Below approximately 820 px, stack the header, thesis/boundary, input/result,
  and evidence columns.
- KPI cells become a 2-by-2 grid.
- Feature fields become two columns, then one column when required by the
  Gradio container width.
- The result state follows the input rather than preceding it.
- No page-level horizontal scroll is permitted. Attribution tables may use a
  bounded internal overflow only when columns cannot remain legible.

## 7. Accessibility and interaction

- Maintain strong foreground/background contrast.
- Provide visible keyboard focus on every input, tab, and button.
- Preserve semantic labels for all 23 features; visual centering must not
  remove label associations.
- Do not rely on placeholder text as a label.
- Use textual state changes in addition to color.
- Keep loading, empty, success, and error geometry stable to prevent layout
  shifts.
- Respect reduced-motion preferences; this design requires no decorative
  animation.

## 8. Implementation boundaries

The redesign may change `app/gradio_ui.py`, focused UI tests, and the minimum
documentation/release evidence required by the changed public surface. It may
add small presentation helpers that read committed evidence but may not alter:

- pipeline, split, Calibration, model, or explanation behavior;
- accepted metrics, raw/derived evidence, or figures;
- API request/response schemas;
- CPU-only Docker policy;
- public exclusion of raw UCI data and serialized model bundles;
- privacy, historical-audit, and non-decision boundaries.

No model, XAI method, UI framework, deployment target, remote, tag, release, or
external service is added.

## 9. Verification

Implementation is complete only when the following pass:

- focused TDD for evidence loading, feature grouping, Traditional Chinese
  language, safe empty/error states, and service-response rendering;
- existing FastAPI/Gradio behavioral tests, including prohibited decision
  language checks;
- a collected-test lower-bound assertion for the `110+` claim;
- Ruff format/check and strict mypy;
- full test suite and release verifier;
- desktop and compact-width browser inspection of the mounted `/ui` route;
- model-absent smoke and synthetic-bundle predict/explain smoke;
- privacy check confirming requests, responses, bundles, and runtime caches do
  not write into the public repository;
- final diff/manifest consistency and clean Git status.

## 10. Approved UX flow

1. **看懂定位:** understand the project and its limitations within five
   seconds.
2. **查看證據:** inspect public verification evidence without a bundle.
3. **建立案例:** edit 23 inputs through four compact feature groups.
4. **讀取結果:** distinguish calibrated probability, model metadata, and
   model-matched explanation without decision language.
