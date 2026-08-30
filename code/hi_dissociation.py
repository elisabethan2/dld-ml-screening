"""
EXPLORATORY (explore/) — HI double-dissociation check:
do working-memory/grammar features vs the phonological feature (nonword repetition)
relate DIFFERENTLY to parent-reported language vs hearing severity (BEHL)?

Motivation: the screener weights digit span / CLPT / grammar and underweights nonword
repetition. Within the 16 HI children we ask whether the model's features track
parent-reported LANGUAGE difficulty while nonword repetition tracks HEARING severity
(BEHL) instead — a dissociation that would explain why model predictions are
hearing-independent (the model uses hearing-independent features by construction).

n = 16 (HI). EXPLORATORY, low-powered: Spearman, descriptive, NO multiple-comparison
correction (~56 correlations); hypothesis-generating only. Cognitive scores are
higher = better and parent difficulty is higher = worse, so genuine relationships appear
as NEGATIVE correlations.

Determinism: screener = LASSO(C=0.1), deterministic; correlations deterministic.
SEED = 42 recorded (no stochastic step).

Config via env: DLD_DATA.
Outputs (explore/): hi_dissociation_corr.csv, hi_fig_dissociation.{png,pdf}, hi_fig_dissociation_heatmap.{png,pdf}
"""
import os, sys, hashlib, platform, datetime, warnings
import numpy as np, pandas as pd, scipy
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
warnings.filterwarnings("ignore")

SEED=42
DATA=os.environ.get("DLD_DATA","data/phddataset_samlet_300626.xlsx")
OUT="explore"; os.makedirs(OUT,exist_ok=True)
FEATURES=["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
          "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
# features examined (label -> data column)
#EXAMINE=[("Digit span forward","LTaF"),("Digit span backward","LTaB"),
#         ("CLPT word recall","LSPHUK"),("CLPT listening span","LSPLRAE"),
#         ("Nonword serial recall","NonLRAE"),("Grammatical comprehension (TROG-2)","TROGB"),
#         ("Odd-One-Out","OOU"),("Verbal fluency (correct)","verbfluantal")]
EXAMINE = [("Digit span forward",                 "LTaF"),
           ("Digit span backward",                "LTaB"),
           ("CLPT word recall",                   "LSPHUK"),
           ("CLPT listening span",                "LSPLRAE"),
           ("Nonword serial recall",              "NonLRAE"),
           ("Grammatical comprehension (TROG-2)", "TROGB"),
           ("Response inhibition (Go/Stop)",      "GåStop"),
           ("Visuospatial WM (Odd-One-Out)",      "OOU"),
           ("Selective attention (Sky Search)",   "HimOpmscore_skala"),
           ("Nonverbal reasoning (Block Design)", "NIQ"),
           ("Verbal fluency: correct",            "verbfluantal"),
           ("Verbal fluency: switches",           "verbfluskift"),
           ("Verbal fluency: subcat.",            "verbflusubkat"),
           ("Verbal fluency: persev.",            "verbflupers"),
           ("Verbal fluency: intrusions",         "verbfluintru")]
DOMAINS={"Attention":range(18,27),"Hyperactivity":range(27,36),"Passivity":range(36,40),
         "Planning":range(40,43),"Memory":range(61,72),"Comprehension":range(72,77),
         "Speech":range(77,90),"Communication":range(90,93)}
LANG=list(range(72,77))+list(range(77,90))+list(range(90,93))
TARGETS=["Language","Speech","Comprehension","Communication","Memory","BEHL","model_prob"]

def sha(p):
    try:
        h=hashlib.sha256()
        with open(p,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

df=pd.read_excel(DATA,sheet_name=0).replace({".":np.nan})
qcols={int(float(c)):c for c in df.columns if str(c).strip().replace('.0','').isdigit()}
def diff(sub,items):
    c=[qcols[i] for i in items if i in qcols]; return (2-sub[c].apply(pd.to_numeric,errors="coerce")).mean(axis=1)

# screener -> model_prob for HI
tr=df[df["Gruppe"].isin([1,2])]; ytr=(tr["Gruppe"]==1).astype(int).values
hi=df[df["Gruppe"]==0].copy()
def design(s): return np.column_stack([s[FEATURES].apply(pd.to_numeric,errors="coerce").values,
                                       pd.to_numeric(s["Alder_mdr"],errors="coerce").values/12.0])
scr=Pipeline([("i",SimpleImputer(strategy="median")),("s",StandardScaler()),
              ("c",LogisticRegression(penalty="l1",solver="liblinear",C=0.1,class_weight="balanced",random_state=SEED))]).fit(design(tr),ytr)
hi["model_prob"]=scr.predict_proba(design(hi))[:,1]
hi["BEHL"]=pd.to_numeric(hi["BEHL"],errors="coerce")
for _,c in EXAMINE: hi[c]=pd.to_numeric(hi[c],errors="coerce")
hi["Language"]=diff(hi,LANG).values
for d,items in DOMAINS.items(): hi[d]=diff(hi,items).values

# correlation matrix
recs=[]
for lbl,col in EXAMINE:
    for tgt in TARGETS:
        m=hi[[col,tgt]].dropna(); r,p=stats.spearmanr(m[col],m[tgt])
        recs.append({"feature":lbl,"target":tgt,"r":round(r,3),"p":round(p,3),"n":len(m)})
corr=pd.DataFrame(recs)
corr.to_csv(f"{OUT}/hi_dissociation_corr.csv",index=False)
R=corr.pivot(index="feature",columns="target",values="r").reindex([l for l,_ in EXAMINE])[TARGETS]

# ---- Figure 1: focused dissociation (r with parent Language vs r with BEHL) ----
labels=[l for l,_ in EXAMINE]; x=np.arange(len(labels)); w=0.38
fig, ax = plt.subplots(figsize=(8.5, 7.5))
y = np.arange(len(labels))[::-1]; h = 0.38
ax.barh(y + h/2, R["Language"], h, label="vs parent-reported language",
        color="#c44e52", edgecolor="black", linewidth=0.5)
ax.barh(y - h/2, R["BEHL"], h, label="vs hearing severity (BEHL)",
        color="#4c72b0", edgecolor="black", linewidth=0.5, hatch="///")
ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9)
ax.set_xlim(-1, 1)
ax.set_xlabel("Spearman r  (higher test scores accompany lower difficulty and\n"
              "lower hearing loss, so expected associations are negative)")
ax.legend(fontsize=9, loc="lower left")


#fig,ax=plt.subplots(figsize=(10,5.2))
#ax.bar(x-w/2, R["Language"], w, label="vs parent-reported Language", color="#c44e52")
#ax.bar(x+w/2, R["BEHL"],     w, label="vs BEHL (hearing severity)",  color="#4c72b0")
#ax.bar(x-w/2, R["Language"], w, label="vs parent-reported language", color="#c44e52", edgecolor="black", linewidth=0.5)
#ax.bar(x+w/2, R["BEHL"],     w, label="vs hearing severity (BEHL)",  color="#4c72b0", edgecolor="black", linewidth=0.5, hatch="///")
#ax.axhline(0,color="k",lw=0.8); ax.set_xticks(x); ax.set_xticklabels(labels,rotation=30,ha="right",fontsize=9)
#ax.set_ylabel("Spearman r"); ax.set_ylim(-1,1)
#ax.set_title("HI children (n = 16): do features track language, or hearing?  (negative = related)",fontsize=11)
#ax.set_title("Children with hearing impairment (n = 15–16): do predictors track "
             #"language, or hearing?  (negative = related)", fontsize=11)
#ax.set_title("Children with hearing impairment (n = 15–16): do predictors track "
#             "language, or hearing?", fontsize=11)
#ax.set_ylabel("Spearman r  (higher test scores accompany lower difficulty,\n"
#              "so expected associations are negative)")
#ax.legend(fontsize=9,loc="lower right")
fig.tight_layout()
for e in ("png","pdf"): fig.savefig(f"{OUT}/hi_fig_dissociation.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)

# ---- Figure 2: full heatmap ----
TARGET_LABELS = ["Model probability" if t == "model_prob" else t for t in TARGETS]
fig,ax=plt.subplots(figsize=(9,5.5))
norm=TwoSlopeNorm(vmin=-1,vcenter=0,vmax=1)
im=ax.imshow(R.values,cmap="RdBu_r",norm=norm,aspect="auto")
ax.set_xticks(range(len(TARGETS))); ax.set_xticklabels(TARGET_LABELS, rotation=30, ha="right", fontsize=9)
#ax.set_xticks(range(len(TARGETS))); ax.set_xticklabels(TARGETS,rotation=30,ha="right",fontsize=9)
#ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels,fontsize=9)
for i in range(len(labels)):
    for j in range(len(TARGETS)):
        v=R.values[i,j]
        ax.text(j,i,f"{v:+.2f}",ha="center",va="center",fontsize=8,color="black" if abs(v)<0.55 else "white")
#ax.set_title("Children with hearing impairment (n = 15–16): predictor × outcome "
#             "correlations  (negative = related)", fontsize=11)
#ax.set_title("HI feature × target Spearman r (n = 16, exploratory)",fontsize=11)
#ax.set_title("Children with hearing impairment (n = 15–16): "
#             "predictor × outcome correlations", fontsize=11)
fig.colorbar(im,ax=ax,label="Spearman r",shrink=0.8)
fig.tight_layout()
for e in ("png","pdf"): fig.savefig(f"{OUT}/hi_fig_dissociation_heatmap.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)

# run log
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{OUT}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — explore/hi_dissociation.py\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | HI n={len(hi)} | SEED={SEED} (deterministic)\n")
    f.write(f"- Spearman feature×target; NO multiple-comparison correction (~{len(EXAMINE)*len(TARGETS)} tests); exploratory\n")
    f.write(f"- Key: Nonword serial recall vs BEHL r={R.loc['Nonword serial recall','BEHL']:.2f}; Digit span fwd vs Language r={R.loc['Digit span forward','Language']:.2f}; Grammatical comprehension vs Language r={R.loc['Grammatical comprehension (TROG-2)','Language']:.2f}\n")
    #f.write(f"- Key: Nonword rep vs BEHL r={R.loc['Nonword repetition','BEHL']:.2f}; Digit span fwd vs Language r={R.loc['Digit span forward','Language']:.2f}; Grammar vs Language r={R.loc['Grammar (TROG-2)','Language']:.2f}\n")
    f.write(f"- Env: python {sys.version.split()[0]}, sklearn (see primary), scipy {scipy.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")

print("=== feature x target Spearman r (HI, n=16) ===")
print(R.round(2).to_string())
print(f"\nWrote hi_dissociation_corr.csv + 2 figures to {OUT}/")

