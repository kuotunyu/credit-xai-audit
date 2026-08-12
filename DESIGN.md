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
  display: 'system-ui, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif / clamp(2rem, 4vw, 3.75rem) / 720 / 1.08 / -0.035em'
  body: 'system-ui, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif / 15px / 400 / 1.5'
  label: 'system-ui, "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif / 12px / 650 / 1.35'
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

Use the local system stack only: `system-ui`, `Noto Sans TC`, `Microsoft JhengHei`, `PingFang TC`, then `sans-serif`. The interface is Traditional Chinese first; retain established technical terms such as Logistic, EBM, LightGBM, Calibration, Bootstrap, SHAP, Faithfulness, and Stability in English. The thesis uses the display token. Ordinary copy must not fall below 14px, and compact metadata must not fall below 12px. Input values should remain visibly larger than their labels.

# Layout

The desktop container is at most 1440px wide. The first viewport follows a 12-column editorial composition: thesis and scope boundary, four equal KPI cells, then an 8/4 input-to-result workspace. At the 820px compact breakpoint, columns stack, KPIs become a 2-by-2 grid, and feature inputs reduce without page-level horizontal scrolling. Center only short, equal-weight content such as status cells, KPI pairs, tab labels, compact controls, short numeric values, and the primary action. Keep thesis copy, explanatory prose, form groups, model metadata, attributions, and evidence rows left-aligned.

# Elevation & Depth

Depth is flat. Create hierarchy with one-pixel rules, tonal fields, aligned columns, type scale, and occasional three-pixel structural boundaries. Do not use shadows, floating panels, blur, glass effects, or decorative gradients.

# Shapes

Square corners (`0px`) are normative for controls, fields, tables, status cells, and content regions. Do not introduce decorative rounded cards or pill badges. Circular geometry is reserved for controls whose semantics genuinely require it; this console currently has none.

# Components

- Masthead: full-width deep-indigo structure with a product lockup and three equal, centered status cells.
- Thesis boundary: large Traditional Chinese statement paired with a concise historical-use limitation; the amber rule is a section boundary, not a card accent.
- KPI strip: four equal square cells with centered number-and-label pairs backed by committed public evidence.
- Case workspace: four feature tabs containing all 23 integer-only inputs in the canonical model order, with compact case selection and one full-width primary action.
- Result field: a stable cool-toned region for empty, loading, success, and safe error states; successful content must come from the loaded bundle.
- Evidence rows: compact left-aligned model/explainer mappings and verification checks sourced from committed public artifacts.

# Do's and Don'ts

Do keep Traditional Chinese primary, use original technical terms, preserve visible focus, maintain stable loading and error geometry, and trace every public claim to committed evidence. Do center only short, equal-weight content. Do preserve the historical educational-audit, privacy, CPU-only, and non-decision boundaries.

Don't use rounded dashboard cards, pills, fabricated numbers, decision language, shadows, decorative animation, or network-loaded visual assets. Don't imply causal proof, current-market fairness, lending eligibility, approval, rejection, or financial advice. Don't let runtime requests, responses, bundles, or caches write into the public repository.
