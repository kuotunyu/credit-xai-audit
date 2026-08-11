**Global top-5 features** (mean |attribution| on the explained test sample):

| Rank | logistic | ebm | lightgbm |
|---|---|---|---|
| 1 | PAY_0 | PAY_0 | PAY_0 |
| 2 | BILL_AMT1 | LIMIT_BAL | LIMIT_BAL |
| 3 | BILL_AMT2 | BILL_AMT1 | BILL_AMT1 |
| 4 | PAY_AMT2 | PAY_AMT2 | PAY_AMT2 |
| 5 | PAY_AMT1 | PAY_AMT1 | PAY_AMT1 |

**Explanation stability** (top-k Jaccard vs the full-data reference; `refit` = model refit on bootstrap resamples of train, `resample` = explanation-sample resampling only):

| Model | Method | Jaccard (refit) | Kendall τ (refit) | Jaccard (resample) | Sign consistency (local, top-5) | Spearman ρ (local) |
|---|---|---|---|---|---|---|
| logistic | linear_shap | 0.634 [0.429, 0.914] | 0.614 [0.446, 0.783] | 1.000 [1.000, 1.000] | 0.961 | 0.837 |
| ebm | ebm_native | 0.612 [0.429, 0.746] | 0.498 [0.390, 0.593] | 0.923 [0.818, 1.000] | 0.930 | 0.500 |
| lightgbm | tree_shap | 0.763 [0.538, 1.000] | 0.743 [0.656, 0.850] | 0.938 [0.818, 1.000] | 0.979 | 0.614 |

**Faithfulness perturbation** (mean |Δ probability| when replacing the top-attributed vs a matched-random feature with validation donor values; ratio > 1 supports faithfulness; sanity check, not causal evidence):

| Model | Δ top | Δ random | Ratio [CI] | n |
|---|---|---|---|---|
| logistic | 0.1026 | 0.0103 | 9.95 [9.32, 10.63] | 2000 |
| ebm | 0.0853 | 0.0142 | 6.02 [5.65, 6.43] | 2000 |
| lightgbm | 0.0902 | 0.0141 | 6.40 [5.97, 6.88] | 2000 |
