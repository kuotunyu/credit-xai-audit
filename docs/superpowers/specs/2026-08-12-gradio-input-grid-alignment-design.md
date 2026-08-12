# Gradio Input Grid Alignment Design

## Goal

Make the case-input workspace read as one ordered instrument panel rather than
several unrelated Gradio rows. Preserve the approved Editorial Audit Console,
copy, behavior, square geometry, result plane, and compact vertical density.

## Root cause

At the verified 1,714px viewport, the 810px input column contains a 127px flex
toolbar. Its full-width heading occupies the first line, the 390px case controls
wrap onto a second line at the right, and the case-status note becomes a third
independent row. The four tab controls occupy only about 337px of the available
width. These separate layout contexts create unrelated horizontal and vertical
baselines even though each component works correctly in isolation.

## Chosen structure

Use one desktop CSS Grid for the direct input-column children. Flatten the
existing toolbar wrapper with `display: contents` so its heading and case
controls participate in the same grid without changing DOM or focus order.

1. The heading and 23-field metadata remain one full-width heading row.
2. The case-status note and case controls share one utility row. The note leads
   at the left; the case index and load action form a fixed-width group at the
   right and align to the same bottom baseline.
3. The real Gradio tablist becomes a four-column grid so every tab owns one
   quarter of the available width and every divider begins and ends together.
4. The feature row keeps equal-width numeric fields. The primary action remains
   compact and aligns with the right edge of the field grid.

No container, card, rounded edge, new copy, or product feature is added.

## Responsive behavior

Above 820px, the utility row uses `minmax(0, 1fr) auto`; below 820px, heading,
case controls, status note, tabs, feature inputs, and action stack in source
order. At 520px and below, the tablist becomes two equal columns and the primary
action becomes full width. Visual order and keyboard order remain consistent.

## Acceptance contract

At 1,714px:

- case status and case controls share the same grid row;
- case controls end on the input-column right edge;
- all four tabs have equal widths and together span the input column;
- the five visible numeric fields remain equal width;
- the primary action ends on the input-column right edge;
- page overflow is zero and the result column retains its verified geometry.

At 1,280px, 768px, and 390px, page overflow remains zero. The compact and phone
layouts stack without visual reordering, clipped labels, or targets below 44px.
Model-absent, loading, error, and synthetic success states keep the same truth
and privacy boundaries.

## Verification

Use a real Playwright geometry contract for RED/GREEN, then inspect the four
responsive widths in one batch. Run the focused Gradio/presenter suite, Ruff,
strict Mypy, the Impeccable layout detector, the full suite, release verifier,
package build, and the CPU-only Docker synthetic/API/UI gates. Temporary
runtime artifacts must remain outside committed paths and be removed.
