"""
make_fig_hi_v2.py — Main-text HI figure (Figure 6), corrected terminology.

Supersedes make_fig_hi.py. Plotting only, from committed explore/ outputs. No model is
refitted, so the plotted values are identical to those already reported. Keep the original
make_fig_hi.py frozen: it is the code behind the previously circulated figure.

CHANGES vs v1
  1. Display labels updated (agreed with A. Esbensen, Aug 2026):
       "Grammar (TROG-2)"    -> "Grammatical comprehension"
       "Nonword repetition"  -> "Nonword serial recall"
     The CSV `feature` values are UNCHANGED, so KEYS below still match the data. Display
     text is held separately in DISPLAY — never rename the lookup keys, or the filter breaks.
  2. Hatching added to the BEHL series. JSLHR requires that figures with colour remain
     interpretable if printed in black and white; red vs blue alone would not survive.
  3. Per-feature n reported (digit span forward is n = 15 owing to one missing value;
     all others n = 16). Printed to stdout for the caption, and shown on the panel.
  4. Panel A annotation moved off the axis line.

Config via env: HI_SCORES, HI_DISSOC, HI_OUT
Output: explore/hi_fig_main_v2.{png,pdf} at 300 dpi (JSLHR minimum)

EXPLORATORY, n = 16. Correlations uncorrected for multiple comparisons.
"""
import os, sys, hashlib, datetime, warnings
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

# ------------------------------------------------------------------ config
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE) if os.path.basename(_HERE) == "code" else _HERE

HI_SCORES = os.environ.get("HI_SCORES", os.path.join(_ROOT, "explore", "hi_scores.csv"))
HI_DISSOC = os.environ.get("HI_DISSOC", os.path.join(_ROOT, "explore", "hi_dissociation_corr.csv"))
OUT = os.environ.get("HI_OUT", os.path.join(_ROOT, "explore"))
STEM = "hi_fig_main_v2"
os.makedirs(OUT, exist_ok=True)

RED, TEAL, BLUE = "#D55E00", "#0072B2", "#4c72b0"
LANG_C, BEHL_C = "0.35", "0.75" 
DPI = 300

# Lookup keys = values in the CSV `feature` column. Do not edit these.
KEYS = ["Digit span forward", "CLPT word recall", 'Grammatical comprehension (TROG-2)', 'Nonword serial recall']
# Display text, in the same order. Edit these freely.
DISPLAY = ["Digit span\nforward", "CLPT\nword recall",
           "Grammatical\ncomprehension", "Nonword\nserial recall"]


def sha16(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return "NA"


# ------------------------------------------------------------------ load
for p in (HI_SCORES, HI_DISSOC):
    if not os.path.exists(p):
        sys.exit(f"ERROR: {p} not found. Set HI_SCORES / HI_DISSOC, or run from the repo root.")

s = pd.read_csv(HI_SCORES)
d = pd.read_csv(HI_DISSOC)

missing = [k for k in KEYS if k not in set(d["feature"])]
if missing:
    sys.exit(f"ERROR: feature(s) not found in {HI_DISSOC}: {missing}\n"
             f"Available: {sorted(set(d['feature']))}\n"
             f"KEYS must match the CSV; change DISPLAY for label text instead.")

sub = d[d.feature.isin(KEYS)].pivot(index="feature", columns="target", values="r").reindex(KEYS)
nsub = d[d.feature.isin(KEYS)].pivot(index="feature", columns="target", values="n").reindex(KEYS)

# ------------------------------------------------------------------ plot
fig, ax = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1, 1.05]})

# Panel A — convergence with clinical designation
for lab, mk, col, name in [(1,"o",RED,"Clinically DLD-like"),
                           (0,"^",TEAL,"Clinically control-like")]:
#for lab, col, name in [(1, RED, "Clinically DLD-like"), (0, TEAL, "Clinically control-like")]:
    m = s[s.clinical_DLDlike == lab]
    ax[0].scatter(m["Language"], m["model_prob"], marker=mk, c=col, s=70,
                  edgecolor="white", linewidth=0.6, label=name, zorder=3)
ax[0].axhline(0.5, color="k", ls="--", lw=1)
r, p = stats.spearmanr(s["Language"], s["model_prob"])
ax[0].set_xlabel("Parent-reported language difficulty (5-15R; 0–2, higher = more)")
ax[0].set_ylabel("Model DLD-like probability")
#ax[0].set_title("A. Model probability vs parent-reported language", fontsize=11)
ax[0].set_title("A", loc="left", fontsize=11, fontweight="bold")
ax[0].legend(fontsize=8, loc="upper left")
ax[0].annotate(f"Spearman r = {r:.2f} (p = {p:.3f})", (0.60, 0.05),
               xycoords="axes fraction", fontsize=9)

# Panel B — feature-level dissociation (signed r; negative = expected direction)
x = np.arange(len(KEYS)); w = 0.38
ax[1].bar(x - w/2, sub["Language"], w, label="vs parent-reported language",
          color=LANG_C, edgecolor="black", linewidth=0.5)
ax[1].bar(x + w/2, sub["BEHL"], w, label="vs hearing severity (BEHL)",
          color=BEHL_C, edgecolor="black", linewidth=0.5, hatch="///")

ax[1].axhline(0, color="k", lw=0.8)
ax[1].set_ylim(-1, 1)
ax[1].set_xticks(x)
ax[1].set_xticklabels(DISPLAY, fontsize=8.5)
#ax[1].set_ylabel("Spearman r  (negative = related)")
ax[1].set_ylabel("Spearman r  (higher scores accompany lower difficulty and\n"
                 "lower hearing loss, so expected associations are negative)")
#ax[1].set_title("B. What each predictor tracks: language, or hearing?", fontsize=11)
ax[1].set_title("B", loc="left", fontsize=11, fontweight="bold")
ax[1].legend(fontsize=8, loc="upper left")  # upper left is empty; lower left collides with the n marker

# Flag the one feature with reduced n directly on the panel.
ns = nsub["Language"].astype(int)
if ns.nunique() > 1:
    for xi, k in enumerate(KEYS):
        if ns[k] != ns.max():
            ax[1].annotate(f"n = {ns[k]}", (xi, -0.88), ha="center", fontsize=8, color="0.25")

#fig.suptitle("Exploratory application to children with hearing impairment (n = 16)",
#             y=1.02, fontsize=11)
fig.tight_layout()

written = []
for e in ("png", "pdf"):
    path = os.path.join(OUT, f"{STEM}.{e}")
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    written.append(path)
plt.close(fig)

# ------------------------------------------------------------------ log
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(os.path.join(OUT, "replot_log.md"), "a", encoding="utf-8") as f:
    f.write(f"\n## HI figure replot {now}\n")
    f.write("- Script: make_fig_hi_v2.py (plotting only; no refit)\n")
    f.write(f"- Inputs: `{HI_SCORES}` (sha256 {sha16(HI_SCORES)}), "
            f"`{HI_DISSOC}` (sha256 {sha16(HI_DISSOC)})\n")
    f.write(f"- Output: {', '.join(written)} at {DPI} dpi\n")
    f.write(f"- Env: python {sys.version.split()[0]}, pandas {pd.__version__}, "
            f"matplotlib {matplotlib.__version__}\n")

# ------------------------------------------------------------------ caption numbers
print(f"Wrote {', '.join(written)}")
print(f"\nPanel A: Spearman r = {r:.2f}, p = {p:.3f}, n = {len(s)}")
print("\nPanel B (for the caption):")
for k, disp in zip(KEYS, DISPLAY):
    lang, behl = sub.loc[k, "Language"], sub.loc[k, "BEHL"]
    print(f"  {disp.replace(chr(10),' '):28s} language r = {lang:+.2f} | BEHL r = {behl:+.2f} | n = {ns[k]}")
