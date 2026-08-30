"""
Age-handling comparison for DLD vs Control classification.

Compares three feature-handling schemes on IDENTICAL cross-validation folds:
  (1) raw scores, no age           -- reference (ignores the confound)
  (2) raw scores + age as feature  -- transparent option
  (3) control-referenced age-residualized features, fit WITHIN each CV fold

Primary classifier: L1-penalized logistic regression (LASSO).
Secondary check:    Random Forest (to confirm conclusions aren't classifier-specific).

Author: (Elisabeth) | Seed = 42 | Internal validation only (no external test set).
"""
import sys, numpy as np, pandas as pd, sklearn
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate

SEED = 42
import os
DATA = os.environ.get("DLD_DATA", "../Kopi af phd datasæt (samlet).xlsx")
#DATA = "/mnt/project/Kopi_af_phd_datasæt_samlet.xlsx"

# --- 15 raw features mapping 1:1 onto the draft's Set-2 constructs ---
FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore","Non","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
BOUNDED = {"LSPHUK"}  # proportion score -> residual z can run extreme (flagged, not transformed)

# --- load, decode SPSS '.' missing marker, restrict to DLD(=1) vs Control(=0) ---
df = pd.read_excel(DATA, sheet_name=0).replace({".": np.nan})
df = df[df["Gruppe"].isin([1, 2])].copy()
y = (df["Gruppe"] == 1).astype(int).values          # 1 = DLD (positive), 0 = Control
age = pd.to_numeric(df["age"], errors="coerce").values
X_feat = df[FEATURES].apply(pd.to_numeric, errors="coerce").values
CONTROL_LABEL = 0

assert not np.isnan(age).any(), "age has missing values"
print(f"n = {len(y)}  (DLD={int(y.sum())}, Control={int((1-y).sum())})  features={len(FEATURES)}")


class ControlReferencedAgeNorm(BaseEstimator, TransformerMixin):
    """Residualize each feature on age using TRAIN-fold controls only, then drop the age column.
    X must have age as its LAST column."""
    def __init__(self, control_label=0, degree=1):
        self.control_label = control_label; self.degree = degree
    def fit(self, X, y):
        a = X[:, -1]; ctrl = (y == self.control_label)
        self.coef_, self.sd_ = [], []
        for j in range(X.shape[1] - 1):
            ok = ctrl & ~np.isnan(X[:, j])
            p = np.polyfit(a[ok], X[ok, j], self.degree)         # fit on training controls only
            self.coef_.append(p)
            self.sd_.append((X[ok, j] - np.polyval(p, a[ok])).std() or 1.0)
        return self
    def transform(self, X):
        a = X[:, -1]; out = np.empty((X.shape[0], X.shape[1] - 1))
        for j, (p, sd) in enumerate(zip(self.coef_, self.sd_)):
            out[:, j] = (X[:, j] - np.polyval(p, a)) / sd
        return out                                                # age column dropped


def make_clf(kind):
    if kind == "LASSO":
        return LogisticRegression(penalty="l1", solver="liblinear", C=1.0,
                                  class_weight="balanced", random_state=SEED)
    return RandomForestClassifier(n_estimators=500, class_weight="balanced",
                                  random_state=SEED, n_jobs=-1)

def pipe(scheme, kind):
    steps = []
    if scheme == "resid":
        steps.append(("agenorm", ControlReferencedAgeNorm(CONTROL_LABEL, degree=1)))
    steps += [("impute", SimpleImputer(strategy="median")),
              ("scale", StandardScaler()),
              ("clf", make_clf(kind))]
    return Pipeline(steps)

# design matrices per scheme (resid needs age appended as last col; scheme2 keeps age as a feature)
X_by_scheme = {
    "raw_noage": X_feat,
    "raw_plusage": np.column_stack([X_feat, age]),
    "resid": np.column_stack([X_feat, age]),
}
LABELS = {"raw_noage":"(1) raw, no age",
          "raw_plusage":"(2) raw + age feature",
          "resid":"(3) control-referenced residual"}

cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=SEED)  # SAME splits for all
scoring = ["balanced_accuracy", "roc_auc"]

print(f"\nenv: python {sys.version.split()[0]} | sklearn {sklearn.__version__} | "
      f"pandas {pd.__version__} | numpy {np.__version__}")
print("CV: repeated stratified 5-fold x20 (seed 42), identical folds across schemes\n")
print(f"{'classifier':10s} {'scheme':32s} {'BalAcc mean':>11s} {'[2.5,97.5]':>16s} {'AUC mean':>9s} {'[2.5,97.5]':>16s}")
print("-"*100)

results = {}
for kind in ["LASSO", "RF"]:
    for scheme in ["raw_noage","raw_plusage","resid"]:
        cvres = cross_validate(pipe(scheme, kind), X_by_scheme[scheme], y,
                               cv=cv, scoring=scoring, n_jobs=-1)
        ba, au = cvres["test_balanced_accuracy"], cvres["test_roc_auc"]
        results[(kind,scheme)] = (ba, au)
        print(f"{kind:10s} {LABELS[scheme]:32s} {ba.mean():11.3f} "
              f"[{np.percentile(ba,2.5):.2f},{np.percentile(ba,97.5):.2f}]  "
              f"{au.mean():9.3f} [{np.percentile(au,2.5):.2f},{np.percentile(au,97.5):.2f}]")

# --- age-importance check for scheme (2): does age dominate the LASSO solution? ---
p2 = pipe("raw_plusage","LASSO").fit(X_by_scheme["raw_plusage"], y)
coef = np.abs(p2.named_steps["clf"].coef_.ravel())
names = FEATURES + ["age"]
order = np.argsort(coef)[::-1]
age_rank = int(np.where(np.array(names)[order] == "age")[0][0]) + 1
print(f"\nAge-importance check (scheme 2, LASSO on full data):")
print(f"  age |coef| = {coef[-1]:.3f}; age ranks #{age_rank} of {len(names)} features")
print(f"  top 5: " + ", ".join(f"{names[i]}({coef[i]:.2f})" for i in order[:5]))

# --- curvature check: is a quadratic age term warranted? (control-only R^2 gain) ---
ctrl = (y == 0)
gains = []
for j,f in enumerate(FEATURES):
    xj = X_feat[ctrl, j]; a = age[ctrl]; ok = ~np.isnan(xj)
    if ok.sum() < 8: continue
    r1 = np.corrcoef(np.polyval(np.polyfit(a[ok],xj[ok],1),a[ok]), xj[ok])[0,1]**2
    r2 = np.corrcoef(np.polyval(np.polyfit(a[ok],xj[ok],2),a[ok]), xj[ok])[0,1]**2
    gains.append(r2-r1)
print(f"\nCurvature check: median R^2 gain from quadratic age = {np.median(gains):.03f} "
      f"(features with gain>0.05: {sum(g>0.05 for g in gains)}/{len(gains)}) -> linear adequate if small")
print(f"\nNote: LSPHUK is a bounded proportion; its residual z can be extreme (logit transform would be cleaner).")
