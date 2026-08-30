"""
Primary modeling pipeline — DLD vs Control screening (LOCKED feature set).

Confirmatory analysis only. HI probe / questionnaire work lives separately in explore/.

Model      : L1 logistic regression (LASSO), C by NESTED CV  +  Random Forest robustness check.
Features   : 15 raw measures standardized WITHIN each CV fold, + age (Alder_mdr/12) as covariate.
             Nonword = NonLRAE (span); attention = HimOpmscore_skala (external test-manual norms).
Validation : repeated stratified 5-fold x20, seed 42 (INTERNAL only; development study).

Outputs (overwrite; confirmatory now that the set is locked):
  results/primary_performance.csv, feature_importance.csv, minimal_battery.csv
  results/run_log.md    (APPENDED each run: date, seed, data hash, params, versions, results)
  results/run_info.json (latest run, machine-readable)
  figures/fig_roc_confusion, fig_calibration, fig_importance, fig_minimal_battery  (.pdf + .png)
"""
import os, sys, json, hashlib, platform, datetime, warnings
import numpy as np, pandas as pd, sklearn
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import (RepeatedStratifiedKFold, StratifiedKFold,
                                     GridSearchCV, cross_validate, cross_val_predict)
from sklearn.metrics import (roc_curve, auc, confusion_matrix, balanced_accuracy_score,
                             ConfusionMatrixDisplay)
from sklearn.calibration import CalibrationDisplay
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------- config
SEED = 42
DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
RESULTS, FIGURES = "results", "figures"
os.makedirs(RESULTS, exist_ok=True); os.makedirs(FIGURES, exist_ok=True)
C_GRID = np.logspace(-2, 1, 10)
N_SPLITS, N_REPEATS = 5, 20
RF_TREES = 500

# LOCKED feature set (15 measures); attention = external-norm skala, nonword = span
FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
PRETTY = {"LSPHUK":"CLPT word recall","LTaF":"Digit span forward","TROGB":"Grammar (TROG-2)",
          "LSPLRAE":"CLPT span","GåStop":"Go/Stop inhibition","verbfluantal":"Verbal fluency: correct",
          "verbfluskift":"Verbal fluency: switches","HimOpmscore_skala":"Sky Search attention",
          "NonLRAE":"Nonword recall (span)","LTaB":"Digit span backward","NIQ":"Nonverbal IQ (Block Design)",
          "verbflusubkat":"Verbal fluency: subcat.","OOU":"Odd-One-Out","verbfluintru":"Verbal fluency: intrusions",
          "verbflupers":"Verbal fluency: persev.","age":"Age"}

def savefig(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(f"{FIGURES}/{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)

def file_sha256(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""): h.update(chunk)
        return h.hexdigest()[:16]
    except Exception: return "NA"

# ---------------------------------------------------------------- load
df = pd.read_excel(DATA, sheet_name=0).replace({".": np.nan})
df = df[df["Gruppe"].isin([1, 2])].copy()
y = (df["Gruppe"] == 1).astype(int).values                 # 1 = DLD (positive)
age = pd.to_numeric(df["Alder_mdr"], errors="coerce").values / 12.0   # decimal age
Xfeat = df[FEATURES].apply(pd.to_numeric, errors="coerce").values
X = np.column_stack([Xfeat, age])
NAMES = FEATURES + ["age"]
print(f"data={DATA} (sha256 {file_sha256(DATA)})")
print(f"n={len(y)} (DLD={int(y.sum())}, Control={int((1-y).sum())}); features={len(FEATURES)}+age")

# ---------------------------------------------------------------- estimators (standardize WITHIN CV)
def lasso_pipe():
    return Pipeline([("impute", SimpleImputer(strategy="median")),
                     ("scale", StandardScaler()),
                     ("clf", LogisticRegression(penalty="l1", solver="liblinear",
                                                class_weight="balanced", random_state=SEED))])
def lasso_nested():
    inner = StratifiedKFold(N_SPLITS, shuffle=True, random_state=SEED)
    return GridSearchCV(lasso_pipe(), {"clf__C": C_GRID}, cv=inner, scoring="roc_auc", n_jobs=-1)
def rf_pipe():
    return Pipeline([("impute", SimpleImputer(strategy="median")),
                     ("scale", StandardScaler()),
                     ("clf", RandomForestClassifier(n_estimators=RF_TREES, class_weight="balanced",
                                                    random_state=SEED, n_jobs=-1))])

outer = RepeatedStratifiedKFold(n_splits=N_SPLITS, n_repeats=N_REPEATS, random_state=SEED)
def ci(a): return (round(a.mean(),3), round(np.percentile(a,2.5),3), round(np.percentile(a,97.5),3))

# ---------------------------------------------------------------- 1. headline performance
perf_rows = []
for name, est in [("LASSO (primary, nested C)", lasso_nested()), ("Random Forest (robustness)", rf_pipe())]:
    cv = cross_validate(est, X, y, cv=outer, scoring=["balanced_accuracy", "roc_auc"], n_jobs=-1)
    ba, au = ci(cv["test_balanced_accuracy"]), ci(cv["test_roc_auc"])
    perf_rows.append({"model": name, "BalAcc": ba[0], "BalAcc_lo": ba[1], "BalAcc_hi": ba[2],
                      "AUC": au[0], "AUC_lo": au[1], "AUC_hi": au[2]})
    print(f"{name:28s} BalAcc {ba[0]:.3f} [{ba[1]:.2f},{ba[2]:.2f}]   AUC {au[0]:.3f} [{au[1]:.2f},{au[2]:.2f}]")
pd.DataFrame(perf_rows).to_csv(f"{RESULTS}/primary_performance.csv", index=False)
best_C = float(lasso_nested().fit(X, y).best_params_["clf__C"])
print(f"Chosen LASSO C (full-data refit): {best_C:.4g}")

# ---------------------------------------------------------------- 2. OOF preds -> ROC / CM / calibration
oof_cv = StratifiedKFold(N_SPLITS, shuffle=True, random_state=SEED)
oof_prob = cross_val_predict(lasso_nested(), X, y, cv=oof_cv, method="predict_proba", n_jobs=-1)[:, 1]
oof_pred = (oof_prob >= 0.5).astype(int)
fpr, tpr, _ = roc_curve(y, oof_prob); roc_auc = auc(fpr, tpr)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
ax[0].plot(fpr, tpr, lw=2, label=f"LASSO (AUC = {roc_auc:.2f})"); ax[0].plot([0,1],[0,1],"k--",lw=1)
ax[0].set_xlabel("False positive rate"); ax[0].set_ylabel("True positive rate")
ax[0].set_title("ROC — DLD vs Control (out-of-fold)"); ax[0].legend(loc="lower right")
ConfusionMatrixDisplay(confusion_matrix(y, oof_pred), display_labels=["Control","DLD"]).plot(ax=ax[1], cmap="Blues", colorbar=False)
ax[1].set_title(f"Confusion matrix @0.5 (BalAcc={balanced_accuracy_score(y,oof_pred):.2f})")
savefig(fig, "fig_roc_confusion")
fig, ax = plt.subplots(figsize=(5.2, 5))
CalibrationDisplay.from_predictions(y, oof_prob, n_bins=5, ax=ax, name="LASSO")
ax.set_title("Calibration (out-of-fold, 5 bins)\nInterpret cautiously at n=59")
savefig(fig, "fig_calibration")

# ---------------------------------------------------------------- 3. feature importance (LASSO coef + RF SHAP + perm)
imp = pd.DataFrame({"feature": NAMES, "label": [PRETTY[n] for n in NAMES]})
lp = lasso_pipe().set_params(clf__C=best_C).fit(X, y)
imp["LASSO_coef"] = lp.named_steps["clf"].coef_.ravel()
rf = rf_pipe().fit(X, y)
Xts = rf.named_steps["scale"].transform(rf.named_steps["impute"].transform(X))
try:
    import shap
    sv = shap.TreeExplainer(rf.named_steps["clf"]).shap_values(Xts)
    sv = sv[1] if isinstance(sv, list) else (sv[:, :, 1] if sv.ndim == 3 else sv)
    imp["RF_SHAP"] = np.abs(sv).mean(axis=0); shap_ok = True; shap_ver = shap.__version__
except Exception as e:
    print(f"[SHAP unavailable: {e}; using RF impurity importance]")
    imp["RF_SHAP"] = rf.named_steps["clf"].feature_importances_; shap_ok = False; shap_ver = "none"
perm = permutation_importance(rf, X, y, scoring="roc_auc", n_repeats=30, random_state=SEED, n_jobs=-1)
imp["Perm_imp"] = perm.importances_mean
imp["abs_coef"] = imp["LASSO_coef"].abs()
imp = imp.sort_values("RF_SHAP", ascending=False).reset_index(drop=True)
imp.to_csv(f"{RESULTS}/feature_importance.csv", index=False)
fig, ax = plt.subplots(1, 2, figsize=(12, 5.5))
d = imp.sort_values("RF_SHAP")
ax[0].barh(d["label"], d["RF_SHAP"], color="#4c72b0")
ax[0].set_title(f"RF importance ({'mean |SHAP|' if shap_ok else 'impurity'})"); ax[0].set_xlabel("importance")
d2 = imp.sort_values("abs_coef"); cols = ["#c44e52" if v < 0 else "#55a868" for v in d2["LASSO_coef"]]
ax[1].barh(d2["label"], d2["LASSO_coef"], color=cols); ax[1].axvline(0, color="k", lw=0.8)
ax[1].set_title(f"LASSO coefficients (C={best_C:.3g})"); ax[1].set_xlabel("coefficient (+ = higher in DLD)")
savefig(fig, "fig_importance")
age_rank = int(imp.index[imp["feature"] == "age"][0]) + 1
print(f"Importance top = {imp.loc[0,'label']}; age ranks #{age_rank}/{len(NAMES)}")

# ---------------------------------------------------------------- 4. minimal battery (age always kept; select tests within CV)
age_idx = [len(FEATURES)]; test_idx = list(range(len(FEATURES)))
def minimal_pipe(k):
    pre = ColumnTransformer([("age", "passthrough", age_idx), ("sel", SelectKBest(f_classif, k=k), test_idx)])
    clf = LogisticRegression(penalty="l1", solver="liblinear", C=best_C, class_weight="balanced", random_state=SEED)
    return Pipeline([("impute", SimpleImputer(strategy="median")), ("select", pre),
                     ("scale", StandardScaler()), ("clf", clf)])
mb = []
for k in range(1, len(FEATURES) + 1):
    cv = cross_validate(minimal_pipe(k), X, y, cv=outer, scoring=["roc_auc","balanced_accuracy"], n_jobs=-1)
    a, b = ci(cv["test_roc_auc"]), ci(cv["test_balanced_accuracy"])
    mb.append({"k_tests": k, "AUC": a[0], "AUC_lo": a[1], "AUC_hi": a[2],
               "BalAcc": b[0], "BalAcc_lo": b[1], "BalAcc_hi": b[2]})
mb = pd.DataFrame(mb); mb.to_csv(f"{RESULTS}/minimal_battery.csv", index=False)
fig, ax = plt.subplots(figsize=(7, 4.8))
ax.plot(mb["k_tests"], mb["AUC"], "-o", color="#4c72b0", label="AUC")
ax.fill_between(mb["k_tests"], mb["AUC_lo"], mb["AUC_hi"], alpha=0.15, color="#4c72b0")
ax.axhline(mb["AUC"].iloc[-1], color="gray", ls="--", lw=1, label="full battery AUC")
ax.set_xlabel("Number of tests (age always included)"); ax.set_ylabel("AUC (repeated CV)")
ax.set_title("Minimal screening battery"); ax.set_ylim(0.5, 1.0); ax.legend(loc="lower right")
savefig(fig, "fig_minimal_battery")
print(f"Minimal battery: k=1 AUC={mb.AUC.iloc[0]:.3f}, k=2 AUC={mb.AUC.iloc[1]:.3f}, full={mb.AUC.iloc[-1]:.3f}")

# ---------------------------------------------------------------- run log (append) + run_info.json (latest)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
env = {"python": sys.version.split()[0], "sklearn": sklearn.__version__, "pandas": pd.__version__,
       "numpy": np.__version__, "shap": shap_ver}
compute = {"platform": platform.platform(), "processor": platform.processor() or "NA",
           "cpu_count": os.cpu_count(), "note": "scikit-learn CPU (no GPU used)"}
info = {"run_datetime": now, "seed": SEED, "data_file": DATA, "data_sha256_16": file_sha256(DATA),
        "n_total": int(len(y)), "n_DLD": int(y.sum()), "n_Control": int((1-y).sum()),
        "features": FEATURES, "age_field": "Alder_mdr/12", "cv": f"RepeatedStratifiedKFold {N_SPLITS}x{N_REPEATS}",
        "lasso": {"penalty": "l1", "C_grid": [round(float(c),4) for c in C_GRID], "chosen_C": best_C, "class_weight": "balanced"},
        "rf": {"n_estimators": RF_TREES, "class_weight": "balanced"},
        "performance": perf_rows, "minimal_battery_AUC": {"k1": float(mb.AUC.iloc[0]), "k2": float(mb.AUC.iloc[1]), "full": float(mb.AUC.iloc[-1])},
        "environment": env, "compute": compute}
with open(f"{RESULTS}/run_info.json", "w") as f: json.dump(info, f, indent=2, ensure_ascii=False)
with open(f"{RESULTS}/run_log.md", "a", encoding="utf-8") as f:
    f.write(f"\n## Run {now}\n")
    f.write(f"- Script: primary_pipeline.py | Seed: {SEED}\n")
    f.write(f"- Data: `{DATA}` (sha256 {file_sha256(DATA)}) | n={len(y)} (DLD {int(y.sum())}, Control {int((1-y).sum())})\n")
    f.write(f"- Features (15+age): {', '.join(FEATURES)} + age (Alder_mdr/12)\n")
    f.write(f"- CV: repeated stratified {N_SPLITS}-fold x{N_REPEATS} | LASSO C grid {C_GRID.min():.2g}-{C_GRID.max():.2g}, chosen C={best_C:.3g} | RF {RF_TREES} trees, balanced\n")
    f.write(f"- LASSO {perf_rows[0]['BalAcc']}/{perf_rows[0]['AUC']} | RF {perf_rows[1]['BalAcc']}/{perf_rows[1]['AUC']} (BalAcc/AUC)\n")
    f.write(f"- Minimal battery AUC: k1 {mb.AUC.iloc[0]}, k2 {mb.AUC.iloc[1]}, full {mb.AUC.iloc[-1]}\n")
    f.write(f"- Env: python {env['python']}, sklearn {env['sklearn']}, pandas {env['pandas']}, numpy {env['numpy']}, shap {env['shap']}\n")
    f.write(f"- Compute: {compute['platform']}, {compute['cpu_count']} CPUs ({compute['note']})\n")
print(f"\nWrote {RESULTS}/ (+ run_log.md, run_info.json) and {FIGURES}/ (.pdf + .png).")
