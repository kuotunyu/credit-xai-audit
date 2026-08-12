# Gradio Visual Chrome Distillation Design

## Problem

The current Editorial Audit Console uses square geometry correctly but applies
it too broadly. Masthead statuses, four KPI cells, tab navigation, every numeric
field, both actions, the workspace split, result metadata, attribution data, and
release evidence all use visible rectangular boundaries. The accumulated chrome
makes the portfolio read like a spreadsheet instead of an authored audit
publication.

The owner wants fewer rectangles, not rounded rectangles. The historical audit,
Traditional Chinese copy, existing palette, evidence integrity, and square
geometry remain fixed.

## Options considered

1. **Recommended — borderless editorial console.** Remove decorative boxes and
   full-height dividers; use typography, proximity, short rules, tonal fields,
   and underline controls. Preserve one strong masthead plane, one result plane,
   and one solid primary action. This directly addresses the criticism without
   changing product behavior.
2. **Soft rounded dashboard.** Group content into rounded cards and pills. This
   reduces hard geometry but contradicts the owner's explicit dislike of rounded
   corners and would make the portfolio more generic.
3. **Ultra-minimal monochrome document.** Remove almost all color and interface
   structure. This is visually quiet but weakens the recognizable indigo/amber
   audit identity and makes interactive states harder to scan.

Option 1 is selected under the owner's standing instruction to make visual
decisions autonomously and continue without approval interruptions.

## Spatial thesis

The reading path is thesis, evidence scale, case input, result interpretation,
then committed verification. Typography and proximity establish those groups.
Lines mark transitions, not containers. Indigo is reserved for the masthead,
primary action, active navigation, and major section rules; amber marks scope or
runtime state only.

## Component treatment

- **Masthead:** retain the indigo plane, but render the three statuses as one
  inline cluster. Remove boxed cells and use spacing plus a single amber state
  marker.
- **KPI row:** remove cell borders. Keep four typographic number-label pairs on
  one quiet baseline with ample internal breathing room.
- **Workspace:** remove the outer rectangular border and the input/result split
  line. The input side remains on the page field; the result side keeps a subtle
  cool tonal plane as the only major content surface.
- **Case controls:** the case index becomes an underline field. The load action
  becomes a compact text action with a bottom rule instead of an outlined box.
- **Feature navigation:** remove tab boxes and vertical separators. Use a single
  active underline and whitespace between labels.
- **Numeric fields:** replace complete borders with bottom rules. Preserve
  centered integer values, 44px minimum target height, focus visibility, and
  canonical feature order.
- **Primary action:** keep one solid rectangular button because its actionable
  role earns the shape, but constrain it to a compact right-aligned width rather
  than a full-width bar.
- **Result and evidence:** retain horizontal reading rules but remove repeated
  row boxes and table outer borders. Empty metadata stays quiet; successful
  attributions remain full width and conditional.

## Responsive behavior

The existing 820px stack and 520px compact treatments remain. Compact layouts
may wrap statuses and KPI pairs, but must not recreate card grids. Tabs wrap as
text labels, fields remain two-up where space permits, and the primary action
becomes full width only below 520px.

## Verification

- Add one real rendered-style regression contract that counts high-chrome
  structural boundaries by semantic region and fails against the boxed design.
- Confirm focus, minimum control height, empty/error behavior, and model/explainer
  mappings remain unchanged.
- Inspect model-absent and synthetic success states at 1900px, 1280px, 768px,
  and 390px. Check visual hierarchy, whitespace, overflow, page errors, and the
  absence of repeated boxed cells.
- Run Ruff, strict Mypy, all tests, release verifier, package build, archive
  privacy audit, identity/trailer audit, and restore the committed-evidence
  model-absent preview before Feature Freeze.
