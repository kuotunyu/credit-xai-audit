"""Deterministic seed derivation.

A single global seed is the only entropy root. Every stochastic component derives
an independent stream from ``(global_seed, step_name, index)`` where ``step_name``
is hashed with blake2s — stable across runs, platforms, and Python processes.
No code anywhere calls ``random.seed`` or ``np.random.seed`` globally.
"""

from __future__ import annotations

import hashlib

import numpy as np


def _step_token(step_name: str) -> int:
    digest = hashlib.blake2s(step_name.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def seed_sequence(global_seed: int, step_name: str, index: int = 0) -> np.random.SeedSequence:
    return np.random.SeedSequence([global_seed, _step_token(step_name), index])


def rng(global_seed: int, step_name: str, index: int = 0) -> np.random.Generator:
    """Independent Generator for a (step, iteration) pair."""
    return np.random.default_rng(seed_sequence(global_seed, step_name, index))


def seed_int(global_seed: int, step_name: str, index: int = 0) -> int:
    """31-bit int suitable for sklearn/lightgbm ``random_state``."""
    state = seed_sequence(global_seed, step_name, index).generate_state(1)[0]
    return int(state % (2**31 - 1))
