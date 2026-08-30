"""
Plot the main-text HI figure from committed explore/ outputs (plotting only; deterministic).

Panel A: model DLD-like probability vs parent-reported language difficulty (from hi_scores.csv),
         coloured by the (corrected) clinical DLD-like designation; 0.5 threshold marked.
Panel B: Spearman r of the model's key predictors with parent-reported language (red) and with
         hearing severity/BEHL (blue) (from hi_dissociation_corr.csv) — the feature-level dissociation.

No randomness (reads committed CSVs). Underlying model probabilities came from the seed-42 fit
recorded by hi_exploration.py. EXPLORATORY, n = 16.

Config via env: HI_SCORES, HI_DISSOC. Output: explore/hi_fig_main.{png,pdf}
"""
import os, warnings
import numpy as np, pandas as pd
from scipy import stats
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

HI_SCORES=os.environ.get("HI_SCORES","explore/hi_scores.csv")
HI_DISSOC=os.environ.get("HI_DISSOC","explore/hi_dissociation_corr.csv")
OUT="explore"; os.makedirs(OUT,exist_ok=True)
RED,TEAL,BLUE="#c44e52","#2a9d8f","#4c72b0"
KEY=["Digit span forward","CLPT word recall","Grammar (TROG-2)","Nonword repetition"]

s=pd.read_csv(HI_SCORES)
d=pd.read_csv(HI_DISSOC)

fig,ax=plt.subplots(1,2,figsize=(12,5.2),gridspec_kw={"width_ratios":[1,1.05]})

# Panel A: convergence
for lab,col,name in [(1,RED,"Clinically DLD-like"),(0,TEAL,"Clinically control-like")]:
    m=s[s.clinical_DLDlike==lab]
    ax[0].scatter(m["Language"],m["model_prob"],c=col,s=70,edgecolor="white",linewidth=0.6,label=name,zorder=3)
ax[0].axhline(0.5,color="k",ls="--",lw=1)
r,p=stats.spearmanr(s["Language"],s["model_prob"])
ax[0].set_xlabel("Parent-reported language difficulty (5-15R; 0–2, higher = more)")
ax[0].set_ylabel("Model DLD-like probability")
ax[0].set_title("A. Model probability vs parent-reported language",fontsize=11)
ax[0].legend(fontsize=8,loc="upper left")
ax[0].annotate(f"Spearman r = {r:.2f} (p = {p:.2f})",(0.03,0.03),xycoords="axes fraction",fontsize=9)

# Panel B: dissociation (signed r; negative = expected direction)
sub=d[d.feature.isin(KEY)].pivot(index="feature",columns="target",values="r").reindex(KEY)
x=np.arange(len(KEY)); w=0.38
ax[1].bar(x-w/2, sub["Language"], w, label="vs parent-reported language", color=RED)
ax[1].bar(x+w/2, sub["BEHL"],     w, label="vs hearing severity (BEHL)",  color=BLUE)
ax[1].axhline(0,color="k",lw=0.8); ax[1].set_ylim(-1,1)
ax[1].set_xticks(x); ax[1].set_xticklabels([k.replace(" (TROG-2)","").replace(" ","\n",1) for k in KEY],fontsize=8.5)
ax[1].set_ylabel("Spearman r  (negative = related)")
ax[1].set_title("B. What each predictor tracks: language, or hearing?",fontsize=11)
ax[1].legend(fontsize=8,loc="lower left")

#fig.suptitle("Exploratory application to children with hearing impairment (n = 16)",y=1.02,fontsize=11)
fig.tight_layout()
for e in ("png","pdf"): fig.savefig(f"{OUT}/hi_fig_main.{e}",dpi=300,bbox_inches="tight")
plt.close(fig)
print(f"Wrote {OUT}/hi_fig_main.png/.pdf | panel A r={r:.2f}; nonword vs BEHL={sub.loc['Nonword repetition','BEHL']:.2f}")
