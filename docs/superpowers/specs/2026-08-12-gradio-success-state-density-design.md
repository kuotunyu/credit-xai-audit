# Gradio Success-State Density Design

## Context

The approved Editorial Audit Console is compact in its empty state, but a real
synthetic LightGBM replay exposes a desktop imbalance: the attribution table
extends the right result column to roughly twice the input column's content
height, leaving a large unused white field below the primary action. The table
is also constrained by the narrow 4-column result rail.

## Decision

Keep the result summary in the 8/4 workspace and move the attribution table to a
full-width result band immediately below it. The attribution band is absent in
the initial, model-unavailable, validation-error, and runtime-error states; it
appears only when the service returns a verified, non-empty attribution frame.

This is preferred over shrinking the existing table because a shorter scroll
box preserves the blank left column and makes evidence harder to scan. A
collapsible panel is rejected because it adds an unnecessary interaction layer.

## Behavior

- The form and result summary retain their existing components, values, copy,
  callbacks, model/explainer validation, and 8/4 desktop relationship.
- A successful replay reveals the same ten attribution rows in one full-width
  table below the workspace.
- Empty and error responses hide the attribution table rather than displaying
  an empty header or reserving vertical space.
- The band stacks naturally at compact breakpoints and must not introduce
  page-level horizontal overflow.
- Formal public evidence remains a separate section sourced from the committed
  summary. Synthetic preview configuration must not be presented as formal
  release evidence.

## Verification

- A Gradio configuration test proves that the attribution component is outside
  the workspace and initially hidden.
- Presenter tests continue to prove success yields ten verified rows and errors
  yield an empty frame.
- Browser checks exercise a real synthetic LightGBM/TreeSHAP replay at 1900px,
  768px, and 390px, confirming the band becomes visible, all rows are present,
  and there is no page-level overflow.
- Ruff, strict Mypy, the full test suite, release verifier, manifest, and package
  build remain green. No accepted metric or model artifact changes.
