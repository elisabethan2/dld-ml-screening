"""
replot_figures_v2.py — Regenerate paper figures with corrected construct terminology.

WHAT THIS DOES
  Re-plots ONLY. It reads saved result CSVs and redraws figures with updated labels.
  It does NOT refit any model, so the plotted numbers are guaranteed identical to those
  already reported in the manuscript tables. Nothing in results/ is modified.

WHY ONLY ONE FIGURE HERE
  Of the four primary figures, only fig_importance carries construct names.
  fig_minimal_battery and fig_roc_confusion contain no construct labels (axis text and
  Control/DLD only), so they need no change. fig_calibration needs no terminology change
  either, though its axis text could be improved (see NOTE at the bottom of this file).

TERMINOLOGY CHANGES APPLIED (agreed with A. Esbensen, Aug 2026)
  TROGB             Grammar (TROG-2)            -> Grammatical comprehension (TROG-2)
  NonLRAE           Nonword recall (span)       -> Nonword serial recall
  NIQ               Nonverbal IQ (Block Design) -> Nonverbal reasoning (Block Design)
  LSPLRAE           CLPT span                   -> CLPT listening span
  GaaStop           Go/Stop inhibition          -> Response inhibition (Go/Stop)
  HimOpmscore_skala Sky Search attention        -> Selective attention (Sky Search)
  OOU               Odd-One-Out                 -> Visuospatial WM (Odd-One-Out)

INPUTS   results/feature_importance.csv   (feature, label, LASSO_coef, RF_SHAP, Perm_imp, abs_coef)
         results/run_info.json            (optional; supplies chosen_C for the panel title)
OUTPUTS  figures/fig_importance_v2.pdf and .png  (300 dpi, JSLHR minimum)
         figures/replot_log.md            (appended: date, inputs, hashes, versions)

USAGE    Place in code/ alongside primary_pipeline.py. Paths are anchored to the repo
         root, so either of these works:
             python code/replot_figures_v2.py     (from the repo root)
             python replot_figures_v2.py          (from inside code/)
         Override with env vars if needed:
             DLD_RESULTS=/path/to/results DLD_FIGURES=/path/to/figures python ...

DETERMINISM
  No randomness is involved: this script only reads and draws. No seed is required.
  Provenance is instead established by hashing the input CSV (recorded in replot_log.md).
"""
import os, sys, json, hashlib, datetime, platform

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------------------------------------------------------ config
# Anchor to the repo root (the parent of code/) so the script runs correctly whether
# invoked from the repo root or from inside code/. Env vars still override.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "code" else _HERE

RESULTS = os.environ.get("DLD_RESULTS", os.path.join(_ROOT, "results"))
FIGURES = os.environ.get("DLD_FIGURES", os.path.join(_ROOT, "figures"))
IMPORTANCE_CSV = os.path.join(RESULTS, "feature_importance.csv")


def _rel(path):
    """Repo-relative path for the log, so a local directory layout is not published."""
    try:
        return os.path.relpath(path, _ROOT)
    except ValueError:
        return os.path.basename(path)
RUN_INFO_JSON = os.path.join(RESULTS, "run_info.json")
OUT_STEM = "fig_importance_v2"

# Sort both panels in the same order so a reader can trace one measure across panels.
# Set to False to restore the original behaviour (each panel sorted by its own metric).
ALIGN_PANEL_ORDER = True

DPI = 300  # JSLHR requires >= 300 dpi for figure files

os.makedirs(FIGURES, exist_ok=True)

# ------------------------------------------------------------------ labels
# Keyed on the `feature` column (dataset variable names), NOT on the stale `label`
# column in the CSV, which still holds the pre-correction wording.
LABELS = {
    "LTaF":              "Digit span forward",
    "LSPHUK":            "CLPT word recall",
    "LSPLRAE":           "CLPT listening span",
    "LTaB":              "Digit span backward",
    "NonLRAE":           "Nonword serial recall",
    "TROGB":             "Grammatical comprehension (TROG-2)",
    "OOU":               "Visuospatial WM (Odd-One-Out)",
    "GåStop":            "Response inhibition (Go/Stop)",
    "HimOpmscore_skala": "Selective attention (Sky Search)",
    "verbfluantal":      "Verbal fluency: correct",
    "verbfluskift":      "Verbal fluency: switches",
    "verbflusubkat":     "Verbal fluency: subcat.",
    "verbflupers":       "Verbal fluency: persev.",
    "verbfluintru":      "Verbal fluency: intrusions",
    "NIQ":               "Nonverbal reasoning (Block Design)",
    "age":               "Age",
}

COL_RF = "#4c72b0"
COL_NEG = "#c44e52"
COL_POS = "#55a868"


def file_sha256(path, n=16):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:n]
    except Exception:
        return "NA"


def savefig(fig, name):
    written = []
    for ext in ("pdf", "png"):
        path = os.path.join(FIGURES, f"{name}.{ext}")
        fig.savefig(path, dpi=DPI, bbox_inches="tight")
        written.append(path)
    plt.close(fig)
    return written


# ------------------------------------------------------------------ load
if not os.path.exists(IMPORTANCE_CSV):
    sys.exit(f"ERROR: {IMPORTANCE_CSV} not found. Set DLD_RESULTS or run from the repo root.")

imp = pd.read_csv(IMPORTANCE_CSV)

required = {"feature", "LASSO_coef", "RF_SHAP"}
missing_cols = required - set(imp.columns)
if missing_cols:
    sys.exit(f"ERROR: {IMPORTANCE_CSV} is missing column(s): {sorted(missing_cols)}")

# Fail loudly on unmapped variables rather than silently plotting a raw code.
unmapped = [f for f in imp["feature"] if f not in LABELS]
if unmapped:
    sys.exit(f"ERROR: no label defined for: {unmapped}\nAdd them to LABELS and re-run.")

imp["label_v2"] = imp["feature"].map(LABELS)
if "abs_coef" not in imp.columns:
    imp["abs_coef"] = imp["LASSO_coef"].abs()

# chosen_C for the panel title; falls back gracefully if run_info.json is absent
chosen_C = None
if os.path.exists(RUN_INFO_JSON):
    try:
        with open(RUN_INFO_JSON, encoding="utf-8") as f:
            chosen_C = json.load(f).get("lasso", {}).get("chosen_C")
    except Exception as e:
        print(f"[warn] could not read chosen_C from {RUN_INFO_JSON}: {e}")

# The published figure carries panel letters instead of titles; chosen_C is reported in
# the caption and in results/run_info.json rather than on the axes.
c_title = f"LASSO coefficients (C={chosen_C:.3g})" if chosen_C else "LASSO coefficients"

# Detect whether RF_SHAP holds SHAP values or impurity importances. The original
# pipeline falls back to impurity if the shap package is unavailable, and the two
# are not interchangeable, so the panel title must say which one is plotted.
rf_metric = "mean |SHAP|"
if os.path.exists(RUN_INFO_JSON):
    try:
        with open(RUN_INFO_JSON, encoding="utf-8") as f:
            if json.load(f).get("environment", {}).get("shap") in ("none", None):
                rf_metric = "impurity"
    except Exception:
        pass

# ------------------------------------------------------------------ plot
if ALIGN_PANEL_ORDER:
    order = imp.sort_values("RF_SHAP", ascending=True)
    left, right = order, order
else:
    left = imp.sort_values("RF_SHAP", ascending=True)
    right = imp.sort_values("abs_coef", ascending=True)

fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))

ax[0].barh(left["label_v2"], left["RF_SHAP"], color=COL_RF)
ax[0].set_xlabel("mean |SHAP| (probability)" if rf_metric == "mean |SHAP|"
                 else "importance (impurity)")

cols = [COL_NEG if v < 0 else COL_POS for v in right["LASSO_coef"]]
ax[1].barh(right["label_v2"], right["LASSO_coef"], color=cols)
ax[1].axvline(0, color="k", lw=0.8)
ax[1].set_xlabel("coefficient (negative = lower scores associated with DLD)")

# Panel letters rather than titles: JSLHR figures are referred to as "Figure 4A/4B",
# and the RF metric and the LASSO penalty are stated in the caption.
for a, letter in zip(ax, ("A", "B")):
    a.text(0.0, 1.02, letter, transform=a.transAxes,
           fontsize=13, fontweight="bold", va="bottom", ha="left")

if ALIGN_PANEL_ORDER:
    # Same row order in both panels: drop the duplicated tick labels on the right.
    ax[1].set_yticklabels([])

fig.tight_layout()
written = savefig(fig, OUT_STEM)

# ------------------------------------------------------------------ log
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_path = os.path.join(FIGURES, "replot_log.md")
with open(log_path, "a", encoding="utf-8") as f:
    f.write(f"\n## Replot {now}\n")
    f.write("- Script: replot_figures_v2.py (re-plot only; no model refit)\n")
    f.write(f"- Input: `{_rel(IMPORTANCE_CSV)}` (sha256 {file_sha256(IMPORTANCE_CSV)})\n")
    f.write(f"- RF panel metric: {rf_metric} | LASSO C: {chosen_C}\n")
    f.write(f"- Panels aligned: {ALIGN_PANEL_ORDER} | panel letters A/B, no panel titles"
            f" (LASSO penalty for the caption: {c_title})\n")
    f.write(f"- Output: {', '.join(_rel(w) for w in written)} at {DPI} dpi\n")
    f.write(f"- Env: python {sys.version.split()[0]}, pandas {pd.__version__}, "
            f"matplotlib {matplotlib.__version__}\n")
    f.write(f"- Platform: {platform.platform()}\n")

print(f"Wrote {', '.join(written)}")
print(f"Appended provenance to {log_path}")
print(f"\nTop by RF importance: {imp.sort_values('RF_SHAP', ascending=False).iloc[0]['label_v2']}")

# ------------------------------------------------------------------ NOTE
# fig_calibration currently labels both axes "(Positive class: 1)", which is
# scikit-learn's default. Changing it to "DLD" requires the out-of-fold
# probabilities, which primary_pipeline.py computes but never saves. To make that
# figure replottable, add this line to primary_pipeline.py after oof_prob is built:
#
#     pd.DataFrame({"y_true": y, "oof_prob": oof_prob}).to_csv(
#         f"{RESULTS}/oof_predictions.csv", index=False)
#
# then ROC, confusion matrix and calibration can all be redrawn without refitting.
