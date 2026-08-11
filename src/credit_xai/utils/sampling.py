"""Shared deterministic sampling helpers."""

from __future__ import annotations

import numpy as np


def stratified_sample(y: np.ndarray, size: int, g: np.random.Generator) -> np.ndarray:
    """Proportional without-replacement class-stratified sample of row positions."""
    size = min(size, len(y))
    positions: list[np.ndarray] = []
    for label in np.unique(y):
        pool = np.flatnonzero(y == label)
        take = max(1, round(size * len(pool) / len(y)))
        positions.append(g.choice(pool, size=min(take, len(pool)), replace=False))
    return np.sort(np.concatenate(positions))[:size]
