from __future__ import annotations

from pathlib import Path

import pytest

from credit_xai.utils.checkpoints import CheckpointError, JsonlCheckpoint, require_complete

HASH_A = "a" * 64
HASH_B = "b" * 64


def _run_iterations(store: JsonlCheckpoint, indices: list[int]) -> None:
    for i in indices:
        store.append({"iter": i, "value": i * 10})


def test_fresh_run_and_completion(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", n_iterations=5, config_hash=HASH_A)
    assert store.begin() == set()
    _run_iterations(store, list(range(5)))
    store.finish()
    records = require_complete(tmp_path, "boot")
    assert [r["iter"] for r in records] == [0, 1, 2, 3, 4]


def test_partial_without_resume_fails_fast(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    _run_iterations(store, [0, 1])
    store.close()
    store2 = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    with pytest.raises(CheckpointError, match="--resume"):
        store2.begin(resume=False)


def test_resume_returns_completed_and_run_completes(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    _run_iterations(store, [0, 1, 3])
    store.close()

    store2 = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    done = store2.begin(resume=True)
    assert done == {0, 1, 3}
    _run_iterations(store2, [2, 4])
    store2.finish()
    assert store2.is_complete()


def test_truncated_final_line_tolerated(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    _run_iterations(store, [0, 1])
    store.close()
    with store.jsonl_path.open("a", encoding="utf-8") as fh:
        fh.write('{"iter": 2, "value"')  # simulated crash mid-write

    store2 = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    assert store2.begin(resume=True) == {0, 1}


def test_corrupt_middle_line_raises(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    store.append({"iter": 0})
    store.close()
    text = store.jsonl_path.read_text(encoding="utf-8")
    store.jsonl_path.write_text("garbage\n" + text, encoding="utf-8")
    with pytest.raises(CheckpointError, match="corrupt"):
        JsonlCheckpoint(tmp_path, "boot", 5, HASH_A).begin(resume=True)


def test_config_hash_mismatch_rejected(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    _run_iterations(store, [0])
    store.close()
    with pytest.raises(CheckpointError, match="different"):
        JsonlCheckpoint(tmp_path, "boot", 5, HASH_B).begin(resume=True)


def test_force_wipes_partial_state(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    _run_iterations(store, [0, 1])
    store.close()
    store2 = JsonlCheckpoint(tmp_path, "boot", 5, HASH_B)
    assert store2.begin(force=True) == set()


def test_finish_with_missing_iterations_raises(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 5, HASH_A)
    store.begin()
    _run_iterations(store, [0, 1])
    with pytest.raises(CheckpointError, match="missing"):
        store.finish()


def test_require_complete_rejects_running(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 2, HASH_A)
    store.begin()
    _run_iterations(store, [0, 1])
    store.close()  # never marked complete
    with pytest.raises(CheckpointError, match="partial"):
        require_complete(tmp_path, "boot")


def test_finish_rejects_duplicate_iteration_ids(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 2, HASH_A)
    store.begin()
    store.append({"iter": 0})
    store.append({"iter": 0})
    store.append({"iter": 1})

    with pytest.raises(CheckpointError, match="duplicate"):
        store.finish()


def test_finish_rejects_out_of_range_iteration_ids(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 2, HASH_A)
    store.begin()
    store.append({"iter": 0})
    store.append({"iter": 1})
    store.append({"iter": 2})

    with pytest.raises(CheckpointError, match="outside"):
        store.finish()


def test_require_complete_rejects_wrong_record_count(tmp_path: Path) -> None:
    store = JsonlCheckpoint(tmp_path, "boot", 2, HASH_A)
    store.begin()
    store.append({"iter": 0})
    store.close()
    store.meta_path.write_text(
        '{"n_iterations": 2, "config_hash": "' + HASH_A + '", "status": "complete"}\n',
        encoding="utf-8",
    )

    with pytest.raises(CheckpointError, match="exactly 2"):
        require_complete(tmp_path, "boot")
