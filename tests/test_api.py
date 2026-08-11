from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from credit_xai.calibration.calibrate import run as calibrate_run
from credit_xai.constants import DEMO_SCOPE, DISCLAIMER
from credit_xai.serving.api import _EXAMPLE_FEATURES, create_app
from credit_xai.training.train import run as train_run
from tests.conftest import make_config


@pytest.fixture(scope="module")
def api_client(tmp_path_factory):
    from credit_xai.data.prepare import run as prepare_run

    cfg = make_config(tmp_path_factory.mktemp("api"), serve={"model": "logistic"})
    prepare_run(cfg)
    train_run(cfg, "logistic")
    calibrate_run(cfg, "logistic")
    return TestClient(create_app(cfg))


def test_health(api_client) -> None:
    resp = api_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["disclaimer"] == DISCLAIMER
    assert body["scope"] == DEMO_SCOPE


def test_health_without_model(test_config) -> None:
    client = TestClient(create_app(test_config))
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is False
    resp = client.post("/predict", json={"features": _EXAMPLE_FEATURES})
    assert resp.status_code == 503


def test_predict(api_client) -> None:
    resp = api_client.post("/predict", json={"features": _EXAMPLE_FEATURES})
    assert resp.status_code == 200
    body = resp.json()
    assert 0.0 <= body["probability_calibrated"] <= 1.0
    assert 0.0 <= body["probability_uncalibrated"] <= 1.0
    assert body["disclaimer"] == DISCLAIMER
    assert body["scope"] == DEMO_SCOPE
    assert body["output_type"] == "historical_model_replay"
    assert not {"approval", "eligibility", "decision", "accept", "reject"} & set(body)


def test_predict_rejects_bad_category(api_client) -> None:
    bad = dict(_EXAMPLE_FEATURES, EDUCATION=9)
    resp = api_client.post("/predict", json={"features": bad})
    assert resp.status_code == 422
    assert "EDUCATION" in resp.json()["detail"]


def test_predict_rejects_missing_feature(api_client) -> None:
    partial = {k: v for k, v in _EXAMPLE_FEATURES.items() if k != "AGE"}
    resp = api_client.post("/predict", json={"features": partial})
    assert resp.status_code == 422
    assert "AGE" in resp.json()["detail"]


def test_explain(api_client) -> None:
    resp = api_client.post("/explain", json={"features": _EXAMPLE_FEATURES})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["attributions_link_scale"]) == 23
    assert len(body["top_attributions"]) == 10
    assert body["method"] == "linear_shap"
    assert body["disclaimer"] == DISCLAIMER
    assert body["scope"] == DEMO_SCOPE
    assert body["output_type"] == "historical_model_replay"


def test_model_card(api_client) -> None:
    resp = api_client.get("/model-card")
    assert resp.status_code == 200
    assert "MODEL CARD" in resp.text
    assert DISCLAIMER in resp.text


def test_openapi_declares_historical_demo_scope(api_client) -> None:
    schema = api_client.get("/openapi.json").json()

    assert DEMO_SCOPE in schema["info"]["description"]
