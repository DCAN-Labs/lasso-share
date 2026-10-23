#!/usr/bin/env python3
"""
Generate a prep tracker CSV for a project directory.

Usage:
    make_prep_tracker.py <project_dir>

The project directory should contain:
  bids/               - BIDS data
  derivatives/nordic  - NORDIC derivatives
  summaries/          - JSON/TSV summaries
  beh/participants.tsv

Output: <project_dir>/prep_tracker.csv

Columns:
  summaries_tsv  - TSV exists in bids_summaries/
  summaries_json - JSON exists in bids_summaries/
  bids           - found/total files from JSON in bids2/; Y if complete
  nordic         - found/total .nii.gz in derivatives/nordic2/ func vs bids2/ (non-phase)
"""

import argparse
import json
import re
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser(description="Generate prep_tracker.tsv for a project directory.")
parser.add_argument("project_dir", help="Path to the project root directory")
parser.add_argument("--participants", help="Path to participants.tsv (overrides default search)")
parser.add_argument("--output", help="Output path for prep_tracker.tsv (default: <project_dir>/prep_tracker.tsv)")
args = parser.parse_args()

ROOT       = Path(args.project_dir).resolve()
BIDS       = ROOT / "bids"
NORDIC     = ROOT / "derivatives" / "nordic"
SUMMARIES  = ROOT / "summaries"
if args.participants:
    PARTS_TSV = Path(args.participants)
else:
    _beh_tsv  = ROOT / "beh" / "participants.tsv"
    _bids_tsv = ROOT / "bids" / "participants.tsv"
    PARTS_TSV = _beh_tsv if _beh_tsv.exists() else (_bids_tsv if _bids_tsv.exists() else None)


# ---------------------------------------------------------------------------
# JSON helpers (shared logic with recode tracker)
# ---------------------------------------------------------------------------

def _extract_ses_label(suffix: str) -> str:
    """Return session label string from the part of a JSON filename after the subject ID."""
    m = re.search(r'[-_]ses[-_]?(\w+)$', suffix)
    if m:
        return m.group(1)
    m = re.search(r'[-_](\w+)$', suffix)
    if m:
        return m.group(1)
    return '1'


def _load_descriptions(json_path: Path) -> list:
    with open(json_path) as f:
        d = json.load(f)
    result = []
    for entry in d.get("descriptions", []):
        if "custom_entities" in entry:
            result.append({
                "datatype":        entry.get("datatype", ""),
                "custom_entities": entry["custom_entities"],
                "suffix":          entry["suffix"],
            })
        elif "customLabels" in entry:
            result.append({
                "datatype":        entry.get("dataType", ""),
                "custom_entities": entry.get("customLabels", ""),
                "suffix":          entry.get("modalityLabel", ""),
            })
    return result


def _find_jsons_for_subject(sub_id: str) -> dict:
    """Return {ses_label (str): json_path} from bids_summaries/."""
    candidates = {}
    for jf in sorted(SUMMARIES.glob(f"{sub_id}*.json")):
        stem = jf.stem
        if not stem.startswith(sub_id):
            continue
        suffix = stem[len(sub_id):]
        if suffix and re.match(r'^[a-zA-Z]$', suffix):
            continue
        try:
            n = len(json.load(open(jf)).get("descriptions", []))
        except Exception:
            continue
        ses_label = _extract_ses_label(suffix)
        if ses_label not in candidates or n > candidates[ses_label][1]:
            candidates[ses_label] = (jf, n)
    return {k: v[0] for k, v in candidates.items()}


def _find_ses_dir(base: Path, sub_id: str, ses_label: str):
    sub_dir = base / f"sub-{sub_id}"
    if not sub_dir.exists():
        return None
    for d in sub_dir.iterdir():
        if d.is_dir() and d.name.startswith("ses-"):
            part = d.name[4:]
            if part.isdigit() and ses_label.isdigit() and int(part) == int(ses_label):
                return d
            elif part == ses_label:
                return d
    return None


def _is_phase(ce: str) -> bool:
    return "part-phase" in ce or "MEph" in ce


# ---------------------------------------------------------------------------
# Column checks
# ---------------------------------------------------------------------------

def has_summaries_file(sub_id: str, ext: str) -> str:
    if any(SUMMARIES.glob(f"{sub_id}*.{ext}")):
        return "Y"
    # TSVs for 2* subjects live in the project root before JSON generation
    if ext == "tsv" and any(ROOT.glob(f"{sub_id}*.tsv")):
        return "Y"
    return ""


def bids_count(sub_id: str) -> str:
    if not any(SUMMARIES.glob(f"{sub_id}*.json")) or not any(SUMMARIES.glob(f"{sub_id}*.tsv")):
        return ""

    json_map = _find_jsons_for_subject(sub_id)
    if not json_map:
        return ""

    found = 0
    total = 0
    for ses_num, jf in json_map.items():
        ses_dir = _find_ses_dir(BIDS, sub_id, ses_num)
        descs = _load_descriptions(jf)
        total += len(descs)
        if ses_dir is None:
            continue
        ses_label = ses_dir.name[4:]
        bids_files = {p.name for p in ses_dir.rglob("*.nii.gz")}
        for entry in descs:
            ce = entry["custom_entities"]
            sfx = entry["suffix"]
            sep = "" if ce.startswith("_") else "_"
            expected = f"sub-{sub_id}_ses-{ses_label}{sep}{ce}_{sfx}.nii.gz"
            if expected in bids_files:
                found += 1

    if not found:
        return ""
    return "Y" if found == total else f"{found}/{total}"


def nordic_count(sub_id: str) -> str:
    nordic_sub = NORDIC / f"sub-{sub_id}"
    found = 0
    if nordic_sub.exists():
        for ses_dir in nordic_sub.iterdir():
            if not ses_dir.is_dir() or not ses_dir.name.startswith("ses-"):
                continue
            sd = ses_dir / "func"
            if sd.exists():
                found += len(list(sd.glob("*.nii.gz")))

    if not found:
        return ""

    bids_sub = BIDS / f"sub-{sub_id}"
    total = 0
    if bids_sub.exists():
        for ses_dir in bids_sub.iterdir():
            if not ses_dir.is_dir() or not ses_dir.name.startswith("ses-"):
                continue
            sd = ses_dir / "func"
            if sd.exists():
                total += sum(
                    1 for f in sd.glob("*.nii.gz")
                    if not _is_phase(f.name)
                )

    if not total:
        return str(found)
    return "Y" if found == total else f"{found}/{total}"


# ---------------------------------------------------------------------------
# Build tracker
# ---------------------------------------------------------------------------

if PARTS_TSV is not None:
    participants = pd.read_csv(PARTS_TSV, sep=None, engine="python")
    participants["participant_id"] = participants["participant_id"].astype(str)
    participants = participants.drop_duplicates(subset="participant_id")
    cohort_map = dict(zip(participants["participant_id"], participants["cohort"]))
    _parts_ids = set(participants["participant_id"])
else:
    cohort_map = {}
    _parts_ids = set()

def sub_ids_from(path: Path, prefix: str = "") -> set:
    if not path.exists():
        return set()
    ids = set()
    for d in path.iterdir():
        if d.is_dir() and (not prefix or d.name.startswith(prefix)):
            ids.add(d.name[len(prefix):])
    return ids

all_ids = _parts_ids

rows = []
for sub in sorted(all_ids):
    rows.append({
        "participant_id": sub,
        "cohort":         cohort_map.get(sub, ""),
        "summaries_tsv":  has_summaries_file(sub, "tsv"),
        "summaries_json": has_summaries_file(sub, "json"),
        "bids":           bids_count(sub),
        "nordic":         nordic_count(sub),
    })

df = pd.DataFrame(rows)
out = Path(args.output) if args.output else ROOT / "prep_tracker.tsv"
df.to_csv(out, index=False, sep="\t")
print(f"Saved: {out}")
print(df.to_string(index=False))
