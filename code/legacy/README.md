# Superseded scripts

Kept for provenance only. **No result reported in the paper comes from these files.**
Use the current scripts in `code/` instead.

| File | Superseded by | Why |
|---|---|---|
| `primary_pipeline_v1.py` | `code/primary_pipeline.py` | v2 only changes the label placement in the importance figure; model, CV, seeds and all CSV outputs are byte-identical |
| `descriptives_v1_noES.py` | `code/descriptives.py` | current version adds the ε² effect size to Table 2 |
| `learning_curve_v1_fixedC.py` | `code/learning_curve.py` | current version re-selects `C` by nested CV at each training-set size |
| `age_handling_comparison.py` | `code/age_sensitivity.py` | early exploration of age handling, before the analysis was locked |
| `hi_application_probe.py` | `code/hi_exploration.py` | used the pre-correction clinical labels (7 DLD-like, 13/16 agreement) and the superseded feature names `Non` / `HimOpmscore` |
| `hi_explanations.py` | `code/hi_exploration.py`, `code/hi_dissociation.py` | same pre-correction labels and superseded feature names; produced per-child explanation figures that are not reported |

The corrected analyses use `NonLRAE` (span) and `HimOpmscore_skala` (external test-manual
norms), and the corrected clinical designations (6 DLD-like children;
model–clinician agreement 12/16). See `explore/run_log.md`.

These scripts still default to old input paths and will not run without editing.
