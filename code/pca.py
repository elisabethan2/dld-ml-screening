"""
PCA — group separation on the 15-measure battery (descriptive / supplementary).

Input : 15 predictors, all three groups (DLD, HI, Control); median-imputed then z-scored.
Output: PC1xPC2 scatter coloured by group + scree plot; loadings and variance CSVs.
PCA uses a full SVD solver -> deterministic; NO random seed needed (recorded in log).

Outputs:
  figures/fig_pca.{pdf,png}, figures/fig_pca_scree.{pdf,png}
  results/pca_variance.csv, results/pca_loadings.csv
  results/run_log.md (appended)
"""
import os, sys, hashlib, platform, datetime
import numpy as np, pandas as pd, sklearn
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
RESULTS, FIGURES = "results", "figures"
os.makedirs(RESULTS, exist_ok=True); os.makedirs(FIGURES, exist_ok=True)
FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
PRETTY = {"LSPHUK":"CLPT word recall","LTaF":"Digit span forward","TROGB":"Grammatical comprehension",
          "LSPLRAE":"CLPT listening span","GåStop":"Response inhibition","verbfluantal":"VF correct",
          "verbfluskift":"VF switches","HimOpmscore_skala":"Selective attention","NonLRAE":"Nonword serial recall",
          "LTaB":"Digit span backward","NIQ":"Nonverbal reasoning","verbflusubkat":"VF subcat.",
          "OOU":"Odd-One-Out (visuospatial WM)","verbfluintru":"VF intrusions","verbflupers":"VF persev."}

COLORS = {"DLD":"#c44e52","HI":"#6a4c93","Control":"#2a9d8f"}
# marker + colour + legend label per group; shape carries the distinction in greyscale
STYLE = {"DLD":     ("o", "#D55E00", "DLD"),
         "HI":      ("^", "#0072B2", "Hearing impairment"),
         "Control": ("s", "#009E73", "Control")}

def sha(path):
    try:
        h=hashlib.sha256()
        with open(path,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

df = pd.read_excel(DATA, sheet_name=0).replace({".":np.nan})
df["grp"]=df["Gruppe"].map({0:"HI",1:"DLD",2:"Control"})
X = df[FEATURES].apply(pd.to_numeric,errors="coerce").values
Xz = StandardScaler().fit_transform(SimpleImputer(strategy="median").fit_transform(X))
pca = PCA(svd_solver="full").fit(Xz)
scores = pca.transform(Xz)
ev = pca.explained_variance_ratio_
print(f"data={DATA} (sha256 {sha(DATA)}); n={len(df)}")
print(f"PC1 {ev[0]*100:.1f}%  PC2 {ev[1]*100:.1f}%  (cum {ev[:2].sum()*100:.1f}%)")

# variance + loadings CSVs
pd.DataFrame({"PC":[f"PC{i+1}" for i in range(len(ev))],
             "explained_var_ratio":np.round(ev,4),
             "cumulative":np.round(np.cumsum(ev),4)}).to_csv(f"{RESULTS}/pca_variance.csv",index=False)
pd.DataFrame(pca.components_[:3].T, index=[PRETTY[f] for f in FEATURES],
             columns=["PC1","PC2","PC3"]).round(3).to_csv(f"{RESULTS}/pca_loadings.csv")

# scatter PC1 x PC2
fig, ax = plt.subplots(figsize=(6.4,5.4))
#for g in ["Control","HI","DLD"]:
#    m=df["grp"].values==g

for g in ["Control","HI","DLD"]:
    m = df["grp"].values == g
    mk, col, lab = STYLE[g]
    ax.scatter(scores[m,0], scores[m,1], marker=mk, c=col, label=lab,
               s=60, alpha=0.8, edgecolor="white", linewidth=0.5)
    #ax.scatter(scores[m,0],scores[m,1],c=COLORS[g],label=g,s=55,alpha=0.85,edgecolor="white",linewidth=0.5)
ax.axhline(0,color="#cccccc",lw=0.8); ax.axvline(0,color="#cccccc",lw=0.8)
ax.set_xlabel(f"PC1 ({ev[0]*100:.1f}% variance)"); ax.set_ylabel(f"PC2 ({ev[1]*100:.1f}% variance)")
#ax.set_title("PCA of the cognitive-linguistic battery"); ax.legend()
ax.legend(loc="best", fontsize=9)
fig.tight_layout()
for e in ("pdf","png"): fig.savefig(f"{FIGURES}/fig_pca.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)

# scree
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(range(1,len(ev)+1),ev*100,color="#4c72b0")
ax.plot(range(1,len(ev)+1),np.cumsum(ev)*100,"-o",color="#c44e52",label="cumulative")
ax.set_xlabel("Principal component"); ax.set_ylabel("Variance explained (%)")
#ax.set_title("PCA scree plot"); ax.legend()
fig.tight_layout()
for e in ("pdf","png"): fig.savefig(f"{FIGURES}/fig_pca_scree.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)

now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{RESULTS}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — pca.py\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | 15 predictors, all 3 groups | median-impute + z-score\n")
    f.write(f"- PCA svd_solver=full (DETERMINISTIC; no seed) | PC1 {ev[0]*100:.1f}%, PC2 {ev[1]*100:.1f}%\n")
    f.write(f"- Env: python {sys.version.split()[0]}, sklearn {sklearn.__version__}, pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")
print("Wrote figures/fig_pca*, results/pca_variance.csv, pca_loadings.csv (+ run_log.md).")
