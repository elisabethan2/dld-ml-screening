# Exploratory hearing-impairment analyses

Exploratory and hypothesis-generating (n = 16). The confirmatory DLD-versus-control
analysis lives in `results/` and `figures/`.

## Current outputs

| File | Script | Where it appears |
|---|---|---|
| `hi_fig_main.{pdf,png}` | `code/make_fig_hi.py` | main-text hearing-impairment figure |
| `hi_fig_domain_corr.{pdf,png}` | `code/hi_exploration.py` | Supplement S6 (domain specificity) |
| `hi_fig_behl.{pdf,png}` | `code/hi_exploration.py` | Supplement S7 (hearing severity) |
| `hi_fig_ageamp.{pdf,png}` | `code/hi_exploration.py` | Supplement S8 (age at amplification) |
| `hi_fig_dissociation_heatmap.{pdf,png}` | `code/hi_dissociation.py` | Supplement S9 (full predictor set) |
| `hi_fig_dissociation.{pdf,png}` | `code/hi_dissociation.py` | focused language/hearing dissociation |
| `hi_fig_language.{pdf,png}`, `hi_fig_combined.{pdf,png}` | `code/hi_exploration.py` | working figures |
| `run_log.md` | — | dated run log for these analyses |

## Superseded outputs — do not cite

These came from the scripts now in `code/legacy/`, which used the **pre-correction**
clinical labels (7 DLD-like children, 13/16 agreement) and the old feature names
`Non` and `HimOpmscore`. The corrected analyses use `NonLRAE` and
`HimOpmscore_skala` and give 6 DLD-like children and 12/16 agreement.

- `hi_probe_distribution.{pdf,png}` — from `code/legacy/hi_application_probe.py`
- `hi_groupmean_attribution.{pdf,png}` — from `code/legacy/hi_explanations.py`

Per-child explanation figures produced by the same superseded script were removed:
they were individual-level participant outputs and are not reportable under the
study's Data Availability Statement.

## Not committed

`hi_scores.csv` holds one row per child (predicted probability, clinical
designation, hearing level, age at amplification, questionnaire domain scores) and is
excluded by `.gitignore`. `code/make_fig_hi.py` panel A needs it, so that panel can
only be regenerated with access to the real data.
