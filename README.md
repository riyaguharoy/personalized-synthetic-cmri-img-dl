# Clinical-profile-conditioned synthetic cardiac MRI

Master's thesis project, University of South-Eastern Norway, in collaboration with Simula Research Laboratory.
Status: work in progress (project proposal stage, autumn 2026).

**Project page:** https://riyaguharoy.github.io/clinical-profile-cmr-synthesis/

## What this project is about

The project asks how information about a patient (a clinical profile) can be used to control the generation of synthetic cardiac MR images together with their segmentation masks, and whether that control is real, useful and safe.

Three questions guide the work:

1. How can a clinical profile be added to a generative model, starting from a baseline without it?
2. Do the generated images and masks keep plausible anatomy and reflect the profile they were conditioned on?
3. How does the conditioned model compare with the baseline on fidelity, downstream utility and privacy?

This is a methods and data project. It does not involve clinicians, patient outcomes or clinical deployment.

## What is in this repository

| Folder | Contents |
|---|---|
| `literature/` | Literature review (`literature_review.md`), the summary spreadsheet and a CSV version |
| `datasets/` | Dataset summary as a document and as a CSV |
| `scripts/` | `audit_datasets.py`, which audits downloaded datasets |
| `docs/` | The project web page (served by GitHub Pages) |

## Datasets

No patient data are stored here. Download each dataset from its official source and follow its licence. See `datasets/dataset_summary.md` for what each one contains.

## Running the dataset audit

```bash
pip install -r requirements.txt

# ACDC: a folder of patientNNN folders with Info.cfg and NIfTI files
python scripts/audit_datasets.py acdc --root data/ACDC/training --out outputs/acdc

# Any metadata table (for example the M&Ms metadata file)
python scripts/audit_datasets.py table --file data/MnMs/metadata.csv --group-by Pathology --out outputs/mnms

# A folder of "key: value" text files (check one file first)
python scripts/audit_datasets.py kv --root data/EMIDEC --pattern "*.txt" --out outputs/emidec
```

The script was tested on small synthetic mock data only. Check the file layout assumptions listed at the top of the script against the real downloads.

## Status

- [x] Project proposal and literature review draft
- [ ] Dataset audit on the real data (in progress)
- [ ] Baseline model
- [ ] Clinical-profile conditioning
- [ ] Evaluation: fidelity, utility, privacy

## Notes

Parts of the documents here were drafted with AI assistance and checked against the cited sources. Items marked "to confirm" or "to verify" are still open.

## Licence

Not chosen yet. Add a licence file before making the repository public.
