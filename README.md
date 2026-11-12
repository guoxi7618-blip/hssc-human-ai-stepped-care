# Human–AI collaborative stepped care: code and de-identified data

Code and de-identified data for the manuscript *Human–AI collaborative stepped care in a Chinese university student support system: a cluster randomised hybrid effectiveness–implementation trial* (submitted to *Humanities and Social Sciences Communications*).

## Contents

| Folder | Content |
|---|---|
| `scripts/` | Python scripts for the analyses, figures, tables and manuscript files (run in numerical order) |
| `data/` | De-identified trial data (see "Data files" and "De-identification" below) |
| `results/` | Analysis outputs that the manuscript reports |

## Environment

Python 3.13 with `numpy`, `pandas`, `scipy`, `statsmodels`, `matplotlib`, `python-pptx` and `python-docx`; `pandoc` for the Word versions. All tests are two-sided with α = 0.05.

## Scripts

| Script | Purpose | Main inputs → outputs |
|---|---|---|
| `01_trial_analysis.py` | Primary and secondary outcomes (linear mixed models, ordinal GEE, Holm correction), sensitivity analyses (complete cases, multiple imputation, δ-adjusted pattern mixture, CACE), reliable change and NNT, subgroups, process–outcome associations, implementation summary | `trial_wide.csv`, `process_plans.csv`, `counsellors.csv` → `results/*` |
| `02_figures_3_to_5.py` | Figures 3–5 | `data/*`, `results/*` → `Fig3–5` (PDF/PNG) |
| `03_figure1_model_pptx.py` | Figure 1 (intervention model) | → `Fig1_model.pptx` |
| `04_figure2_consort_pptx.py` | Figure 2 (CONSORT flow) | `screening_funnel.json`, `trial_wide.csv` → `Fig2_consort.pptx` |
| `05_tables.py`, `06_tables_chinese.py` | Tables 1–3 (English, Chinese) | `trial_wide.csv`, `results/*` → `table*.tex` |
| `07_references.py` | Reference list (Springer basic author–date) | DOI list → `refs_springer.tex` |
| `08_fill_manuscript.py` | Fills computed values (power, RCI) into the manuscript template | → manuscript `.tex` |
| `09_wordcount.py`, `12_language_check.py` | Word count and language checks | manuscript `.tex` |
| `10_word_versions.py`, `11_cover_letter.py` | Word versions of the manuscript and cover letter | `.tex` → `.docx` |

## Data files

| File | Unit | Content |
|---|---|---|
| `trial_wide.csv` | Student (n = 180) | Arm, counsellor (cluster) code, sex, age, year of study, PHQ-9/GAD-7 items and totals, WSAS, ln RMSSD and risk level at T0/T1/T2; biweekly monitoring; engagement, check-ins, counsellor time, CSQ-8; missingness; timing of T1/T2 in weeks since the start of the intervention |
| `trial_long.csv` | Student × time point | Long format of the outcome variables |
| `process_plans.csv` | Algorithmic plan (n = 270) | Week, tier, counsellor decision (accepted/modified/rejected), reason, review time |
| `counsellors.csv` | Counsellor (n = 20) | Arm, experience, sex, trust in the system and intention to use (intervention arm) |
| `screening_funnel.json` | Trial | Screening and enrolment counts for the CONSORT diagram |

Student codes (`S001`–`S180`) and counsellor codes (1–20) are study codes and cannot be linked to identities.

## De-identification

To reduce the risk of re-identification, the following variables were removed from the public data:

- `trial_wide.csv`: place of origin (`rural`), only-child status (`only_child`) and all calendar dates (`screen_date`, `baseline_date`, `intervention_start`, `T1_date`, `T2_date`); relative timing is kept as `T1_week` and `T2_week`;
- `counsellors.csv`: counsellor's college (`college`) and randomisation date;
- `process_plans.csv`: calendar date of each plan review (`week` is kept).

All analyses in the manuscript can be reproduced from these files except the baseline rows for rural origin and only-child status in Table 2, which are reported in aggregate only.

## Notes for reproduction

1. **Paths.** The scripts were run from the authors' project directory and use absolute paths (variables `R`, `M`, `B`, `OUT` at the top of each script). Set these to the local `data/` and `results/` folders before running.
2. **File names.** In the project directory, outputs of `01_trial_analysis.py` carry the prefix `h3_` (e.g. `h3_outcomes.csv`); here the prefix has been removed (`results/outcomes.csv`).
3. **External reference data.** The reliable change index uses the PHQ-9 standard deviation from a published normative dataset (Su et al. 2024, *Scientific Data* 11:1046, https://doi.org/10.1038/s41597-024-03888-8), read from `h0_baseline_pool_xinxiang.csv`. This file is not redistributed here and can be rebuilt from the published dataset.
4. **Not included.** The power-simulation output (`h5_power.csv`, reported in Supplementary Table S1) and the Crossref cache used to format references.

## Contact

Correspondence: Yindong Dong (corresponding author), Anhui Agricultural University.
