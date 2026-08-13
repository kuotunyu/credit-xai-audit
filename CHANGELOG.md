# Changelog

All notable public changes are documented here.

## Unreleased

### Changed

- Made Traditional Chinese the default GitHub README, with a complete English
  version one click away.
- Replaced two oversized architecture diagrams with one accurate end-to-end
  view of data, models, four audit outputs, evidence, serving, and release gates.
- Removed internal agent instructions, design-tool state, implementation plans,
  and owner-only publication notes from the current public tree.
- Condensed release verification and failure notes to durable engineering
  evidence rather than chronological UI iteration logs.
- Updated the deterministic public manifest from `unpublished` to `published`.

No accepted model, metric, dataset artifact, explanation method, API schema, or
non-decision boundary changed.

## 0.1.0 — 2026-08-13

### Added

- A reproducible comparison of Logistic Regression, EBM, and LightGBM under one
  frozen 70/15/15 split and validation-only calibration contract.
- Bootstrap uncertainty, descriptive group metrics, explanation stability, and
  perturbation-faithfulness evidence generated from committed raw artifacts.
- A typed Python package, CLI, FastAPI service, Traditional-Chinese-first Gradio
  audit console, CPU-only Docker deployment, and synthetic smoke pipeline.
- Claim, privacy, manifest, package, portability, API, and container release
  gates enforced by tests and GitHub Actions.
- Model and data cards, citation metadata, security guidance, and an explicit
  public-artifact boundary.

### Security

- Pinned official UCI archive bytes and fail-closed checksum verification.
- Upgraded the optional serving stack to Gradio 6.24.0, Pillow 12.3.0, and
  Starlette 1.6.0; all 29 dependency alerts found during publication were fixed
  rather than dismissed.
- Sanitized missing-model, invalid-input, and inference-failure states without
  fabricated predictions or local exception details.

### Evidence retained

- Three model families, 1,000 stratified metric bootstraps per model, 1,000
  group bootstraps per model, 20 explanation refits, 200 explanation resamples,
  2,000 faithfulness instances per model, full-test attribution artifacts,
  derived tables, and six figures from the accepted CPU run.
