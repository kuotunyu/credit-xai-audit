# Gradio Form Ledger Rhythm Design

Date: 2026-08-12

## Problem

The case workspace is mathematically regular but visually disorderly. At a
1,908px viewport, the four tab centers are approximately 349, 547, 744, and
942px while the five visible field centers are approximately 329, 487, 645,
804, and 962px. The four-column navigation and five-column data row therefore
create two incompatible vertical rhythms. Centered labels, centered values,
and five unrelated short underlines amplify the effect into floating islands.

## Options considered

1. **Editorial ledger (selected).** Treat tabs as a compact group index rather
   than a data grid. Treat the active fields as one ledger row with shared top
   and bottom rules, equal cells, internal hairline separators, and left-aligned
   labels and values. This creates one dominant data rhythm without adding
   rounded cards or feature scope.
2. Keep the full-width four-column tabs and add separators. This would make
   both rows more explicit but preserve the conflicting four-versus-five axes.
3. Remove tabs and expose all 23 fields. This would eliminate the navigation
   mismatch but make the first task surface long and cognitively dense.

## Selected layout

- Keep the existing four feature groups, canonical feature order, values,
  callbacks, accessibility semantics, and API behavior.
- On desktop and compact widths, render the tab list as a left-aligned,
  content-sized index rail. It must remain visually distinct from the field
  ledger and must not imply column alignment with the fields below.
- Render visible fields as one equal-width ledger on desktop. Each cell owns a
  consistent inset; internal hairlines separate cells, while one shared top
  and bottom rule replace disconnected input underlines.
- Align field labels and values to the same left inset. Numeric inputs remain
  at least 46px tall and tab targets remain at least 44px tall.
- Preserve the existing responsive behavior: three field columns at compact
  width, two on phones, and a two-column tab index on phones. Wrapped field
  rows retain consistent horizontal and vertical separators.
- Keep the primary action right-aligned on non-phone layouts and full-width on
  phones. Do not add cards, rounded corners, shadows, animation, new copy, new
  controls, or model behavior.

## Verification contract

At desktop width, the tab rail must occupy materially less than the input
plane, visible field cells must have equal widths, and every label/value pair
must share the same left inset. The field row must expose one continuous top
and bottom boundary with internal separators and no per-input bottom border.
At 1,714px, 1,280px, 768px, and 390px, the page must have no horizontal
overflow or browser errors, labels must fit, and visible field columns must be
5/5/3/2 for the basic-data group. A synthetic-bundle interaction must continue
to show the correct model, calibration, explanation method, and attribution
table without changing formal artifacts or financial-decision boundaries.

## Scope boundary

This is a presentation-only correction. It changes no feature set, model,
metric, result artifact, configuration, dependency, API schema, Docker policy,
claim, or product capability.
