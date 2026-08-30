
## Run 2026-07-05 22:01:54 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.12, sklearn (see primary), scipy 1.18.0, pandas 2.3.3, numpy 2.4.3
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-07-05 22:44:27 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword rep vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammar vs Language r=-0.73
- Env: python 3.13.12, sklearn (see primary), scipy 1.18.0, pandas 2.3.3, numpy 2.4.3
- Compute: Linux-6.12.0-124.56.5.el10_1.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Note on HI script versions (2026-07-06)
hi_exploration.py and hi_dissociation.py (corrected clinical labels: dataset-H11
reclassified NOT DLD-like against the clinical designations supplied by A. Esbensen
(unpublished working table), which resolve a known error in the dataset's own column;
6 DLD-like children; model–clinician agreement 12/16) SUPERSEDE the earlier
explore/hi_application_probe.py and explore/hi_explanations.py, which used the
pre-correction labels (7 DLD-like;
agreement 13/16 = 81%) and are retained only as history. Use hi_exploration.py for
all current HI results.

## Run 2026-08-21 18:07:35 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:03:35 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:11:50 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:12:02 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:36:21 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 19:37:44 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 20:14:34 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 20:15:10 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 20:41:25 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:22:06 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-21 23:27:39 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~56 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-22 00:09:34 — explore/hi_dissociation.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | HI n=16 | SEED=42 (deterministic)
- Spearman feature×target; NO multiple-comparison correction (~105 tests); exploratory
- Key: Nonword serial recall vs BEHL r=-0.61; Digit span fwd vs Language r=-0.64; Grammatical comprehension vs Language r=-0.73
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)

## Run 2026-08-22 00:52:17 — explore/hi_exploration.py
- Data: `data/phddataset_samlet_300626.xlsx` (sha256 7aaf1d0e1375d9b8) | labels: `data/hi_clinical_dldlike.csv` (sha f1a83c2d6bbe65e5) | age-amp: `data/hi_age_amplification.csv` (sha 311dab5381636bec)
- HI n=16 | SEED=42 (deterministic screener + correlations) | corrected clinical labels (H11 fixed)
- Agreement (corrected): 12/16 (75.0%) — NOT independent (shares TROG-2)
- Env: python 3.13.13, sklearn (see primary), scipy 1.18.0, pandas 3.0.5, numpy 2.5.2
- Compute: Linux-6.12.0-211.40.1.el10_2.x86_64-x86_64-with-glibc2.39, 256 CPUs (CPU only)
