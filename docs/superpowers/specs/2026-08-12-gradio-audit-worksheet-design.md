# Gradio Audit Worksheet Design

Date: 2026-08-12
Status: Approved through the owner's standing authorization to make UI/UX
decisions autonomously and the explicit instruction to rebuild the marked case
input area.

## Problem

The current case-input plane is not failing because of one font size or one
margin. It is split into four unrelated horizontal bands: heading, case loader,
group tabs, and active fields, followed by a detached action. At a 1,280px
viewport the controls consume about 90px of height, the tab list occupies only
79% of the form width, and the gap between the form and primary action is about
55px. The result is a large, irregular composition with hidden fields and
unused space even though the product has 23 useful inputs.

## Options considered

1. **Complete audit worksheet (selected).** Expose all 23 fields in four
   visible, ordered groups. Give each group one label rail and one continuous
   field ledger. This replaces navigation and empty bands with useful content,
   keeps all inputs scannable, and makes the plane read like one professional
   review instrument.
2. Vertical group rail with one active group. This would make navigation more
   orderly but would still hide data, create variable empty space, and require
   users to move between groups before auditing one case.
3. Four accordions. This would shorten the initial page but add boxes,
   disclosure controls, and another hierarchy that conflicts with the approved
   square, low-chrome editorial language.

## Selected structure

- Keep the existing global header, hero, evidence statistics, two-plane
  workspace, result plane, palette, callbacks, feature order, and model
  behavior.
- Replace the left plane with one complete worksheet:
  - a compact toolbar containing the case-input heading and local case loader;
  - four visible feature groups in canonical order: `基本資料`, `還款狀態`,
    `帳單金額`, and `繳款金額`;
  - one group label rail per row with ordinal, Traditional Chinese name, and
    field count;
  - one equal-track field ledger per group with a shared horizontal boundary
    and only necessary internal hairlines;
  - one footer containing case status/context on the left and the primary
    `執行審計` action on the right.
- Remove tabs completely. No fields are hidden and no tab state is introduced.
- Keep the established labels for the 23 source features because they are the
  dataset's technical schema. Supporting copy remains Traditional Chinese.
- Preserve source and focus order: group order and field order in the DOM must
  match visual reading order and the existing callback input order.

## Geometry and visual rules

- The desktop group row uses a fixed editorial label rail and a flexible field
  ledger. Five- and six-field groups use five and six equal tracks,
  respectively.
- The four group rows touch through shared rules; they are not cards. Do not add
  rounded corners, shadows, gradients, pills, decorative boxes, or floating
  underlines.
- Field labels and numeric values align to the same inset. Each interactive
  control remains at least 44px tall.
- The toolbar must stay compact and vertically centered. The case loader reads
  as one action cluster, not a second content band.
- The footer follows the final group without an artificial spacer. The primary
  action is a stable compact width on desktop and full width on phones.
- At 820px and below, field ledgers use three columns. At 520px and below, the
  group heading becomes a horizontal strip, fields use two columns, and the
  footer/action stack.
- The input plane is content-driven: useful controls fill its height. At
  desktop widths the blank tail after the primary action should not exceed
  12px.

## Verification contract

At 1,908px and 1,280px, the page must show all four groups and all 23 controls
without tabs, positive horizontal overflow, clipped labels, or detached action
bands. Every row's fields must have equal widths within one pixel. The group
ledger must use 5/6/6/6 tracks and a single consistent label rail.

At 768px and 390px, groups must use 3 and 2 field columns, respectively;
source/focus order must remain canonical, touch targets must be at least 44px,
and the page must have no positive horizontal overflow or browser errors.

The existing model-absent preview and isolated synthetic-bundle interaction
must still work. The success state must report the bundle's matching model,
calibration, explanation method, and attributions without changing any formal
metric, committed artifact, API schema, or financial-decision boundary.

## Scope boundary

This is a structural presentation correction to the Gradio case-input plane.
It adds no model, XAI method, UI feature, dataset, metric, dependency, remote
action, deployment, or real lending capability.
