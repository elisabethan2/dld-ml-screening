# What in this repository produces what in the paper

Every numbered table and figure in the manuscript and supplement, the script that
produces it, and the committed output it comes from.

## Main text

| Paper | Script | Output |
|---|---|---|
| Table 1 — demographics |  `code/descriptives_v2_ddof0.py` | `results/table1_demographics.csv` |
| Table 2 — predictor set, constructs and instruments | — (descriptive; no computation) | variable names documented in `docs/data_dictionary.csv` |
| Table 3 — group comparison (M, SD, Kruskal–Wallis, ε², Dunn's) | `code/descriptives_v2_ddof0.py`, formatted by `code/table3.py` | `results/table2_group_comparison.csv` |
| Table 4 — classification performance | `code/primary_pipeline.py` | `results/primary_performance.csv` |
| Table 5 — performance by battery size | `code/primary_pipeline.py` | `results/minimal_battery.csv` |
| Figure 1 — PCA by group | `code/pca.py` | `figures/fig_pca.{pdf,png}`, `results/pca_loadings.csv`, `results/pca_variance.csv` |
| Figure 2 — ROC and confusion matrix | `code/primary_pipeline.py` | `figures/fig_roc_confusion.{pdf,png}`, `results/oof_predictions.csv` |
| Figure 3 — calibration | `code/primary_pipeline.py` | `figures/fig_calibration.{pdf,png}` |
| Figure 4 — feature importance | `code/replot_figures_v2.py` (restyles the pipeline output) | `figures/fig_importance_v2.{pdf,png}` — **see the note below**. `figures/fig_importance.{pdf,png}` is the raw `primary_pipeline.py` output it restyles; `results/feature_importance.csv` holds the values |
| Figure 5 — battery size | `code/primary_pipeline.py` | `figures/fig_minimal_battery.{pdf,png}` |
| Figure 6 — HI probe | `code/make_fig_hi_v2.py` | `explore/hi_fig_main_v2.{pdf,png}`; `explore/hi_fig_main.{pdf,png}` is the superseded first version |

> **Which figure version the paper uses.** Verified against the images embedded in the
> 29 Aug manuscript: Figure 1 is `fig_pca.png` (byte-identical), Figure 6 is
> `hi_fig_main_v2.png`, and Figure 4 uses the v2 construct terminology.
>
> **Figure 4 does not match any committed file.** The manuscript version carries the v2
> labels and the same values as `fig_importance_v2.png`, but drops the two panel titles,
> adds bold **A**/**B** panel letters, and labels the left x-axis "mean |SHAP|
> (probability)" instead of "importance". The committed `code/replot_figures_v2.py`
> produces the titled, letterless version, so it does not regenerate the published
> figure. Either commit the newer script that produced it, or regenerate Figure 4 from
> the committed script and use that in the paper.

> The manuscript's **Table 3** is the file named `results/table2_group_comparison.csv`.
> The numbering diverged when a descriptive table was inserted as Table 2; the file
> names were not renumbered.

## Supplemental material

| Paper | Script | Output |
|---|---|---|
| S1 — participant flow | `code/participant_flow.py` | `figures/fig_participant_flow.{pdf,png}`, `results/participant_flow.csv` |
| S2 — learning curve | `code/learning_curve.py` | `figures/fig_learning_curve.{pdf,png}`, `results/learning_curve.csv` |
| S3 — classifier comparison | `code/classifier_comparison.py` | `results/classifier_comparison.csv` |
| S4 — PCA scree plot | `code/pca.py` | `figures/fig_pca_scree.{pdf,png}` |
| S5 — age-handling sensitivity | `code/age_sensitivity.py` | `results/age_sensitivity.csv` |
| S6 — domain specificity of model–parent-report convergence | `code/hi_exploration.py` | `explore/hi_correlations.csv`, `explore/hi_fig_domain_corr.{pdf,png}` |
| S7 — probability vs hearing severity (BEHL) | `code/hi_exploration.py` | `explore/hi_fig_behl.{pdf,png}` |
| S8 — probability vs age at amplification | `code/hi_exploration.py` | `explore/hi_fig_ageamp.{pdf,png}` |
| S9 — feature-level dissociation, full predictor set | `code/hi_dissociation.py` | `explore/hi_dissociation_corr.csv`, `explore/hi_fig_dissociation_heatmap.{pdf,png}` |

## Promised in the Data Availability Statement

| Promise | Where |
|---|---|
| Analysis code | `code/` |
| Pinned software environment | `requirements.txt`, `docs/environment_freeze.txt` |
| The trained model, as LASSO coefficients | `results/model_coefficients.csv`, `results/model_card.md`, `results/model_card.json` |
| Dated run log | `results/run_log.md`, `explore/run_log.md`, `results/run_info.json` |
| Data dictionary (referenced in the Table 2 note) | `docs/data_dictionary.csv` |
| TRIPOD+AI checklist | `docs/TRIPOD_AI_checklist.docx` (submitted supplemental file), `docs/TRIPOD_AI_checklist.md` (web-readable rendering) |

## Not part of the paper

`code/legacy/` — superseded scripts, kept for provenance.
`explore/hi_probe_distribution.*`, `explore/hi_groupmean_attribution.*` — superseded
outputs from those scripts. See `explore/README.md`.
