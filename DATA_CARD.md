# DATA CARD — UCI Default of Credit Card Clients

> **Historical 2005 educational audit. Not for lending decisions. Not financial advice.**

## Provenance

| Field | Value |
|---|---|
| Name | Default of Credit Card Clients |
| Source | [UCI Machine Learning Repository, id=350](https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients) |
| Creator | Yeh, I-Cheng (2016 donation; data from a Taiwanese bank, April–September 2005) |
| Dataset citation | Yeh, I. (2009). *Default of Credit Card Clients* [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C55S3H](https://doi.org/10.24432/C55S3H). |
| Associated paper | Yeh, I. C., & Lien, C. H. (2009). *The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients.* Expert Systems with Applications, 36(2), 2473–2480. |
| License | CC BY 4.0 (per UCI dataset page) |
| Rows | 30,000 |
| Features | 23 (X1–X23) + binary target (`default payment next month`, renamed internally to `default`) |
| Positive rate | ≈ 22.1% |
| Acquisition | Primary: official static zip from `archive.ics.uci.edu` (ZIP sha256 and canonical-content sha256 pinned in [`manifests/dataset_fingerprint.json`](manifests/dataset_fingerprint.json) and verified before extraction/processing). Fallback for transport/parsing failures: UCI's documented `ucimlrepo` client, followed by the same canonical-content check. A pinned ZIP checksum mismatch fails closed and never triggers fallback. Raw files are cached in gitignored `data/raw/` and **never committed**. |

The original `.xls` has a known quirk: its first row holds X1..X23 placeholder
labels and the real header is the second row (`header=1` in `data/load.py`).

## Feature schema

23 integer features, frozen in [`manifests/feature_schema.json`](manifests/feature_schema.json):
`LIMIT_BAL`; demographics `SEX`, `EDUCATION`, `MARRIAGE`, `AGE`; repayment
status `PAY_0`, `PAY_2`–`PAY_6`; bill amounts `BILL_AMT1`–`BILL_AMT6`; payment
amounts `PAY_AMT1`–`PAY_AMT6` (NT dollars). There are no missing values.

## Cleaning policy

Applied before splitting. All three rules are fixed value mappings that use no
statistics of the data, so they cannot leak information across splits. Exact
per-run counts are recorded in `results/raw/data/prepare_meta.json`.

1. **`ID` dropped** (row identifier, not a feature).
2. **EDUCATION** — documented codes: 1 = graduate school, 2 = university,
   3 = high school, 4 = others. Observed undocumented codes and mapping
   (counts from the pinned 30,000-row dataset):

   | Original code | Rows | Mapped to |
   |---|---|---|
   | 0 | 14 | 4 (others) |
   | 5 | 280 | 4 (others) |
   | 6 | 51 | 4 (others) |

3. **MARRIAGE** — documented codes: 1 = married, 2 = single, 3 = others.
   Observed undocumented code 0 (54 rows) mapped to 3 (others).

Codes 0/5/6 (EDUCATION) and 0 (MARRIAGE) are undocumented in the UCI variable
dictionary; we collapse them into the documented "others" categories. **This is
a labeling convention, not a substantive claim about those individuals.**
Rejected alternatives: keeping a separate "undocumented" level (tiny, unstable
cells) and dropping the rows (silently changes the population).

**PAY_\*** are kept as ordinal numeric values (−2…8). Codes −2 and 0 are
undocumented in the UCI dictionary and are commonly *interpreted* as "no
consumption" / "revolving credit"; we adopt no such interpretation and enforce
no monotonicity.

## Split

Stratified 70/15/15 (train 21,000 / validation 4,500 / test 4,500), seed 42,
frozen as explicit row indices with class counts and a content-hash binding in
[`manifests/split_manifest.json`](manifests/split_manifest.json). Downstream
code loads the manifest and never re-splits; a test re-derives the split and
asserts equality, and every load re-verifies the partition and class counts.

Fixed local-explanation cases: label-stratified, deterministic draws from the
**validation** split, frozen in [`manifests/local_cases.json`](manifests/local_cases.json).

## Sensitive attributes and limitations

- `SEX` (1 = male, 2 = female — UCI coding reported verbatim), `AGE`,
  `EDUCATION`, and `MARRIAGE` are demographic attributes. They are used (a) as
  model inputs, mirroring the original dataset's design, and (b) to compute the
  **descriptive** group-metric snapshot. Nothing in this repository supports
  conclusions about discrimination, lending practices, or any individual.
- The data reflects one Taiwanese bank's credit-card portfolio in 2005. It is
  unrepresentative of any current population, product, or economy. Models
  trained here must not inform any real decision.
- The target ("default payment next month") is itself a product of 2005-era
  collection and business practices we cannot audit.
