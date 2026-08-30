"""
Descriptives — Table 1 (demographics) and Table 2 (group comparison on the battery).

Groups: DLD, HI, Control (all three).
Table 2: raw scores; Kruskal-Wallis omnibus (Holm-corrected across the 15 measures)
         + epsilon-squared effect size [eps2 = H/(n-1); Tomczak & Tomczak, 2014]
         + Dunn's pairwise post-hoc (Holm-corrected within each measure).
No randomness in this script (descriptive statistics + rank tests) -> no seed needed.

Outputs:
  results/table1_demographics.csv
  results/table2_group_comparison.csv
  results/run_log.md  (appended)
"""
import os, sys, hashlib, platform, datetime
import numpy as np, pandas as pd, scipy
from scipy import stats

DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
RESULTS = "results"; os.makedirs(RESULTS, exist_ok=True)

FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore_skala","NonLRAE","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]
PRETTY = {"LSPHUK":"CLPT word recall","LTaF":"Digit span forward","TROGB":"Grammar (TROG-2)",
          "LSPLRAE":"CLPT span","GåStop":"Go/Stop inhibition","verbfluantal":"Verbal fluency: correct",
          "verbfluskift":"Verbal fluency: switches","HimOpmscore_skala":"Sky Search attention",
          "NonLRAE":"Nonword recall (span)","LTaB":"Digit span backward","NIQ":"Nonverbal IQ (Block Design)",
          "verbflusubkat":"Verbal fluency: subcat.","OOU":"Odd-One-Out","verbfluintru":"Verbal fluency: intrusions",
          "verbflupers":"Verbal fluency: persev."}
GROUPS = [("DLD",1),("HI",0),("Control",2)]

def sha(path):
    try:
        h=hashlib.sha256()
        with open(path,"rb") as f:
            for c in iter(lambda:f.read(8192),b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception: return "NA"

def holm(pvals):
    p=np.asarray(pvals,float); m=len(p); order=np.argsort(p); adj=np.empty(m); prev=0.0
    for rank,idx in enumerate(order):
        v=min((m-rank)*p[idx],1.0); v=max(v,prev); adj[idx]=v; prev=v
    return adj

def dunn(groups):   # groups in fixed order; returns dict of pair->p (uncorrected)
    clean=[np.asarray(g,float) for g in groups]; clean=[g[~np.isnan(g)] for g in clean]
    allv=np.concatenate(clean); N=len(allv); ranks=stats.rankdata(allv)
    _,counts=np.unique(allv,return_counts=True); ties=np.sum(counts**3-counts)
    var_base=(N*(N+1)/12.0) - ties/(12.0*(N-1))
    mr=[]; ns=[]; idx=0
    for g in clean:
        n=len(g); mr.append(ranks[idx:idx+n].mean()); ns.append(n); idx+=n
    out={}
    for (i,j) in [(0,2),(0,1),(1,2)]:   # DLD-Con, DLD-HI, HI-Con
        se=np.sqrt(var_base*(1.0/ns[i]+1.0/ns[j])); z=(mr[i]-mr[j])/se
        out[(i,j)]=2*(1-stats.norm.cdf(abs(z)))
    return out

df = pd.read_excel(DATA, sheet_name=0).replace({".":np.nan})
df["grp"]=df["Gruppe"].map({0:"HI",1:"DLD",2:"Control"})
print(f"data={DATA} (sha256 {sha(DATA)}); n={len(df)}")

# ---- Table 1: demographics ----
age=pd.to_numeric(df["Alder_mdr"],errors="coerce")/12.0
niq=pd.to_numeric(df["NIQ"],errors="coerce")
t1=[]
for name,code in GROUPS:
    s=df["Gruppe"]==code; n=int(s.sum()); male=int((df.loc[s,"Køn"]==1).sum())
    t1.append({"Group":name,"n":n,"Male_n":male,"Male_pct":round(100*male/n,1),
               "Age_M":round(age[s].mean(),2),"Age_SD":round(age[s].std(),2),
               "Age_min":round(age[s].min(),1),"Age_max":round(age[s].max(),1),
               "NIQ_M":round(niq[s].mean(),1),"NIQ_SD":round(niq[s].std(),1)})
pd.DataFrame(t1).to_csv(f"{RESULTS}/table1_demographics.csv",index=False)
print("Table 1 written.")

# ---- Table 2: group comparison ----
kw_p=[]; rows=[]
for f in FEATURES:
    v=pd.to_numeric(df[f],errors="coerce")
    g={name:v[df["Gruppe"]==code].dropna().values for name,code in GROUPS}
    H,p=stats.kruskal(g["DLD"],g["HI"],g["Control"]); kw_p.append(p)
    n_test = len(g["DLD"]) + len(g["HI"]) + len(g["Control"])   # non-missing N entering this KW test
    eps2 = H / (n_test - 1)                                     # epsilon-squared (Tomczak & Tomczak, 2014); 0-1
    dn=dunn([g["DLD"],g["HI"],g["Control"]])
    dn_holm=holm([dn[(0,2)],dn[(0,1)],dn[(1,2)]])   # within-measure Holm over 3 pairs
    rows.append({"Measure":PRETTY[f],"variable":f,
        "DLD_M_SD":f"{g['DLD'].mean():.2f} ({g['DLD'].std():.2f})",
        "HI_M_SD":f"{g['HI'].mean():.2f} ({g['HI'].std():.2f})",
        "Control_M_SD":f"{g['Control'].mean():.2f} ({g['Control'].std():.2f})",
        "n_test":n_test,"KW_H":round(H,2),"KW_p":p,"epsilon2":round(eps2,3),
        "Dunn_DLDvsControl_p_holm":round(dn_holm[0],4),
        "Dunn_DLDvsHI_p_holm":round(dn_holm[1],4),
        "Dunn_HIvsControl_p_holm":round(dn_holm[2],4)})
kw_holm=holm(kw_p)
for r,ph in zip(rows,kw_holm): r["KW_p_holm15"]=round(ph,4); r["KW_p"]=round(r["KW_p"],4)
cols=["Measure","variable","DLD_M_SD","HI_M_SD","Control_M_SD","n_test","KW_H","KW_p","KW_p_holm15","epsilon2",
      "Dunn_DLDvsControl_p_holm","Dunn_DLDvsHI_p_holm","Dunn_HIvsControl_p_holm"]
pd.DataFrame(rows)[cols].to_csv(f"{RESULTS}/table2_group_comparison.csv",index=False)
print("Table 2 written.")

# ---- run log ----
now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{RESULTS}/run_log.md","a",encoding="utf-8") as f:
    f.write(f"\n## Run {now} — descriptives.py\n")
    f.write(f"- Data: `{DATA}` (sha256 {sha(DATA)}) | groups DLD/HI/Control | no randomness (no seed)\n")
    f.write(f"- Table 1 (demographics) + Table 2 (15 measures: Kruskal-Wallis + epsilon-squared effect size [H/(n-1)], Holm across 15; Dunn's pairwise, Holm within measure)\n")
    f.write(f"- Env: python {sys.version.split()[0]}, pandas {pd.__version__}, numpy {np.__version__}, scipy {scipy.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")
print("Wrote results/table1_demographics.csv, table2_group_comparison.csv (+ run_log.md).")
