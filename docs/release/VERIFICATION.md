# Published release verification

This document records the durable evidence for the public portfolio release.
It is not a chronological development log.

## Release identity

- Repository: <https://github.com/kuotunyu/credit-xai-audit>
- Release: [`v0.1.0`](https://github.com/kuotunyu/credit-xai-audit/releases/tag/v0.1.0)
- Released commit: `ee35e644766673881bca7438b17a4d4791aa943a`
- Exact-SHA CI: [GitHub Actions run 31682107906](https://github.com/kuotunyu/credit-xai-audit/actions/runs/31682107906)
- Source lineage: audited snapshot
  `58cd1ab6190b6c6bf7a1e4a23391dce2213f1e61`; unrelated donor history was not
  merged or copied.

The published tag and Release remain immutable. Later documentation-only main
changes are checked by the same protected-branch workflow.

## Source and test gates

The v0.1.0 publication gate passed:

- Ruff check and format verification.
- Strict Mypy across 65 source files.
- 159 pytest tests on Windows, including Unicode-checkout non-editable install.
- Claim, privacy, manifest, package, API, and archive verification.
- Linux GitHub Actions jobs for `lint`, `test`, and `docker` on the released
  commit.

The current commands are:

```bash
python scripts/setup_environment.py
uv run --no-sync ruff check src app tests
uv run --no-sync ruff format --check src app tests
uv run --no-sync mypy --strict src app
uv run --no-sync pytest
uv run --no-sync python -m credit_xai.release.verify all
uv run --no-sync python -m build
```

## Dependency and security evidence

- Publication upgraded the optional UI stack to Gradio 6.24.0, Pillow 12.3.0,
  and Starlette 1.6.0.
- GitHub reclassified all 29 initially detected dependency alerts as fixed;
  none was dismissed.
- `pip-audit 2.10.1` reported no known vulnerability in the release
  environment; the local package itself is not a PyPI dependency.
- Secret scanning, push protection, Dependabot security updates, and private
  vulnerability reporting are enabled on GitHub.

## Dataset and report provenance

The UCI archive is downloaded outside Git and verified before extraction:

- archive bytes: `5,539,494`
- archive SHA-256:
  `56c885f84457f6680f8438f02bfcdac9579323d8a94465ee5f26e32baa727602`
- canonical content SHA-256:
  `f6c131c25f5ea6716c1439d986550832a5ba1ed218fbbfc3013bb92bb78dcee2`

Two isolated report builds from the committed raw artifacts produced
byte-identical `summary.json`, four Markdown tables, six PNG figures, and both
README evidence blocks. A separate full CPU reproduction preserved dataset and
config hashes, calibration/explainer choices, and all top-10 feature rankings;
the maximum floating-point tail difference was
`2.2151169787321123e-12` after excluding host/time/latency metadata.

Accepted evidence budgets per model are:

| Evidence | Count |
|---|---:|
| Metric bootstrap replicates | 1,000 |
| Group bootstrap replicates | 1,000 |
| Explanation refits | 20 |
| Explanation resamples | 200 |
| Faithfulness instances | 2,000 |
| Explained test rows | 4,500 |

## Container and API evidence

The final Linux/amd64 CPU image used a non-root user and completed a
network-disabled, 2,000-row synthetic pipeline covering data preparation,
Logistic Regression, EBM and LightGBM training, validation-only calibration,
evaluation, matching explainers, and report generation.

Runtime smoke checks confirmed:

- healthy `/health`, `/ui/`, and `/ui/config` endpoints;
- safe HTTP 503 behavior when no local model bundle is mounted;
- successful `/predict` and `/explain` responses with a verified synthetic
  bundle;
- read-only API root filesystem and model mount;
- no GPU device request and no writable host project mount;
- cleanup of test containers, network, and disposable volume.

## Distribution evidence

The v0.1.0 GitHub Release contains:

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `credit_xai_audit-0.1.0-py3-none-any.whl` | 85,454 | `7806045f0f4589f00f2806b0d4f726392e4420f9cdc2929cff99daf3d5a191a8` |
| `credit_xai_audit-0.1.0.tar.gz` | 251,553 | `e45ba6ffe139fd0f5f59c61fb7a66b3e83fd8a30a22dbe29116e9a37f1070479` |

Archive inspection found no raw UCI data, serialized model, credential,
machine path, private note, environment, or Git history. The wheel imports from
an isolated site-packages directory; the sdist retains the intended application
and documentation sources.

## Interpretation boundary

This is an educational audit of one Taiwanese bank's 2005 historical dataset.
It is not a lending system, financial advice, causal research, evidence about
modern credit-market fairness, or a production security claim. Group metrics
are descriptive model-behavior snapshots, small-cell confidence intervals are
suppressed, and explanation faithfulness does not prove real-world causation.
