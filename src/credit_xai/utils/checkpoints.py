"""Append-only JSONL checkpointing with deterministic resume.

Layout per checkpointed step::

    <dir>/<name>.jsonl       one JSON record per completed iteration ("iter" key)
    <dir>/<name>.meta.json   {n_iterations, config_hash, status: running|complete}

Rules enforced here (tested in tests/test_checkpoints.py):
- Resuming under a different config_hash is a hard error — a changed config
  invalidates partial results.
- Partial results without --resume fail fast; --force wipes and restarts.
- A truncated final JSONL line (crash mid-write) is tolerated and re-run.
- Aggregation must only accept stores whose meta status is "complete".
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from credit_xai.utils.io import atomic_write_json, ensure_dir, read_json

logger = logging.getLogger(__name__)


class CheckpointError(RuntimeError):
    """Raised on any inconsistent checkpoint state."""


class JsonlCheckpoint:
    def __init__(self, directory: str | Path, name: str, n_iterations: int, config_hash: str):
        self.directory = Path(directory)
        self.name = name
        self.n_iterations = n_iterations
        self.config_hash = config_hash
        self.jsonl_path = self.directory / f"{name}.jsonl"
        self.meta_path = self.directory / f"{name}.meta.json"
        self._fh: Any = None

    # -- lifecycle -----------------------------------------------------------
    def begin(self, resume: bool = False, force: bool = False) -> set[int]:
        """Validate state and return the set of already-completed iteration indices."""
        ensure_dir(self.directory)
        if force:
            self._wipe()
        if self.meta_path.exists():
            meta = read_json(self.meta_path)
            if meta.get("config_hash") != self.config_hash:
                raise CheckpointError(
                    f"{self.meta_path}: existing checkpoint was produced under a different "
                    f"config (hash {meta.get('config_hash', '?')[:12]}... != "
                    f"{self.config_hash[:12]}...). Use --force to discard it."
                )
            if int(meta.get("n_iterations", -1)) != self.n_iterations:
                raise CheckpointError(
                    f"{self.meta_path}: n_iterations changed "
                    f"({meta.get('n_iterations')} != {self.n_iterations}). Use --force."
                )
            done = self.completed_indices()
            if meta.get("status") == "complete":
                logger.info("%s: already complete (%d iterations)", self.name, len(done))
                return done
            if not resume:
                raise CheckpointError(
                    f"partial results exist for step '{self.name}' in {self.directory}. "
                    "Pass --resume to continue or --force to discard and restart."
                )
            logger.info(
                "%s: resuming, %d/%d iterations done", self.name, len(done), self.n_iterations
            )
            return done
        atomic_write_json(
            self.meta_path,
            {
                "n_iterations": self.n_iterations,
                "config_hash": self.config_hash,
                "status": "running",
            },
        )
        return set()

    def append(self, record: dict[str, Any]) -> None:
        if "iter" not in record:
            raise CheckpointError("checkpoint records must carry an 'iter' key")
        if self._fh is None:
            self._fh = self.jsonl_path.open("a", encoding="utf-8", newline="\n")
        self._fh.write(json.dumps(record, sort_keys=True, default=str) + "\n")
        self._fh.flush()

    def sync(self) -> None:
        """fsync the JSONL file — called every checkpoint_every iterations."""
        if self._fh is not None:
            os.fsync(self._fh.fileno())

    def finish(self) -> None:
        """Close the writer and mark the store complete (only if all iterations exist)."""
        self.close()
        done = self.completed_indices()
        missing = set(range(self.n_iterations)) - done
        if missing:
            raise CheckpointError(
                f"cannot mark '{self.name}' complete: {len(missing)} iterations missing "
                f"(e.g. {sorted(missing)[:5]})"
            )
        atomic_write_json(
            self.meta_path,
            {
                "n_iterations": self.n_iterations,
                "config_hash": self.config_hash,
                "status": "complete",
            },
        )

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None

    # -- reading -------------------------------------------------------------
    def records(self) -> list[dict[str, Any]]:
        """All valid records; tolerates a truncated final line."""
        if not self.jsonl_path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.jsonl_path.open("r", encoding="utf-8") as fh:
            lines = fh.readlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                if i == len(lines) - 1:
                    logger.warning(
                        "%s: dropping truncated final line (crash mid-write)", self.jsonl_path
                    )
                else:
                    raise CheckpointError(
                        f"{self.jsonl_path}: corrupt JSONL at line {i + 1} (not the final line)"
                    ) from None
        return records

    def completed_indices(self) -> set[int]:
        records = self.records()
        try:
            iterations = [int(record["iter"]) for record in records]
        except (KeyError, TypeError, ValueError) as exc:
            raise CheckpointError(
                f"{self.jsonl_path}: every record must contain an integer iteration id"
            ) from exc
        if len(iterations) != len(set(iterations)):
            raise CheckpointError(f"{self.jsonl_path}: duplicate iteration ids")
        outside = sorted(i for i in iterations if i < 0 or i >= self.n_iterations)
        if outside:
            raise CheckpointError(
                f"{self.jsonl_path}: iteration ids outside 0..{self.n_iterations - 1}: "
                f"{outside[:5]}"
            )
        return set(iterations)

    def is_complete(self) -> bool:
        if not self.meta_path.exists():
            return False
        return bool(read_json(self.meta_path).get("status") == "complete")

    # -- internals -----------------------------------------------------------
    def _wipe(self) -> None:
        self.close()
        for p in (self.jsonl_path, self.meta_path):
            if p.exists():
                logger.info("discarding %s (--force)", p)
                p.unlink()


def require_complete(directory: str | Path, name: str) -> list[dict[str, Any]]:
    """Aggregation entry point: load records only when the store is complete."""
    meta_path = Path(directory) / f"{name}.meta.json"
    if not meta_path.exists():
        raise CheckpointError(f"missing checkpoint meta: {meta_path}")
    meta = read_json(meta_path)
    if meta.get("status") != "complete":
        raise CheckpointError(
            f"checkpoint '{name}' in {directory} has status "
            f"{meta.get('status')!r}; refusing to aggregate partial results"
        )
    store = JsonlCheckpoint(directory, name, int(meta["n_iterations"]), str(meta["config_hash"]))
    records = store.records()
    completed = store.completed_indices()
    expected = set(range(store.n_iterations))
    if completed != expected or len(records) != store.n_iterations:
        raise CheckpointError(
            f"checkpoint '{name}' in {directory} must contain exactly "
            f"{store.n_iterations} unique iterations"
        )
    return records
