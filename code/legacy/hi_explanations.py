"""
EXPLORATORY / DISCUSSION ONLY — not for the paper.

Per-HI-child prediction explanations from BOTH models, plus an HI-group mean:
  * LASSO (C=0.1): contribution_j = coef_j * standardized_score_j  (log-odds units; sparse)
  * Random Forest: TreeExplainer SHAP values                       (probability units)

For each HI child: a two-panel figure (RF | LASSO), fixed feature order, colored by direction
(red = pushes toward DLD-like, teal = toward control-like). A final HI-group-mean comparison.

Caveats: n(HI)=16, provisional features, model never trained on HI -> explanations describe the
MODEL's reasoning, not ground truth; a feature pushing "DLD-like" may reflect genuine difficulty
OR a hearing-related artifact (e.g., nonword repetition). Interpret with the co-author.

Outputs (explore/):
  explore/hi_individual_explanations.pdf      -- one page per child + group-mean page
  explore/hi_individual/hi_explain_<ID>.png   -- per-child PNGs (for slides)
  explore/hi_groupmean_attribution.{pdf,png}  -- HI-group mean |attribution|, RF vs LASSO
  explore/hi_attributions_long.csv            -- per child x feature: RF SHAP + LASSO contribution
"""
import os, sys
import numpy as np, pandas as pd, sklearn
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import shap

SEED = 42; CHOSEN_C = 0.1
DATA = os.environ.get("DLD_DATA", "../Kopi af phd datasæt (samlet).xlsx")
OUT = "explore"; IND = f"{OUT}/hi_individual"
os.makedirs(IND, exist_ok=True)
RED, TEAL = "#c44e52", "#2a9d8f"

FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore","Non","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
PRETTY = {"LSPHUK":"CLPT word recall","LTaF":"Digit span forward","TROGB":"Grammar (TROG-2)",
          "LSPLRAE":"CLPT span","GåStop":"Go/Stop inhibition","verbfluantal":"Verbal fluency: correct",
          "verbfluskift":"Verbal fluency: switches","HimOpmscore":"Sky Search attention","Non":"Nonword recall",
          "LTaB":"Digit span backward","NIQ":"Nonverbal IQ","verbflusubkat":"Verbal fluency: subcat.",
          "OOU":"Odd-One-Out","verbfluintru":"Verbal fluency: intrusions","verbflupers":"Verbal fluency: persev.",
          "age":"Age"}
NAMES = FEATURES + ["age"]; LABELS = [PRETTY[n] for n in NAMES]

def load(p):
    df = (pd.read_csv(p, sep=";", decimal=",") if p.lower().endswith(".csv") else pd.read_excel(p, sheet_name=0))
    return df.replace({".": np.nan})
def design(sub):
    age = pd.to_numeric(sub["age"], errors="coerce").values
    return np.column_stack([sub[FEATURES].apply(pd.to_numeric, errors="coerce").values, age])

df = load(DATA)
train = df[df["Gruppe"].isin([1,2])].copy(); y = (train["Gruppe"]==1).astype(int).values
hi = df[df["Gruppe"]==0].copy()
Xtr, Xhi = design(train), design(hi); hi_ids = hi["ID"].values
print(f"train n={len(y)} | HI n={len(hi)}")

# ---- fit both models on DLD-vs-control ----
imp = SimpleImputer(strategy="median").fit(Xtr)
sc  = StandardScaler().fit(imp.transform(Xtr))
Xtr_s, Xhi_s = sc.transform(imp.transform(Xtr)), sc.transform(imp.transform(Xhi))

lasso = LogisticRegression(penalty="l1", solver="liblinear", C=CHOSEN_C,
                           class_weight="balanced", random_state=SEED).fit(Xtr_s, y)
rf = RandomForestClassifier(n_estimators=500, class_weight="balanced",
                            random_state=SEED, n_jobs=-1).fit(Xtr_s, y)

# LASSO contributions (log-odds): coef * standardized value
lasso_contrib = Xhi_s * lasso.coef_.ravel()            # (16, 16)
p_lasso = lasso.predict_proba(Xhi_s)[:,1]

# RF SHAP (probability units) for class 1
sv = shap.TreeExplainer(rf).shap_values(Xhi_s)
sv = sv[1] if isinstance(sv, list) else (sv[:,:,1] if np.ndim(sv)==3 else sv)
rf_shap = np.asarray(sv)                                # (16, 16)
p_rf = rf.predict_proba(Xhi_s)[:,1]

# fixed feature order = HI-group mean |RF SHAP|, descending (top at top of barh)
order = np.argsort(np.abs(rf_shap).mean(0))            # ascending -> barh puts largest on top
labels_o = [LABELS[i] for i in order]

# ---- long-format CSV ----
rows = []
for r, cid in enumerate(hi_ids):
    for j, n in enumerate(NAMES):
        rows.append({"ID":cid,"feature":n,"label":PRETTY[n],
                     "RF_shap":round(float(rf_shap[r,j]),4),
                     "LASSO_contrib":round(float(lasso_contrib[r,j]),4)})
pd.DataFrame(rows).to_csv(f"{OUT}/hi_attributions_long.csv", index=False)

def panel(ax, vals, title, xlabel):
    v = vals[order]; colors = [RED if x>0 else TEAL for x in v]
    ax.barh(range(len(v)), v, color=colors); ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(v))); ax.set_yticklabels(labels_o, fontsize=8)
    ax.set_title(title, fontsize=10); ax.set_xlabel(xlabel, fontsize=8)

def child_fig(r):
    cid = hi_ids[r]
    fig, ax = plt.subplots(1, 2, figsize=(11, 5.2))
    panel(ax[0], rf_shap[r], f"Random Forest (SHAP)   p={p_rf[r]:.2f}", "push toward DLD-like (prob.)")
    panel(ax[1], lasso_contrib[r], f"LASSO   p={p_lasso[r]:.2f}", "push toward DLD-like (log-odds)")
    ax[1].set_yticklabels([])
    agree = "agree" if (p_rf[r]>=.5)==(p_lasso[r]>=.5) else "DISAGREE"
    fig.suptitle(f"HI child {cid}   (models {agree})   —   red = DLD-like, teal = control-like",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    return fig

# ---- per-child PNGs + multipage PDF ----
with PdfPages(f"{OUT}/hi_individual_explanations.pdf") as pdf:
    # cover note
    fig = plt.figure(figsize=(11,5.2)); fig.text(0.5,0.6,"HI per-child prediction explanations",
        ha="center", fontsize=15, weight="bold")
    fig.text(0.5,0.45,"EXPLORATORY / DISCUSSION ONLY — provisional features, n=16, uncalibrated.\n"
        "Explanations describe the model's reasoning, not ground truth.\n"
        "Same feature order on every page (by HI-group mean |SHAP|).", ha="center", fontsize=9)
    pdf.savefig(fig); plt.close(fig)
    for r in np.argsort(-p_rf):                          # order pages most -> least DLD-like
        fig = child_fig(r); pdf.savefig(fig, bbox_inches="tight")
        fig.savefig(f"{IND}/hi_explain_{hi_ids[r]}.png", dpi=200, bbox_inches="tight"); plt.close(fig)
    # group-mean page
    figG, axG = plt.subplots(1, 2, figsize=(11, 5.2))
    panel(axG[0], np.abs(rf_shap).mean(0), "RF: HI-group mean |SHAP|", "mean |push| (prob.)")
    panel(axG[1], np.abs(lasso_contrib).mean(0), "LASSO: HI-group mean |contribution|", "mean |push| (log-odds)")
    axG[1].set_yticklabels([])
    for a in axG:  # group mean is magnitude only -> recolor neutral
        for b in a.patches: b.set_color("#4c72b0")
    figG.suptitle("HI-group mean attribution (what drives predictions across the HI group)", y=1.02, fontsize=11)
    figG.tight_layout(); pdf.savefig(figG, bbox_inches="tight")
    figG.savefig(f"{OUT}/hi_groupmean_attribution.png", dpi=300, bbox_inches="tight")
    figG.savefig(f"{OUT}/hi_groupmean_attribution.pdf", bbox_inches="tight"); plt.close(figG)

# console summary
disagree = [hi_ids[r] for r in range(len(hi_ids)) if (p_rf[r]>=.5)!=(p_lasso[r]>=.5)]
gm_rf = pd.Series(np.abs(rf_shap).mean(0), index=LABELS).sort_values(ascending=False)
gm_la = pd.Series(np.abs(lasso_contrib).mean(0), index=LABELS).sort_values(ascending=False)
print(f"Models disagree on classification for: {disagree if disagree else 'none'}")
print("HI-group top drivers — RF :", ", ".join(gm_rf.head(4).index))
print("HI-group top drivers — LASSO:", ", ".join(gm_la[gm_la>0].head(4).index))
print(f"\nenv: python {sys.version.split()[0]} | sklearn {sklearn.__version__} | shap {shap.__version__}")
print(f"Wrote {OUT}/hi_individual_explanations.pdf (+ per-child PNGs, group mean, long CSV).")
