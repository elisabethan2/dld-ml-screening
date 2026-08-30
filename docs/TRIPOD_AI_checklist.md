# TRIPOD+AI reporting checklist

Completed checklist for this study, following Collins et al. (2024, BMJ 385:e078378). This is a development study with internal validation only (repeated stratified cross-validation, single dataset); evaluation-only items are marked N/A with justification (grey). Use the official item wording from Collins et al. (2024) in the submitted version; the wording here is abbreviated. Page and line references correspond to the paginated manuscript with continuous line numbers (ML_DLD_ManusAugust2026_newVersion290826).

The authoritative version is [`TRIPOD_AI_checklist.docx`](TRIPOD_AI_checklist.docx),
submitted as a supplemental file with the paper. This Markdown rendering is generated
from that file so the checklist can be read on the web.

| # | Checklist item (TRIPOD+AI, abbreviated) | Where addressed / status | Page/line |
|---|---|---|---|
| **Title & Abstract** | | | |
| 1 | Title — identify as developing a multivariable prediction/classification model, target population, outcome | Title page | p. 1, lines 1–2; p. 3, lines 44–49 |
| 2 | Abstract — structured summary per TRIPOD+AI for Abstracts | Abstract (effect sizes only per JSLHR; describe discrimination qualitatively) | p. 3, lines 42–65 |
| **Introduction** | | | |
| 3a | Background; state the model is diagnostic; rationale; existing models | Introduction (¶1–2; ML positioning: Borovsky, Justice & Ahn, Georgiou) | p. 5–7, lines 69–124 |
| 3b | Target population, intended use in the care pathway, intended users | Introduction / Discussion (screening in assessment-light systems; flag for full assessment) | p. 5, lines 79–90; p. 26, lines 546–563 |
| 3c | Known health inequalities between sociodemographic groups | Introduction — variability in identification by municipality, school resources, family capacity; girls and multilingual children; Discussion (Limitations) notes multilingual exclusion | p. 5–6, lines 90–96; p. 27, lines 570–574 |
| 4 | Objectives; state development vs validation | Introduction (objectives: development with internal validation) | p. 8, lines 136–145 |
| **Methods — Data, participants, outcome, predictors** | | | |
| 5a | Data sources and rationale; representativeness | Methods: Participants & Setting | p. 8, lines 147–152; p. 13, lines 257–262 |
| 5b | Accrual dates | Methods (Dec 2013–June 2014) | p. 8, lines 156–157 |
| 6a | Setting; number/location of centres | Methods: Participants & Setting (multi-region recruitment; region confound noted) | p. 8, lines 152–153; p. 18, line 350 |
| 6b | Eligibility criteria | Methods: Participants and Setting (referral by municipal PPR SLTs for persistent language difficulties; exclusion criteria listed) | p. 9, lines 160–177; p. 10, lines 186–194 |
| 6c | Treatments received and handling (if relevant) | Methods/HI section (HI amplification; unaided BEHL) | — |
| 7 | Data preparation; quality checks; applied equally across groups | Methods: Data Preparation (in-fold imputation/standardization, applied identically) | p. 12–13, lines 248–255 |
| 8a | Outcome definition; how/when assessed; consistency across groups | Methods: Participants and Setting (DLD status assigned by municipal SLTs; reference standard is clinical judgement, not a research protocol — stated as a limitation) | p. 10, lines 186–204 |
| 8b | If subjective outcome, assessor qualifications | Methods: Participants and Setting (certified speech-language therapists in municipal PPR services) | p. 10, lines 187–190 |
| 8c | Blinding of outcome assessment | Methods: Participants and Setting — group membership known to assessors; blinding of outcome assessment not possible in this design | p. 10, lines 199–204 |
| 9a | Initial predictors and any pre-selection before modelling | Methods: Predictors (one-score-per-task; exclusions) + Analytical (selection inside CV) | p. 11–12, lines 206–245 |
| 9b | Define predictors; how/when measured; blinding | Methods: Predictors (assessors not blind to group; all tasks objectively scored, residual influence acknowledged) | p. 11, lines 207–212 |
| 9c | If subjective predictors, assessor qualifications | Methods: Participants & Setting (author + trained SLT students) | p. 11, lines 208–211 |
| **Methods — Sample size, missing data, analysis** | | | |
| 10 | Sample size and justification of sufficiency | Methods: Sample Size (fixed convenience sample; learning curve) | p. 13–14, lines 256–271 |
| 11 | Missing-data handling and reasons for omissions | Methods: Data Preparation (median in-fold; structural-missingness timing vars dropped) | p. 12–13, lines 228–235, 248–255; p. 17–18, lines 351–354 |
| 12a | How data were used/partitioned | Methods: Analytical (repeated stratified 5-fold CV = internal validation) | p. 14, lines 273–279; p. 15, lines 292–299 |
| 12b | Predictor handling (rescaling/standardization) | Methods: Analytical (standardized within folds) | p. 14, lines 276–279 |
| 12c | Model type, rationale, ALL model-building steps incl. tuning, internal-validation method | Methods: Analytical (LASSO primary + RF robustness; nested-CV C; selection in-fold) | p. 14, lines 280–291 |
| 12d | Heterogeneity across clusters (centres/regions) | Methods/Limitations (multi-region; not modelled — stated as limitation) | — |
| 12e | Discrimination, calibration, clinical utility; model comparison | Methods + Results (AUC/balanced accuracy; calibration Fig 3; LASSO vs RF) | p. 15, lines 297–310; Figures 2–3 (pp. 40–41) |
| 12f | Model updating from evaluation | N/A — development study; no external evaluation | — |
| 12g | How predictions calculated for evaluation | N/A — no external evaluation dataset | p. 15, lines 304–310 |
| **Methods — Imbalance, fairness, output, ethics** | | | |
| 13 | Class-imbalance handling and effect on calibration | Methods: Analytical (balanced accuracy + stratified CV; no resampling; calibration noted) | p. 15, lines 300–303 |
| 14 | Fairness approaches and rationale | Methods: Analytical Methods (exploratory check by sex and age band; formal subgroup estimation not supportable at n = 59 — only six girls in the DLD group); Discussion (Limitations) | p. 15–16, lines 311–316; p. 27, lines 568–570 |
| 15 | Model output (probabilities vs class) and threshold rationale | Methods: Analytical (probabilities; 0.5 default threshold; justified) | p. 15, lines 304–308; p. 28, lines 592–594 |
| 16 | Differences between development and evaluation data | N/A — single dataset | — |
| 17 | Ethical approval and consent | Methods: Participants and Setting — no ethics-committee approval required under Danish law for non-biomedical research at a humanities faculty; notified to the Danish Data Protection Agency (journal no. 2013-41-2136); written parental informed consent; Declaration of Helsinki | p. 8–9, lines 153–159 |
| **Open science & patient involvement** | | | |
| 18a | Funding and role of funders | Acknowledgments — original data collection funded (funder masked for review); present secondary analysis received no specific grant | p. 29, lines 612–614 |
| 18b | Conflicts of interest | Disclosed via the Editorial Manager submission portal per ASHA policy; none declared | Submission portal (ASHA policy) |
| 18c | Protocol availability, or state none | Methods: Analytical Methods — retrospective secondary analysis; no study protocol was prepared | p. 17, lines 338–339 |
| 18d | Registration, or state not registered | Methods: Analytical Methods — analysis was not pre-registered | p. 17, lines 338–339 |
| 18e | Study-data availability | Data Availability Statement — data not available; consent obtained at collection does not permit onward sharing, and disclosure is restricted by Danish data protection law. Summary statistics reported in Tables 1 and 3 | p. 29, lines 616–619 |
| 18f | Analytical-code availability | Data Availability Statement — analysis code, pinned software environment with exact package versions, trained model (LASSO coefficients) and dated run log openly available at the repository DOI | p. 29, lines 619–621 |
| 19 | Patient/public involvement, or state none | Acknowledgments — children, families and clinicians were not involved in setting the research question, designing the study, or interpreting the results | p. 29, lines 606–610 |
| **Results** | | | |
| 20a | Participant flow; numbers with/without outcome; diagram | Results: Sample Characteristics; Supplemental Material S1 (83 assessed, 8 excluded on eligibility grounds with reasons, 75 retained; n = 59 for the primary analysis) | p. 9, lines 172–177; p. 17, lines 342–343; S1 |
| 20b | Characteristics; key predictors; demographics; missing-data amounts; group differences | Results: Sample Characteristics + Table 1 (demographics, nonverbal reasoning); Table 3 (predictor distributions by group); Methods: Data Preparation states missing values were no more than 8.5% on any retained measure | p. 17–18, lines 341–354; Tables 1 and 3 |
| 20c | Compare evaluation vs development predictor distributions | N/A — single dataset | — |
| 21 | Participants and outcome events per analysis | Results (n = 59 DLD-vs-control; group sizes as events) | p. 14, line 274; p. 17, lines 343–345 |
| 22 | Full model for predictions in new individuals | Results/Fig 4 (LASSO coefficients) + trained object in repo | p. 19, lines 397–402; repository |
| 23a | Performance with confidence/uncertainty intervals; key subgroups; plots | Results + Tables 4–5 (percentile intervals; ROC/confusion Fig 2); subgroup limits at n=59 | p. 18, lines 370–377; Table 4 |
| 23b | Heterogeneity in performance across clusters | Limitations (multi-region; not formally modelled) | — |
| 24 | Results of model updating | N/A — no evaluation/updating | — |
| **Discussion** | | | |
| 25 | Interpretation incl. fairness; vs objectives and prior work | Discussion (¶1–5; comparison with prior ML; fairness in Limitations) | p. 23–26, lines 468–545 |
| 26 | Limitations incl. non-representative sample, size, overfitting, missing data | Discussion: Limitations (consolidated) | p. 27–28, lines 566–594 |
| 27a | How poor/unavailable input data are handled at implementation | Discussion: Toward scalable screening — the model requires complete predictor scores; a deployed screener should return no result rather than substitute imputed values | p. 26, lines 552–556 |
| 27b | User interaction and expertise required | Discussion: Toward scalable screening — intended users are speech-language therapists or trained assessors under supervision, not untrained staff or parents | p. 26–27, lines 556–561 |
