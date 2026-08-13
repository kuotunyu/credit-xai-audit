# Owner publication record

Version 0.1.0 was owner-authorized for public release on 2026-08-13. This
record supersedes the pre-publication checklist while preserving the ongoing
public-boundary responsibilities below.

## Completed for v0.1.0

- Reviewed the bilingual README, model/data cards, security policy, citation,
  limitations, and public artifact boundary.
- Created the owner-controlled public repository at
  <https://github.com/kuotunyu/credit-xai-audit> without unrelated history.
- Recorded the canonical repository URL and release date in `CITATION.cff`.
- Published `main` only from owner-authored commits under
  `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Verified the product-code SHA with GitHub Actions lint, strict Mypy, release
  and package gates, 159 tests, and the CPU-only Docker pipeline:
  <https://github.com/kuotunyu/credit-xai-audit/actions/runs/31681831572>.
- Enabled Dependabot alerts/security updates, secret scanning, push protection,
  and private vulnerability reporting. All 29 alerts found in the initial
  dependency graph were fixed by the published Gradio 6 lock refresh; none was
  dismissed.
- Added the approved repository description and ten capability topics.
- Protected `main` with required `lint`, `test`, and `docker` checks, disabled
  force pushes and deletion, and published the annotated `v0.1.0` tag and
  GitHub Release from the final verified commit.

## Ongoing owner responsibilities

- Keep raw UCI rows, archives, serialized bundles, credentials, and runtime
  request/response data outside the public repository.
- Treat the API and Gradio UI as a localhost historical replay demonstration,
  not as a lending service or public decision endpoint.
- Reopen Feature Freeze only for a real bug, security/dependency update,
  incorrect public claim, or an explicitly approved release-maintenance task.
- Require fresh release/privacy gates and exact-SHA CI before any future tag.
