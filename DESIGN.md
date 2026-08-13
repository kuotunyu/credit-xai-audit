---
name: Credit XAI Audit
description: A restrained editorial research console for inspecting a historical Trustworthy AI audit.
colors:
  field: "#F6F3EC"
  structure: "#202D65"
  action: "#283B86"
  amber: "#C88725"
  amber-light: "#E4AD4F"
  result: "#F0F1F6"
  text: "#202838"
  muted: "#606777"
  rule: "#BFC1C8"
  rule-warm: "#C8C7C2"
  white: "#FFFDF8"
typography:
  display: 'system-ui, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif / clamp(2.25rem, 2.35vw, 2.5rem) / 720 / 1.08 / -0.035em'
  body: 'system-ui, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif / 17px / 400 / 1.5'
  label: 'system-ui, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif / 15.5px / 650 / 1.35'
spacing:
  tight: 4px
  field: 7px
  section: 16px
radius:
  square: 0px
primary-button:
  background: "#283B86"
  foreground: "#FFFDF8"
  focus: "3px solid #C88725"
  radius: 0px
---

# Overview

Creative North Star: `The Editorial Audit Console`.

Credit XAI Audit presents verified Machine Learning and Trustworthy AI evidence as a compact editorial research console. A warm reading field, deep-indigo structure, restrained amber state accents, large Traditional Chinese thesis copy, and dense evidence rows make the interface feel like a serious technical publication rather than a generic risk dashboard. The product remains an educational replay of a historical 2005 dataset, never a lending system or financial decision tool.

# Colors

Use the palette in an approximate 80/15/5 distribution: warm field for reading, indigo for structure and action, and amber only for state, focus, or a deliberate boundary. The cool result field separates model output without creating a detached card. Primary and muted text remain dark enough for sustained reading. Color never carries status alone; every status also has a text label.

# Typography

Use the local system stack only: `system-ui`, `Noto Sans TC`, `Microsoft JhengHei`, `PingFang TC`, then `sans-serif`. The interface is Traditional Chinese first; retain established technical terms such as Logistic, EBM, LightGBM, Calibration, Bootstrap, SHAP, Faithfulness, and Stability in English. The thesis uses a restrained 36–40px desktop range, a 32–36px compact range, and a 30–33px phone range so it leads without overwhelming the audit controls. Ordinary copy is 17px, supporting copy is 16px, field labels are 15.5px, and compact metadata does not fall below 15px. Input values remain visibly larger than their labels at 19px.

# Layout

The desktop container is fluid up to 1600px wide, allowing a 1908px portfolio viewport to use the available stage without becoming edge-to-edge. The first viewport follows a 12-column editorial composition: thesis and content-sized scope boundary, four equal unboxed KPI pairs, then an 8/4 input-to-result workspace that keeps the case task dominant. The input plane is one complete audit worksheet: a compact heading and case loader share the toolbar; all four canonical feature groups remain visible as open sections; and every section uses the same six-column mother grid. `LIMIT_BAL` spans the first two columns while the remaining first-group fields occupy one column each, so field edges, group headings, toolbar content, and footer content share one vertical rhythm. Field labels and values are left-aligned over quiet input underlines, with no side rail or vertical cell separators. The case note and primary action share one immediate footer instead of floating below the fields. The cool result plane follows its useful content height rather than stretching to match the form. Inside it, calibrated probability and model metadata share one content-driven facts row on non-phone layouts; below 520px they stack in source order. Successful attributions occupy a conditional full-width evidence band below the workspace; empty and error states reserve no table space. At the 820px compact breakpoint, columns stack in source order and the six-column mother grid resolves into three equal visual columns; below 520px it resolves into two equal visual columns without page-level horizontal scrolling. The primary action is compact and right-aligned on wider screens, then full-width only on narrow phones. Center only short, equal-weight content such as status labels, KPI pairs, compact controls, and the primary action. Keep thesis copy, explanatory prose, group and form labels, field values, model metadata, attributions, and evidence rows left-aligned.

# Elevation & Depth

Depth is flat. Create hierarchy with typography, aligned columns, one-pixel transition rules, and a single cool tonal result field. Lines mark transitions; they do not enclose every item. Do not use shadows, floating panels, blur, glass effects, decorative gradients, or repeated container chrome.

# Shapes

When a control or data structure needs an edge, square corners (`0px`) are normative. Most status labels, KPIs, group headings, numeric fields, and content regions remain unboxed; use section rules for grouping and one quiet underline for each editable value instead of complete rectangles or cell grids. Do not introduce decorative rounded cards or pill badges. Circular geometry is reserved for controls whose semantics genuinely require it; this console currently has none.

# Components

- Masthead: full-width deep-indigo structure with a product lockup and three compact inline status labels.
- Thesis boundary: large Traditional Chinese statement paired with a concise historical-use limitation; the amber rule is a section boundary, not a card accent.
- KPI strip: four equal, unboxed number-and-label pairs backed by committed public evidence.
- Case workspace: one compact toolbar followed by four always-visible open form sections containing all 23 integer-only inputs in canonical model order, then an immediate case-context/action footer.
- Result field: the only major cool-toned content surface, reserved for empty, loading, success, and safe error states; probability and model metadata form a responsive facts band, successful content must come from the loaded bundle, and its verified attributions appear in the full-width band below.
- Evidence rows: compact left-aligned model/explainer mappings and verification checks sourced from committed public artifacts.

# Input and state contract

Every model input displays a readable Traditional Chinese name as the primary
label and retains its canonical feature code as secondary component information.
This improves first-pass comprehension while preserving an exact bridge to the
23-field API and model schema. The code remains visible; it is never replaced by
an inferred business meaning. The interface does not assign low, medium, or high
risk bands.

Case indices are finite, integer, and bounded by the processed-case table. The
presenter does not truncate decimals, wrap out-of-range values, or expose raw
exceptions. Missing bundles, invalid input or expected schema rejection, and
unexpected inference/result failures are separate states. All fail closed, hide
probabilities and attributions, and preserve the same historical non-decision
boundary.

# Do's and Don'ts

Do keep Traditional Chinese primary, use original technical terms, preserve visible focus, maintain stable loading and error geometry, and trace every public claim to committed evidence. Do use rules to mark section transitions rather than to build containers. Do center only short, equal-weight content. Do preserve the historical educational-audit, privacy, CPU-only, and non-decision boundaries.

Don't use rounded dashboard cards, pills, repeated rectangles, full-width desktop actions, fabricated numbers, decision language, shadows, decorative animation, or network-loaded visual assets. Don't imply causal proof, current-market fairness, lending eligibility, approval, rejection, or financial advice. Don't let runtime requests, responses, bundles, or caches write into the public repository.
