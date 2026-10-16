"""Regression tests for the int64 representability check at the serving input
boundary.

Before the check, `PredictionService.frame_from_features` cast the coerced
Python integers with `.astype(np.int64)`, which is unsafe: an input of 2**63 was
inferred as uint64 and wrapped silently to a negative int64 (so a prediction was
replayed for an input that was never submitted), while 2**64 or -(2**63)-1 were
inferred as object and raised `OverflowError` — not one of the exceptions
`serving.api` converts to a 422, hence a 500 on /predict and /explain.

These tests are offline and model-free: no dataset is prepared, no bundle is
loaded, and no estimator, calibrator or explainer is constructed or invoked. The
service collaborators are faked; the input-validation path
(`frame_from_features`) and the FastAPI app (`create_app`) are the real ones.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from credit_xai.constants import CATEGORICAL_FEATURES, FEATURES, TARGET
from credit_xai.data.schema import SchemaError, build_schema
from credit_xai.serving.service import PredictionService, ServiceError

INT64_MIN = int(np.iinfo(np.int64).min)
INT64_MAX = int(np.iinfo(np.int64).max)

# A valid row: categoricals inside their documented domains, numerics arbitrary.
VALID_ROW = {f: 1 for f in FEATURES} | {
    "SEX": 2,
    "EDUCATION": 2,
    "MARRIAGE": 1,
    "AGE": 35,
    "LIMIT_BAL": 200000,
}

NUMERIC_FEATURE = "LIMIT_BAL"
assert NUMERIC_FEATURE not in CATEGORICAL_FEATURES
CATEGORICAL_FEATURE = "SEX"

# Values that are not representable as int64, on either side of the range.
UNREPRESENTABLE = [
    pytest.param(2**63, id="int64_max_plus_1_formerly_wrapped_silently"),
    pytest.param(2**64, id="2**64_formerly_OverflowError"),
    pytest.param(-(2**63) - 1, id="int64_min_minus_1_formerly_OverflowError"),
    pytest.param(-(2**64), id="negative_2**64"),
]


def _reference_schema() -> dict:
    """Schema built from the real build_schema over a two-row valid frame."""
    frame = pd.DataFrame(
        [VALID_ROW | {TARGET: 0}, VALID_ROW | {TARGET: 1}],
        columns=[*FEATURES, TARGET],
    ).astype(np.int64)
    return build_schema(frame)


class FakeService(PredictionService):
    """Real `frame_from_features`; every model collaborator faked.

    `__init__` deliberately does not call `super().__init__`, so no bundle is
    read and no estimator/calibrator/explainer is built. `predict` and `explain`
    run the real validation path and then return fixed output, so the tests
    exercise input validation and the API error mapping only.
    """

    def __init__(self, cfg: object = None, model_name: str | None = None):
        self.cfg = cfg
        self.model_name = model_name or "fake"
        self.schema = _reference_schema()

    def predict(self, features: dict) -> dict:
        frame = self.frame_from_features(features)
        return {
            "model": self.model_name,
            "output_type": "historical_model_replay",
            "probability_calibrated": 0.5,
            "probability_uncalibrated": 0.5,
            "calibration_method": "fake",
            "validated_value": int(frame[NUMERIC_FEATURE].iloc[0]),
        }

    def explain(self, features: dict, top_k: int = 10) -> dict:
        return {**self.predict(features), "method": "fake", "top_attributions": []}


@pytest.fixture
def service() -> FakeService:
    return FakeService()


# -- service boundary ---------------------------------------------------------


@pytest.mark.parametrize("value", [INT64_MAX, INT64_MIN, 0, -1, 10**18])
def test_representable_int64_round_trips_exactly(service, value) -> None:
    """int64 endpoints and large in-range values stay exact and unwrapped."""
    frame = service.frame_from_features(VALID_ROW | {NUMERIC_FEATURE: value})
    assert frame[NUMERIC_FEATURE].dtype == np.int64
    assert int(frame[NUMERIC_FEATURE].iloc[0]) == value


@pytest.mark.parametrize("value", UNREPRESENTABLE)
def test_unrepresentable_numeric_raises_service_error(service, value) -> None:
    with pytest.raises(ServiceError) as excinfo:
        service.frame_from_features(VALID_ROW | {NUMERIC_FEATURE: value})
    detail = str(excinfo.value)
    assert NUMERIC_FEATURE in detail
    assert "int64" in detail


@pytest.mark.parametrize("value", UNREPRESENTABLE)
def test_unrepresentable_categorical_raises_service_error(service, value) -> None:
    """Categoricals are rejected too; previously 2**63 reached the domain check
    as a wrapped negative. Both paths map to 422, so the API contract is kept."""
    with pytest.raises((ServiceError, SchemaError)):
        service.frame_from_features(VALID_ROW | {CATEGORICAL_FEATURE: value})


def test_silent_wraparound_no_longer_reaches_the_frame(service) -> None:
    """The core regression: 2**63 must not be replayed as a negative int64."""
    with pytest.raises(ServiceError):
        service.frame_from_features(VALID_ROW | {NUMERIC_FEATURE: 2**63})


def test_all_features_are_checked(service) -> None:
    for feature in FEATURES:
        with pytest.raises((ServiceError, SchemaError)):
            service.frame_from_features(VALID_ROW | {feature: 2**64})


def test_offending_features_are_all_named(service) -> None:
    payload = VALID_ROW | {NUMERIC_FEATURE: 2**64, "BILL_AMT1": -(2**64)}
    with pytest.raises(ServiceError) as excinfo:
        service.frame_from_features(payload)
    detail = str(excinfo.value)
    assert NUMERIC_FEATURE in detail and "BILL_AMT1" in detail


# -- unchanged behaviour the check must not disturb ---------------------------


def test_valid_row_still_accepted(service) -> None:
    frame = service.frame_from_features(VALID_ROW)
    assert list(frame.columns) == FEATURES
    assert len(frame) == 1


def test_observed_min_max_stay_reference_only(service) -> None:
    """A numeric value far outside observed_max is still accepted: the new check
    bounds representability, not the feature domain."""
    schema = _reference_schema()
    assert schema["features"][NUMERIC_FEATURE]["observed_max"] == 200000
    frame = service.frame_from_features(VALID_ROW | {NUMERIC_FEATURE: 10**15})
    assert int(frame[NUMERIC_FEATURE].iloc[0]) == 10**15


def test_existing_coercion_behaviour_preserved(service) -> None:
    """int()-coercible inputs still coerce exactly as before the check."""
    frame = service.frame_from_features(VALID_ROW | {NUMERIC_FEATURE: "12"})
    assert int(frame[NUMERIC_FEATURE].iloc[0]) == 12


def test_non_integer_still_service_error(service) -> None:
    with pytest.raises(ServiceError, match="must be integers"):
        service.frame_from_features(VALID_ROW | {NUMERIC_FEATURE: "abc"})


def test_categorical_domain_validation_preserved(service) -> None:
    with pytest.raises(SchemaError, match="EDUCATION"):
        service.frame_from_features(VALID_ROW | {"EDUCATION": 9})


def test_missing_feature_still_service_error(service) -> None:
    partial = {k: v for k, v in VALID_ROW.items() if k != "AGE"}
    with pytest.raises(ServiceError, match="AGE"):
        service.frame_from_features(partial)


# -- API boundary: controlled 422 instead of 500 ------------------------------


@pytest.fixture
def client(monkeypatch, test_config):
    """Real create_app with the service class swapped for the fake, so the app
    is built without a model bundle on disk."""
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from credit_xai.serving import api

    monkeypatch.setattr(api, "PredictionService", FakeService)
    return fastapi_testclient.TestClient(api.create_app(test_config))


@pytest.mark.parametrize("endpoint", ["/predict", "/explain"])
@pytest.mark.parametrize("value", UNREPRESENTABLE)
def test_api_returns_422_not_500(client, endpoint, value) -> None:
    payload = {"features": VALID_ROW | {NUMERIC_FEATURE: value}}
    resp = client.post(endpoint, json=payload)
    assert resp.status_code == 422, resp.text
    assert NUMERIC_FEATURE in resp.json()["detail"]


@pytest.mark.parametrize("endpoint", ["/predict", "/explain"])
@pytest.mark.parametrize("value", [INT64_MAX, INT64_MIN])
def test_api_accepts_int64_endpoints(client, endpoint, value) -> None:
    payload = {"features": VALID_ROW | {NUMERIC_FEATURE: value}}
    resp = client.post(endpoint, json=payload)
    assert resp.status_code == 200, resp.text
    assert resp.json()["validated_value"] == value
