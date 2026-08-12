# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary audience is a portfolio reviewer or recruiter encountering the
project from GitHub. They need to understand within seconds that this is a
serious, reproducible Machine Learning / Trustworthy AI project rather than a
generic model demo. A secondary audience is an ML/XAI practitioner who wants to
inspect the workflow and evidence in more detail.

## Product Purpose

Credit XAI Audit presents an educational audit of three models trained on the
historical 2005 UCI credit-default dataset. Success means that a reviewer can
quickly recognize the project's technical depth, then inspect a local historical
model replay without mistaking it for a lending product or financial advice.

## Positioning

The project connects model comparison with calibration, 1,000-replicate
bootstrap uncertainty, model-appropriate SHAP/EBM explanations, explanation
stability, faithfulness checks, and descriptive group metrics. It makes the
claim-to-evidence boundary auditable rather than presenting an unexplained risk
score.

## Operating Context

The public GitHub candidate is CPU-only and excludes raw UCI rows and serialized
model bundles. Its Gradio interface is mounted under the FastAPI service at
`/ui`. Public verified project evidence must remain useful without a local
bundle; case-level probability and explanation results appear only when a
hash-verified local bundle is loaded.

## Capabilities and Constraints

- Preserve logistic, EBM, and LightGBM evidence; do not add models or XAI
  methods for presentation value.
- Treat the data as a historical educational artifact. The interface must never
  imply lending approval, eligibility, recommendation, causal proof, or a
  present-day fairness conclusion.
- Use verified values from committed evidence; do not invent case predictions,
  benchmarks, or claims for an empty state.
- Keep FastAPI, Gradio, CPU-only Docker operation, local-only model loading, and
  the existing request/response boundary.
- The redesign may improve hierarchy, grouping, responsive behavior, copy, and
  presentation, but must not alter accepted metrics or modeling behavior.

## Brand Commitments

- The product name is `Credit XAI Audit`.
- 正體中文 (`zh-TW`) is the primary interface language. Established Machine
  Learning and XAI terminology remains in English where translation would make
  it less precise.
- The tone is confident, factual, and concise. The design should feel considered
  but not decorative or flashy.
- Typography should be visibly larger than the current Gradio defaults, while
  layout should minimize empty space and unnecessary nesting.
- Target a 14px minimum for ordinary interface copy and 12px only for compact
  metadata. Use the available desktop width before reducing text size, and
  avoid oversized vertical padding that pushes the working area below the fold.
- Center short, equal-weight status and KPI content on both axes. Keep
  narrative copy, form labels, and evidence rows left-aligned for scanning.
- Avoid rounded corners unless the shape communicates a genuinely circular
  control or state. Use square geometry, rules, and color fields for hierarchy
  instead of pill badges or rounded cards.

## Evidence on Hand

- `results/derived/summary.json` and the compact evidence under `results/raw/`
  support the published metrics and explanations.
- `assets/` contains six deterministic report figures.
- `README.md`, `README_zh-TW.md`, `MODEL_CARD.md`, `DATA_CARD.md`,
  `FAILURES.md`, and `docs/release/VERIFICATION.md` define the interpretation
  and release boundaries.
- No public model bundle is available and the interface must not disguise that
  absence.

## Product Principles

1. Lead with verifiable evidence, not AI spectacle.
2. Make technical depth legible to a non-specialist before exposing detail.
3. Separate public project evidence from live case-level model output.
4. Prefer one clear information layer over nested cards and empty decoration.
5. Keep every result inside the historical educational-audit boundary.

## Accessibility & Inclusion

Use comfortably large type, strong contrast, visible focus states, semantic
labels, and a responsive layout that remains usable without horizontal page
scrolling. Do not rely on color alone to communicate attribution direction or
model state.
