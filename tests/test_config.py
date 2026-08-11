from __future__ import annotations

import pytest
from pydantic import ValidationError

from credit_xai.config import load_config
from tests.conftest import REPO_ROOT, make_config


@pytest.mark.parametrize("name", ["smoke.yaml", "full.yaml"])
def test_shipped_configs_are_valid(name: str) -> None:
    cfg = load_config(REPO_ROOT / "configs" / name)
    assert cfg.run.seed == 42
    assert cfg.data.source == "uci_static"
    assert abs(cfg.data.split.train + cfg.data.split.val + cfg.data.split.test - 1.0) < 1e-9


def test_config_hash_is_stable_and_sensitive(tmp_path) -> None:
    a = make_config(tmp_path)
    b = make_config(tmp_path)
    assert a.config_hash == b.config_hash
    c = make_config(tmp_path, run={"seed": 8})
    assert c.config_hash != a.config_hash


def test_bad_split_rejected(tmp_path) -> None:
    with pytest.raises(ValidationError, match="sum to 1.0"):
        make_config(tmp_path, data={"split": {"train": 0.5, "val": 0.1, "test": 0.1}})


def test_unknown_keys_rejected(tmp_path) -> None:
    with pytest.raises(ValidationError):
        make_config(tmp_path, run={"name": "x", "typo_key": 1})


def test_missing_file_raises(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nope.yaml")
