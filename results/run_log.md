
## Run 2026-07-01 14:53:14
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.12, sklearn 1.9.0, pandas 2.3.3, numpy 2.4.3, shap 0.52.0
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-07-03 17:53:16 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.12, sklearn 1.9.0, pandas 2.3.3, numpy 2.4.3
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-07-03 17:53:44 — descriptives.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | groups DLD/HI/Control | no randomness (no seed)
- Table 1 (demographics) + Table 2 (15 measures: Kruskal-Wallis, Holm across 15; Dunn's pairwise, Holm within measure)
- Env: python 3.13.12, pandas 2.3.3, numpy 2.4.3, scipy 1.18.0
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-07-03 17:55:09 — learning_curve.py (v2, nested C)
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 | SEED=42
- LASSO with nested C selection (inner 5-fold, C grid 0.01-10) | outer repeated stratified 5-fold x20
- Train sizes 0.30-1.00 | CV AUC 0.885->0.968
- Env: python 3.13.12, sklearn 1.9.0, pandas 2.3.3, numpy 2.4.3
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-07-03 18:39:43 — descriptives.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | groups DLD/HI/Control | no randomness (no seed)
- Table 1 (demographics) + Table 2 (15 measures: Kruskal-Wallis + epsilon-squared effect size [H/(n-1)], Holm across 15; Dunn's pairwise, Holm within measure)
- Env: python 3.13.12, pandas 2.3.3, numpy 2.4.3, scipy 1.18.0
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-07-04 15:41:29 — age_sensitivity.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 | SEED=42
- Schemes: (a) raw+age covariate; (b) control-referenced residualization (linear, controls-only, within-fold); (c) raw no age
- LASSO nested-C (grid 0.01-10) | repeated stratified 5-fold x20
  - (a) raw + age covariate: BalAcc 0.885 [0.698,1.0], AUC 0.969 [0.845,1.0]
  - (b) control-referenced residualization: BalAcc 0.875 [0.667,1.0], AUC 0.932 [0.758,1.0]
  - (c) raw, no age: BalAcc 0.89 [0.698,1.0], AUC 0.969 [0.847,1.0]
- Env: python 3.13.12, sklearn 1.9.0, pandas 2.3.3, numpy 2.4.3
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-07-06 00:45:11 — classifier_comparison.py (supplementary S3)
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32) | 15 features + age
- 4 models, nested CV (inner 5-fold GridSearchCV, balanced-accuracy); outer repeated stratified 5-fold x20 (100 folds); SEED=42
- Env: python 3.13.12, scikit-learn 1.9.0, scipy 1.18.0, pandas 2.3.3, numpy 2.4.3
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only). NOTE: RF/GB may shift slightly across sklearn versions.

## Run 2026-08-21 17:53:03
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap none
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-21 18:22:51 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 18:27:39 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 18:29:24 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 18:42:54
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-21 18:56:59 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:11:15
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-21 19:11:39 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:35:58
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-21 19:36:11 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 21:08:05 — descriptives.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | groups DLD/HI/Control | no randomness (no seed)
- Table 1 (demographics) + Table 2 (15 measures: Kruskal-Wallis + epsilon-squared effect size [H/(n-1)], Holm across 15; Dunn's pairwise, Holm within measure)
- Env: python 3.13.13, pandas 3.0.5, numpy 2.5.2, scipy 1.18.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 21:45:49 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 22:28:30
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-21 22:49:23 — learning_curve.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 | SEED=42
- LASSO C=0.1 | repeated stratified 5-fold x20 | train sizes 0.30-1.00
- CV AUC range 0.500->0.975 across training sizes
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:04:20 — learning_curve.py (v2, nested C)
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 | SEED=42
- LASSO with nested C selection (inner 5-fold, C grid 0.01-10) | outer repeated stratified 5-fold x20
- Train sizes 0.30-1.00 | CV AUC 0.885->0.968
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:16:25 — learning_curve.py (v2, nested C)
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 | SEED=42
- LASSO with nested C selection (inner 5-fold, C grid 0.01-10) | outer repeated stratified 5-fold x20
- Train sizes 0.30-1.00 | CV AUC 0.885->0.968
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:20:19 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:35:22 — participant_flow.py (S1)
- Counts declared in script; verified against `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) = True
- 83 assessed -> 0 excluded -> 75 analysed (DLD 27 / HI 16 / Control 32)
- Deterministic drawing; no randomness (SEED NA)
- Status: DRAFT — exclusion reasons pending
- Env: python 3.13.13, matplotlib 3.11.1, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:47:28 — participant_flow.py (S1)
- Counts declared in script; verified against `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) = True
- 83 assessed -> 8 excluded -> 75 analysed (DLD 27 / HI 16 / Control 32)
- Deterministic drawing; no randomness (SEED NA)
- Exclusion reasons per A. Esbensen; pre-exclusion group sizes {'DLD': 28, 'HI': 19, 'Control': 36}
- Env: python 3.13.13, matplotlib 3.11.1, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-22 00:24:38 — pca.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | 15 predictors, all 3 groups | median-impute + z-score
- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 45.1%, PC2 8.4%
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-22 00:34:37
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-22 00:41:22
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-22 01:00:36
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-22 01:04:20
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-22 09:20:43
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-22 09:37:13
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-22 09:58:56
- Script: primary_pipeline.py | Seed: 42
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 (DLD 27, Control 32)
- Features (15+age): LSPHUK, LTaF, TROGB, LSPLRAE, GåStop, verbfluantal, verbfluskift, HimOpmscore_skala, NonLRAE, LTaB, NIQ, verbflusubkat, OOU, verbfluintru, verbflupers + age (Alder_mdr/12)
- CV: repeated stratified 5-fold x20 | LASSO C grid 0.01-10, chosen C=0.1 | RF 500 trees, balanced
- LASSO 0.885/0.969 | RF 0.89/0.963 (BalAcc/AUC)
- Minimal battery AUC: k1 0.945, k2 0.974, full 0.975
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2, shap 0.52.0
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (scikit-learn CPU (no GPU used))

## Run 2026-08-30 09:56:28 — export_model.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | n=59 | SEED=42
- Full-data refit of the primary LASSO; nested-CV C = 0.1; intercept 0.0000; 3/16 predictors retained
- Wrote results/model_coefficients.csv, model_card.json, model_card.md
- Env: python 3.13.13, sklearn 1.9.0, pandas 3.0.5, numpy 2.5.2
