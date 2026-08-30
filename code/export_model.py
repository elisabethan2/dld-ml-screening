"""
Export the fitted primary model in a form someone else can actually apply.

The paper's Data Availability Statement promises "the trained model (as LASSO
coefficients)". Coefficients alone are not enough to score a new child: the model is
fitted on median-imputed, standardized predictors, so the imputation medians and the
standardization mean/SD are part of the model. This script writes all of them out.

The exported constants are aggregate summary statistics (medians, means, SDs over the
n = 59 DLD-vs-control sample). They contain no individual-level information and are
safe to publish alongside the code.

Requires the real dataset (see data/README.md). Run it once, on the same data and
environment as the locked primary run, and commit the two outputs:

    DLD_DATA=data/phddataset_samlet_300626.xlsx python code/export_model.py

Outputs:
    results/model_coefficients.csv   per-predictor: median, mean, SD, coefficient
    results/model_card.json          the same, machine-readable, plus intercept and metadata
    results/model_card.md            human-readable model card with a worked scoring example
"""
import datetime, hashlib, json, os, platform, sys
import numpy as np
import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GridSearchCV

SEED = 42
# Outputs always land in the repository's results/, whatever directory you run from.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.environ.get("DLD_DATA", os.path.join(REPO, "data", "phddataset_samlet_300626.xlsx"))
RESULTS = os.path.join(REPO, "results")
C_GRID = np.logspace(-2, 1, 10)
THRESHOLD = 0.5

FEATURES = ["LSPHUK", "LTaF", "TROGB", "LSPLRAE", "GåStop", "verbfluantal", "verbfluskift",
            "HimOpmscore_skala", "NonLRAE", "LTaB", "NIQ", "verbflusubkat", "OOU",
            "verbfluintru", "verbflupers"]
PRETTY = {"LSPHUK": "CLPT word recall", "LTaF": "Digit span forward", "TROGB": "Grammar (TROG-2)",
          "LSPLRAE": "CLPT span", "GåStop": "Go/Stop inhibition", "verbfluantal": "Verbal fluency: correct",
          "verbfluskift": "Verbal fluency: switches", "HimOpmscore_skala": "Sky Search attention",
          "NonLRAE": "Nonword recall (span)", "LTaB": "Digit span backward",
          "NIQ": "Nonverbal IQ (Block Design)", "verbflusubkat": "Verbal fluency: subcat.",
          "OOU": "Odd-One-Out", "verbfluintru": "Verbal fluency: intrusions",
          "verbflupers": "Verbal fluency: persev.", "age": "Age (years)"}


def sha(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for c in iter(lambda: f.read(8192), b""):
                h.update(c)
        return h.hexdigest()[:16]
    except OSError:
        return "NA"


def main():
    if not os.path.exists(DATA):
        print(f"ERROR: dataset not found at {DATA}\n", file=sys.stderr)
        print("This script needs the real study dataset, which is not distributed with the\n"
              "repository (see data/README.md). Point it at your copy with DLD_DATA:\n\n"
              "    DLD_DATA=/path/to/phddataset_samlet_300626.xlsx python code/export_model.py\n\n"
              "or place the file at data/phddataset_samlet_300626.xlsx in the repository root.\n"
              "To try the script without the real data, generate a synthetic stand-in first:\n\n"
              "    python code/make_synthetic_data.py\n"
              "    DLD_DATA=data/synthetic/synthetic_dataset.xlsx python code/export_model.py",
              file=sys.stderr)
        return 1

    os.makedirs(RESULTS, exist_ok=True)
    # Record the file name only — an absolute local path would leak directory structure
    # into published outputs.
    data_name = os.path.basename(DATA)
    df = pd.read_excel(DATA, sheet_name=0).replace({".": np.nan})
    df = df[df["Gruppe"].isin([1, 2])].copy()
    y = (df["Gruppe"] == 1).astype(int).values
    age = pd.to_numeric(df["Alder_mdr"], errors="coerce").values / 12.0
    X = np.column_stack([df[FEATURES].apply(pd.to_numeric, errors="coerce").values, age])
    names = FEATURES + ["age"]
    print(f"data={data_name} (sha256 {sha(DATA)}); n={len(y)} (DLD {int(y.sum())}, Control {int((1 - y).sum())})")

    def pipe(**kw):
        return Pipeline([("impute", SimpleImputer(strategy="median")),
                         ("scale", StandardScaler()),
                         ("clf", LogisticRegression(penalty="l1", solver="liblinear",
                                                    class_weight="balanced", random_state=SEED, **kw))])

    # Same nested-CV C selection as primary_pipeline.py, refit on the full sample.
    inner = StratifiedKFold(5, shuffle=True, random_state=SEED)
    search = GridSearchCV(pipe(), {"clf__C": C_GRID}, cv=inner, scoring="roc_auc", n_jobs=-1).fit(X, y)
    best_C = float(search.best_params_["clf__C"])
    fit = pipe(C=best_C).fit(X, y)
    print(f"chosen C (full-data refit) = {best_C:.4g}")

    medians = fit.named_steps["impute"].statistics_
    means = fit.named_steps["scale"].mean_
    sds = fit.named_steps["scale"].scale_
    coefs = fit.named_steps["clf"].coef_.ravel()
    intercept = float(fit.named_steps["clf"].intercept_[0])

    tbl = pd.DataFrame({"feature": names,
                        "label": [PRETTY[n] for n in names],
                        "impute_median": np.round(medians, 6),
                        "standardize_mean": np.round(means, 6),
                        "standardize_sd": np.round(sds, 6),
                        "coefficient": np.round(coefs, 6)})
    tbl["retained"] = tbl["coefficient"] != 0
    tbl.to_csv(f"{RESULTS}/model_coefficients.csv", index=False)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    card = {"model": "L1-regularized (LASSO) logistic regression",
            "outcome": "P(DLD) — 1 = DLD, 0 = typically developing control",
            "fitted_on": {"n": int(len(y)), "n_DLD": int(y.sum()), "n_control": int((1 - y).sum()),
                          "data_file": data_name, "data_sha256_16": sha(DATA)},
            "hyperparameters": {"penalty": "l1", "solver": "liblinear", "C": best_C,
                                "class_weight": "balanced", "seed": SEED},
            "preprocessing": "median imputation, then standardization (both fitted on the training sample)",
            "decision_threshold": THRESHOLD,
            "intercept": round(intercept, 6),
            "predictors": tbl.to_dict(orient="records"),
            "validation": "internal only — repeated stratified 5-fold CV, 20 repeats; no external validation",
            "intended_use": "research / model development. NOT validated for clinical decision-making.",
            "exported": now,
            "environment": {"python": sys.version.split()[0], "sklearn": sklearn.__version__,
                            "numpy": np.__version__, "pandas": pd.__version__,
                            "platform": platform.platform()}}
    with open(f"{RESULTS}/model_card.json", "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)

    kept = tbl[tbl["retained"]]
    with open(f"{RESULTS}/model_card.md", "w", encoding="utf-8") as f:
        f.write("# Model card — DLD screening classifier\n\n")
        f.write(f"Exported {now} from `{data_name}` (sha256 {sha(DATA)}) by `code/export_model.py`.\n\n")
        f.write("## Intended use\n\n")
        f.write("Research and model development. This is an internally validated development model "
                "trained on 59 Danish children (27 DLD, 32 control). It has **not** been externally "
                "validated and must not be used to make clinical decisions about a child.\n\n")
        f.write("## Specification\n\n")
        f.write(f"- L1-regularized logistic regression, `liblinear`, `C = {best_C:g}`, "
                f"`class_weight='balanced'`, seed {SEED}\n")
        f.write("- Predictors: the 15 locked cognitive-linguistic measures + chronological age in years\n")
        f.write("- Preprocessing: median imputation, then standardization, using the constants below\n")
        f.write(f"- Intercept: `{intercept:.6f}`\n")
        if intercept == 0:
            f.write("  (liblinear applies the L1 penalty to the intercept as well as the coefficients, "
                    "so an intercept of exactly zero is a property of the fitted model, not a missing "
                    "value. It means the model predicts P = 0.5 for a child at the sample mean on "
                    "every predictor.)\n")
        f.write(f"- Decision threshold: {THRESHOLD} (not clinically tuned)\n\n")
        f.write("## Scoring a new child\n\n")
        f.write("For each predictor *j*: replace a missing value with `impute_median`, then compute\n")
        f.write("`z = (value - standardize_mean) / standardize_sd`. Then\n\n")
        f.write("```\nlog-odds = intercept + sum_j (coefficient_j * z_j)\nP(DLD)   = 1 / (1 + exp(-log-odds))\n```\n\n")
        f.write(f"Predictors with a coefficient of 0 were dropped by the LASSO and can be ignored: "
                f"{len(kept)} of {len(tbl)} predictors are retained.\n\n")
        f.write("## Coefficients and preprocessing constants\n\n")
        f.write("| Predictor | Impute median | Mean | SD | Coefficient |\n")
        f.write("|---|---|---|---|---|\n")
        for _, r in tbl.iterrows():
            f.write(f"| {r['label']} (`{r['feature']}`) | {r['impute_median']:g} | "
                    f"{r['standardize_mean']:g} | {r['standardize_sd']:g} | {r['coefficient']:g} |\n")
        f.write("\nA negative coefficient means a *higher* score pushes the prediction toward control; "
                "on all measures except the two verbal-fluency error counts, higher = better performance.\n")

    with open(f"{RESULTS}/run_log.md", "a", encoding="utf-8") as f:
        f.write(f"\n## Run {now} — export_model.py\n")
        f.write(f"- Data: `{data_name}` (sha256 {sha(DATA)}) | n={len(y)} | SEED={SEED}\n")
        f.write(f"- Full-data refit of the primary LASSO; nested-CV C = {best_C:g}; intercept {intercept:.4f}; "
                f"{len(kept)}/{len(tbl)} predictors retained\n")
        f.write(f"- Wrote results/model_coefficients.csv, model_card.json, model_card.md\n")
        f.write(f"- Env: python {sys.version.split()[0]}, sklearn {sklearn.__version__}, "
                f"pandas {pd.__version__}, numpy {np.__version__}\n")

    print(f"retained {len(kept)}/{len(tbl)} predictors: {', '.join(kept['label'])}")
    print(f"wrote {RESULTS}/model_coefficients.csv, model_card.json, model_card.md (+ run_log.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
