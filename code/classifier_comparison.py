"""
Supplementary all-classifier comparison (DLD vs control) on the LOCKED feature set.

Supports the main-text claim that a simple linear model suffices: four model families
are compared on the same 15 features + age, in the same repeated-stratified-CV pipeline
with within-fold standardization, each fairly tuned by nested CV.

Models: LASSO (L1-logistic, primary), Random Forest, SVM-RBF, Gradient Boosting.
Validation: repeated stratified 5-fold x 20 (100 outer folds), seed 42 (== primary_pipeline).
Tuning: inner 5-fold GridSearchCV (scoring = balanced accuracy) over a small grid per model;
        nested CV gives a performance ESTIMATE (not a single deployable hyperparameter).
Class weight: 'balanced' for LASSO/RF/SVM; Gradient Boosting has no class_weight (classes
        are near-balanced, 27:32) and is left unweighted (noted).
Metrics: balanced accuracy (primary), AUC, F1-macro; mean + 2.5-97.5 percentile bands across folds.

Determinism: SEED=42 for splits and RF/GB. SVM/LASSO deterministic given data. RF/GB values can
shift slightly across scikit-learn versions (as for the primary RF robustness check).

Config via env: DLD_DATA. Output: results/classifier_comparison.csv, results/run_log.md
"""
import os, sys, hashlib, platform, datetime, warnings
import numpy as np, pandas as pd, scipy, sklearn
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import RepeatedStratifiedKFold, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import balanced_accuracy_score, roc_auc_score, f1_score
warnings.filterwarnings("ignore")

SEED=42
DATA=os.environ.get("DLD_DATA","data/phddataset_samlet_300626.xlsx")
N_REPEATS=int(os.environ.get("N_REPEATS","20"))
OUT="results"; os.makedirs(OUT,exist_ok=True)
FEATURES=["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
          "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]

def sha(p):
    try:
        h=hashlib.sha256()
        with open(p,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

df=pd.read_excel(DATA,sheet_name=0).replace({".":np.nan})
d=df[df["Gruppe"].isin([1,2])].copy()
y=(d["Gruppe"]==1).astype(int).values
X=np.column_stack([d[FEATURES].apply(pd.to_numeric,errors="coerce").values,
                   pd.to_numeric(d["Alder_mdr"],errors="coerce").values/12.0])
print(f"n={len(y)} (DLD={int(y.sum())}, Control={int((y==0).sum())}); {X.shape[1]} predictors (15 + age)")

def pipe(clf): return Pipeline([("i",SimpleImputer(strategy="median")),("s",StandardScaler()),("c",clf)])
MODELS={
 "LASSO (L1-logistic)": (pipe(LogisticRegression(penalty="l1",solver="liblinear",class_weight="balanced",random_state=SEED)),
                         {"c__C":[0.01,0.1,1,10]}),
 "Random Forest":       (pipe(RandomForestClassifier(n_estimators=500,class_weight="balanced",random_state=SEED)),
                         {"c__max_depth":[None,3,5]}),
 "SVM (RBF)":           (pipe(SVC(kernel="rbf",class_weight="balanced",random_state=SEED)),
                         {"c__C":[0.1,1,10],"c__gamma":["scale","auto"]}),
 "Gradient Boosting":   (pipe(GradientBoostingClassifier(n_estimators=200,random_state=SEED)),
                         {"c__learning_rate":[0.05,0.1],"c__max_depth":[2,3]}),
}

outer=RepeatedStratifiedKFold(n_splits=5,n_repeats=N_REPEATS,random_state=SEED)
rows=[]
for name,(pl,grid) in MODELS.items():
    ba,au,f1=[],[],[]
    for tr,te in outer.split(X,y):
        gs=GridSearchCV(pl,grid,scoring="balanced_accuracy",cv=5,n_jobs=-1)
        gs.fit(X[tr],y[tr]); best=gs.best_estimator_
        pred=best.predict(X[te])
        if hasattr(best,"predict_proba"): score=best.predict_proba(X[te])[:,1]
        else: score=best.decision_function(X[te])
        ba.append(balanced_accuracy_score(y[te],pred))
        au.append(roc_auc_score(y[te],score))
        f1.append(f1_score(y[te],pred,average="macro"))
    def ci(v): v=np.array(v); return round(v.mean(),3),round(np.percentile(v,2.5),3),round(np.percentile(v,97.5),3)
    bam,bal,bah=ci(ba); aum,aul,auh=ci(au); f1m,f1l,f1h=ci(f1)
    rows.append({"Classifier":name,"BalAcc":bam,"BalAcc_lo":bal,"BalAcc_hi":bah,
                 "AUC":aum,"AUC_lo":aul,"AUC_hi":auh,"F1_macro":f1m,"F1_lo":f1l,"F1_hi":f1h})
    print(f"  {name:<22} BalAcc {bam:.3f} [{bal:.3f},{bah:.3f}]  AUC {aum:.3f} [{aul:.3f},{auh:.3f}]  F1 {f1m:.3f}")

res=pd.DataFrame(rows)
res.to_csv(f"{OUT}/classifier_comparison.csv",index=False)

now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{OUT}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — classifier_comparison.py (supplementary S3)\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | n={len(y)} (DLD {int(y.sum())}, Control {int((y==0).sum())}) | 15 features + age\n")
    f.write(f"- 4 models, nested CV (inner 5-fold GridSearchCV, balanced-accuracy); outer repeated stratified 5-fold x{N_REPEATS} ({N_REPEATS*5} folds); SEED={SEED}\n")
    f.write(f"- Env: python {sys.version.split()[0]}, scikit-learn {sklearn.__version__}, scipy {scipy.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only). NOTE: RF/GB may shift slightly across sklearn versions.\n")
print(f"\nWrote {OUT}/classifier_comparison.csv | sklearn {sklearn.__version__}")
