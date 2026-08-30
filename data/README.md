# Data

This directory is where the study data goes when the analysis is run. **It is empty
in the published repository, and it must stay that way** — `.gitignore` excludes
everything in `data/` except this file, so the dataset cannot be committed by
accident.

---

## 1. The data are not available

From the paper's Data Availability Statement:

> The data that support the findings of this study are not publicly available: they
> contain sensitive information about children, and their disclosure is restricted by
> the consent obtained from participants' families and by Danish data protection law.

The dataset holds individual-level cognitive, linguistic, audiological and
parent-report records for 75 children aged 7–12, together with their clinical group.
Even with direct identifiers removed, the combination of group, age in months, sex,
region, degree of hearing loss and a 15-measure test profile is close to unique for
each child.

The consent given by the participating families covers use of the data within the
research project. It does not cover onward disclosure, and this repository makes no
offer of access.

## 2. What is openly available instead

| What | Where |
|---|---|
| All analysis code | `code/` |
| Pinned software environment | `requirements.txt`, `docs/environment_freeze.txt` |
| The fitted model — coefficients, intercept, and the imputation and standardization constants needed to apply it | `results/model_coefficients.csv`, `results/model_card.md` |
| Dated run log with seeds, package versions and input-data hashes | `results/run_log.md`, `explore/run_log.md`, `results/run_info.json` |
| Group-level descriptive statistics for every measure (paper Tables 1 and 3) | `results/table1_demographics.csv`, `results/table2_group_comparison.csv` |
| Full variable-level data dictionary — every column, coding, units, % missing | `docs/data_dictionary.csv` |
| The result tables behind every figure and supplement | `results/`, `explore/` |
| A synthetic dataset with the same structure, so the code can be executed | generate with `code/make_synthetic_data.py` |

`docs/PAPER_FILE_MAP.md` maps each table and figure in the paper to the script and
output file that produce it.

## 3. Synthetic data — running the code without the real data

`code/make_synthetic_data.py` builds an artificial dataset with the same file layout,
column names, coding, value ranges, group sizes, per-group means/SDs and one-factor
correlation structure as the real data, calibrated to the aggregate tables in
`results/`. It contains **no real participant data** — every value is drawn from a
random number generator.

```bash
python code/make_synthetic_data.py
DLD_DATA=data/synthetic/synthetic_dataset.xlsx python code/primary_pipeline.py
```

Every script in `code/` runs against it. Results will be in the right ballpark but
will **not** equal the published numbers — only the real dataset reproduces those.
The synthetic files are not committed; regenerate them with the command above.

## 4. Expected file layout

If you are running the analysis on the real data, place the files here:

```
data/
  phddataset_samlet_300626.xlsx   main dataset (sheet 0)
  hi_clinical_dldlike.csv         ID, clinical_DLDlike        (HI group only)
  hi_age_amplification.csv        ID, age_first_aid_years     (HI group only)
```

Or point the scripts elsewhere with environment variables:

```bash
DLD_DATA=/secure/path/dataset.xlsx \
HI_LABELS=/secure/path/hi_clinical_dldlike.csv \
HI_AGEAMP=/secure/path/hi_age_amplification.csv \
python code/primary_pipeline.py
```

### Columns the scripts use

`docs/data_dictionary.csv` documents every column in the dataset. The analysis needs:

| Column | Meaning |
|---|---|
| `ID` | participant identifier (`S`/`H`/`K` + number) |
| `Gruppe` | group: `0` = hearing impaired, `1` = DLD, `2` = control |
| `Køn` | sex: `1` = boy, `2` = girl |
| `Alder_mdr` | age in months (decimal age = `Alder_mdr / 12`) |
| `BEHL` | best-ear hearing level in dB (HI group only) |
| the 15 predictors | `LSPHUK`, `LTaF`, `TROGB`, `LSPLRAE`, `GåStop`, `verbfluantal`, `verbfluskift`, `HimOpmscore_skala`, `NonLRAE`, `LTaB`, `NIQ`, `verbflusubkat`, `OOU`, `verbfluintru`, `verbflupers` |
| `18`–`92` | 5-15R parent-questionnaire items, column-named by item number (DLD and HI groups only; `0` = passer godt, `1` = til en vis grad, `2` = passer ikke) |

Missing values may be coded as `.`; the scripts convert them to `NaN`.

The locked primary run used a file with sha256 prefix `7aaf1d0e1375d9b8` — every
script prints the hash of its input, so a run can be checked against it.
