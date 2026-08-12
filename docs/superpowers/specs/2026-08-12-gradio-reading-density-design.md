# Gradio Reading Density Design

**Status:** Approved through the owner's standing authorization for autonomous UI judgment on 2026-08-12

## Problem

The Editorial Audit Console is orderly, but its supporting text remains too
small relative to the space assigned to each region. At a 1,714px viewport the
stage stops at 1,440px, most support copy resolves to 14.0–15.04px, and the
evidence section begins 32px below the workspace. At a 1,908px owner viewport,
the same cap uses only about 75% of the available width. The result looks sparse
even though the primary section gaps themselves are not excessive.

The correction must improve information density without returning to the old
crowded form, oversized thesis, disconnected rectangles, or center-aligned
field islands.

## Considered approaches

1. **Increase every font size.** This improves immediate legibility but makes
   the phone page substantially longer and weakens the thesis hierarchy.
2. **Compress spacing only.** This shortens the page but leaves 14–15px support
   text under-scaled inside 44–64px interaction rows.
3. **Balanced stage, type, and rhythm correction.** Widen the desktop stage,
   raise only the support scale, and remove low-information padding. This is
   selected because it addresses both causes while preserving the approved
   visual world.

## Spatial thesis

The primary reading path remains thesis → verified release facts → historical
case replay → public evidence. The stage should use the available desktop width
without feeling edge-to-edge, while phone content remains one continuous source
order. Text should occupy the rows built for it; spacing should separate major
ideas rather than inflate controls.

## Selected design

- Raise the desktop stage cap from 1,440px to 1,600px. Below that cap the layout
  remains fluid and retains its existing one-rem outer insets.
- Keep the thesis at its existing 30–40px responsive range. Increase the
  ordinary body token to 17px, support copy to 16px, labels to 15.5px, metadata
  to 15px, and field values to 19px.
- Preserve the existing Editorial Audit Console palette, square geometry,
  left-aligned form ledger, 7/5 workspace, and responsive source order.
- Reduce low-information vertical padding in the hero, workspace input plane,
  feature ledger, result field, evidence heading, and footer. Do not reduce any
  interactive target below 44px.
- Reduce the workspace-to-evidence transition from 32px to no more than 24px.
  Keep the KPI-to-workspace transition at 12px or less and the input tail below
  10px.
- On compact and phone layouts, retain three- and two-column field ledgers. The
  larger type may wrap naturally, but page-level horizontal overflow, clipped
  labels, or reordered focus flow is not allowed.

## Browser contract

The real rendered UI must satisfy all of the following:

- At 1,908px, the application stage is at least 1,580px wide and no wider than
  1,600px.
- Support, label, metadata, and field-value sizes are at least 16px, 15px,
  15px, and 19px respectively; the phone thesis remains no larger than 33px.
- Desktop workspace-to-evidence space is at most 24px, KPI-to-workspace space
  is at most 12px, and the input tail is at most 10px.
- Desktop fields remain equal within 0.1px and the action remains one active
  ledger track. Phone fields remain two columns and the action remains full
  width.
- Desktop and phone have zero page-level horizontal overflow, zero browser
  exceptions, complete labels, and at least 44px targets.
- Model-absent and synthetic success states preserve truthful copy and the
  existing model/explainer mapping. No model, result, API, or accepted metric is
  changed.

## Scope boundary

This is a CSS-only refinement plus design/release evidence. It does not add a
model, XAI method, UI feature, dependency, network asset, claim, or financial
decision language. It does not modify committed metrics, bundles, or datasets.
