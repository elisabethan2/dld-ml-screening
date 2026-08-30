# Model card — DLD screening classifier

Exported 2026-08-30 09:56:28 from `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) by `code/export_model.py`.

## Intended use

Research and model development. This is an internally validated development model trained on 59 Danish children (27 DLD, 32 control). It has **not** been externally validated and must not be used to make clinical decisions about a child.

## Specification

- L1-regularized logistic regression, `liblinear`, `C = 0.1`, `class_weight='balanced'`, seed 42
- Predictors: the 15 locked cognitive-linguistic measures + chronological age in years
- Preprocessing: median imputation, then standardization, using the constants below
- Intercept: `0.000000`
- Decision threshold: 0.5 (not clinically tuned)

## Scoring a new child

For each predictor *j*: replace a missing value with `impute_median`, then compute
`z = (value - standardize_mean) / standardize_sd`. Then

```
log-odds = intercept + sum_j (coefficient_j * z_j)
P(DLD)   = 1 / (1 + exp(-log-odds))
```

Predictors with a coefficient of 0 were dropped by the LASSO and can be ignored: 3 of 16 predictors are retained.

## Coefficients and preprocessing constants

| Predictor | Impute median | Mean | SD | Coefficient |
|---|---|---|---|---|
| CLPT word recall (`LSPHUK`) | 0.625 | 0.570049 | 0.235143 | -0.249355 |
| Digit span forward (`LTaF`) | 4 | 4.59322 | 1.29036 | -0.754306 |
| Grammar (TROG-2) (`TROGB`) | 15 | 13.6271 | 4.74395 | -0.14877 |
| CLPT span (`LSPLRAE`) | 2 | 2.10169 | 1.24458 | 0 |
| Go/Stop inhibition (`GåStop`) | 14 | 12.0847 | 4.61864 | 0 |
| Verbal fluency: correct (`verbfluantal`) | 14 | 14.9153 | 5.9583 | 0 |
| Verbal fluency: switches (`verbfluskift`) | 19 | 20.1525 | 7.57743 | 0 |
| Sky Search attention (`HimOpmscore_skala`) | 9 | 9.13559 | 4.45869 | 0 |
| Nonword recall (span) (`NonLRAE`) | 3 | 2.98305 | 1.33393 | 0 |
| Digit span backward (`LTaB`) | 3 | 3.23729 | 1.47681 | 0 |
| Nonverbal IQ (Block Design) (`NIQ`) | 26 | 30.5424 | 15.0134 | 0 |
| Verbal fluency: subcat. (`verbflusubkat`) | 11 | 10.5932 | 3.53251 | 0 |
| Odd-One-Out (`OOU`) | 3 | 3.59322 | 1.85142 | 0 |
| Verbal fluency: intrusions (`verbfluintru`) | 0 | 0.372881 | 0.9187 | 0 |
| Verbal fluency: persev. (`verbflupers`) | 0 | 0.559322 | 0.849151 | 0 |
| Age (years) (`age`) | 9.66667 | 9.69633 | 1.54992 | 0 |

A negative coefficient means a *higher* score pushes the prediction toward control; on all measures except the two verbal-fluency error counts, higher = better performance.
