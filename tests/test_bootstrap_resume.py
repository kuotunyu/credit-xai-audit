from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from credit_xai.metrics.bootstrap import (
    percentile_ci,
    run_checkpointed_bootstrap,
    stratified_indices,
    summarize_records,
)
from credit_xai.utils.seeding import rng

HASH = "e" * 64


def _compute(i: int) -> dict[str, Any]:
    g = rng(123, "test/boot", i)
    return {"value": float(g.random())}


def test_stratified_resample_preserves_class_counts() -> None:
    y = np.array([0] * 80 + [1] * 20)
    g = rng(1, "s")
    idx = stratified_indices(y, g)
    assert len(idx) == 100
    assert int(y[idx].sum()) == 20  # class counts preserved exactly


def test_kill_and_resume_matches_uninterrupted_run(tmp_path) -> None:
    clean_records = run_checkpointed_bootstrap(
        directory=tmp_path / "clean",
        name="boot",
        n_iterations=12,
        checkpoint_every=4,
        config_hash=HASH,
        compute_fn=_compute,
    )

    class Boom(RuntimeError):
        pass

    calls = {"n": 0}

    def crashing(i: int) -> dict[str, Any]:
        calls["n"] += 1
        if calls["n"] == 6:
            raise Boom()
        return _compute(i)

    with pytest.raises(Boom):
        run_checkpointed_bootstrap(
            directory=tmp_path / "resumed",
            name="boot",
            n_iterations=12,
            checkpoint_every=4,
            config_hash=HASH,
            compute_fn=crashing,
        )

    resumed_records = run_checkpointed_bootstrap(
        directory=tmp_path / "resumed",
        name="boot",
        n_iterations=12,
        checkpoint_every=4,
        config_hash=HASH,
        compute_fn=_compute,
        resume=True,
    )
    by_iter_clean = {r["iter"]: r["value"] for r in clean_records}
    by_iter_resumed = {r["iter"]: r["value"] for r in resumed_records}
    assert by_iter_resumed == by_iter_clean  # resume changes nothing


def test_summarize_and_ci() -> None:
    records = [{"iter": i, "m": float(i)} for i in range(101)]
    summary = summarize_records(records, ["m"], ci_level=0.95)
    assert summary["m"]["mean"] == pytest.approx(50.0)
    assert summary["m"]["ci_low"] == pytest.approx(2.5)
    assert summary["m"]["ci_high"] == pytest.approx(97.5)
    low, high = percentile_ci(np.array([1.0, 2.0, 3.0, 4.0]), 0.5)
    assert low < high

    with_nones = [{"iter": 0, "m": None}, {"iter": 1, "m": 2.0}]
    s = summarize_records(with_nones, ["m"], 0.95)
    assert s["m"]["n_boot"] == 1
