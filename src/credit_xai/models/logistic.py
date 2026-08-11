"""Logistic regression: one-hot categoricals + standardized numerics."""

from __future__ import annotations

from typing import Any, ClassVar

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from credit_xai.config import Config
from credit_xai.constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES, step_train
from credit_xai.data.schema import CATEGORICAL_DOMAINS
from credit_xai.models.base import ModelAdapter
from credit_xai.utils.seeding import seed_int


class LogisticAdapter(ModelAdapter):
    name: ClassVar[str] = "logistic"
    explainer_kind: ClassVar[str] = "linear_shap"

    def build(self, cfg: Config) -> Pipeline:
        params = cfg.models.logistic
        preprocessor = ColumnTransformer(
            [
                (
                    "cat",
                    OneHotEncoder(
                        categories=[CATEGORICAL_DOMAINS[c] for c in CATEGORICAL_FEATURES],
                        drop="if_binary",
                        handle_unknown="error",
                        sparse_output=False,
                    ),
                    CATEGORICAL_FEATURES,
                ),
                ("num", StandardScaler(), NUMERIC_FEATURES),
            ],
            verbose_feature_names_out=False,
        )
        clf = LogisticRegression(
            C=params.C,
            max_iter=params.max_iter,
            solver="lbfgs",
            random_state=seed_int(cfg.run.seed, step_train(self.name)),
        )
        return Pipeline([("prep", preprocessor), ("clf", clf)])

    # -- explanation support (used by explain.explainers) ----------------------
    @staticmethod
    def transformed_parents(estimator: Pipeline) -> list[str]:
        """Parent (original) feature name for every transformed column, in order."""
        preprocessor: ColumnTransformer = estimator.named_steps["prep"]
        encoder: OneHotEncoder = preprocessor.named_transformers_["cat"]
        parents: list[str] = []
        for col, cats in zip(CATEGORICAL_FEATURES, encoder.categories_, strict=True):
            n_out = 1 if (len(cats) == 2 and encoder.drop == "if_binary") else len(cats)
            parents.extend([col] * n_out)
        parents.extend(NUMERIC_FEATURES)
        return parents

    @staticmethod
    def transform(estimator: Pipeline, X: Any) -> Any:
        return estimator.named_steps["prep"].transform(X)

    @staticmethod
    def final_estimator(estimator: Pipeline) -> LogisticRegression:
        return estimator.named_steps["clf"]
