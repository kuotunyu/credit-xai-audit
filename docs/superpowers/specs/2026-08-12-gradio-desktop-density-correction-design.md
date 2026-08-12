# Gradio Desktop Density Correction Design

**Status:** Approved through owner-authorized autonomous design judgment on 2026-08-12

**Primary target:** `app/gradio_theme.css` and the case-toolbar composition in `app/gradio_ui.py`

**Visual world:** Preserve the shipped Editorial Audit Console: Traditional Chinese first, warm paper field, indigo structure, restrained amber, flat depth, and square geometry.

## 1. Problem and evidence

The 1,900-by-975 desktop screenshot exposes a real scale and density defect rather than a browser issue:

- the thesis reaches the current 60px clamp maximum and dominates the full viewport;
- the scope boundary uses `align-self: stretch`, so a short paragraph inherits the two-line thesis height and creates unused vertical area;
- metadata is commonly 12–13px while the thesis is 60px, producing a discontinuous type scale;
- the case title and case controls occupy separate rows, leaving a large unused horizontal region before the feature tabs;
- KPI, form, and result regions use different density standards, so they read like adjacent subsystems instead of one console.

The layout detector reported no mechanical violation. The defect is therefore a hierarchy and rhythm problem that requires rendered judgment, not a lint-only fix.

## 2. Selected approach

Use a structural rebalance rather than a cosmetic shrink or a full high-density redesign.

- Preserve the persuasive editorial first viewport, but cap the desktop thesis at 48px.
- Raise supporting copy and operational metadata to a coherent 13–16px range.
- Let the scope boundary size to its content instead of stretching to the thesis height.
- Combine the case heading and case-loader controls into one responsive toolbar.
- Tighten KPI and workspace rhythm while keeping all controls at least 44px high.
- Preserve the 8/4 input/result topology, all 23 inputs, every evidence claim, and all interaction behavior.

This option removes unused space without turning the portfolio surface into a dense administration panel.

## 3. Desktop type scale

At widths above 820px:

- thesis: `clamp(2.35rem, 2.7vw, 3rem)`, or approximately 38–48px;
- method line and scope copy: 15–16px;
- section titles: 21–25px;
- ordinary interface copy: 14–15px;
- operational labels and metadata: 13–14px;
- compact disclaimer/footer copy: no smaller than 12.5px;
- KPI values: no larger than approximately 37px.

The thesis remains the primary element, but its maximum is less than four times the compact metadata size. Input values remain larger than field labels without becoming a second headline.

## 4. Spatial model

The primary reading and task path is:

1. historical-audit thesis and scope;
2. four proof-oriented KPIs;
3. one compact case toolbar;
4. grouped integer inputs and the adjacent honest result state;
5. detailed public evidence.

The hero uses a narrower gap and content-sized scope boundary. KPI cells reduce from 82px to approximately 70px minimum height. The input column uses one deliberate rhythm: 4px inside labels, 8px within controls, 12px within the toolbar, and 16px between major regions.

The case toolbar places the section index/title on the left and the case index/load action on the right. The descriptive note follows immediately below. Feature tabs and inputs then begin without an empty intermediate band. At intermediate widths the toolbar wraps as a unit; it must never cause horizontal overflow.

## 5. Component corrections

### Hero

- Preserve the copy and two-column relationship.
- Cap the thesis at 48px and reduce the column gap to at most 48px.
- Change the scope boundary from stretched height to content height and vertically center it.
- Keep the amber rule because it carries the approved interpretation-boundary meaning.

### KPI strip

- Preserve four equal cells and all evidence-derived values.
- Reduce value scale and cell height.
- Increase label size slightly so number and label feel like one unit.

### Case toolbar and feature form

- Introduce an `audit-input-toolbar` row containing the existing heading and existing case controls.
- Preserve the same Gradio components, callback wiring, integer semantics, labels, and button actions.
- Reduce framework column gaps instead of deleting meaningful group separation.
- Keep tabs centered and all inputs at least 44px high.

### Result state

- Reduce the empty-state headline to a maximum around 25px.
- Increase metadata and disclaimer text enough to read comfortably on a wide monitor.
- Preserve em dashes, safe errors, model-matched explanation labels, and the non-decision boundary.

## 6. Responsive behavior

- Above 1080px: heading and case controls share one line when content fits.
- From 821px to 1080px: the case toolbar may wrap, but related controls remain grouped and full labels remain visible.
- At 820px and below: preserve the existing stacked workspace and 2-by-2 KPI grid while using a smaller thesis maximum.
- At 520px and below: controls may stack to one column; no page-level horizontal scrolling is allowed.
- DOM and keyboard order remain heading, case index, load action, note, tabs, feature inputs, primary action, then result.

## 7. Accessibility and truth boundaries

- Keep visible 3px focus outlines.
- Keep interactive targets at least 44px high.
- Do not use color as the sole state indicator.
- Do not alter factual copy, accepted metrics, public evidence, or model behavior.
- Do not add decision, eligibility, approval, rejection, causal, or financial-advice language.
- Do not add external fonts, network assets, animation, shadows, rounded cards, or product features.

## 8. Verification

Implementation is complete only when:

- a focused source test first fails on the old 60px thesis, stretched boundary, separate case rows, and undersized result metadata;
- focused Gradio tests pass after the minimal HTML/CSS correction;
- 1,900-by-975 and compact-width renders show a continuous type scale and no page-level horizontal overflow;
- the first visible feature-input row moves materially upward without hiding the scope, KPIs, or case note;
- the model-absent state remains honest and the synthetic result state remains model/explainer correct;
- Ruff, strict mypy, the full test suite, release verifier, manifest verification, and Git audits pass;
- only UI source/tests, this spec/plan, design documentation, release evidence, and the release manifest change.
