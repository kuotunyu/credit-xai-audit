# MODEL CARD — credit-xai-audit

> **Historical 2005 educational audit. Not for lending decisions. Not financial advice.**

Served verbatim by the API at `GET /model-card`.

## Intended use

Education and methods demonstration only: how to audit historical tabular
default-prediction
models for calibration, explanation stability, and explanation faithfulness on
a historical public dataset. **Out of scope:** any lending, credit-scoring, or
individual-level decision; any claim about present-day populations; any causal
or discrimination claim; any advice on obtaining credit.

## Models

All models consume the same cleaned 23-feature frame (see
[DATA_CARD.md](DATA_CARD.md)) and are trained on the frozen 70/15/15 split.
Hyperparameters live in `configs/*.yaml`; nothing is tuned on the test set.

| Model | Implementation | Encoding | Explainer |
|---|---|---|---|
| logistic | sklearn `LogisticRegression` (lbfgs) in a Pipeline | one-hot SEX/EDUCATION/MARRIAGE + standardized numerics | exact linear SHAP; one-hot attributions summed back to parent features |
| ebm | interpret `ExplainableBoostingClassifier` | native (explicit nominal/continuous feature types) | native additive term contributions (`eval_terms`); interactions split 50/50 to parents |
| lightgbm | `LGBMClassifier` (deterministic, early stopping on validation) | native pandas categoricals | TreeSHAP (interventional preferred; falls back to LightGBM `pred_contrib`, i.e. path-dependent TreeSHAP — the mode used is recorded in each artifact) |

Documented fallbacks (triggered automatically, recorded in artifacts and
[FAILURES.md](FAILURES.md)): `interpret` unavailable → EBM step fails with an
install hint (other models unaffected); `lightgbm` unavailable → sklearn
`HistGradientBoostingClassifier` stand-in.

## Calibration and reporting threshold

Platt (sigmoid) and isotonic calibrators are fit on **validation** predictions
only; the winner is selected by validation log loss. The reporting threshold is
the validation quantile at (1 − validation base rate) of calibrated
probabilities. Both decisions are frozen to `results/raw/<model>/calibration.json`
before any test evaluation; the evaluate step only reads the frozen record.

## Evaluation protocol

- Test-set metrics: ROC-AUC, PR-AUC, log loss (probabilities clipped at 1e-6),
  Brier, ECE (equal-frequency 15-bin), CPU latency (batch and per-row).
- 95% CIs from a stratified test-set bootstrap (class counts preserved,
  percentile intervals, deterministic per-iteration seeds).
- Group snapshot: n, prevalence, AUC, FPR, FNR, selection rate by SEX and
  predeclared age bins (21–29 / 30–39 / 40–49 / 50–59 / 60+), with CIs
  suppressed for cells having fewer than 20 members of either class.

## Explainability protocol

- Global importance = mean |attribution| over a fixed, seed-derived test
  sample; identical background/explained rows across models.
- Rank stability: refit-based (bootstrap resamples of train) and
  explanation-resample variants, reported separately (Jaccard of top-k vs the
  full-data reference; Kendall τ over all 23 features).
- Local stability: predeclared validation cases; majority-sign frequency over
  each case's top-5 features and Spearman ρ of |attribution| ranks across
  refits.
- Faithfulness: mean |Δ predicted probability| when the top-attributed feature
  is replaced by validation donor values, against a uniformly chosen other
  feature under the identical mechanism; ratio with paired bootstrap CI. This
  is a sanity check on the explainer-model pair, **not** causal evidence.

Attribution values live on each model's link (log-odds) scale against
different baselines; they are compared qualitatively, never numerically,
across models. They describe **model behavior**, not real-world causes.

## Serialization and serving

Models are stored as local joblib bundles with sha256-verified manifests
(`models/`, gitignored). A colocated hash detects accidental change relative to
that manifest; it does **not** authenticate who produced either file. Python
pickle/joblib loading can execute code, so only owner-produced local bundles
may be loaded. The FastAPI service exposes
`/health`, `/predict`, `/explain`, `/model-card`; every prediction and
explanation response carries the fixed disclaimer and historical-replay scope.
A Gradio UI is mounted at `/ui`. Neither interface provides a decision,
recommendation, eligibility assessment, or production control.

## Ethical notes and wording constraints

Group-metric differences on 2005 historical data cannot support conclusions
about discrimination, lending practices, or any individual — sample
composition, label quality, and 20 years of distribution shift are all
unmodeled. Report text in this repository deliberately avoids "bias",
"discrimination", and causal language, and every artifact carries:
**Historical 2005 educational audit. Not for lending decisions. Not financial
advice.**
