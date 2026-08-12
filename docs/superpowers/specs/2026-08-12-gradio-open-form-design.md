# Gradio Open Form Design

Date: 2026-08-12
Status: Approved through the owner's explicit request for a better presentation
and standing authorization to make UI/UX decisions without interrupting the
work for additional choices.

## Diagnosis

The complete worksheet solved hidden fields and empty input space, but its
vertical separators, narrow left label rail, and equal-height cells turn the
case surface into a database table. Twenty-three technical labels compete at
the same visual weight. The cool result plane stretches to the full input
height even when it contains only an empty state, creating an uncomfortable
heavy block beside the dense grid.

The primary task is still simple: adjust one historical case, run one audit,
then inspect a bounded result. The interface should support that path without
making data entry look like a spreadsheet.

## Approaches considered

1. **Four open form sections (selected).** Keep every field visible, move each
   group heading above its fields, remove the label rail and all vertical cell
   borders, and give fields one quiet underline. This retains overview and
   source order while replacing the table metaphor with a conventional form.
2. Progressive disclosure with one expanded group. This would lower initial
   density but reintroduce hidden inputs and navigation friction similar to the
   rejected tabs.
3. Two-column group panels. This would make groups visually obvious but create
   four large rectangles and conflict with the owner's preference against
   card-like chrome.

## Selected composition

- Preserve the masthead, hero, evidence statistics, palette, typography,
  Traditional Chinese language, square geometry, callbacks, feature schema,
  right-side result semantics, and all product boundaries.
- Keep all 23 inputs visible and in canonical source/focus order.
- Render each feature group as an open section:
  - one full-width heading line containing ordinal, Traditional Chinese group
    name, and field count;
  - one five- or six-column field row below the heading;
  - no vertical label rail, no vertical cell separators, and no closed box;
  - field labels and values share a left edge and use one quiet underline;
  - one horizontal rule and a deliberate section gap separate groups.
- Increase the input plane's share of the desktop workspace so six-field rows
  remain readable. The result plane supports rather than dominates.
- Stop stretching the result plane to match the complete form. Empty, error,
  and success results use content height; the existing attribution table stays
  below the workspace only when a verified result exists.
- Keep the case loader integrated with the heading and keep case context plus
  the primary action in one immediate footer.

## Responsive behavior

- Wide and standard desktop: five/six columns, open group headings, input/result
  ratio approximately 8/4.
- At 820px and below: workspace stacks and feature rows use three columns.
- At 520px and below: feature rows use two columns, the case loader stays on one
  compact line where labels fit, and the primary action becomes full width.
- DOM order and keyboard focus order always match visual order.

## Visual contract

- Zero visible vertical separators inside the input plane.
- Zero closed borders, rounded cards, shadows, gradients, pills, or decorative
  panels in the rebuilt area.
- Every feature group has one full-width heading above its fields.
- Field rows use equal tracks within one pixel, with 44px-or-larger controls.
- At 1,908px, 1,280px, 768px, and 390px: all 23 inputs remain visible, labels
  are not clipped, and page-level horizontal overflow is zero.
- The result plane height equals its content rather than the left form height;
  its empty state must not create a large unused cool field.

## Product and evidence boundary

This is a presentation-only refinement. It changes no dataset, model,
calibration, threshold, metric, formal result, explanation method, API schema,
dependency, Docker policy, decision language, or publication state. The public
build remains a historical educational model replay and fails closed without a
local verified bundle.
