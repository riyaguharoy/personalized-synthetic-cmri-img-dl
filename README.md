# Clinical-Profile-Conditioned Synthetic Cardiac MRI Generation

Master's thesis project, University of South-Eastern Norway (USN), in collaboration with Simula Research Laboratory.

**Project page:** https://riyaguharoy.github.io/personalized-synthetic-cmri-img-dl/

The aim is to generate synthetic cardiac MR images and their segmentation masks that are guided by a patient's clinical profile (diagnosis group, body measurements, measured volumes), and to test whether that guidance is real, useful and safe. A baseline model without clinical conditioning is compared with a conditioned model built on top of it, so any difference can be traced to the conditioning itself.

> **Status: work in progress.** Datasets are audited and preprocessed. The mask-to-image baseline code is written and training is starting. The conditioned model and the evaluation are still to do. Nothing here makes a claim about clinical impact.

## Plan in short

- **Data:** ACDC for training and testing, M&Ms as the external test set.
- **Models:** (1) baseline, segmentation mask to image (SPADE-style conditional GAN); (2) two-stage conditioned model, clinical profile to mask, then mask to image using the baseline.
- **Unit:** 2D short-axis slices at end-diastole (ED) and end-systole (ES). Full 3D volumes are a possible later extension.
- **Evaluation:** whether the conditioning worked (measurements on generated masks), fidelity (FID, KID), segmentation utility (train on synthetic, test on real), privacy (nearest-neighbour distance, membership inference), with several random seeds.
- **Splits:** always by patient, never by slice.

## What is in this repository

| Path | What it does |
|---|---|
| `audit_datasets.py` (also `scripts/`) | Builds a patient-level table, derived measures and distributions from the downloaded data |
| `preprocess_acdc.py` | ACDC to 2D slices: resample, crop, normalise, patient-level split, QC picture |
| `preprocess_mnms.py` | M&Ms to the same format (labels converted to the ACDC convention, slice order made consistent) |
| `check_orientation.py` | Checks that slices run base to apex in both datasets |
| `cmr_data.py` | PyTorch dataset for the processed slices |
| `baseline_spade.py` | Baseline training (mask to image). Resumes automatically, built for free Colab |
| `literature/` | Literature review and summary table |
| `datasets/` | Dataset summary |
| `docs/` | The project page |

## Reproduce the preprocessing

The datasets are **not** included. Download them from their official sources and use them under their own licences:

- ACDC: https://www.creatis.insa-lyon.fr/Challenge/acdc/
- M&Ms: https://www.ub.edu/mnms/

Requirements: Python 3.10+, `numpy pandas nibabel scipy matplotlib`, and `torch` for training.

```bash
# audit (optional)
python audit_datasets.py acdc --help

# preprocess (use the same size and spacing for both)
python preprocess_acdc.py --root ACDC/database/training --out data/processed/acdc_128 --size 128 --spacing 1.5
python preprocess_mnms.py --root MnMs --csv "MnMs/211230_MnMs_Dataset_information_diagnosis_opendataset.csv" --out data/processed/mnms_128 --size 128 --spacing 1.5

# sanity check: both should report a similar, high percentage
python check_orientation.py --dir data/processed/acdc_128/volumes
python check_orientation.py --dir data/processed/mnms_128/volumes

# baseline training
python baseline_spade.py --data data/processed/acdc_128 --out runs/baseline --epochs 150 --batch 16
```

Check the M&Ms CSV file name in your download, because it differs between releases.

## What the data audits found

- **ACDC** (100 labelled training patients, 20 per group): clinical information is only diagnosis group, height and weight. There is no age or sex. Diagnosis is the strong signal, for example mean LV ejection fraction is about 18% in DCM and 60% in normal subjects.
- **M&Ms** (345 cases): age, sex, weight, vendor and centre are present, height is missing for 61%. Diagnosis is entangled with scanner vendor. The DCM group is milder and more varied than in ACDC (mean LV EF 48%, range 5% to 85%), so the same label does not mean the same severity in the two datasets. Results on M&Ms are therefore also reported by measured ejection fraction.
- After preprocessing: ACDC 100 patients and 1,902 slices, M&Ms 345 cases and 7,908 slices, at 128x128 pixels and 1.5 mm.

## Data and privacy

No patient data are stored in this repository, and none may be added. `.gitignore` excludes the dataset folders and processed arrays.

## Supervisors

Vimala Nunavath (USN), Vajira Thambawita and Molly Maleckar (Simula).

## Note on AI assistance

Parts of the code and documents were drafted with AI assistance and then checked by the author. Items marked "to confirm" in the documents are still open.
