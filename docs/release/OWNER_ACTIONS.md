# Owner actions after local candidate verification

No action in this file has been performed by the release-hardening workflow.

## Suggested GitHub metadata

**Description:** Reproducible CPU-only audit of calibration, bootstrap
uncertainty, SHAP/EBM faithfulness, stability, and descriptive group metrics on
the 2005 UCI credit-default dataset.

**Topics:** `machine-learning`, `explainable-ai`, `trustworthy-ai`,
`model-calibration`, `shap`, `interpretability`, `group-metrics`, `fastapi`,
`reproducibility`, `uci-machine-learning`.

## Tomorrow's owner checklist

1. Read `docs/release/VERIFICATION.md`, unresolved limitations, and the final
   Git identity/trailer/privacy audits.
2. Review the bilingual README, cards, security policy, citation, and public
   artifact boundary. Confirm that attribution-row artifacts are acceptable for
   public release under the dataset license.
3. Create an empty owner-controlled GitHub repository. Do not initialize it
   with a README, license, or `.gitignore`.
4. Add the remote and push `main` manually only after the local candidate is
   accepted. The hardening workflow deliberately creates no remote, tag,
   release, pull request, deployment, or model upload.
5. Add the final repository URL to `CITATION.cff`, rerun the manifest and all
   gates, and commit that owner-authored metadata change before publishing.
6. Enable secret scanning, dependency alerts, private vulnerability reporting,
   branch protection, and required CI checks.
7. Keep raw data and joblib bundles local. If demonstrating the API, train a
   local bundle and bind the service to localhost; do not deploy this demo as a
   decision service.
