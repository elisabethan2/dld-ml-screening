"""
EXPLORATORY (explore/) — HI clinical-application probe, consolidated on CORRECTED labels.

Merges the corrected clinical DLD-like labels and age-at-amplification with the screener's
DLD-like probabilities and the 5-15R questionnaire, and computes four analyses:

 INDEPENDENT of the clinical label (trustworthy):
  (1) model probability vs parent-reported questionnaire difficulty (per domain + language + total)
  (2a) model probability vs BEHL (unaided hearing severity)
  (2b) model probability vs age at first amplification
 INVOLVING the clinical label (report with the TROG-2 circularity caveat):
  (3) model vs clinician agreement (corrected labels)
  (4) questionnaire language difficulty vs corrected clinical label (independent instruments)

n = 16 (HI). All results EXPLORATORY and low-powered (Spearman, descriptive; no correction).
Coding: 5-15R difficulty = mean(2 - raw) per domain (higher = more difficulty).

Determinism: screener = LASSO(C=0.1), deterministic; correlations deterministic. SEED=42 recorded
(no stochastic step). Clinical labels are read from HI_LABELS, NOT the dataset column: they are
the clinical designations supplied by A. Esbensen (unpublished working table), which resolve a
known error in the dataset's own column for H11.

Config via env: DLD_DATA, HI_LABELS, HI_AGEAMP.
Outputs (explore/): hi_scores.csv, hi_correlations.csv, hi_agreement.csv,
                    hi_fig_domain_corr, hi_fig_language, hi_fig_behl, hi_fig_ageamp, hi_fig_combined (png+pdf)
"""
import os, sys, hashlib, platform, datetime, warnings
import numpy as np, pandas as pd, scipy
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
warnings.filterwarnings("ignore")

SEED=42
DATA=os.environ.get("DLD_DATA","data/phddataset_samlet_300626.xlsx")
HI_LABELS=os.environ.get("HI_LABELS","data/hi_clinical_dldlike.csv")
HI_AGEAMP=os.environ.get("HI_AGEAMP","data/hi_age_amplification.csv")
OUT="explore"; os.makedirs(OUT,exist_ok=True)
FEATURES=["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
          "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
DOMAINS={"Attention":range(18,27),"Hyperactivity":range(27,36),"Passivity":range(36,40),
         "Planning":range(40,43),"Memory":range(61,72),"Comprehension":range(72,77),
         "Speech":range(77,90),"Communication":range(90,93)}
LANG=list(DOMAINS["Comprehension"])+list(DOMAINS["Speech"])+list(DOMAINS["Communication"])
RED,TEAL="#D55E00","#0072B2"

def sha(p):
    try:
        h=hashlib.sha256()
        with open(p,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

df=pd.read_excel(DATA,sheet_name=0).replace({".":np.nan})
qcols={int(float(c)):c for c in df.columns if str(c).strip().replace('.0','').isdigit()}
def difficulty(sub,items):
    cols=[qcols[i] for i in items if i in qcols]
    return (2-sub[cols].apply(pd.to_numeric,errors="coerce")).mean(axis=1)

# ---- screener: train DLD vs control, predict HI ----
tr=df[df["Gruppe"].isin([1,2])].copy(); ytr=(tr["Gruppe"]==1).astype(int).values
hi=df[df["Gruppe"]==0].copy()
def design(s): return np.column_stack([s[FEATURES].apply(pd.to_numeric,errors="coerce").values,
                                       pd.to_numeric(s["Alder_mdr"],errors="coerce").values/12.0])
scr=Pipeline([("i",SimpleImputer(strategy="median")),("s",StandardScaler()),
              ("c",LogisticRegression(penalty="l1",solver="liblinear",C=0.1,class_weight="balanced",random_state=SEED))]).fit(design(tr),ytr)
hi=hi.assign(model_prob=scr.predict_proba(design(hi))[:,1])
hi["model_pred"]=(hi["model_prob"]>=0.5).astype(int)
hi["BEHL"]=pd.to_numeric(hi["BEHL"],errors="coerce")

# ---- merge corrected labels + age-at-amplification (by ID) ----
lab=pd.read_csv(HI_LABELS)[["ID","clinical_DLDlike"]]
amp=pd.read_csv(HI_AGEAMP)[["ID","age_first_aid_years"]]
hi=hi.merge(lab,on="ID",how="left").merge(amp,on="ID",how="left")
assert hi["clinical_DLDlike"].notna().all(), "missing corrected labels for some HI IDs"

# ---- questionnaire domain scores ----
for d,items in DOMAINS.items(): hi[d]=difficulty(hi,items).values
hi["Language"]=difficulty(hi,LANG).values
hi["Total"]=difficulty(hi,sorted(qcols)).values

# ---- per-child scores CSV ----
score_cols=["ID","model_prob","model_pred","clinical_DLDlike","BEHL","age_first_aid_years"]+list(DOMAINS)+["Language","Total"]
hi[score_cols].round(3).sort_values("model_prob",ascending=False).to_csv(f"{OUT}/hi_scores.csv",index=False)

# ---- correlations ----
def sp(a,b):
    m=hi[[a,b]].dropna(); r,p=stats.spearmanr(m[a],m[b]); return round(r,3),round(p,3),len(m)
rows=[]
for d in list(DOMAINS)+["Language","Total"]:
    r,p,n=sp("model_prob",d); rows.append({"analysis":"(1) model_prob vs questionnaire","variable":d,"r":r,"p":p,"n":n,"kind":"INDEPENDENT"})
for v,lbl in [("BEHL","(2a) model_prob vs BEHL"),("age_first_aid_years","(2b) model_prob vs age-at-amplification")]:
    r,p,n=sp("model_prob",v); rows.append({"analysis":lbl,"variable":v,"r":r,"p":p,"n":n,"kind":"INDEPENDENT"})
# (4) questionnaire language vs corrected clinical label
r,p,n=sp("clinical_DLDlike","Language"); rows.append({"analysis":"(4) clinical label vs questionnaire","variable":"Language","r":r,"p":p,"n":n,"kind":"label (indep. instruments)"})
corr=pd.DataFrame(rows); corr.to_csv(f"{OUT}/hi_correlations.csv",index=False)

# ---- (3) agreement on corrected labels ----
tab=pd.crosstab(hi["clinical_DLDlike"],hi["model_pred"])
agree=int((hi["clinical_DLDlike"]==hi["model_pred"]).sum()); N=len(hi)
pd.DataFrame({"metric":["n","agreement_n","agreement_pct",
             "clinDLD_modelDLD","clinDLD_modelCtrl","clinCtrl_modelDLD","clinCtrl_modelCtrl"],
     "value":[N,agree,round(100*agree/N,1),
              int(((hi.clinical_DLDlike==1)&(hi.model_pred==1)).sum()),
              int(((hi.clinical_DLDlike==1)&(hi.model_pred==0)).sum()),
              int(((hi.clinical_DLDlike==0)&(hi.model_pred==1)).sum()),
              int(((hi.clinical_DLDlike==0)&(hi.model_pred==0)).sum())]}).to_csv(f"{OUT}/hi_agreement.csv",index=False)

# ================= FIGURES =================
STYLE = [(1, "o", RED,  "Clinically DLD-like"),
         (0, "^", TEAL, "Clinically control-like")]

def scatter(ax,xcol,xlabel,title):
    for lab_, mk, col, name in STYLE:
        m=hi[hi.clinical_DLDlike==lab_]
        ax.scatter(m[xcol],m["model_prob"],marker=mk,c=col,s=60,
                   edgecolor="white",linewidth=0.6,label=name,zorder=3)
    ax.axhline(0.5,color="k",ls="--",lw=1)
    d=hi[[xcol,"model_prob"]].dropna(); r,p=stats.spearmanr(d[xcol],d["model_prob"])
    ax.set_xlabel(xlabel); ax.set_ylabel("Model DLD-like probability")
    ax.annotate(f"Spearman r = {r:.2f} (p = {p:.2f}, n = {len(d)})",(0.03,0.03),xycoords="axes fraction",fontsize=8)
def dombar(ax):
    d=corr[corr.analysis.str.startswith("(1)")].sort_values("r")
    ax.barh(d["variable"],d["r"],color=[RED if v>0 else "#888" for v in d["r"]])
    ax.axvline(0,color="k",lw=0.8); ax.set_xlim(-1,1)
    ax.set_xlabel("Spearman r with model probability")
    #; ax.set_title("Questionnaire domains vs model (HI, n = 16)",fontsize=10)

# separate figures
def save(fig,name):
    fig.tight_layout()
    for e in ("png","pdf"): fig.savefig(f"{OUT}/{name}.{e}",dpi=300,bbox_inches="tight")
    plt.close(fig)

f,a=plt.subplots(figsize=(6.2,5)); dombar(a); save(f,"hi_fig_domain_corr")
f,a=plt.subplots(figsize=(6.2,5)); scatter(a,"Language","Parent-reported language difficulty (0-2)","Model vs parent-reported language"); a.legend(fontsize=8); save(f,"hi_fig_language")
f,a=plt.subplots(figsize=(6.2,5)); scatter(a,"BEHL","BEHL — unaided hearing level (dB)","Model vs hearing severity"); save(f,"hi_fig_behl")
f,a=plt.subplots(figsize=(6.2,5)); scatter(a,"age_first_aid_years","Age at first amplification (years)","Model vs age at amplification"); save(f,"hi_fig_ageamp")

# combined 2x2
fig,ax=plt.subplots(2,2,figsize=(12,9.5))
scatter(ax[0,0],"Language","Parent-reported language difficulty (0-2)","A. Model vs parent-reported language"); ax[0,0].legend(fontsize=7)
dombar(ax[0,1]); ax[0,1].set_title("B. Questionnaire domains vs model")
scatter(ax[1,0],"BEHL","BEHL — unaided hearing level (dB)","C. Model vs hearing severity")
scatter(ax[1,1],"age_first_aid_years","Age at first amplification (years)","D. Model vs age at amplification")
#fig.suptitle("Exploratory application of the DLD screener to children with hearing impairment (n = 16)",y=1.01,fontsize=11)
save(fig,"hi_fig_combined")

# ---- run log ----
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{OUT}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — explore/hi_exploration.py\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | labels: `{HI_LABELS}` (sha {sha(HI_LABELS)}) | age-amp: `{HI_AGEAMP}` (sha {sha(HI_AGEAMP)})\n")
    f.write(f"- HI n={N} | SEED={SEED} (deterministic screener + correlations) | corrected clinical labels (H11 fixed)\n")
    f.write(f"- Agreement (corrected): {agree}/{N} ({round(100*agree/N,1)}%) — NOT independent (shares TROG-2)\n")
    f.write(f"- Env: python {sys.version.split()[0]}, sklearn (see primary), scipy {scipy.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")

print("=== correlations ==="); print(corr.to_string(index=False))
print(f"\nAgreement (corrected labels): {agree}/{N} ({round(100*agree/N,1)}%)")
print("crosstab (rows=clinical, cols=model):"); print(tab)
print(f"\nWrote hi_scores.csv, hi_correlations.csv, hi_agreement.csv + 5 figures (png/pdf) to {OUT}/")

