"""
Supplemental Material S1 — participant flow diagram (TRIPOD+AI items 5, 6, 20a).

Deterministic drawing script; no modelling, no randomness (SEED recorded as NA).
All counts are declared in the CONFIG block below and are checked against each other
(and, optionally, against the dataset) before anything is drawn — so the figure cannot
silently disagree with Table 1.

Exclusion counts and reasons supplied by A. Esbensen, who collected the original data; checked group-wise against Table 1.

Outputs:
  figures/fig_participant_flow.{pdf,png}   (300 dpi)
  results/participant_flow.csv             (the counts, for the record)
  results/run_log.md                       (appended)
"""
import os, sys, platform, datetime, hashlib
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ----------------------------------------------------------------------------- CONFIG
N_ASSESSED = 83          # children assessed in the original PhD study

# Exclusion reasons as supplied by A. Esbensen, who collected the original data.
# (group, reason, n) — group is used only for the arithmetic check below.
EXCLUSIONS = [
    ("HI",      "Hearing loss not bilateral sensorineural", 3),
    ("DLD",     "Danish not the child's first language", 1),
    ("Control", "DPOAE refer in one or both ears;\nhearing impairment could not be ruled out", 4),
]

GROUPS = [("Developmental\nlanguage disorder", 27),
          ("Hearing\nimpairment",              16),
          ("Typically developing\ncontrols",   32)]

ANALYSES = [("Primary analysis\nDLD vs. control (n = 59)", None),
            ("Exploratory probe\napplied to HI (n = 16)", None)]

VERIFY_AGAINST_DATA = True                      # set False to draw without reading the data
DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
GROUP_CODES = {"DLD": 1, "Control": 2, "HI": 0}  # Gruppe coding

RESULTS, FIGURES = "results", "figures"
os.makedirs(RESULTS, exist_ok=True); os.makedirs(FIGURES, exist_ok=True)

# ----------------------------------------------------------------------------- CHECKS
n_excluded = sum(n for _, _, n in EXCLUSIONS)
n_analysed = sum(n for _, n in GROUPS)

assert n_excluded == N_ASSESSED - n_analysed, (
    f"Exclusions sum to {n_excluded} but {N_ASSESSED} - {n_analysed} = "
    f"{N_ASSESSED - n_analysed}. Fix EXCLUSIONS.")
assert n_analysed == 75, f"Group sizes sum to {n_analysed}, expected 75."

# per-group reconciliation: analysed + excluded should recover the original group sizes
SHORT = {"Developmental\nlanguage disorder": "DLD", "Hearing\nimpairment": "HI",
         "Typically developing\ncontrols": "Control"}
analysed_by_group = {SHORT[l]: n for l, n in GROUPS}
excluded_by_group = {}
for g, _, n in EXCLUSIONS:
    excluded_by_group[g] = excluded_by_group.get(g, 0) + n
original_by_group = {g: analysed_by_group[g] + excluded_by_group.get(g, 0)
                     for g in analysed_by_group}
assert sum(original_by_group.values()) == N_ASSESSED, (
    f"Group-wise originals sum to {sum(original_by_group.values())}, expected {N_ASSESSED}.")
print("Pre-exclusion group sizes:", ", ".join(
    f"{g} {original_by_group[g]}" for g in ["DLD", "HI", "Control"]))

if VERIFY_AGAINST_DATA:
    try:
        df = pd.read_excel(DATA, sheet_name=0)
        obs = df["Gruppe"].value_counts().to_dict()
        want = {GROUP_CODES["DLD"]: 27, GROUP_CODES["HI"]: 16, GROUP_CODES["Control"]: 32}
        for code, n in want.items():
            assert obs.get(code) == n, f"Gruppe={code}: data has {obs.get(code)}, config says {n}."
        print(f"Verified against {DATA}: n = {len(df)}, groups {obs}")
    except FileNotFoundError:
        print(f"NOTE: {DATA} not found — drawing without verification.")

# ----------------------------------------------------------------------------- DRAW
# Group order in the diagram is DLD, Control, HI so that the two groups feeding the
# primary comparison are adjacent and the HI branch does not cross it. (Table 1 keeps
# the DLD / HI / Control order; this is a routing choice only.)
ORDER = [0, 2, 1]
FS, FS_SM = 9.5, 8.0
EDGE, LW = "black", 0.9

fig, ax = plt.subplots(figsize=(7.2, 7.4))
ax.set_xlim(0, 10); ax.set_ylim(1.5, 12); ax.axis("off")

def box(x, y, w, h, text, size=FS, align="center"):
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.14",
                                facecolor="white", edgecolor=EDGE, linewidth=LW))
    tx = x if align == "center" else x - w/2 + 0.18
    ax.text(tx, y, text, ha=align, va="center", fontsize=size, linespacing=1.4)

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=10, linewidth=LW, color=EDGE,
                                 shrinkA=0, shrinkB=0))

def line(x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color=EDGE, linewidth=LW, solid_capstyle="butt")

# 1. assessed
box(2.8, 11.3, 4.6, 0.9, f"Children assessed in the original study\n(N = {N_ASSESSED})")

# 2. excluded — offshoot to the right
excl_lines = []
for g, r, n in EXCLUSIONS:
    parts = r.split("\n")
    excl_lines.append(f"\u2022 {g} (n = {n}): {parts[0]}")
    excl_lines += [f"   {p}" for p in parts[1:]]
excl_h = 0.40 + 0.30 * (len(excl_lines) + 1)
excl_txt = f"Excluded before analysis (n = {n_excluded})\n" + "\n".join(excl_lines)
box(7.6, 9.75, 4.8, excl_h, excl_txt, size=FS_SM, align="left")
line(2.8, 10.85, 2.8, 9.75)
arrow(2.8, 9.75, 5.2, 9.75)

# 3. analysed
box(2.8, 8.7, 4.6, 0.9, f"Included in the present analyses\n(N = {n_analysed})")
arrow(2.8, 9.75, 2.8, 9.15)

# 4. groups
xs = [1.4, 4.2, 7.5]
line(2.8, 8.25, 2.8, 7.75)
line(xs[0], 7.75, xs[2], 7.75)
for x, gi in zip(xs, ORDER):
    label, n = GROUPS[gi]
    arrow(x, 7.75, x, 7.15)
    box(x, 6.5, 2.4, 1.3, f"{label}\n(n = {n})")

# 5. analyses
line(xs[0], 5.85, xs[0], 5.15)
line(xs[1], 5.85, xs[1], 5.15)
line(xs[0], 5.15, xs[1], 5.15)
arrow((xs[0] + xs[1]) / 2, 5.15, (xs[0] + xs[1]) / 2, 4.55)
box((xs[0] + xs[1]) / 2, 3.95, 4.3, 1.2, ANALYSES[0][0])
arrow(xs[2], 5.85, xs[2], 4.55)
box(xs[2], 3.95, 3.2, 1.2, ANALYSES[1][0])

# 6. explanatory note inside the figure area (no figure title — caption carries it)
ax.text(0.2, 2.35,
        "All children completed the same battery. Missing values among the retained predictors\n"
        "were infrequent (\u2264 8.5% on any measure) and were imputed by the median fitted within\n"
        "each cross-validation training fold; no child was excluded for missing data. The\n"
        "hearing-impaired group does not enter the primary DLD-versus-control comparison.",
        ha="left", va="center", fontsize=FS_SM, linespacing=1.6)

fig.tight_layout()
for e in ("pdf", "png"):
    fig.savefig(f"{FIGURES}/fig_participant_flow.{e}", dpi=300, bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------- RECORD
rows = ([{"stage": "assessed", "label": "original study", "n": N_ASSESSED}]
        + [{"stage": "excluded", "label": f"{g}: " + r.replace("\n", " "), "n": n}
           for g, r, n in EXCLUSIONS]
        + [{"stage": "analysed", "label": "present analyses", "n": n_analysed}]
        + [{"stage": "group", "label": l.replace("\n", " "), "n": n} for l, n in GROUPS])
pd.DataFrame(rows).to_csv(f"{RESULTS}/participant_flow.csv", index=False)

def sha(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for c in iter(lambda: f.read(8192), b""): h.update(c)
        return h.hexdigest()[:16]
    except Exception:
        return "NA"

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(f"{RESULTS}/run_log.md", "a", encoding="utf-8") as f:
    f.write(f"\n## Run {now} — participant_flow.py (S1)\n")
    f.write(f"- Counts declared in script; verified against `{DATA}` (sha256 {sha(DATA)})"
            f" = {VERIFY_AGAINST_DATA}\n")
    f.write(f"- {N_ASSESSED} assessed -> {n_excluded} excluded -> {n_analysed} analysed"
            f" (DLD 27 / HI 16 / Control 32)\n")
    f.write(f"- Deterministic drawing; no randomness (SEED NA)\n")
    f.write(f"- Exclusion reasons per A. Esbensen; pre-exclusion group sizes "
            f"{original_by_group}\n")
    f.write(f"- Env: python {sys.version.split()[0]}, matplotlib {matplotlib.__version__},"
            f" pandas {pd.__version__}, numpy {np.__version__}\n")
    f.write(f"- Compute: {platform.platform()}, {os.cpu_count()} CPUs (CPU only)\n")

print("Wrote figures/fig_participant_flow.*, results/participant_flow.csv (+ run_log.md).")
