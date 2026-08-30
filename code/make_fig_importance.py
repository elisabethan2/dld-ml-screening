"""
Regenerate the feature-importance figure from committed results (plotting only).

Reads results/feature_importance.csv (written by primary_pipeline.py) and redraws
fig_importance with the LASSO-panel labels moved to the outer (right) edge, so the
feature labels no longer overlap the bars.

Deterministic (plotting from a fixed CSV); no randomness, no seed required.

Output: figures/fig_importance.{pdf,png}
"""
import os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = os.environ.get("IMPORTANCE_CSV", "results/feature_importance.csv")
FIGURES = "figures"; os.makedirs(FIGURES, exist_ok=True)
imp = pd.read_csv(CSV)
imp["abs_coef"] = imp["LASSO_coef"].abs()

fig, ax = plt.subplots(1, 2, figsize=(12.5, 5.6))
plt.subplots_adjust(wspace=0.45)

# --- left: RF importance (labels on left, bars grow right) ---
d = imp.sort_values("RF_SHAP")
ax[0].barh(d["label"], d["RF_SHAP"], color="#4c72b0")
ax[0].set_title("RF importance (mean |SHAP|)")
ax[0].set_xlabel("importance")

# --- right: LASSO coefficients (labels on RIGHT, bars grow left from 0) ---
d2 = imp.sort_values("abs_coef")
colors = ["#c44e52" if v < 0 else "#55a868" for v in d2["LASSO_coef"]]
ax[1].barh(d2["label"], d2["LASSO_coef"], color=colors)
ax[1].axvline(0, color="k", lw=0.8)
ax[1].yaxis.tick_right()                 # move tick labels to the outer edge
ax[1].yaxis.set_label_position("right")
ax[1].set_title("LASSO coefficients (C = 0.1)")
ax[1].set_xlabel("coefficient (+ = higher in DLD)")
# a little right padding so labels aren't clipped
xlo, xhi = ax[1].get_xlim()
ax[1].set_xlim(xlo, xhi + (xhi - xlo) * 0.02)

fig.tight_layout()
for e in ("pdf", "png"):
    fig.savefig(f"{FIGURES}/fig_importance.{e}", dpi=300, bbox_inches="tight")
plt.close(fig)
print(f"Wrote {FIGURES}/fig_importance.pdf/.png from {CSV}")
print("LASSO nonzero:", ", ".join(f"{r.label} ({r.LASSO_coef:.2f})"
      for _, r in imp[imp.LASSO_coef != 0].iterrows()))
