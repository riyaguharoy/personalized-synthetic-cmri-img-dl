#!/usr/bin/env python3
"""
Dataset audit for the clinical-profile-conditioned CMR project.

Three commands:

  acdc     Walk an ACDC folder (patientNNN/Info.cfg + NIfTI files), build one table
           with metadata, derived measures (BMI, BSA, volumes, ejection fraction)
           and image properties, and draw the distributions.

  kv       Read a folder of small text files made of "key: value" lines (this is the
           format of ACDC's Info.cfg and may fit other clinical-information files,
           for example EMIDEC). Check one file by eye first and adjust if needed.

  table    Profile any metadata table (CSV or Excel), for example the M&Ms
           metadata file: columns, missing values, category counts, summaries.

Every command writes a CSV, a short Markdown report and some PNG plots into the
output folder (default: outputs/dataset_audit).

Examples
--------
  python scripts/audit_datasets.py acdc  --root data/ACDC/training --out outputs/acdc
  python scripts/audit_datasets.py kv    --root data/EMIDEC --pattern "*.txt" --out outputs/emidec
  python scripts/audit_datasets.py table --file data/MnMs/metadata.csv --group-by Pathology --out outputs/mnms

Assumptions to check on the real data (they are the usual ACDC layout):
  * each patient folder has Info.cfg with lines like "ED: 1", "ES: 12", "Group: DCM",
    "Height: 184.0", "Weight: 95.0", "NbFrame: 30"
  * images are patientNNN_frameMM.nii.gz and masks patientNNN_frameMM_gt.nii.gz, MM zero-padded
  * mask labels are 1 = right ventricle cavity, 2 = myocardium, 3 = left ventricle cavity
"""
import argparse
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MYO_DENSITY_G_PER_ML = 1.05
LABELS = {1: "RV", 2: "MYO", 3: "LV"}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def parse_kv_file(path):
    """Read 'key: value' or 'key = value' lines into a dict. Numbers are converted."""
    out = {}
    for line in Path(path).read_text(errors="replace").splitlines():
        m = re.match(r"^\s*([^:=#]+?)\s*[:=]\s*(.*?)\s*$", line)
        if not m:
            continue
        key, val = m.group(1).strip(), m.group(2).strip()
        try:
            out[key] = float(val) if re.fullmatch(r"-?\d+(\.\d+)?", val) else val
        except ValueError:
            out[key] = val
    return out


def bmi(height_cm, weight_kg):
    if not height_cm or not weight_kg:
        return np.nan
    return weight_kg / ((height_cm / 100.0) ** 2)


def bsa_mosteller(height_cm, weight_kg):
    if not height_cm or not weight_kg:
        return np.nan
    return math.sqrt(height_cm * weight_kg / 3600.0)


def write_report(df, out_dir, title, group_col=None):
    """Write the table, a Markdown profile and plots."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "metadata_table.csv", index=False)

    lines = [f"# {title}", "", f"Rows: {len(df)}  |  Columns: {len(df.columns)}", ""]

    miss = df.isna().sum()
    lines += ["## Missing values", "", "| column | missing | % |", "|---|---|---|"]
    for c in df.columns:
        lines.append(f"| {c} | {int(miss[c])} | {100 * miss[c] / max(len(df), 1):.1f} |")
    lines.append("")

    def is_id_like(col):
        # one value per row (patient names, file names) is not worth counting
        return df[col].nunique() >= max(len(df) * 0.9, 30) and not pd.api.types.is_numeric_dtype(df[col])

    cat_cols = [c for c in df.columns
                if (df[c].dtype == object or df[c].nunique() <= 12)
                and df[c].nunique() > 1 and not is_id_like(c)
                and df[c].nunique() <= 30]
    num_cols = [c for c in df.columns
                if pd.api.types.is_numeric_dtype(df[c]) and df[c].nunique() > 12]

    for c in cat_cols:
        vc = df[c].value_counts(dropna=False)
        lines += [f"## Counts: {c}", "", "| value | n | % |", "|---|---|---|"]
        for k, v in vc.items():
            lines.append(f"| {k} | {v} | {100 * v / len(df):.1f} |")
        lines.append("")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        vc.plot.bar(ax=ax, color="#4C72B0")
        ax.set_title(f"{c}")
        ax.set_ylabel("count")
        fig.tight_layout()
        fig.savefig(out_dir / f"counts_{re.sub(r'[^A-Za-z0-9]+', '_', str(c))}.png", dpi=150)
        plt.close(fig)

    if num_cols:
        lines += ["## Numeric summaries", "", df[num_cols].describe().round(2).to_markdown(), ""]
        for c in num_cols:
            fig, ax = plt.subplots(figsize=(6, 3.2))
            if group_col and group_col in df.columns and df[group_col].nunique() <= 12:
                for g, sub in df.groupby(group_col):
                    ax.hist(sub[c].dropna(), bins=15, alpha=0.55, label=str(g))
                ax.legend(fontsize=7)
            else:
                ax.hist(df[c].dropna(), bins=20, color="#4C72B0")
            ax.set_title(c)
            fig.tight_layout()
            fig.savefig(out_dir / f"hist_{re.sub(r'[^A-Za-z0-9]+', '_', str(c))}.png", dpi=150)
            plt.close(fig)

        if group_col and group_col in df.columns:
            lines += [f"## Numeric summaries by {group_col}", ""]
            lines.append(df.groupby(group_col)[num_cols].agg(["mean", "std"]).round(2).to_markdown())
            lines.append("")

    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_dir / 'metadata_table.csv'} and {out_dir / 'report.md'} (+ plots)")


# --------------------------------------------------------------------------
# acdc
# --------------------------------------------------------------------------
def structure_volumes_ml(mask, spacing):
    voxel_ml = float(np.prod(spacing)) / 1000.0
    return {name: float((mask == lab).sum()) * voxel_ml for lab, name in LABELS.items()}


def cmd_acdc(args):
    try:
        import nibabel as nib
    except ImportError:
        sys.exit("nibabel is needed for this command: pip install nibabel")

    root = Path(args.root)
    patients = sorted(p for p in root.iterdir() if p.is_dir() and p.name.lower().startswith("patient"))
    if not patients:
        sys.exit(f"No patient folders found under {root}")

    rows = []
    for p in patients:
        info_path = p / "Info.cfg"
        row = {"patient": p.name}
        if info_path.exists():
            info = parse_kv_file(info_path)
            row.update({k.lower(): v for k, v in info.items()})
        else:
            row["info_missing"] = True

        h, w = row.get("height"), row.get("weight")
        row["bmi"] = bmi(h, w)
        row["bsa_mosteller"] = bsa_mosteller(h, w)

        for phase in ("ed", "es"):
            frame = row.get(phase)
            if frame is None:
                continue
            frame = int(frame)
            gt = p / f"{p.name}_frame{frame:02d}_gt.nii.gz"
            img = p / f"{p.name}_frame{frame:02d}.nii.gz"
            if img.exists():
                hdr = nib.load(str(img)).header
                shape = hdr.get_data_shape()
                zooms = hdr.get_zooms()[:3]
                if phase == "ed":
                    row["shape"] = "x".join(map(str, shape[:3]))
                    row["spacing_mm"] = "x".join(f"{z:.2f}" for z in zooms)
                    row["n_slices"] = int(shape[2])
            if gt.exists():
                nii = nib.load(str(gt))
                mask = np.asarray(nii.dataobj).astype(int)
                vols = structure_volumes_ml(mask, nii.header.get_zooms()[:3])
                for name, v in vols.items():
                    row[f"{phase}_{name.lower()}_ml"] = round(v, 1)
            else:
                row[f"{phase}_gt_missing"] = True

        if "ed_lv_ml" in row and "es_lv_ml" in row and row["ed_lv_ml"]:
            row["lv_ef_pct"] = round(100.0 * (row["ed_lv_ml"] - row["es_lv_ml"]) / row["ed_lv_ml"], 1)
        if "ed_myo_ml" in row:
            row["ed_myo_mass_g"] = round(row["ed_myo_ml"] * MYO_DENSITY_G_PER_ML, 1)
        if "ed_rv_ml" in row and "es_rv_ml" in row and row["ed_rv_ml"]:
            row["rv_ef_pct"] = round(100.0 * (row["ed_rv_ml"] - row["es_rv_ml"]) / row["ed_rv_ml"], 1)
        rows.append(row)

    df = pd.DataFrame(rows)
    group_col = "group" if "group" in df.columns else None
    write_report(df, Path(args.out), f"ACDC audit ({root})", group_col)


# --------------------------------------------------------------------------
# kv
# --------------------------------------------------------------------------
def cmd_kv(args):
    root = Path(args.root)
    files = sorted(root.rglob(args.pattern))
    if not files:
        sys.exit(f"No files matching {args.pattern} under {root}")
    rows = []
    for f in files:
        d = parse_kv_file(f)
        if d:
            d = {"file": str(f.relative_to(root)), **d}
            rows.append(d)
    if not rows:
        sys.exit("Found files but could not read any 'key: value' lines. Open one and adjust the parser.")
    df = pd.DataFrame(rows)
    write_report(df, Path(args.out), f"Key-value audit ({root})", args.group_by)


# --------------------------------------------------------------------------
# table
# --------------------------------------------------------------------------
def cmd_table(args):
    path = Path(args.file)
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path, sep=None, engine="python")
    df.columns = [str(c).strip() for c in df.columns]
    print("Columns found:", ", ".join(df.columns))
    write_report(df, Path(args.out), f"Table audit ({path.name})", args.group_by)


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("acdc", help="audit an ACDC folder")
    a.add_argument("--root", required=True, help="folder that contains patientNNN folders")
    a.add_argument("--out", default="outputs/dataset_audit/acdc")
    a.set_defaults(func=cmd_acdc)

    k = sub.add_parser("kv", help="audit a folder of key: value text files")
    k.add_argument("--root", required=True)
    k.add_argument("--pattern", default="*.txt", help="file pattern, for example *.txt or Info.cfg")
    k.add_argument("--group-by", default=None, help="column to split numeric plots by")
    k.add_argument("--out", default="outputs/dataset_audit/kv")
    k.set_defaults(func=cmd_kv)

    t = sub.add_parser("table", help="audit a CSV or Excel metadata table")
    t.add_argument("--file", required=True)
    t.add_argument("--group-by", default=None, help="column to split numeric plots by")
    t.add_argument("--out", default="outputs/dataset_audit/table")
    t.set_defaults(func=cmd_table)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
