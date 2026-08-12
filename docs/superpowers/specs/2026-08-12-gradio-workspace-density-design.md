# Gradio Workspace Density Design

## Decision status

Approved through the owner's standing instruction to make visual decisions autonomously and continue without approval interruptions. The request targets the unused area below the active feature form in the desktop workspace.

## Measured problem

At a 1,734 by 984 browser viewport, the input and result columns are both 509px tall. The input content ends 113px above the shared workspace bottom, even though its internal gaps are already only 7–10px. The extra height is imposed by the result column, not by input padding. The result shell uses 481px because probability and four metadata rows are stacked sequentially above a 121px interpretation boundary.

## Considered approaches

1. **Compact result facts band — selected.** Place calibrated probability and the four metadata rows side by side inside the result plane, remove the empty-state body's reserved second line, and retain the interpretation boundary below. This removes the height that creates the left-side void without inventing content.
2. **Vertically distribute the input controls.** Moving the button to the bottom and centering fields would relocate the same empty space rather than remove it.
3. **Add helper content.** A new hint, checklist, or card would fill pixels but add an unnecessary layer and repeat information already present.

## Spatial thesis

The task path remains heading and case selection, case note, feature group, values, then audit action. The result plane supports that path with one compact facts band: calibrated probability leads on the left, model metadata scans on the right, and the educational boundary closes the region. The input form stays unboxed and left-aligned; only short values and actions remain centered.

On wide and intermediate layouts, the result facts band uses two internal columns. At 520px and below it returns to source-order stacking, preserving DOM and focus order. No touch target becomes smaller than 44px, no page-level horizontal scrolling is introduced, and the result plane remains the only major tonal region.

## Functional and safety boundaries

- No new copy, control, model, metric, API field, XAI method, or product feature.
- Preserve the full Traditional Chinese and English historical educational-audit boundary.
- Preserve model-absent em dashes and synthetic success values without fabricated public output.
- Keep square corners, current colors and typography, local assets, and CPU-only verification.
- Do not change accepted artifacts, download UCI data, or write runtime data into committed paths.

## Acceptance criteria

- The 1,734px model-absent workspace has no more than 32px below the primary action, reduced from 113px.
- Input and result columns differ by no more than 4px on desktop and remain free of horizontal overflow.
- Probability and metadata share one desktop facts row; the 390px layout stacks them in source order.
- The model-absent state contains no fabricated percentage.
- The synthetic state displays LightGBM, `isotonic`, TreeSHAP, and attributions without decision language.
- Focused tests, Ruff, strict Mypy, the full suite, release verifier, package build, archive audit, and current-image Docker smoke pass before Feature Freeze is renewed.
