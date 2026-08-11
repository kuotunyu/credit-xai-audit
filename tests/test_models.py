from __future__ import annotations

import numpy as np
import pytest

from credit_xai.constants import FEATURES, MODEL_NAMES, TARGET
from credit_xai.data.prepare import load_processed
from credit_xai.models.base import ModelAdapter
from credit_xai.models.persistence import (
    PersistenceError,
    load_model,
    model_dir,
    save_model,
)
from credit_xai.models.registry import get_adapter
from credit_xai.training.train import run as train_run
from credit_xai.utils.io import read_json
from tests.conftest import make_config


def test_registry_knows_all_models(test_config) -> None:
    for name in MODEL_NAMES:
        adapter = get_adapter(name, test_config)
        assert isinstance(adapter, ModelAdapter)
        assert adapter.name == name
    with pytest.raises(ValueError, match="unknown model"):
        get_adapter("nope", test_config)


@pytest.mark.parametrize("model_name", MODEL_NAMES)
def test_train_step_end_to_end(prepared_config, model_name) -> None:
    train_run(prepared_config, model_name)
    meta = read_json(prepared_config.raw_results_dir / model_name / "train_meta.json")
    assert meta["model_name"] == model_name
    assert meta["config_hash"] == prepared_config.config_hash
    val = meta["val_point_metrics_uncalibrated"]
    # synthetic data carries real signal; anything close to random is a wiring bug
    assert val["roc_auc"] > 0.55, val
    assert 0 < val["log_loss"] < 2

    estimator = load_model(prepared_config, model_name)
    adapter = get_adapter(model_name, prepared_config)
    splits = load_processed(prepared_config)
    p = adapter.predict_proba(estimator, splits["val"][FEATURES])
    assert p.shape == (len(splits["val"]),)
    assert np.all((p >= 0) & (p <= 1))


def test_serialization_roundtrip_is_exact(prepared_config) -> None:
    adapter = get_adapter("logistic", prepared_config)
    splits = load_processed(prepared_config)
    X_tr, y_tr = splits["train"][FEATURES], splits["train"][TARGET]
    X_val, y_val = splits["val"][FEATURES], splits["val"][TARGET]
    fitted = adapter.fit(adapter.build(prepared_config), X_tr, y_tr, X_val, y_val)
    before = adapter.predict_proba(fitted, X_val)

    save_model(prepared_config, adapter, fitted)
    loaded = load_model(prepared_config, "logistic")
    after = adapter.predict_proba(loaded, X_val)
    np.testing.assert_array_equal(before, after)


def test_tampered_payload_rejected(prepared_config) -> None:
    train_run(prepared_config, "logistic")
    payload = model_dir(prepared_config, "logistic") / "model.joblib"
    with payload.open("ab") as fh:
        fh.write(b"tamper")
    with pytest.raises(PersistenceError, match="sha256 mismatch"):
        load_model(prepared_config, "logistic")


def test_config_hash_guard_on_load(prepared_config, tmp_path) -> None:
    train_run(prepared_config, "logistic")
    other = make_config(tmp_path, run={"seed": 99})
    with pytest.raises(PersistenceError, match="different config"):
        load_model(other, "logistic")


def test_target_never_in_feature_list() -> None:
    assert TARGET not in FEATURES
    assert len(FEATURES) == 23
