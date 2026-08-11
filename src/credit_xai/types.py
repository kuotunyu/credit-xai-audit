"""Shared static types for NumPy values crossing module boundaries."""

from __future__ import annotations

from typing import Any, TypeAlias

from numpy.typing import NDArray

Array: TypeAlias = NDArray[Any]
