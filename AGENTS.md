# Repository identity

This repository is the canonical public candidate for the credit XAI audit
portfolio project.

## Stable rules

- Keep the repository identity, package name, release boundary, and public
  documentation under `credit-xai-audit`.
- Treat the former development repository as a read-only donor. Selectively
  reconcile reviewed improvements; do not bulk-copy its tree.
- Do not merge unrelated Git history, rewrite this repository from the donor,
  or copy donor-only data, models, notebooks, progress files, agent traces, or
  private evidence into this repository.
- Preserve the evidence-first interpretation boundary: this project audits
  model behavior on a historical public dataset and is not a credit decision
  product.
- Before committing a public change, run the relevant tests and the release and
  privacy verifiers. Do not publish, tag, release, or deploy unless the user
  explicitly authorizes it.

