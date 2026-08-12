# Gradio Typography Rebalance Design

## Decision status

Approved by the owner's standing instruction to make visual decisions autonomously and continue without mid-task questions. The current request specifically identifies oversized title copy, undersized interface copy, and inefficient use of browser space.

## Measured problem

At a 1,656px browser viewport, the shipped page renders the thesis at 44.71px while the most frequent visible text role is 13.12px (40 occurrences). Another 18 visible roles render at 13.44px. Section markers reach 12.16px, the result disclaimer reaches 12.80px, and table headings reach 12.80px. The resulting ratio makes the thesis dominate while controls, labels, evidence, and boundaries recede.

The prior 8/4 workspace also compressed the result copy while leaving the five-field input row visually sparse. This amplified the small-text impression and produced awkward toolbar wrapping at intermediate browser widths.

## Considered approaches

1. **Balanced editorial type system — selected.** Reduce the thesis to a 36–40px desktop range, establish 16px ordinary copy, raise operational labels and metadata to 14–15px, use 18px numeric values, rebalance the workspace to 7/5, and give the case toolbar two stable rows. This fixes the ratio at its source and preserves the approved visual identity.
2. **Enlarge small text only.** This improves legibility but leaves the thesis disproportionately dominant and increases vertical pressure in the result plane.
3. **Shrink the thesis only.** This reduces the most obvious symptom but leaves the majority of the interface below a comfortable operating size.

## Typography system

- Keep the existing local system font stack; do not add a network font or a second family.
- Thesis: `clamp(2.25rem, 2.35vw, 2.5rem)` on desktop; 32–36px on compact screens; 30–33px on narrow phones.
- Product title and section titles: 23–25px.
- Ordinary body and result copy: 16px with 1.5–1.6 line height.
- Controls, tabs, table cells, KPI labels, and form metadata: 14.5–15px.
- Truly compact provenance/footer roles: 13.5–14px, never lower.
- Numeric input values: 18px; primary and secondary actions: 16px.
- KPI numbers: 32–34px; calibrated probability: 32–34px. These remain prominent without competing with the thesis.

## Layout and density

- Preserve the 1,440px maximum container and rebalance the workspace from 8/4 to 7/5 so the result plane wraps less while the input form remains comfortable.
- Place the case heading and metadata on one row, then case selection and loading on a stable second row. Preserve square geometry, unboxed inputs, the single tonal result plane, and responsive stacking behavior.
- Tighten only spacing made excessive by the smaller thesis: hero padding, KPI band height, and the workspace/result gap. Do not compress touch targets below 44px.
- Keep prose left-aligned and short status/KPI/action content centered.

## Functional and safety boundaries

- No copy, model, metric, API, pipeline, XAI method, or decision boundary changes.
- No external font, JavaScript dependency, animation, image, or network request.
- Model-absent and synthetic success states must retain their current semantics.
- The public candidate still excludes model bundles and must not fabricate a probability.

## Verification

- A browser RED contract must fail on the current 1,656px render because the thesis exceeds 42px and multiple named operational roles are below 14px.
- GREEN requires thesis 36–40px, ordinary copy at least 15px, operational labels at least 14px, input values at least 18px, and no page-level overflow at 1,656px, 1,280px, 768px, and 390px.
- Inspect all four widths in one batch, make at most one consolidated visual correction, then confirm once.
- Re-run focused Gradio tests, Ruff, strict Mypy, full tests, release verifier, package build, archive audit, and current-image Docker UI smoke before renewing Feature Freeze.
