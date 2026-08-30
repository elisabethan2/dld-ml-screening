# Pre-publication checklist

Status of this repository against what the manuscript promises. The repository is
currently **private**; nothing here has been disclosed yet.

Legend: **[x]** done in this repository · **[ ]** still requires action

---

## A. Blocking — must be resolved before the repository goes public

### A1. Publish from a fresh repository (per-child figures must not reach the public history)

`explore/hi_individual/hi_explain_H*.png` (16 files) and
`explore/hi_individual_explanations.pdf` were **individual-level participant outputs**:
one figure per hearing-impaired child, keyed to that child's study ID, showing their
predicted DLD-like probability and their profile across all 15 measures. Publishing
them would contradict the Data Availability Statement.

- [x] Deleted from the working tree
- [x] `.gitignore` blocks them and the per-child CSVs from being re-added
- [x] `explore/README.md` records why they are gone
- [ ] **They are still in this repository's history**, and a clone retrieves them.
      The plan is to publish from a **new repository with a single clean commit**,
      leaving this one private as the working archive. Full procedure:
      **[`docs/PUBLISHING.md`](PUBLISHING.md)**. Do it last, once everything below
      is done — whatever is in the working tree at that point becomes the public
      repository's first commit.

### A2. Restore what was removed for anonymisation

Review is **single-blind**: reviewers see the authors, so nothing in the manuscript or
the repository needs to be anonymised. The repository can be public from the start and
its URL goes straight into the Data Availability Statement.

Four markers remain in the 29 Aug manuscript:

- [ ] **Sample Size** — "all children assessed in a prior PhD project ... *(reference
      removed for anonymization)*". Restore the PhD reference; it is the provenance of
      the convenience sample and a reviewer will want it.
- [ ] **Acknowledgments / patient involvement** — "data collected during the doctoral
      project of *[name and reference removed for anonymization]*". Restore the name
      and reference.
- [ ] **Funding** — "The original data collection was supported by *(Removed for
      anonymization)*". Restore the Oticon Foundation and grant 12-4105. Check while
      you are there that the second sentence ("the present secondary analysis received
      no specific grant") is still accurate, since funder reporting depends on it.
- [ ] **Predictors** — restore the three battery references describing the tasks. They
      are methodological citations for the section a reviewer scrutinises most closely.

Repository-side:

- [x] A. Esbensen's name restored in the run logs and script docstrings. It had been
      replaced with a role description while masked review was assumed; under
      single-blind that served no purpose, and naming the researcher who collected the
      data and agreed the corrected terminology is the accurate provenance.

### A3. Fill in the placeholders

Search the tree for `TODO`:

- [x] `README.md` — paper title and journal filled in; the two DOIs now read "to be
      added" rather than TODO
- [x] `LICENSE` — copyright held by the three authors
- [x] `CITATION.cff` — authors, ORCIDs, affiliations and journal filled in
- [ ] The three remaining `TODO`s are the DOIs and the release date in `CITATION.cff`.
      They do not exist until the Zenodo release; fill them at step 6 of
      `docs/PUBLISHING.md`, using the **concept** DOI so later versions do not
      invalidate the citation printed in the article.
- [ ] `data/README.md` — no placeholders remain; it now states unavailability only
      and offers no access route, matching the paper's Data Availability Statement

### A4. Export the fitted model

The Data Availability Statement promises "the trained model (as LASSO coefficients)".
`results/feature_importance.csv` has the coefficients but not the intercept, nor the
imputation medians and standardization constants — without those the model cannot be
applied to a new child. `code/export_model.py` produces all of it.

- [x] `code/export_model.py` written and tested
- [ ] Run it once on the real dataset and commit the outputs. The script resolves
      `results/` relative to the repository, so it works from any directory; point
      `DLD_DATA` at wherever your copy of the dataset actually lives:

      ```bash
      DLD_DATA=/path/to/phddataset_samlet_300626.xlsx python code/export_model.py
      ```

      → `results/model_coefficients.csv`, `results/model_card.json`, `results/model_card.md`

      Only the file *name* and its sha256 are recorded in the outputs, never the full path.

### A5. Commit the aggregate outputs behind Supplements S6 and S9

`code/make_fig_hi.py` reads `explore/hi_scores.csv` and
`explore/hi_dissociation_corr.csv`, and neither is in the repository, so the main-text
hearing-impairment figure cannot currently be regenerated from what is published.

- [ ] Commit `explore/hi_dissociation_corr.csv` (Supplement S9), `explore/hi_correlations.csv`
      (Supplement S6) and `explore/hi_agreement.csv` — all aggregate, all safe
- [ ] Do **not** commit `explore/hi_scores.csv` — it is one row per child. Either keep
      `make_fig_hi.py` panel A dependent on restricted data and say so, or commit a
      version with the ID column dropped and rows shuffled, if you judge that
      acceptable for n = 16

## B. Data availability — what is now in place

- [x] `data/README.md`: why the data cannot be shared (consent + GDPR/Danish Data
      Protection Act) and what is openly available instead. It offers no access
      route, so it commits the institution to nothing and needs no sign-off
- [x] `code/make_synthetic_data.py`: generates an artificial dataset with the same
      structure, group sizes, per-group means/SDs and one-factor correlation structure,
      calibrated to the published aggregate tables. Every script in `code/` was verified
      to run against it end to end
- [x] `docs/data_dictionary.csv`: every column, coding, units, missingness (already present)
- [x] Group-level descriptives for all 15 measures (`results/table1_*`, `table2_*`)
- [x] `data/` locked down in `.gitignore` — nothing but the README can be committed there
- [x] No institutional sign-off needed: `data/README.md` states unavailability and
      makes no offer of access, so it commits SDU to nothing

## C. Repository hygiene — done

- [x] `README.md`: what the study is, data availability up front, quick start, script
      table, reproducibility, model, citation, licence
- [x] `LICENSE` (MIT for code, CC BY 4.0 for docs/figures/tables)
- [x] `CITATION.cff`
- [x] `requirements.txt` replaced with an installable pinned file (the previous version
      was a 259-line conda `pip freeze` in which most entries pointed at
      `file:///home/conda/...` build paths and could not be installed by anyone else).
      The original freeze is kept as `docs/environment_freeze.txt`
- [x] Superseded scripts moved to `code/legacy/` with a README explaining what
      supersedes what
- [x] Hardcoded absolute paths removed from `code/make_data_dictionary.py`
      (`/mnt/project/...`, `/mnt/user-data/outputs/...`)
- [x] Root `run_log.md` (previously a one-line stub) now points at the real logs
- [x] Verified: no dataset has ever been committed, in any commit on any branch

## D. Manuscript corrections found while auditing

- [ ] **Table 1 and Table 3 SDs.** The versions committed before 2026-08-30 used
      population SDs (ddof = 0) because Table 3 computed them on numpy arrays via
      `.values`. The manuscript reports sample SDs, as its own Table 3 note states.
      The regenerated tables (`descriptives_v2_ddof0.py`) match the manuscript and
      supersede them.
- [x] **Figure 2 and Figure 3 captions** corrected in the 29 Aug manuscript: both now
      state that the out-of-fold predictions come from a single stratified 5-fold
      cross-validation with nested C selection, one prediction per child, and Figure 2
      quotes the curve's own AUC (.970) while distinguishing it from the repeated-CV
      estimate in Table 4.
- [ ] **Figure 2 caption, one number.** It cites Table 4 as "AUC = .969, balanced
      accuracy = .878". Table 4 and `results/primary_performance.csv` give balanced
      accuracy = **.885** for the primary LASSO; .878 is the LASSO row of the
      classifier comparison in Supplement S3 (`results/classifier_comparison.csv`),
      which selects C by balanced accuracy rather than AUC and so differs slightly.
      The AUC (.969) is right; the balanced accuracy should be .885.

## E. Worth doing before release

- [x] Figure versions identified: Figure 1 = `fig_pca.png` (colour), Figure 6 =
      `hi_fig_main_v2.png`, Figure 4 = v2 terminology. See `docs/PAPER_FILE_MAP.md`.
- [x] **Figure 4 is reproducible again.** `git diff` confirmed the committed
      `replot_figures_v2.py` was identical to the copy on disk, so the manuscript's
      Figure 4 came from a version that no longer exists. The script now produces that
      styling directly: bold A/B panel letters instead of panel titles, and the left
      x-axis labelled "mean |SHAP| (probability)". Verified against the image embedded
      in the manuscript. Its provenance log also records repo-relative paths now
      rather than absolute ones.
- [ ] Re-run it on UCloud so the committed figure and log entry come from the pinned
      environment, then commit the regenerated files:

      ```bash
      python code/replot_figures_v2.py
      git add figures/fig_importance_v2.png figures/fig_importance_v2.pdf figures/replot_log.md
      git commit -m "Regenerate Figure 4 from the updated replot script"
      ```
- [x] `figures/fig_pca_grey.png` deleted — Figure 1 is the colour version. The two
      lines that generated it (appended to `pca.py` and `primary_pipeline.py`) are gone
      too, so it does not reappear on the next run. Removing them also fixes two latent
      bugs: they imported Pillow, which was never in `requirements.txt`, and
      `primary_pipeline.py` read `fig_pca.png`, a file only `pca.py` produces — so on a
      clean install either script would have failed at the last line.

- [x] Completed TRIPOD+AI checklist added: `docs/TRIPOD_AI_checklist.docx` (the
      submitted supplemental file) plus `docs/TRIPOD_AI_checklist.md`, generated from
      it so the checklist is readable on the web. Its own note says to restore the
      official Collins et al. (2024) item wording and add page/line references once
      the manuscript is paginated — both still to do in the .docx
- [ ] Squash or rename the commit `725413f "Update fmt.Println to print 'Goodbye World'"`
      — it is an unrelated auto-generated message on a real data-dictionary change, and
      it will look careless in a repository attached to a paper
- [ ] Archive the tagged release on Zenodo and put the DOI in the paper, `README.md` and
      `CITATION.cff`. A bare GitHub URL is not a persistent identifier; most journals now
      require one
- [ ] Note in `README.md` or the paper that the analysis pins scikit-learn 1.9.0
      deliberately: `LogisticRegression(penalty=...)` is deprecated there and is removed
      in 1.10, so the scripts will need `l1_ratio=1` to run on a newer scikit-learn
- [ ] Consider a `figures/README.md` mapping each file to its figure number in the
      paper — the main-text hearing-impairment figure lives in `explore/`, not
      `figures/`, which is easy to trip over
- [ ] Consider whether `results/run_info.txt` (a three-line older duplicate of
      `run_info.json`) should be removed
