"""
EXPLORATORY / DEMONSTRATION — NOT a confirmatory result.

HI clinical-application probe: train the DLD-vs-Control screener (primary LASSO),
then score each hearing-impaired (HI) child by predicted probability of being "DLD-like".

Status caveats (read before interpreting):
  * Provisional features (Non / HimOpmscore / CLPT mappings unconfirmed) and provisional
    DLD/HI definitions -> results may change after the co-author meeting.
  * The screener NEVER saw HI data, so probabilities are NOT calibrated for the HI group.
    Read them as relative rankings ("more vs less DLD-like"), not literal risks.
  * n(HI) = 16 -> any subgroup split is illustrative, not inferential.
  * Training scheme = simple/transparent: fit once on ALL DLD-vs-control data, apply to HI.

Outputs (in explore/ — keep OUT of the confirmatory results/figures):
  explore/hi_probe_distribution.{pdf,png}   -- HI predicted-probability distribution
  explore/hi_probe_scores.csv               -- per-child probability + DLD-like/control-like label
"""
import os, sys
import numpy as np, pandas as pd, sklearn
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

SEED = 42
DATA = os.environ.get("DLD_DATA", "../Kopi af phd datasæt (samlet).xlsx")
OUT = "explore"; os.makedirs(OUT, exist_ok=True)
CHOSEN_C = 0.1          # from the primary pipeline (nested-CV selection); keep consistent
THRESH = 0.5            # default decision threshold (provisional; not clinically tuned)

FEATURES = ["LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
            "HimOpmscore","Non","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"]

def load(path):
    df = (pd.read_csv(path, sep=";", decimal=",") if path.lower().endswith(".csv")
          else pd.read_excel(path, sheet_name=0))
    return df.replace({".": np.nan})

df = load(DATA)
def design(sub):
    age = pd.to_numeric(sub["age"], errors="coerce").values
    X = sub[FEATURES].apply(pd.to_numeric, errors="coerce").values
    return np.column_stack([X, age])

train = df[df["Gruppe"].isin([1, 2])].copy()           # DLD(1) + Control(2)
y = (train["Gruppe"] == 1).astype(int).values          # 1 = DLD
hi = df[df["Gruppe"] == 0].copy()                       # HI group
Xtr, Xhi = design(train), design(hi)
print(f"train (DLD+Control) n={len(y)} | HI n={len(hi)}")

# train the screener ONCE on all DLD-vs-control data, apply to HI
screener = Pipeline([("impute", SimpleImputer(strategy="median")),
                     ("scale", StandardScaler()),
                     ("clf", LogisticRegression(penalty="l1", solver="liblinear", C=CHOSEN_C,
                                                class_weight="balanced", random_state=SEED))])
screener.fit(Xtr, y)
p_hi = screener.predict_proba(Xhi)[:, 1]               # P(DLD-like) for each HI child

res = pd.DataFrame({"ID": hi["ID"].values, "p_DLD_like": np.round(p_hi, 3)})
res["classification"] = np.where(res["p_DLD_like"] >= THRESH, "DLD-like", "control-like")
res = res.sort_values("p_DLD_like", ascending=False).reset_index(drop=True)
res.to_csv(f"{OUT}/hi_probe_scores.csv", index=False)

n_dld = int((res["classification"] == "DLD-like").sum())
print(f"HI split @{THRESH}: DLD-like {n_dld}/{len(res)} ({100*n_dld/len(res):.0f}%), "
      f"control-like {len(res)-n_dld}/{len(res)}")
print(res.to_string(index=False))

# sanity reference: where do the training groups fall? (overlay medians)
p_dld = screener.predict_proba(Xtr[y == 1])[:, 1]
p_con = screener.predict_proba(Xtr[y == 0])[:, 1]

fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.hist(p_hi, bins=np.linspace(0, 1, 11), color="#6a4c93", edgecolor="white", alpha=0.85)
ax.axvline(THRESH, color="k", ls="--", lw=1, label=f"threshold = {THRESH}")
ax.axvline(np.median(p_con), color="#2a9d8f", ls=":", lw=2, label="control median (train)")
ax.axvline(np.median(p_dld), color="#e76f51", ls=":", lw=2, label="DLD median (train)")
ax.set_xlabel("Predicted probability of being DLD-like"); ax.set_ylabel("Number of HI children")
ax.set_title("HI clinical-application probe (DEMONSTRATION — provisional)\n"
             "DLD screener applied to hearing-impaired children; probabilities uncalibrated for HI")
ax.legend(fontsize=8, loc="upper center")
fig.tight_layout()
for ext in ("pdf", "png"):
    fig.savefig(f"{OUT}/hi_probe_distribution.{ext}", dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"\nenv: python {sys.version.split()[0]} | sklearn {sklearn.__version__}")
print(f"Wrote {OUT}/ (DEMONSTRATION outputs — keep separate from confirmatory results).")
