Calibration method selected on validation log loss only; the test set never participates in selection.

| Model | Val log loss (sigmoid) | Val log loss (isotonic) | Selected | Test ECE uncal → cal | Threshold* |
|---|---|---|---|---|---|
| logistic | 0.4594 | 0.4405 | **isotonic** | 0.0571 → 0.0098 | 0.218 |
| ebm | 0.4303 | 0.4253 | **isotonic** | 0.0152 → 0.0131 | 0.339 |
| lightgbm | 0.4274 | 0.4206 | **isotonic** | 0.0208 → 0.0203 | 0.354 |

\* Threshold = validation-quantile at (1 − validation base rate), frozen before test evaluation.
