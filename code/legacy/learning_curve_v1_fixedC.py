"""
Learning curve — primary LASSO model, DLD vs Control (supports Sample Size section).

Model : L1 logistic regression (LASSO, C=0.1 = value chosen by nested CV in primary_pipeline).
CV    : repeated stratified 5-fold x20, seed 42; scoring = ROC-AUC.
Shows CV AUC as a function of training-set size; interpret whether performance has plateaued.

SEED = 42 (data shuffling / CV splits). Recorded below.

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
from sklearn.model_selection import RepeatedStratifiedKFold, learning_curve
warnings.filterwarnings("ignore")

SEED = 42
DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
RESULTS, FIGURES = "results", "figures"
os.makedirs(RESULTS, exist_ok=True); os.makedirs(FIGURES, exist_ok=True)
CHOSEN_C = 0.1
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
                 ("clf",LogisticRegression(penalty="l1",solver="liblinear",C=CHOSEN_C,
                                           class_weight="balanced",random_state=SEED))])
cv = RepeatedStratifiedKFold(n_splits=5,n_repeats=20,random_state=SEED)
train_sizes = np.linspace(0.3,1.0,8)
ts, train_sc, test_sc = learning_curve(pipe, X, y, cv=cv, scoring="roc_auc",
                                       train_sizes=train_sizes, n_jobs=-1, shuffle=True, random_state=SEED)
tr_m, tr_s = train_sc.mean(1), train_sc.std(1)
te_m, te_s = test_sc.mean(1), test_sc.std(1)
pd.DataFrame({"train_size":ts,"train_AUC":tr_m.round(3),"train_SD":tr_s.round(3),
             "cv_AUC":te_m.round(3),"cv_SD":te_s.round(3)}).to_csv(f"{RESULTS}/learning_curve.csv",index=False)
print("CV AUC by training size:", [f"{n}:{a:.3f}" for n,a in zip(ts,te_m)])

fig, ax = plt.subplots(figsize=(7,4.8))
ax.plot(ts,te_m,"-o",color="#4c72b0",label="Cross-validation AUC")
ax.fill_between(ts,te_m-te_s,te_m+te_s,alpha=0.15,color="#4c72b0")
ax.plot(ts,tr_m,"--o",color="#c44e52",label="Training AUC")
ax.fill_between(ts,tr_m-tr_s,tr_m+tr_s,alpha=0.10,color="#c44e52")
ax.set_xlabel("Training-set size (children)"); ax.set_ylabel("ROC-AUC")
#ax.set_title("Learning curve — primary LASSO (DLD vs Control)"); ax.set_ylim(0.5,1.02); ax.legend(loc="lower right")
fig.tight_layout()
for e in ("pdf","png"): fig.savefig(f"{FIGURES}/fig_learning_curve.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)

now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{RESULTS}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — learning_curve.py\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | n={len(y)} | SEED={SEED}\n")
    f.write(f"- LASSO C={CHOSEN_C} | repeated stratified 5-fold x20 | train sizes {train_sizes[0]:.2f}-{train_sizes[-1]:.2f}\n")
    f.write(f"- CV AUC range {te_m.min():.3f}->{te_m.max():.3f} across training sizes\n")
    f.write(f"- Env: python {sys.version.split()[0]}, sklearn {sklearn.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")
print("Wrote figures/fig_learning_curve.*, results/learning_curve.csv (+ run_log.md).")
