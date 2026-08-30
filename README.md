# Machine-learning screening for developmental language disorder (DLD)

Analysis code, results and documentation for the study *"Machine-Learning Screening of
Developmental Language Disorder in a Context with Limited Standardized Language
Assessments: Evidence from Danish Children"* (Esbensen, Andersen, & Morini), submitted
to the *Journal of Speech, Language, and Hearing Research*.

The study develops an interpretable classifier that separates Danish children with
developmental language disorder from typically developing peers using a 15-measure
cognitive-linguistic battery, reduces it to a minimal screening battery, and probes
the model on a group of children with hearing impairment. It is a **model-development
study with internal validation only** — the model is not clinically deployable.

- **Paper:** DOI to be added on publication
- **Archived release of this repository:** Zenodo DOI to be added at release
- **Reporting standard:** TRIPOD+AI (Collins et al., 2024) — completed checklist:
  [`docs/TRIPOD_AI_checklist.md`](docs/TRIPOD_AI_checklist.md)

---

## Data availability, in one paragraph

The individual-level data are **not** in this repository and cannot be published:
they are health data on identifiable children, restricted by the consent given by
participants' families and by the GDPR / the Danish Data Protection Act. What *is*
open: all analysis code, the pinned environment, the complete variable-level data
dictionary, group-level descriptive statistics for every measure, every result table
behind every figure, the fitted model (coefficients plus the constants needed to
apply it), a dated run log, and a **synthetic dataset generator** so that all of the
code can be executed and inspected without the confidential data. This repository
makes no offer of access to the underlying data.

**[`data/README.md`](data/README.md) is the full statement.**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. build a synthetic stand-in dataset (no real participant data)
python code/make_synthetic_data.py

# 2. run the primary analysis against it
DLD_DATA=data/synthetic/synthetic_dataset.xlsx python code/primary_pipeline.py
```

Every script takes its input path from the `DLD_DATA` environment variable (plus
`HI_LABELS` / `HI_AGEAMP` for the hearing-impairment analyses), so the same commands
work against the real data on a secure platform.

> **Note:** the scripts overwrite `results/` and `figures/` in place. Run them on a
> branch or a copy if you want to keep the committed outputs, which were produced
> from the real data.

## Repository layout

```
code/       analysis scripts (see table below)
results/    result tables, run log, run metadata — the numbers behind the paper
figures/    main-text figures (.pdf + .png)
explore/    exploratory hearing-impairment analyses and their figures
docs/       data dictionary, full environment freeze, publication checklist
data/       empty by design — see data/README.md
```

## Scripts

| Script | What it produces |
|---|---|
| `code/primary_pipeline.py` | **Primary analysis.** LASSO (nested-CV `C`) + random-forest robustness check; ROC/confusion, calibration, feature importance, minimal battery. Figures 2–5, Table of performance |
| `code/descriptives.py` | Tables 1 and 2 (demographics; group comparison with Kruskal–Wallis, ε², Dunn's) |
| `code/pca.py` | Principal component analysis of the battery — Figure 1 and Supplement S4 |
| `code/learning_curve.py` | Learning curve with nested `C` selection — Supplement S2 |
| `code/classifier_comparison.py` | LASSO vs random forest vs SVM vs gradient boosting — Supplement S3 |
| `code/age_sensitivity.py` | Three age-handling schemes — Supplement S5 |
| `code/hi_exploration.py` | Hearing-impairment probe: model probability vs parent report, hearing level, age at amplification — Supplements S6–S8 |
| `code/hi_dissociation.py` | Feature-level language/hearing dissociation — Supplement S9 |
| `code/make_fig_hi.py` | Main-text hearing-impairment figure, plotted from committed CSVs |
| `code/make_fig_importance.py` | Re-plots the importance figure from `results/feature_importance.csv` |
| `code/export_model.py` | Exports the fitted model: coefficients, intercept, imputation/standardization constants, model card |
| `code/make_data_dictionary.py` | Regenerates `docs/data_dictionary.csv` from the dataset |
| `code/make_synthetic_data.py` | Builds the synthetic stand-in dataset |

`code/legacy/` holds superseded versions kept for provenance; they are not used for
any reported result.

## Reproducibility

- Seed **42** for every random operation (CV splits, shuffling, random-forest fitting).
- Environment pinned in `requirements.txt`; the full original freeze is in
  `docs/environment_freeze.txt`.
- Every script prints and logs a sha256 prefix of its input file. The locked runs used
  a dataset hashing to `7aaf1d0e1375d9b8`.
- `results/run_log.md` and `explore/run_log.md` record, per run: date, script, seed,
  data hash, parameters, package versions, compute, and headline results.
  `results/run_info.json` holds the latest primary run in machine-readable form.
- Under the pinned environment the results are deterministic. Random-forest and
  gradient-boosting values can shift slightly on other scikit-learn versions, which is
  why the random forest serves only as a robustness check.

## The model

`results/model_coefficients.csv` and `results/model_card.md` contain everything needed
to score a new child: the retained LASSO coefficients, the intercept, and the median
imputation and standardization constants. These are aggregate statistics over the
n = 59 development sample and contain no individual-level information.

**The model is not validated for clinical use.** It was internally validated on 59
children from one country, with no external or temporally independent test set.

## Citation

See `CITATION.cff`. If you use this code, please cite the paper and the archived
release.

## Licence

Code is released under the MIT Licence (`LICENSE`). Documentation, figures and result
tables are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
No licence is granted to the underlying data, which are not distributed here.
