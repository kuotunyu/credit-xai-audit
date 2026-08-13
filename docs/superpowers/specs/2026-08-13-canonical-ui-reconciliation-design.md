# Canonical UI Reconciliation Design

## Status

The owner approved the direction on 2026-08-13: `credit-xai-audit` remains the
only public release candidate, while later UI work from `3_ML_xAI` is treated as
a donor source and reviewed selectively. This document fixes the exact
integration and archival boundaries before implementation.

## Problem and lineage

`credit-xai-audit` was created as a clean, unrelated-history export from the
audited `3_ML_xAI` source snapshot
`58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`. The export intentionally excluded
the source repository's Git history, local progress material, raw data, model
payloads, environments, and machine-specific state.

Both repositories were subsequently developed:

- Source/donor: `3_ML_xAI` at
  `ef48f5a119a2625448a8d7bd9125f29a2689490a`.
- Canonical/public candidate: `credit-xai-audit` at
  `e9d4e918ca6d295c54136e6ae164df23a83f61bb` before this design commit.

The histories are intentionally unrelated. The source added a recruiter-first
Traditional Chinese UI, theme and presenter modules, responsive layout work,
UI tests, a bilingual README structure, and portability fixes. The canonical
candidate independently added an evidence-first public console, a fail-closed
presenter, public-evidence rendering, release verification, privacy checks,
packaging checks, and a different visual system.

The task is therefore reconciliation, not a Git merge and not a directory
copy.

## Options considered

### 1. Canonical-first selective reconciliation — chosen

Keep the canonical candidate's architecture and publication controls. Review
every source-side change after the audited snapshot, then reimplement only
behavior or presentation that is both better and not already superseded.

This has the smallest publication risk and retains the strongest current UI:
the canonical console already presents verified evidence, an honest no-model
state, bounded language, compact desktop density, and responsive input groups.

### 2. Replace the canonical UI with the source UI — rejected

Copy `app/gradio_ui.py`, `app/ui_presenters.py`, `app/ui_theme.py`, and their
tests wholesale. This would discard the canonical presenter's model/explainer
contract, release-evidence surface, fail-closed rendering, CSS architecture,
and accumulated visual verification. It would also reintroduce duplicated
responsibilities under different module names.

### 3. Merge the canonical candidate back into the source — rejected

This would retain the source repository's reachable history and invalidate the
reason for creating a clean public candidate. Making the source publishable
would require a new history/privacy audit and would provide no product benefit.

## Canonical architecture

The following canonical modules remain authoritative:

- `app/gradio_ui.py`: page structure, Gradio components, event wiring.
- `app/gradio_presenter.py`: validation, sanitization, result rendering, and
  committed-evidence rendering.
- `app/gradio_theme.css`: visual tokens and responsive behavior.
- `src/credit_xai/release/`: public claims, manifest, privacy, and verification.
- `tests/test_gradio.py` and `tests/test_gradio_presenter.py`: UI behavior and
  presentation contracts.

The donor modules are reference material only. They are not copied as parallel
production modules and are not added to the canonical package under their old
names.

## Reconciliation matrix

### Adopt in the canonical implementation

1. Human-readable Traditional Chinese feature labels while retaining each
   original feature code. This improves interview readability without changing
   the service payload.
2. Strict case-index validation. `NaN`, infinity, fractional values, and text
   must fail with user guidance instead of being truncated or wrapped.
3. Distinct sanitized presentation for invalid input, unavailable model, and
   unexpected inference failure. No traceback, local path, exception message,
   or model payload may reach the page.
4. Recruiter-first README opening in both language versions: one-sentence
   thesis, a 30-second capability table, an honest UI image, and direct links to
   methodology, limitations, and verification.
5. The portable configuration/provenance hash correction from source commit
   `ef48f5a`, but only if a semantic diff proves it is not already present in
   the canonical candidate and it passes the canonical portability tests.

### Already covered or stronger in the canonical candidate

- HTML escaping and probability finiteness checks.
- Model-to-explainer matching and `historical_model_replay` output validation.
- Honest model-absent rendering.
- Committed evidence loading that fails closed.
- Responsive four-group input ledger.
- Output-only attribution table and bounded non-causal language.
- Release, privacy, package, Docker, and clean-export gates.

These behaviors must not be replaced by weaker donor equivalents.

### Do not adopt

- The donor's 22 px global type floor and oversized, long-scroll two-column
  console. The canonical layout has better information density while retaining
  readable labels and responsive behavior.
- Risk-band labels such as low, medium, or high. They can be mistaken for a
  lending recommendation and conflict with the historical replay boundary.
- Separate increasing/reducing tables when one direction-labelled attribution
  ledger communicates the same evidence more compactly.
- The donor screenshot. A new image must be captured from the canonical tree so
  visual evidence and shipped code cannot diverge.
- Donor Git history, progress files, notebooks, local artifacts, data, model
  payloads, environments, or machine-specific paths.

## README and screenshot contract

English remains the default `README.md`; `README_zh-TW.md` remains the complete
Traditional Chinese version. Both receive the same recruiter-first opening and
retain every generated evidence block unchanged.

The tracked UI image must be generated from the canonical code at the
integration commit. It must:

- contain no personal data, raw dataset rows, local paths, secrets, or model
  payload;
- show the historical educational boundary without cropping it away;
- use a deterministic public-safe state, with no fabricated prediction;
- be checked at desktop width and remain below the public file-size ceiling;
- have a caption that describes exactly whether the model is absent or a
  disposable synthetic/public test bundle is loaded.

## Repository identity and mistake prevention

The canonical repository receives a public `AGENTS.md` that states only stable
repository policy: this is the canonical public candidate; unrelated-history
source repositories are read-only donors; bulk copying, history merging, and
publication actions are prohibited without a new audit. It must contain no
absolute machine path or private handoff material.

The workspace-level XAI project map, stored outside the public repository,
records the exact local active and archive locations. The donor receives a
large archive marker only after all processes using it have stopped.

After integration and verification:

1. Confirm the donor worktree is clean and record its exact HEAD.
2. Confirm no Codex, Python, terminal, editor, or server process is using the
   donor directory.
3. Move the donor repository into the existing recoverable
   `superseded-20260813` archive; do not delete it.
4. Update `ARCHIVE_MANIFEST.md` and the workspace XAI project map with the
   canonical path, donor archive path, both exact SHAs, and recovery steps.
5. Ensure no active directory named `3_ML_xAI` remains. This makes an accidental
   future session fail visibly instead of silently editing the wrong repository.

If any process still uses the donor directory, archival is deferred. The
canonical integration may complete, but the move must not be forced.

## Data and control flow

1. The Gradio form emits 23 ordered values.
2. The presenter validates integer inputs and maps them to canonical feature
   codes.
3. The existing service performs a local historical model replay.
4. The presenter validates output type, model/explainer pairing,
   probabilities, and attributions.
5. The UI renders a bounded result or one of the sanitized failure states.
6. README claims and public evidence remain backed by committed artifacts and
   the release verifier.

The integration changes presentation and input validation only. It does not
change training, calibration, evaluation, model selection, explanation
algorithms, dataset processing, serving schemas, or committed experimental
results.

## Error handling

- Missing bundle: retain the explicit no-model public state.
- Missing processed test cases: keep manual entry available and explain the
  limitation.
- Invalid case index: do not apply modulo, truncation, or coercion; return a
  Traditional Chinese validation message.
- Invalid feature input: do not call the service.
- Expected serving/schema rejection: return a sanitized invalid-input state.
- Unexpected inference failure: return a distinct temporary-service failure
  state and log only the exception type through the existing logger policy.
- Invalid result payload: fail closed and render no probability or attribution.

## Testing and acceptance

Implementation follows red-green-refactor for each new behavior. Acceptance
requires all of the following from the canonical integration commit:

1. Focused presenter and Gradio tests cover labels, strict case indices, all
   failure states, output hiding, and responsive structure.
2. Existing canonical tests remain green; donor tests are not copied blindly.
3. Ruff check, Ruff format check, strict Mypy, lock verification, package build,
   isolated wheel import, public privacy scan, release verifier, and clean
   committed-export tests pass.
4. Browser verification covers model-absent desktop and mobile states and, when
   a disposable verified bundle is available, one successful analysis without
   changing committed scientific evidence.
5. Screenshots show no horizontal overflow, broken text, console exception,
   fabricated result, or missing usage boundary.
6. The release manifest is regenerated only from the final tracked public tree
   and contains no donor-only or private file.
7. Git author and committer remain
   `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` with no added
   contributor trailer.

No push, remote creation, tag, release, GitHub publication, Hugging Face sync,
or deployment is authorized by this design.
