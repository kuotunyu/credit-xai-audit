# credit-xai-audit（繁體中文）

[![CI](https://github.com/kuotunyu/credit-xai-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/kuotunyu/credit-xai-audit/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange?logo=gradio&logoColor=white)
[![License: MIT](https://img.shields.io/badge/License-MIT-2EA44F.svg)](LICENSE)

> **Historical 2005 educational audit. Not for lending decisions. Not financial advice.**  
> （2005 年歷史資料之教育用途稽核。不得用於授信決策。非財務建議。）

這個 Repository 要檢驗的不是「模型能不能吐出預測」，而是其機率與解釋是否有足夠證據可供審查。[English version](README.md)

![Credit XAI Audit canonical model-absent console](assets/ui_audit_console.png)

*公開候選版本不包含 model bundle。這張 canonical 截圖刻意呈現模型尚未載入的狀態，不含任何虛構預測。*

---

## 30 秒作品摘要

| Capability | 這個 Repository 證明什麼 |
|---|---|
| Model comparison | 在同一份凍結切分與評估契約下比較 Logistic Regression、EBM 與 LightGBM。 |
| Probability quality | 只用 Validation set 選擇校準方法，並用 Bootstrap 區間呈現辨識與校準指標的不確定性。 |
| Explainability | 依模型選用合適歸因方法，並檢驗解釋穩定性與 Perturbation Faithfulness。 |
| Delivery | Typed Python package、FastAPI、Gradio、CPU-only container、CI、隱私掃描與可重現證據。 |

解讀結果前請先看[方法摘要](#方法摘要)、[限制與使用範圍](#限制與使用範圍)與[發布驗證紀錄](docs/release/VERIFICATION.md)。

本專案是對 [UCI Default of Credit Card Clients](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) 資料集（台灣，2005 年，30,000 筆、23 個特徵）進行的教育用途、可完整重現的可解釋性（XAI）稽核。三個模型家族 — Logistic Regression、Explainable Boosting Machine (EBM)、LightGBM — 依序完成訓練、機率校準與稽核：

- **機率品質**：ROC-AUC、PR-AUC、Log Loss、Brier、ECE、Latency，皆附 95% Bootstrap 信賴區間；
- **解釋穩定性**：Bootstrap Top-k 排名穩定性與固定案例的 Local Attribution 穩定性；
- **解釋忠實度 (Faithfulness)**：Top-attributed 特徵替換 vs Matched-random 替換；
- **族群指標快照**：依 SEX 與預先宣告的年齡分箱，僅作描述性報告。

本專案**不做因果宣稱**、**不做歧視認定**，也**不提供任何取得授信的建議**。它是在 20 年前公開資料上的方法展示。以下所有數字皆由 [`results/derived/summary.json`](results/derived/summary.json) 經 `python -m credit_xai.cli report` 自動產生，絕不手動編輯。English version: [README.md](README.md).

---

## 系統架構與 Pipeline

### 1. 信用模型 XAI 審計與評測 Pipeline

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    subgraph DataStage ["階段一：決定性資料工程與凍結切分 (Data & Frozen Split)"]
        direction LR
        UCI[("UCI 信用卡違約資料集<br/>(30,000 筆 · 23 個特徵)")] --> Clean["資料清洗與編碼收斂<br/>(EDUCATION/MARRIAGE 映射)"] --> Split[("分層凍結切分 (70/15/15)<br/>(21k Train · 4.5k Val · 4.5k Test)")]
    end

    subgraph ModelStage ["階段二：模型訓練與驗證集校準 (Training & Calibration)"]
        direction LR
        Split --> Models["三大模型家族訓練<br/>(Logistic · EBM · LightGBM)"] --> Calib["Validation 驗證集校準選擇<br/>(Platt Sigmoid vs Isotonic 回歸)"] --> Frozen["凍結決策門檻與參數<br/>(1 - Validation Base Rate)"]
    end

    subgraph AuditStage ["階段三：四大維度 XAI 審計與評估 (Four Audit Dimensions)"]
        direction LR
        Frozen --> D1["1. 機率品質與校準<br/>(ROC/PR-AUC · ECE · Brier)"] & D2["2. 解析式歸因解釋<br/>(Linear SHAP · EBM · TreeSHAP)"] & D3["3. 穩定度與忠實度檢驗<br/>(Refit Jaccard · 擾動替換 Ratio)"]
        D1 & D2 & D3 --> Rep[("不可變審計報告<br/>(results/derived/summary.json)")]
    end

    DataStage --> ModelStage --> AuditStage

    classDef srcStyle fill:#e7f5ff,stroke:#1971c2,stroke-width:2px,color:#212529
    classDef procStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#212529
    classDef evalStyle fill:#e6fcf5,stroke:#0ca678,stroke-width:2px,color:#212529

    class UCI,Split,Frozen,Rep srcStyle
    class Clean,Models,Calib,D1,D2,D3 procStyle

    style DataStage fill:#f8f9fa,stroke:#1971c2,stroke-width:2px,color:#1971c2,stroke-dasharray: 4 4
    style ModelStage fill:#faf5ff,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2,stroke-dasharray: 4 4
    style AuditStage fill:#f4fbf7,stroke:#0ca678,stroke-width:2px,color:#0ca678,stroke-dasharray: 4 4
```

### 2. 服務架構與發布驗證防護

```mermaid
%%{init: {'themeVariables': {'fontSize': '18px'}}}%%
flowchart TD
    subgraph ServStage ["階段一：API 服務與互動控制台 (Serving & UI Console)"]
        direction LR
        Bundle[("本地訓練模型權重<br/>(Model Bundles)")] --> API["FastAPI 後端 API<br/>(未載入權重回傳 503 防護)"] --> WebUI(["Gradio 審計控制台<br/>(歷史模型重放 · 歸因展示)"])
    end

    subgraph GateStage ["階段二：多層發布驗證門禁 (Multi-gate Release Verification)"]
        direction LR
        Artifacts[("審計證據與指標檔案<br/>(results/ · manifests/)")] --> Verify{"Release Gates 驗證器<br/>(Claims · Privacy · Manifest)"} --> Public(["安全公開候選版本<br/>(Clean Publication)"])
    end

    ServStage --> GateStage

    classDef srcStyle fill:#e7f5ff,stroke:#1971c2,stroke-width:2px,color:#212529
    classDef procStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#212529
    classDef condStyle fill:#fff9db,stroke:#f59f00,stroke-width:2px,color:#212529
    classDef safeStyle fill:#e6fcf5,stroke:#0ca678,stroke-width:2px,color:#212529

    class Bundle,Artifacts srcStyle
    class API,WebUI procStyle
    class Verify condStyle
    class Public safeStyle

    style ServStage fill:#faf5ff,stroke:#7b1fa2,stroke-width:2px,color:#7b1fa2,stroke-dasharray: 4 4
    style GateStage fill:#f4fbf7,stroke:#0ca678,stroke-width:2px,color:#0ca678,stroke-dasharray: 4 4
```

---

## 結果

### 測試集指標

<!-- AUTOGEN:METRICS:START -->
<!-- generated by `credit-xai report` from results/derived/summary.json (run: full / config 187eaca76743); do not edit by hand -->
Test-set metrics, calibrated model (mean and 95% bootstrap CI over 1000 stratified replicates; run: `full`).

| Metric | logistic | ebm | lightgbm |
|---|---|---|---|
| ROC-AUC | 0.726 [0.707, 0.745] | 0.780 [0.764, 0.796] | 0.781 [0.764, 0.798] |
| PR-AUC | 0.490 [0.461, 0.516] | 0.547 [0.519, 0.574] | 0.540 [0.511, 0.568] |
| Log loss | 0.454 [0.440, 0.468] | 0.430 [0.418, 0.443] | 0.441 [0.424, 0.461] |
| Brier | 0.140 [0.136, 0.145] | 0.134 [0.129, 0.139] | 0.135 [0.130, 0.139] |
| ECE | 0.016 [0.009, 0.025] | 0.020 [0.013, 0.028] | 0.024 [0.016, 0.034] |
| Latency (median) | 5.39 ms/row · 2.0 ms/1k | 1.57 ms/row · 1.9 ms/1k | 5.48 ms/row · 10.6 ms/1k |
<!-- AUTOGEN:METRICS:END -->

![ROC and PR curves](assets/roc_pr_curves.png)

### 機率校準

校準方法（Platt sigmoid / isotonic）只用 validation set 選擇（validation log loss），test set 完全不參與選擇；決策 threshold 亦於 validation 凍結。

<!-- AUTOGEN:CALIBRATION:START -->
<!-- generated by `credit-xai report` from results/derived/summary.json (run: full / config 187eaca76743); do not edit by hand -->
Calibration method selected on validation log loss only; the test set never participates in selection.

| Model | Val log loss (sigmoid) | Val log loss (isotonic) | Selected | Test ECE uncal → cal | Threshold* |
|---|---|---|---|---|---|
| logistic | 0.4594 | 0.4405 | **isotonic** | 0.0571 → 0.0098 | 0.218 |
| ebm | 0.4303 | 0.4253 | **isotonic** | 0.0152 → 0.0131 | 0.339 |
| lightgbm | 0.4274 | 0.4206 | **isotonic** | 0.0208 → 0.0203 | 0.354 |

\* Threshold = validation-quantile at (1 − validation base rate), frozen before test evaluation.
<!-- AUTOGEN:CALIBRATION:END -->

![Reliability diagram](assets/reliability_diagram.png)

### 可解釋性

每個模型使用其類別對應的精確／解析式歸因方法：LightGBM 用 TreeSHAP、logistic regression 用精確 linear SHAP（one-hot 歸因加總回母特徵）、EBM 用其原生的可加 term 貢獻。跨模型只做定性比較，不做數值比較。

<!-- AUTOGEN:XAI:START -->
<!-- generated by `credit-xai report` from results/derived/summary.json (run: full / config 187eaca76743); do not edit by hand -->
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
<!-- AUTOGEN:XAI:END -->

![Global importance](assets/global_importance.png)

![EBM shape functions](assets/ebm_shapes_top.png)

![Faithfulness perturbation](assets/faithfulness.png)

### 族群指標快照

以下為模型在 2005 年歷史資料上行為的描述性快照（凍結 threshold 下計算），不構成對任何個人或授信實務的結論；小樣本格的信賴區間予以抑制。

<!-- AUTOGEN:GROUPS:START -->
<!-- generated by `credit-xai report` from results/derived/summary.json (run: full / config 187eaca76743); do not edit by hand -->
Descriptive snapshot of model behavior on 2005 historical data, by SEX (UCI coding: 1 = male, 2 = female) and predeclared age bins, at the frozen base-rate threshold. These numbers support no conclusions about individuals or lending practices. CIs are suppressed for small cells.

**logistic**

| Group | n | AUC | FPR | FNR | Selection rate |
|---|---|---|---|---|---|
| sex=1_male | 1790 | 0.721 [0.694, 0.749] | 0.270 [0.247, 0.294] | 0.397 [0.354, 0.439] | 0.349 [0.328, 0.371] |
| sex=2_female | 2710 | 0.727 [0.701, 0.754] | 0.143 [0.129, 0.158] | 0.456 [0.413, 0.498] | 0.228 [0.214, 0.243] |
| age=21-29 | 1408 | 0.743 [0.708, 0.775] | 0.152 [0.132, 0.173] | 0.429 [0.380, 0.481] | 0.249 [0.229, 0.269] |
| age=30-39 | 1718 | 0.712 [0.678, 0.743] | 0.171 [0.152, 0.192] | 0.476 [0.424, 0.530] | 0.239 [0.221, 0.257] |
| age=40-49 | 991 | 0.717 [0.675, 0.757] | 0.238 [0.209, 0.269] | 0.415 [0.355, 0.476] | 0.325 [0.297, 0.352] |
| age=50-59 | 331 | 0.784 [0.725, 0.840] | 0.324 [0.265, 0.383] | 0.282 [0.192, 0.385] | 0.417 [0.369, 0.468] |
| age=60+ | 52 | 0.554 (small cell) | 0.378 (small cell) | 0.533 (small cell) | 0.404 (small cell) |

**ebm**

| Group | n | AUC | FPR | FNR | Selection rate |
|---|---|---|---|---|---|
| sex=1_male | 1790 | 0.766 [0.738, 0.793] | 0.160 [0.140, 0.179] | 0.449 [0.401, 0.494] | 0.252 [0.234, 0.270] |
| sex=2_female | 2710 | 0.789 [0.767, 0.811] | 0.107 [0.095, 0.120] | 0.467 [0.423, 0.507] | 0.197 [0.185, 0.211] |
| age=21-29 | 1408 | 0.786 [0.758, 0.815] | 0.129 [0.109, 0.149] | 0.451 [0.401, 0.503] | 0.226 [0.205, 0.245] |
| age=30-39 | 1718 | 0.768 [0.736, 0.795] | 0.125 [0.108, 0.143] | 0.500 [0.448, 0.561] | 0.197 [0.178, 0.215] |
| age=40-49 | 991 | 0.781 [0.746, 0.816] | 0.124 [0.101, 0.147] | 0.448 [0.383, 0.512] | 0.231 [0.208, 0.255] |
| age=50-59 | 331 | 0.803 [0.741, 0.858] | 0.150 [0.107, 0.190] | 0.346 [0.244, 0.462] | 0.269 [0.227, 0.308] |
| age=60+ | 52 | 0.770 (small cell) | 0.081 (small cell) | 0.533 (small cell) | 0.192 (small cell) |

**lightgbm**

| Group | n | AUC | FPR | FNR | Selection rate |
|---|---|---|---|---|---|
| sex=1_male | 1790 | 0.764 [0.736, 0.789] | 0.161 [0.142, 0.180] | 0.449 [0.404, 0.492] | 0.253 [0.234, 0.272] |
| sex=2_female | 2710 | 0.792 [0.769, 0.813] | 0.110 [0.097, 0.124] | 0.469 [0.429, 0.509] | 0.200 [0.187, 0.212] |
| age=21-29 | 1408 | 0.784 [0.750, 0.813] | 0.136 [0.115, 0.156] | 0.460 [0.407, 0.519] | 0.229 [0.208, 0.249] |
| age=30-39 | 1718 | 0.776 [0.749, 0.802] | 0.120 [0.103, 0.138] | 0.494 [0.442, 0.548] | 0.194 [0.178, 0.211] |
| age=40-49 | 991 | 0.776 [0.743, 0.811] | 0.124 [0.101, 0.148] | 0.452 [0.387, 0.512] | 0.230 [0.209, 0.254] |
| age=50-59 | 331 | 0.796 [0.730, 0.854] | 0.178 [0.130, 0.225] | 0.359 [0.256, 0.462] | 0.287 [0.245, 0.329] |
| age=60+ | 52 | 0.812 (small cell) | 0.135 (small cell) | 0.400 (small cell) | 0.269 (small cell) |

<!-- AUTOGEN:GROUPS:END -->

![Group AUC](assets/group_auc.png)

---

## 快速開始

需要 Python 3.11+ 與 [uv](https://docs.astral.sh/uv/)。

```bash
python scripts/setup_environment.py  # 鎖定 CPU-only 非可編輯安裝

# 完整 pipeline（自動下載 UCI 資料集至 data/raw/，不進 git）
uv run --no-sync python -m credit_xai.cli data prepare --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli train --model logistic --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli train --model ebm      --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli train --model lightgbm --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli calibrate --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli evaluate  --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli explain   --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli report    --config configs/smoke.yaml
uv run --no-sync python -m credit_xai.cli serve     --config configs/smoke.yaml  # API + /ui
```

`configs/smoke.yaml` 可以在一般筆電 CPU 上數分鐘內跑完；`configs/full.yaml` 提高所有預算（1,000 次 Bootstrap 重抽樣、20 次 Refit、完整測試集 SHAP）。被接受的 Full run 在 Colab CPU 上約需 4.5 小時。長任務在每次迭代皆存有 Checkpoint，支援 `--resume` 斷點續跑。全流程不依賴 GPU。

Docker 容器化（CPU-only）：

```bash
docker compose up api                      # 啟動 API 於 :8000
docker compose --profile smoke run smoke   # 於容器內對合成資料執行完整 pipeline
```

公開發布版本不包含 Model bundle。在沒有本地訓練模型的情況下，API 維持健康但推論端點回傳 503。

---

## 專案結構

```text
configs/          smoke.yaml / full.yaml（僅預算與樣本數不同）
manifests/        凍結資料指紋、切分索引、結構契約與固定案例
src/credit_xai/   核心邏輯（data, models, calibration, metrics, explain, fairness, reporting, serving）
results/raw/      機器產生的步驟輸出（不可變審計追蹤）
results/derived/  summary.json 與 Markdown 表格（README 數據之唯一來源）
assets/           圖表與展示截圖
app/              FastAPI 應用程式與 Gradio 審計控制台 UI
notebooks/        輕量展示封裝
```

---

## 方法摘要

- **資料**：UCI id=350，官方典藏庫下載（SHA-256 鎖定於 `manifests/dataset_fingerprint.json`）。移除 `ID`，未記載代碼收斂至既有類別（EDUCATION {0,5,6}→4, MARRIAGE {0}→3），詳見 [DATA_CARD.md](DATA_CARD.md)。
- **切分**：分層 70/15/15（21,000 / 4,500 / 4,500），以明確索引凍結於 `manifests/split_manifest.json`，下游代碼絕不重新隨機切分。
- **校準**：Platt sigmoid 與 Isotonic 回歸僅於 Validation 預測上擬合；以 Validation Log Loss 擇優；決策門檻凍結於 Validation 之 (1 − Base Rate) 分位數。
- **信賴區間**：分層 Test-set Bootstrap（保持類別比例），固定種子生成，支援重現與成對比較。
- **穩定度**：`refit` = 重新訓練於 Bootstrap 訓練重抽樣（流程穩定度）；`resample` = 僅重抽樣解釋樣本（估計器雜訊底限）。
- **忠實度**：將 Top-attributed 特徵替換為 Validation 供體值，對比隨機替換特徵之 |Δp| 比值。此為 Explainer-model 配對之 Sanity check，非因果推論。
- **族群快照**：僅作描述性快照，小樣本格抑制 CI，詳見 [MODEL_CARD.md](MODEL_CARD.md)。

---

## 限制與使用範圍

- 2005 年台灣單一銀行之歷史資料，不代表任何現代人口母體。**不得**將這些模型或數字用於任何真實授信決策。
- 歸因值依賴各解釋器之數學假設（Linear SHAP 之特徵獨立性、TreeSHAP 之路徑條件期望值、EBM 之可加分解）；它們描述的是模型行為，而非真實世界因果。
- 已知環境降級與偏差記錄於 [FAILURES.md](FAILURES.md)。

---

## 發布驗證與公開邊界

公開版本保留精簡機器證據，排除未處理之原始個資、序列化模型、內部筆記與私人 Git 歷史。詳見 [PUBLIC_BOUNDARY.md](docs/release/PUBLIC_BOUNDARY.md) 與 [`release_manifest.json`](manifests/release_manifest.json)。

---

## 授權與引用

程式碼採 [MIT License](LICENSE) 授權。UCI 資料集遵循 CC BY 4.0：Yeh, I. (2009), *Default of Credit Card Clients*, UCI Machine Learning Repository, [doi:10.24432/C55S3H](https://doi.org/10.24432/C55S3H)。資料集不隨本 Repository 散布。詳見 [CITATION.cff](CITATION.cff)。
