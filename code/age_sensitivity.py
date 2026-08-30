"""
Age-handling sensitivity analysis (supplementary) — DLD vs Control.

Compares three ways of handling age, using the LASSO primary model (nested C):
  (a) raw features + age as a covariate   [the primary scheme]
  (b) control-referenced residualization  [regress each feature on age in controls,
                                           within the training fold; age not a feature]
  (c) raw features, no age                [for completeness]

All settings inherit the primary pipeline: locked 15 features, age = Alder_mdr/12,
repeated stratified 5-fold x20, seed 42, nested-C grid 0.01-10. Internal validation only.

The residualization is fit WITHIN each CV training fold, on control cases only, so no
held-out information leaks. Residualization regression is deterministic; CV splits use seed 42.

Outputs:
  results/age_sensitivity.csv   (scheme | BalAcc [lo,hi] | AUC [lo,hi])
  results/run_log.md            (appended)
"""
import os, sys, hashlib, platform, datetime, warnings
import numpy as np, pandas as pd, sklearn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (RepeatedStratifiedKFold, StratifiedKFold,
                                     GridSearchCV, cross_validate)
warnings.filterwarnings("ignore")

SEED = 42
DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
RESULTS = "results"; os.makedirs(RESULTS, exist_ok=True)
C_GRID = np.logspace(-2, 1, 10)
N_SPLITS, N_REPEATS = 5, 20
FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]

def sha(path):
    try:
        h=hashlib.sha256()
        with open(path,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

class ControlResidualizer(BaseEstimator, TransformerMixin):
    """Regress each feature on age using CONTROL cases only (fit on the training fold),
    then return age-residualized features for all cases; age column is dropped."""
    def __init__(self, age_col=-1):
        self.age_col = age_col
    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        age = X[:, self.age_col]
        feats = np.delete(X, self.age_col, axis=1)
        controls = (np.asarray(y) == 0)
        ac = age[controls]
        self.coef_ = []
        for j in range(feats.shape[1]):
            slope, intercept = np.polyfit(ac, feats[controls, j], 1)  # deterministic
            self.coef_.append((slope, intercept))
        return self
    def transform(self, X):
        X = np.asarray(X, dtype=float)
        age = X[:, self.age_col]
        feats = np.delete(X, self.age_col, axis=1)
        out = np.empty_like(feats)
        for j, (slope, intercept) in enumerate(self.coef_):
            out[:, j] = feats[:, j] - (slope * age + intercept)
        return out

# ---- data ----
df = pd.read_excel(DATA, sheet_name=0).replace({".": np.nan})
df = df[df["Gruppe"].isin([1, 2])].copy()
y = (df["Gruppe"] == 1).astype(int).values
age = pd.to_numeric(df["Alder_mdr"], errors="coerce").values / 12.0
Xfeat = df[FEATURES].apply(pd.to_numeric, errors="coerce").values
X_full = np.column_stack([Xfeat, age])   # 15 features + age (last col)
X_noage = Xfeat                           # 15 features only
print(f"data={DATA} (sha256 {sha(DATA)}); n={len(y)} (DLD {int(y.sum())}, Control {int((1-y).sum())})")

def lasso_clf():
    return LogisticRegression(penalty="l1", solver="liblinear", class_weight="balanced", random_state=SEED)
def nested(pipe):
    inner = StratifiedKFold(N_SPLITS, shuffle=True, random_state=SEED)
    return GridSearchCV(pipe, {"clf__C": C_GRID}, cv=inner, scoring="roc_auc", n_jobs=1)

pipe_a = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler()), ("clf", lasso_clf())])
pipe_b = Pipeline([("impute", SimpleImputer(strategy="median")), ("resid", ControlResidualizer(age_col=-1)),
                   ("scale", StandardScaler()), ("clf", lasso_clf())])
pipe_c = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler()), ("clf", lasso_clf())])

outer = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
def ci(a): return (round(a.mean(),3), round(np.percentile(a,2.5),3), round(np.percentile(a,97.5),3))

schemes = [("(a) raw + age covariate", nested(pipe_a), X_full),
           ("(b) control-referenced residualization", nested(pipe_b), X_full),
           ("(c) raw, no age", nested(pipe_c), X_noage)]
rows = []
for name, est, X in schemes:
    cv = cross_validate(est, X, y, cv=outer, scoring=["balanced_accuracy", "roc_auc"], n_jobs=-1)
    ba, au = ci(cv["test_balanced_accuracy"]), ci(cv["test_roc_auc"])
    rows.append({"scheme": name, "BalAcc": ba[0], "BalAcc_lo": ba[1], "BalAcc_hi": ba[2],
                 "AUC": au[0], "AUC_lo": au[1], "AUC_hi": au[2]})
    print(f"{name:42s} BalAcc {ba[0]:.3f} [{ba[1]:.2f},{ba[2]:.2f}]   AUC {au[0]:.3f} [{au[1]:.2f},{au[2]:.2f}]")
pd.DataFrame(rows).to_csv(f"{RESULTS}/age_sensitivity.csv", index=False)

# ---- run log ----
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{RESULTS}/run_log.md", "a", encoding="utf-8") as f:
    f.write(f"\n## Run {now} — age_sensitivity.py\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | n={len(y)} | SEED={SEED}\n")
    f.write(f"- Schemes: (a) raw+age covariate; (b) control-referenced residualization (linear, controls-only, within-fold); (c) raw no age\n")
    f.write(f"- LASSO nested-C (grid {C_GRID.min():.2g}-{C_GRID.max():.2g}) | repeated stratified {N_SPLITS}-fold x{N_REPEATS}\n")
    for r in rows:
        f.write(f"  - {r['scheme']}: BalAcc {r['BalAcc']} [{r['BalAcc_lo']},{r['BalAcc_hi']}], AUC {r['AUC']} [{r['AUC_lo']},{r['AUC_hi']}]\n")
    f.write(f"- Env: python {sys.version.split()[0]}, sklearn {sklearn.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")
print(f"\nWrote {RESULTS}/age_sensitivity.csv (+ run_log.md).")
