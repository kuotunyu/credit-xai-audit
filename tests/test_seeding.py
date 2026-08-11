from __future__ import annotations

import numpy as np

from credit_xai.utils.seeding import rng, seed_int


def test_same_inputs_same_stream() -> None:
    a = rng(42, "split").integers(0, 1_000_000, size=10)
    b = rng(42, "split").integers(0, 1_000_000, size=10)
    assert np.array_equal(a, b)


def test_step_names_give_independent_streams() -> None:
    a = rng(42, "split").integers(0, 1_000_000, size=10)
    b = rng(42, "eval/bootstrap/logistic").integers(0, 1_000_000, size=10)
    assert not np.array_equal(a, b)


def test_index_varies_stream() -> None:
    a = rng(42, "eval/bootstrap/logistic", 0).integers(0, 1_000_000, size=10)
    b = rng(42, "eval/bootstrap/logistic", 1).integers(0, 1_000_000, size=10)
    assert not np.array_equal(a, b)


def test_seed_int_deterministic_and_in_range() -> None:
    x = seed_int(42, "train/lightgbm")
    assert x == seed_int(42, "train/lightgbm")
    assert 0 <= x < 2**31 - 1
    assert x != seed_int(43, "train/lightgbm")
