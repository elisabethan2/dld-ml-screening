"""
Build a SYNTHETIC stand-in dataset with the same structure as the real study data.

WHY THIS EXISTS
---------------
The real dataset cannot be shared (sensitive data on children; restricted by the
consent given by participants' families and by Danish/EU data-protection law — see
data/README.md). Without some input file, none of the analysis code in this
repository can be executed by a reader, which makes the code impossible to inspect
in action, to test, or to reuse.

This script generates a fully artificial dataset that has:
  * the same file layout, sheet, column names, coding and value ranges as the real file;
  * per-group means and SDs taken from the published aggregate tables in results/
    (table1_demographics.csv, table2_group_comparison.csv);
  * a one-factor correlation structure calibrated to the published PC1 loadings
    (results/pca_loadings.csv), so the battery has the single dominant dimension
    reported in the paper;
  * a comparable amount and pattern of missing data.

WHAT IT IS NOT
--------------
It contains NO real participant data of any kind. Every row is drawn from a random
number generator. It reproduces the *shape* of the data, not the data. Numbers
produced by running the pipeline on this file will be in the right ballpark but will
NOT equal the values reported in the paper; only the real dataset reproduces those.
See data/README.md.

USAGE
-----
    python code/make_synthetic_data.py                 # writes to data/synthetic/
    python code/make_synthetic_data.py --seed 7        # a different draw
    python code/make_synthetic_data.py --out data/synthetic

Then run any analysis script against it, e.g.:

    DLD_DATA=data/synthetic/synthetic_dataset.xlsx python code/primary_pipeline.py
    DLD_DATA=data/synthetic/synthetic_dataset.xlsx \
      HI_LABELS=data/synthetic/hi_clinical_dldlike.csv \
      HI_AGEAMP=data/synthetic/hi_age_amplification.csv \
      python code/hi_exploration.py

OUTPUTS
-------
    <out>/synthetic_dataset.xlsx      main file (mirrors the real .xlsx)
    <out>/hi_clinical_dldlike.csv     HI clinical designation side file
    <out>/hi_age_amplification.csv    HI age-at-first-hearing-aid side file
    <out>/README.txt                  provenance stamp for the generated draw
"""
import argparse, datetime, os, sys
import numpy as np
import pandas as pd

# ---------------------------------------------------------------- constants shared with the pipeline
FEATURES = ["LSPHUK", "LTaF", "TROGB", "LSPLRAE", "GåStop", "verbfluantal", "verbfluskift",
            "HimOpmscore_skala", "NonLRAE", "LTaB", "NIQ", "verbflusubkat", "OOU",
            "verbfluintru", "verbflupers"]

# Table 2 label -> dataset column, used to read the published group means/SDs.
GROUP_CODE = {"DLD": 1, "HI": 0, "Control": 2}

# 5-15R parent-questionnaire item blocks (column names are the item numbers, as in the real file).
DOMAINS = {"Attention": range(18, 27), "Hyperactivity": range(27, 36), "Passivity": range(36, 40),
           "Planning": range(40, 43), "Memory": range(61, 72), "Comprehension": range(72, 77),
           "Speech": range(77, 90), "Communication": range(90, 93)}
LANG_ITEMS = list(DOMAINS["Comprehension"]) + list(DOMAINS["Speech"]) + list(DOMAINS["Communication"])
ALL_ITEMS = sorted({i for r in DOMAINS.values() for i in r})

# Measures that are counts of errors (higher = poorer) and are heavily zero-inflated.
ERROR_COUNTS = {"verbfluintru", "verbflupers"}
# Measures that must stay non-negative integers on the real scale.
INTEGER_MEASURES = {"LTaF", "LTaB", "LSPLRAE", "NonLRAE", "OOU", "TROGB", "GåStop", "NIQ",
                    "verbfluantal", "verbfluskift", "verbflusubkat", "HimOpmscore_skala",
                    "verbfluintru", "verbflupers"}
# LSPHUK is a proportion in 0-1.
PROPORTION_MEASURES = {"LSPHUK"}

# Approximate missingness actually observed (from the data dictionary / Table 2 n).
MISSING_RATE = {f: 0.013 for f in FEATURES}
MISSING_RATE["NIQ"] = 0.085


def parse_m_sd(cell):
    """'3.52 (0.57)' -> (3.52, 0.57)"""
    m, sd = str(cell).split("(")
    return float(m.strip()), float(sd.strip().rstrip(")"))


def load_targets(results_dir):
    """Read the published aggregate tables that define the synthetic distributions."""
    t1 = pd.read_csv(os.path.join(results_dir, "table1_demographics.csv"))
    t2 = pd.read_csv(os.path.join(results_dir, "table2_group_comparison.csv"))
    load = pd.read_csv(os.path.join(results_dir, "pca_loadings.csv"), index_col=0)
    var = pd.read_csv(os.path.join(results_dir, "pca_variance.csv"))

    demo = {r["Group"]: r for _, r in t1.iterrows()}
    stats = {}
    for _, r in t2.iterrows():
        col = r["variable"]
        stats[col] = {g: parse_m_sd(r[f"{g}_M_SD"]) for g in ("DLD", "HI", "Control")}

    # PC1 eigenvector -> one-factor loadings: lambda_j = v_j * sqrt(eigenvalue).
    # Table 2 and the PCA table list the measures in the same order.
    eigval = float(var.loc[var["PC"] == "PC1", "explained_var_ratio"].iloc[0]) * len(FEATURES)
    lam = load["PC1"].to_numpy()[: len(FEATURES)] * np.sqrt(eigval)
    lam = np.clip(lam, -0.95, 0.95)
    return demo, stats, lam


def one_factor_scores(rng, n, lam):
    """z_ij = lam_j * f_i + sqrt(1 - lam_j^2) * e_ij  -> unit-variance, PC1-like correlations."""
    f = rng.standard_normal(n)
    e = rng.standard_normal((n, len(lam)))
    return np.outer(f, lam) + e * np.sqrt(1.0 - lam ** 2)


def to_scale(z, mean, sd, col, rng):
    """Map standardized values onto the observed scale and enforce the real measure's range."""
    x = mean + sd * z
    if col in PROPORTION_MEASURES:
        return np.clip(x, 0.0, 1.0).round(3)
    if col in ERROR_COUNTS:
        # Error counts are zero-inflated; a normal draw is a poor model, so resample as Poisson
        # with the published mean, keeping the rank order induced by the latent factor.
        lamb = max(mean, 0.01)
        draw = np.sort(rng.poisson(lamb, size=len(x)))
        return draw[np.argsort(np.argsort(x))].astype(float)
    x = np.clip(x, 0, None)
    return np.round(x) if col in INTEGER_MEASURES else np.round(x, 2)


def make_group(rng, group, n, demo, stats, lam, id_prefix, start_id):
    z = one_factor_scores(rng, n, lam)
    out = {}
    for j, col in enumerate(FEATURES):
        mean, sd = stats[col][group]
        out[col] = to_scale(z[:, j], mean, sd, col, rng)

    d = demo[group]
    age_years = np.clip(rng.normal(d["Age_M"], d["Age_SD"], n), d["Age_min"], d["Age_max"])
    df = pd.DataFrame(out)
    df.insert(0, "ID", [f"{id_prefix}{i}" for i in range(start_id, start_id + n)])
    df.insert(1, "Gruppe", GROUP_CODE[group])
    df.insert(2, "Køn", np.where(rng.random(n) < d["Male_pct"] / 100.0, 1, 2))
    df.insert(3, "Alder_mdr", np.round(age_years * 12).astype(int))
    df.insert(4, "Aldersgruppe", np.clip(np.floor(age_years).astype(int) - 6, 1, 6))
    # The latent factor is kept out of the file; it is only used to build the questionnaire below.
    return df, z[:, FEATURES.index("TROGB")]


def add_questionnaire(rng, df, latent_difficulty):
    """5-15R items, present for the DLD and HI groups only (as in the real data).

    Coding follows the real file: 0 = passer godt, 1 = til en vis grad, 2 = passer ikke,
    and the analysis scripts read difficulty as (2 - value).
    """
    n = len(df)
    has_q = df["Gruppe"].isin([0, 1]).to_numpy()
    for item in ALL_ITEMS:
        # Language-domain items track the child's latent language difficulty; other domains do not.
        w = 0.85 if item in LANG_ITEMS else 0.15
        eta = w * latent_difficulty + np.sqrt(1 - w ** 2) * rng.standard_normal(n)
        vals = np.digitize(eta, [-0.45, 0.45]).astype(float)   # -> 0 / 1 / 2
        vals[~has_q] = np.nan
        df[item] = vals
    return df


def inject_missing(rng, df):
    for col, rate in MISSING_RATE.items():
        mask = rng.random(len(df)) < rate
        df.loc[mask, col] = np.nan
    return df


def main():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", default=os.path.join(here, "data", "synthetic"))
    ap.add_argument("--results", default=os.path.join(here, "results"))
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    demo, stats, lam = load_targets(args.results)
    os.makedirs(args.out, exist_ok=True)

    # Same group sizes as the analysed sample (Table 1): 27 DLD, 16 HI, 32 Control.
    dld, lat_dld = make_group(rng, "DLD", int(demo["DLD"]["n"]), demo, stats, lam, "S", 1)
    hi, lat_hi = make_group(rng, "HI", int(demo["HI"]["n"]), demo, stats, lam, "H", 1)
    ctrl, lat_ctrl = make_group(rng, "Control", int(demo["Control"]["n"]), demo, stats, lam, "K", 1)

    # Latent language difficulty (higher = more difficulty) drives the questionnaire.
    lat = np.concatenate([-lat_dld, -lat_hi, -lat_ctrl])
    df = pd.concat([dld, hi, ctrl], ignore_index=True)

    # BEHL: hearing level, HI group only. Independent of language difficulty by construction,
    # but linked to nonword recall — the dissociation the paper reports.
    behl = np.full(len(df), np.nan)
    is_hi = (df["Gruppe"] == 0).to_numpy()
    hearing = rng.normal(0, 1, is_hi.sum())
    behl[is_hi] = np.round(np.clip(45 + 15 * hearing, 20, 90), 1)
    df["BEHL"] = behl
    non = pd.to_numeric(df.loc[is_hi, "NonLRAE"], errors="coerce").to_numpy()
    order = np.argsort(np.argsort(-hearing))                    # worse hearing -> lower nonword recall
    df.loc[is_hi, "NonLRAE"] = np.sort(non)[order]

    df = add_questionnaire(rng, df, lat)
    df = inject_missing(rng, df)

    xlsx = os.path.join(args.out, "synthetic_dataset.xlsx")
    df.to_excel(xlsx, index=False, sheet_name="data")

    # HI side files, keyed by ID exactly like the real ones.
    hi_ids = df.loc[is_hi, "ID"].tolist()
    lang_diff = lat[is_hi]
    clinical = (lang_diff >= np.quantile(lang_diff, 1 - 6 / len(hi_ids))).astype(int)
    pd.DataFrame({"ID": hi_ids, "clinical_DLDlike": clinical}).to_csv(
        os.path.join(args.out, "hi_clinical_dldlike.csv"), index=False)
    pd.DataFrame({"ID": hi_ids,
                  "age_first_aid_years": np.round(rng.uniform(0.2, 6.0, len(hi_ids)), 2)}).to_csv(
        os.path.join(args.out, "hi_age_amplification.csv"), index=False)

    with open(os.path.join(args.out, "README.txt"), "w", encoding="utf-8") as f:
        f.write("SYNTHETIC DATA — NO REAL PARTICIPANTS\n")
        f.write("=====================================\n\n")
        f.write(f"Generated {datetime.datetime.now():%Y-%m-%d %H:%M:%S} by code/make_synthetic_data.py\n")
        f.write(f"seed = {args.seed} | numpy {np.__version__} | pandas {pd.__version__}\n\n")
        f.write("Every value in these files was drawn from a random number generator, calibrated to\n")
        f.write("the aggregate statistics published in results/ (Tables 1 and 2, PCA loadings).\n")
        f.write("They exist so that the analysis code can be executed and inspected without the\n")
        f.write("confidential dataset. Results computed from them do NOT reproduce the paper.\n")

    n_by_group = df["Gruppe"].value_counts().to_dict()
    print(f"wrote {xlsx}")
    print(f"  n={len(df)} (DLD {n_by_group.get(1)}, HI {n_by_group.get(0)}, Control {n_by_group.get(2)})"
          f" | {len(df.columns)} columns | seed {args.seed}")
    print(f"  + hi_clinical_dldlike.csv, hi_age_amplification.csv, README.txt in {args.out}")
    print("\nRun the pipeline against it with:")
    print(f"  DLD_DATA={os.path.relpath(xlsx, here)} python code/primary_pipeline.py")


if __name__ == "__main__":
    sys.exit(main())
