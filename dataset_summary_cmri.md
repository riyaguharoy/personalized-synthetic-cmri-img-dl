# Candidate datasets: what they contain and what they can condition on

**Status:** working draft, 6 October 2026. Facts marked **confirmed** were checked against the dataset's official page or a paper from its organisers. **Secondary** means it comes from a later paper that used the dataset. **To confirm** means it must be checked on the downloaded data (use `scripts/audit_datasets.py`).

The point of this table is simple: a clinical-profile-conditioned model can only use the patient information a dataset actually carries. That information is very uneven across the open datasets.

## 1. Summary

| Dataset | Image type | Size | Groups | Clinical information available | Masks | Access |
|---|---|---|---|---|---|---|
| **ACDC** (MICCAI 2017) | Cine SSFP, short axis, 1.5 T and 3 T | 150 patients (100 train, 50 test), one centre in Dijon | 5 groups of 30: NOR, MINF, DCM, HCM, RV | Diagnosis group, height, weight, ED and ES frame. **No age or sex.** | LV cavity, RV cavity, myocardium at ED and ES | Public challenge data |
| **M&Ms** (MICCAI 2020) | Cine, short axis | 375 CMR datasets, 4 vendors, 6 hospitals, 3 countries | NOR, DCM, HCM, HHD, ARV, IHD, AHS, LVNC, other | Pathology, vendor, centre. **Age, sex, height and weight: to confirm.** | LV and RV blood pools, LV myocardium at ED and ES | Open access |
| **M&Ms-2** (2021) | Cine, short and long axis | 360 studies (200 train, 160 test), Spain, 3 vendors | Right-ventricle focus (list from your PDF, **to confirm**) | **To confirm** | LV, myocardium, RV at ED and ES | Open access |
| **EMIDEC** (2020) | Delayed-enhancement (late gadolinium) MRI, short axis, left ventricle | 150 exams (100 train, 50 test) | Normal vs myocardial infarction (100 train: 67 MI and 33 normal; 50 test: 33 MI and 17 normal) | Sex, age, tobacco, overweight, hypertension, diabetes, family history, ECG, troponin, Killip class, LVEF, NTproBNP | Myocardium and diseased areas | emidec.com |
| **MyoPS 2020** | Three paired sequences: bSSFP, LGE, T2 | 45 cases (25 train labelled, 20 test) | Patients with myocardial scar | None found | LV and RV blood pools, LV myocardium, scar, edema | Challenge data |
| **UK Biobank** | Cine, several views | Tens of thousands (43,352 participants in one paper, 42,129 scans in another) | Population cohort | Age, sex, BMI, hospital records (ICD-10), lifestyle, genetics | Manual contours for a small subset, automatic for the rest | Application and approval |

## 2. Notes on each dataset

### ACDC (confirmed)
Each of the 150 exams comes with weight, height and the ED and ES frame numbers. The 100 training cases have manual segmentations for the left ventricle cavity, right ventricle cavity and myocardium at ED and ES. The five groups are defined by clinical criteria, for example DCM by a diastolic LV volume above 100 mL/m² and an LV ejection fraction below 40%.

What this means: ACDC is the cleanest starting point. It is balanced, single-centre and has a usable if small clinical profile (diagnosis, height, weight). Body surface area, BMI, ejection fraction and chamber volumes can be derived from height, weight and the masks. Age and sex are not available.

One secondary source reports mean values by group (LV EF about 60% for normal, 31% for MINF, 18% for DCM, 67% for HCM and 41% for RV). Treat these as an example only and recompute them from the data.

### M&Ms (confirmed for size and design)
The organisers describe 375 heterogeneous CMR datasets from four scanner vendors (Siemens, Philips, GE, Canon) in six hospitals in Spain, Canada and Germany. A downstream paper reports approximate disease shares: DCM about 28%, normal about 26%, HCM about 25%, HHD 7%, other 7%, ARV 4%, IHD 1.4%, AHS 0.9% and LVNC 0.6% (secondary).

Sources disagree on the exact count (375 in the organisers' paper, but 350 and 345 appear in later papers), so confirm the numbers from the files you download.

What this means: the rare classes (IHD, AHS, LVNC) are too small to condition on individually. Group them (for example normal, DCM, HCM, other), or use M&Ms mainly as the external test set for a model trained on ACDC.

### M&Ms-2 (partly confirmed)
Confirmed: 360 studies in total (200 training and 160 test), short-axis and long-axis views, acquired in Spain on three vendors (Siemens, GE, Philips), with LV, myocardium and RV segmented at ED and ES. The disease list in your uploaded PDF (dilated RV, tricuspid insufficiency, ARVC, tetralogy of Fallot, atrial septal defect, pulmonary hypertension, healthy) is not confirmed. Cao et al. (2026) use 157 of its patients as an external test.

### EMIDEC (confirmed)
The clinical information is stored in a text file per case and includes sex, age, tobacco use, overweight (BMI above 25), arterial hypertension, diabetes, family history of coronary disease, ECG (ST elevation or not), troponin, Killip class, ejection fraction and NTproBNP. The authors describe it as the first dataset that pairs annotated DE-MRI with clinical characteristics.

What this means: it has the richest clinical profile of the open datasets, but the diagnosis is only normal versus infarction, the images are delayed-enhancement rather than cine, and only the left ventricle is covered. Mixing it with ACDC or M&Ms would mix two different image types. If used, treat it as a separate experiment.

### MyoPS 2020 (confirmed for design)
Forty-five patients with three paired sequences, with 25 labelled training cases publicly available. A later paper reports the data come from a 1.5 T Philips scanner at one hospital in Shanghai, and that all patients have myocardial infarction (secondary). No clinical metadata were found.

What this means: too small and too homogeneous to condition on. It could only support an extra pathology or LGE experiment.

### UK Biobank (partly confirmed)
A population cohort of more than 500,000 participants aged 40 to 69 at recruitment, with cardiac MRI at an imaging visit. One paper reports 43,352 participants with short- and long-axis scans, aged 45 to 82 (mean 64.1), on a 1.5 T Siemens scanner; another cites 42,129 CMR scans. Manual contours exist for only a small subset (764 four-chamber annotations in one paper); the rest use automatic segmentation.

What this means: the best source for age, sex and BMI conditioning, but access needs an application and approval, which can take months. Keep it as an extension, as the proposal does.

## 3. From your uploaded PDF, not re-checked

The PDF also lists CMRxRecon (2023 and 2024), OCMR, HVSMR-2.0, MSD Task 02, MESA, DETERMINE, Sunnybrook and a Kaggle "Heart CT & MRI" set. I did not verify these. My reading, from the PDF alone:

- **Not useful for conditioning:** CMRxRecon and OCMR (raw k-space, healthy volunteers) and MSD Task 02 (left atrium only).
- **Possible rare-disease extension:** HVSMR-2.0 (congenital heart disease, 60 patients, whole-heart labels).
- **Rich demographics but no manual masks:** MESA and DETERMINE.
- **Exclude:** the Kaggle set, which is described as simulated.

Some entries in that PDF look machine-written, so check each against the official source before relying on it.

## 4. What this suggests for the conditioning variables

| Dataset | Usable conditioning variables |
|---|---|
| ACDC | Diagnosis group (5), height, weight, plus derived BMI, BSA, ejection fraction and chamber volumes from the masks |
| M&Ms | Pathology group (merged), vendor and centre; age, sex, height and weight only if the metadata file has them |
| EMIDEC | Full clinical profile, for a separate DE-MRI study |
| UK Biobank | Age, sex, BMI, diagnoses, if access is granted |

A sensible first design to discuss with your supervisors: train and condition on ACDC using diagnosis group, height and weight, then test on M&Ms. Confirm after the first audit run which extra variables M&Ms offers.

## 5. Next step

Run `scripts/audit_datasets.py` on the downloaded data. It builds a table of every patient with their metadata, derived measures and image properties, and draws the distributions. Those outputs replace the "to confirm" items above.
