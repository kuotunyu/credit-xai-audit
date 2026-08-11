Test-set metrics, calibrated model (mean and 95% bootstrap CI over 1000 stratified replicates; run: `full`).

| Metric | logistic | ebm | lightgbm |
|---|---|---|---|
| ROC-AUC | 0.726 [0.707, 0.745] | 0.780 [0.764, 0.796] | 0.781 [0.764, 0.798] |
| PR-AUC | 0.490 [0.461, 0.516] | 0.547 [0.519, 0.574] | 0.540 [0.511, 0.568] |
| Log loss | 0.454 [0.440, 0.468] | 0.430 [0.418, 0.443] | 0.441 [0.424, 0.461] |
| Brier | 0.140 [0.136, 0.145] | 0.134 [0.129, 0.139] | 0.135 [0.130, 0.139] |
| ECE | 0.016 [0.009, 0.025] | 0.020 [0.013, 0.028] | 0.024 [0.016, 0.034] |
| Latency (median) | 5.39 ms/row · 2.0 ms/1k | 1.57 ms/row · 1.9 ms/1k | 5.48 ms/row · 10.6 ms/1k |
