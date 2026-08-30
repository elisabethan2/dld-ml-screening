"""Generate data_dictionary.csv for the DLD/ML dataset.
Combines codebook metadata with data-derived fields (missingness, n present) computed
from the actual file after decoding the SPSS '.' missing marker.

Config via env: DLD_DATA (input dataset), DICT_OUT (output path).
Note: the PRIMARY set below still lists the pre-lock names `Non` and `HimOpmscore`;
the locked analysis uses `NonLRAE` and `HimOpmscore_skala`. The committed
docs/data_dictionary.csv is the finalized version and documents both.
"""
import os
import numpy as np, pandas as pd, csv

DATA = os.environ.get("DLD_DATA", "data/phddataset_samlet_300626.xlsx")
df = pd.read_excel(DATA, sheet_name=0).replace({".": np.nan})
N = len(df)

# 15 raw columns that map 1:1 onto the draft's Set-2 constructs
PRIMARY = {"LSPHUK","LTaF","TROGB","LSPLRAE","GåStop","verbfluantal","verbfluskift",
           "HimOpmscore","Non","LTaB","NIQ","verbflusubkat","OOU","verbfluintru","verbflupers"}

TROG_STRUCT = {  # individual TROG-2 blocks: grammatical structure targeted
 "A":"two elements","B":"negation","C":"reversible in/on","D":"three elements","E":"reversible SVO",
 "F":"four elements","G":"subject relative clause","H":"not only X but also Y","I":"reversible above/below",
 "J":"comparative","K":"reversible passive","L":"zero anaphor","M":"pronoun gender/number",
 "N":"pronoun binding","O":"neither-nor","P":"X but not Y","Q":"postmodified subject",
 "R":"singular/plural","S":"object relative clause","T":"embedded sentence"}

# explicit metadata: column -> (label_en, construct, instrument, type, coding, units, role, flag, note)
META = {
 "ID":("Informant number","Identifier","-","id","H=HI, S=SLI/DLD, K=Control + number","-","identifier","",""),
 "Gruppe":("Group","Group membership","-","label","0=hearing-impaired, 1=SLI/DLD, 2=control","-","target","Y",
    "Coded SLI; paper uses DLD. Confirm SLI->DLD mapping and diagnostic/inclusion criteria (esp. nonverbal IQ)."),
 "Køn":("Sex","Demographic","-","demographic","1=boy, 2=girl","-","covariate","",""),
 "Fødselsdato":("Date of birth","Demographic","-","date","dd-mm-yyyy","-","source","",""),
 "Alder":("Age (year;month)","Demographic","-","demographic","year;month coded (e.g. 8.11 = 8y 11m)","years;months","do-not-average","Y",
    "Year;month encoding, NOT decimal. Table 1 ages were averaged from this column (invalid). Use 'age' (decimal)."),
 "Aldersgruppe":("Age band","Demographic","-","demographic","1=7y,2=8y,3=9y,4=10y,5=11y,6=12y","-","covariate","",""),
 "Alder_mdr":("Age in months","Demographic","-","demographic","integer months","months","covariate","",""),
 "Region":("Region","Demographic","-","demographic","Danish region (text labels)","-","covariate","Y",
    "61% from Syddanmark, 1 from Nordjylland. Representativeness limitation; too skewed for cluster modelling."),
 "age":("Age (decimal)","Demographic","derived from DOB","demographic","decimal years","years","covariate","Y",
    "Derived (not in codebook). Confirm this is the canonical age field for reporting and as a model feature."),
 "NIQ":("Block Design (nonverbal IQ)","Nonverbal reasoning","WISC-IV","raw_score","raw points","points","primary-feature","",""),
 # digit span forward
 "TaF":("Digit span forward (points)","Verbal short-term memory","WISC-IV","raw_score","raw points","points","candidate","",""),
 "LTaF":("Digit span forward (longest span)","Verbal short-term memory","WISC-IV","span_score","longest sequence","items","primary-feature","",""),
 "TaF_samletscore":("Digit span forward composite","Verbal STM","-","composite","timing-based composite","-","not-used","Y",
    "Composite labelled 'times:score'. Confirm exactly how computed (appears to fold in timing)."),
 # digit span backward
 "TaB":("Digit span backward (points)","Verbal working memory","WISC-IV","raw_score","raw points","points","candidate","",""),
 "LTaB":("Digit span backward (longest span)","Verbal working memory","WISC-IV","span_score","longest sequence","items","primary-feature","",""),
 "TaB_samletscore":("Digit span backward composite","Verbal WM","-","composite","timing-based composite","-","not-used","Y",
    "Confirm composite computation (folds in timing)."),
 # OOU
 "OOU":("Odd-One-Out (longest span)","Visuospatial working memory","-","span_score","longest sequence","items","primary-feature","",""),
 "OOUperception":("Odd-One-Out perception","Visual perception check","-","subscore","percent correct","%","not-used","Y",
    "Ceiling/low variance (dropped in draft). Confirm it is a perceptual control, not a WM measure."),
 "OOUhuk":("Odd-One-Out memory","Visuospatial WM","-","subscore","percent correct","%","candidate","",""),
 "OOU_samletscore":("Odd-One-Out composite","Visuospatial WM","-","composite","timing-based composite","-","not-used","Y","Confirm composite computation."),
 # CLPT / listening span
 "LSPLRAE":("Listening span (longest span)","Verbal WM (processing+storage)","CLPT","span_score","longest sequence","items","primary-feature","Y",
    "Confirm this raw column underlies CLPTspan_skala."),
 "LSPSEM":("Listening span semantic accuracy","Sentence comprehension","CLPT","subscore","percent correct","%","candidate","",""),
 "LSPHUK":("Listening span word recall","Verbal WM (storage)","CLPT","raw_score","percent correct","%","primary-feature","Y",
    "Top predictor. Bounded proportion -> residual-z extreme (logit transform cleaner). Confirm it underlies CLPTwordrecall_skala."),
 "LSP_samletscore":("Listening span composite","Verbal WM","-","composite","timing-based composite","-","not-used","Y","Confirm composite computation."),
 # nonword
 "Non":("Nonword serial recall (points)","Phonological STM","-","raw_score","raw points","points","primary-feature","Y",
    "Confirm whether Non (points) or NonLRAE (span) is the intended measure / underlies Nonwords_skala."),
 "NonLRAE":("Nonword serial recall (longest span)","Phonological STM","-","span_score","longest sequence","items","candidate","Y",
    "See Non: confirm canonical nonword measure."),
 "NonLRAE_samletscore":("Nonword composite","Phonological STM","-","composite","timing-based composite","-","not-used","Y","Confirm composite computation."),
 # attention / executive
 "GåStop":("Go/Stop (inhibition)","Response inhibition","TEA-Ch-like","raw_score","raw score","-","primary-feature","",""),
 "Himmålobjekt":("Sky Search targets found","Selective attention","TEA-Ch (Sky Search)","raw_score","count","targets","candidate","",""),
 "THim":("Sky Search time per target","Attention/speed","TEA-Ch (Sky Search)","raw_score","seconds per target","s","candidate","",""),
 "HimOpmscore":("Sky Search attention score","Selective attention","TEA-Ch (Sky Search)","raw_score","attention score","-","primary-feature","Y",
    "One of three attention scores. Confirm which is canonical (HimOpmscore vs Himmålobjekt)."),
 # TROG summary
 "TROGB":("TROG-2 blocks correct","Grammar comprehension","TROG-2","raw_score","blocks passed","blocks","primary-feature","",""),
 "TROGgen":("TROG-2 repetitions","Grammar (process)","TROG-2","raw_score","count","-","not-used","",""),
 "TROGlekfejl":("TROG-2 lexical errors","Grammar (process)","TROG-2","raw_score","count","-","not-used","",""),
 "TROGsysfejl":("TROG-2 systematic errors","Grammar (process)","TROG-2","raw_score","count","-","not-used","",""),
 # verbal fluency
 "verbfluantal":("Verbal fluency: correct","Semantic fluency","Category (animals)","raw_score","count","items","primary-feature","",""),
 "verbflupers":("Verbal fluency: perseverations","Executive (fluency)","Category (animals)","raw_score","count","-","primary-feature","",""),
 "verbfluintru":("Verbal fluency: intrusions","Executive (fluency)","Category (animals)","raw_score","count","-","primary-feature","",""),
 "verbflusubkat":("Verbal fluency: subcategories","Semantic organization","Category (animals)","raw_score","count","-","primary-feature","",""),
 "verbflucluster":("Verbal fluency: mean cluster size","Semantic organization","Category (animals)","raw_score","mean size","-","not-used","",""),
 "verbfluskift":("Verbal fluency: switches","Executive search","Category (animals)","raw_score","count","-","primary-feature","",""),
}

def meta_for(col):
    if col in META: return META[col]
    # timing blocks
    for pre, lab in [("TTaF","Digit span forward"),("TTaB","Digit span backward"),
                     ("TOOU","Odd-One-Out"),("TLSP","Listening span"),("TNon","Nonword recall")]:
        if col.startswith(pre) and col[len(pre):].startswith("B"):
            return (f"{lab} time block {col[-1]}", lab, "-", "timing",
                    "seconds (per block/level)", "s", "dropped-high-missing", "Y",
                    "Timing block. '.' here likely = block not reached (structural/informative missingness). Confirm meaning.")
    # TROG individual blocks
    if col.startswith("TROG_") and col.split("_")[1] in TROG_STRUCT:
        L = col.split("_")[1]
        return (f"TROG-2 block {L}: {TROG_STRUCT[L]}", "Grammar comprehension", "TROG-2",
                "trog_block", "1=pass, 0=fail", "binary", "Set3-only", "", "")
    # scaled scores
    if col.lower().endswith("skala"):
        return (f"{col} (standardized)", "Standardized score", "-", "standardized",
                "rescaled to mean 10, SD 3 on full sample", "-", "do-not-use", "Y",
                "NOT age-normed: = raw rescaled (r=1.0), age trend intact. Confirm derivation/intent; use raw instead.")
    return (col, "?", "-", "unknown", "?", "-", "review", "Y", "Not in codebook map - review.")

rows = []
for col in df.columns:
    label,construct,instr,typ,coding,units,role,flag,note = meta_for(col)
    s = df[col]
    miss = round(s.isna().mean()*100, 1)
    rows.append({
        "column_excel": col, "label_en": label, "construct": construct, "instrument": instr,
        "type": typ, "coding_values": coding, "units": units,
        "n_present": int(s.notna().sum()), "pct_missing": miss,
        "analysis_role": role, "clarify_flag": flag, "clarify_note": note,
    })

out = os.environ.get("DICT_OUT", "docs/data_dictionary.csv")
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

flagged = [r for r in rows if r["clarify_flag"] == "Y"]
print(f"Wrote {out}: {len(rows)} variables, {len(flagged)} flagged for clarification.")
print("\nFlagged (excluding the repetitive timing/scaled families):")
for r in flagged:
    if r["type"] not in ("timing","standardized"):
        print(f"  - {r['column_excel']:18s} [{r['analysis_role']}] {r['clarify_note'][:75]}")
print(f"\n  + all {sum(r['type']=='timing' for r in flagged)} timing blocks (missing-marker meaning)")
print(f"  + all {sum(r['type']=='standardized' for r in flagged)} _skala columns (derivation)")
