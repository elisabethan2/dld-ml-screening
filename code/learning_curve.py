"""
Learning curve (v2, adaptive C) — primary LASSO model, DLD vs Control.

Differs from v1: C is re-selected by NESTED CV within each training-set size
(GridSearchCV inner loop), so the model is not forced to over-regularize at small n.
This removes the degenerate all-zero-coefficient regime that pinned v1 at AUC=0.5.

CV     : outer = repeated stratified 5-fold x REPEATS, seed 42; inner = stratified 5-fold.
Scoring: ROC-AUC.  SEED = 42 (splits/shuffle). Recorded below.

Outputs:
  figures/fig_learning_curve.{pdf,png}
  results/learning_curve.csv
  results/run_log.md (appended)
"""
import os, sys, hashlib, platform, datetime, warnings
import numpy as np, pandas as pd, sklearn
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (RepeatedStratifiedKFold, StratifiedKFold,
                                     GridSearchCV, learning_curve)
warnings.filterwarnings("ignore")

SEED = 42
DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
RESULTS, FIGURES = "results", "figures"
os.makedirs(RESULTS, exist_ok=True); os.makedirs(FIGURES, exist_ok=True)
C_GRID = np.logspace(-2, 1, 10)
REPEATS = 20
FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]

def sha(path):
    try:
        h=hashlib.sha256()
        with open(path,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

df = pd.read_excel(DATA, sheet_name=0).replace({".":np.nan})
df = df[df["Gruppe"].isin([1,2])].copy()
y = (df["Gruppe"]==1).astype(int).values
age = pd.to_numeric(df["Alder_mdr"],errors="coerce").values/12.0
X = np.column_stack([df[FEATURES].apply(pd.to_numeric,errors="coerce").values, age])
print(f"data={DATA} (sha256 {sha(DATA)}); n={len(y)} (DLD {int(y.sum())}, Control {int((1-y).sum())})")

pipe = Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler()),
                 ("clf",LogisticRegression(penalty="l1",solver="liblinear",
                                           class_weight="balanced",random_state=SEED))])
inner = StratifiedKFold(5, shuffle=True, random_state=SEED)
estimator = GridSearchCV(pipe, {"clf__C": C_GRID}, cv=inner, scoring="roc_auc", n_jobs=1)  # nested C
outer = RepeatedStratifiedKFold(n_splits=5, n_repeats=REPEATS, random_state=SEED)
train_sizes = np.linspace(0.3, 1.0, 8)
ts, train_sc, test_sc = learning_curve(estimator, X, y, cv=outer, scoring="roc_auc",
                                       train_sizes=train_sizes, n_jobs=-1, shuffle=True, random_state=SEED)
tr_m, tr_s = train_sc.mean(1), train_sc.std(1)
te_m, te_s = test_sc.mean(1), test_sc.std(1)
pd.DataFrame({"train_size":ts,"train_AUC":tr_m.round(3),"train_SD":tr_s.round(3),
             "cv_AUC":te_m.round(3),"cv_SD":te_s.round(3)}).to_csv(f"{RESULTS}/learning_curve.csv",index=False)
print("CV AUC by training size:", [f"{int(n)}:{a:.3f}" for n,a in zip(ts,te_m)])

fig, ax = plt.subplots(figsize=(7,4.8))
ax.plot(ts,te_m,"-o",color="#4c72b0",label="Cross-validation AUC")
ax.fill_between(ts,te_m-te_s,te_m+te_s,alpha=0.15,color="#4c72b0")
ax.plot(ts,tr_m,"--o",color="#c44e52",label="Training AUC")
ax.fill_between(ts,tr_m-tr_s,tr_m+tr_s,alpha=0.10,color="#c44e52")
ax.set_xlabel("Training-set size (children)"); ax.set_ylabel("ROC-AUC")
#ax.set_title("Learning curve — LASSO with nested C selection (DLD vs Control)")
ax.set_ylim(0.5,1.02); ax.legend(loc="lower right")
fig.tight_layout()
for e in ("pdf","png"): fig.savefig(f"{FIGURES}/fig_learning_curve.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)

now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{RESULTS}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — learning_curve.py (v2, nested C)\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | n={len(y)} | SEED={SEED}\n")
    f.write(f"- LASSO with nested C selection (inner 5-fold, C grid {C_GRID.min():.2g}-{C_GRID.max():.2g}) | outer repeated stratified 5-fold x{REPEATS}\n")
    f.write(f"- Train sizes {train_sizes[0]:.2f}-{train_sizes[-1]:.2f} | CV AUC {te_m.min():.3f}->{te_m.max():.3f}\n")
    f.write(f"- Env: python {sys.version.split()[0]}, sklearn {sklearn.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")
print("Wrote figures/fig_learning_curve.*, results/learning_curve.csv (+ run_log.md).")
