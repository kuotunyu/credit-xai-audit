# syntax=docker/dockerfile:1
# CPU-only, multi-stage, non-root. Contains no dataset, cache, tokens, or secrets.
# Historical 2005 educational audit. Not for lending decisions. Not financial advice.

FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock LICENSE ./
# Hatchling's `readme = "README_en.md"` metadata field only requires the file
# during resolution; a placeholder avoids coupling this expensive layer
# (installs numpy/pandas/sklearn/shap/lightgbm/interpret/gradio, minutes) to
# the real README's content, which changes on every `report` run.
RUN echo "placeholder for dependency resolution; real README copied in the runtime stage" > README_en.md
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --all-extras --no-install-project
# The project's own package is never installed into the venv (no `uv sync
# --no-editable` / src copy here): the venv holds only third-party
# dependencies, so it never needs rebuilding when src/ changes. The runtime
# stage adds our code to PYTHONPATH instead (see below) — `python -m
# credit_xai.cli` resolves the package from there either way.

FROM python:3.11-slim-bookworm AS runtime
# libgomp1: OpenMP runtime required by lightgbm wheels on slim images
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src ./src
COPY app ./app
COPY configs ./configs
COPY manifests ./manifests
COPY MODEL_CARD.md DATA_CARD.md README.md README_en.md LICENSE ./
RUN mkdir -p models results assets tmp data && chown -R appuser:appuser /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    PYTHONUNBUFFERED=1 \
    CREDIT_XAI_CONFIG=configs/smoke.yaml
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status==200 else 1)"
CMD ["python", "-m", "credit_xai.cli", "serve", "--config", "configs/smoke.yaml", "--host", "0.0.0.0", "--port", "8000"]
