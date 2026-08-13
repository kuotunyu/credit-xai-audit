# Security policy

## Scope

This is an educational portfolio artifact, not a production service. It has no
authentication, authorization, rate limiting, persistent user store, or
operational monitoring. Do not expose the FastAPI or Gradio demo to untrusted
networks or use it for real decisions.

## Model bundles

Python joblib/pickle payloads can execute code during loading. A SHA-256 stored
beside a bundle detects accidental drift relative to that manifest, but does
not authenticate its publisher. Only load bundles produced locally by the
owner; never mount downloaded or third-party model directories.

## Data and privacy

The public release contains aggregate/derived evidence and selected
attribution rows, but no raw UCI dataset, serialized model, credential, or
private progress/handoff material. The original public dataset is historical
and contains no direct identifier after `ID` is dropped; it must still remain
outside version control.

## Reporting a vulnerability

Use the repository's private security-advisory channel. Do not include real
credentials, private data, or an untrusted pickle in a public issue.
