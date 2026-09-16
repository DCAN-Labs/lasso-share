#!/usr/bin/env python3
"""
IntendedFor_JSBR_prenordic.py
(ShimSetting-gated, raw-mag preferred, block-aware, AP/PA mirroring, no-subject paths)

Populate fmap/*.json "IntendedFor" by assigning each functional run (grouped across echoes)
to EPI fieldmaps. Primary gating uses ShimSetting equality to prevent cross-session contamination.
Within each ShimSetting group, assignment is *block-aware*: each fieldmap is labeled as pre- or
post-block scan based on local timeline density; runs inside its window are matched to it, with
opposite-PE + geometry preference. AP/PA pairs mirror IntendedFor lists.

Functional selection preference:
  1) Use ONLY original (non-NORDIC) magnitude BOLDs: filenames contain "_part-mag_" and NOT "NORDIC"
  2) Else use any BOLD that is NOT a phase image (exclude "part-phase")  covers post-NORDIC layouts

IntendedFor entries are written WITHOUT the leading subject folder, e.g.:
  "ses-7T1/func/sub-XYZ_ses-7T1_task-rest_run-01_echo-1_part-mag_bold.nii.gz"

Examples:
  python IntendedFor_JSBR_prenordic.py /path/bids --sub sub-01 --ses ses-7T1               # dry run
  python IntendedFor_JSBR_prenordic.py /path/bids --sub sub-01 --ses ses-7T1 --write
  python IntendedFor_JSBR_prenordic.py /path/bids --sub sub-01 --ses ses-7T1 --write --backup
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict

FLOAT_TOL = 1e-6

# ---------------- I/O helpers ----------------

def read_json(p: Path):
    try:
        with p.open("r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to read {p}: {e}", file=sys.stderr)
        return {}

def write_json(p: Path, obj, backup=False):
    try:
        if backup and p.exists():
            bak = p.with_suffix(p.suffix + ".bak")
            bak.write_text(p.read_text())
        with p.open("w") as f:
            json.dump(obj, f, indent=4)
            f.write("\n")
    except Exception as e:
        print(f"[ERROR] Failed to write {p}: {e}", file=sys.stderr)

# ---------------- robust time parsing ----------------

def parse_date(s):
    if not s:
        return None
    try:
        if "-" in s:
            return datetime.strptime(s, "%Y-%m-%d").date()
        return datetime.strptime(s, "%Y%m%d").date()
    except Exception:
        return None

def parse_time_any(s):
    if not s:
        return None
    s = s.strip()
    try:
        if ":" in s:
            if "." in s:
                base, frac = s.split(".")
                frac = (frac + "000000")[:6]
                return datetime.strptime(f"{base}.{frac}", "%H:%M:%S.%f").time()
            return datetime.strptime(s, "%H:%M:%S").time()
        else:
            if "." in s:
                base, frac = s.split(".")
                frac = (frac + "000000")[:6]
                return datetime.strptime(f"{base}.{frac}", "%H%M%S.%f").time()
            return datetime.strptime(s, "%H%M%S").time()
    except Exception:
        return None

def parse_datetime_any(s):
    if not s:
        return None
    s = s.strip().replace("T", " ")
    try:
        if "." in s:
            base, frac = s.split(".")
            frac = (frac + "000000")[:6]
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y%m%d %H%M%S.%f"):
                try:
                    return datetime.strptime(f"{base}.{frac}", fmt)
                except Exception:
                    pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y%m%d %H%M%S"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
    except Exception:
        pass
    return None

def get_timestamp(meta: dict, path: Path):
    """
    Seconds since epoch from (in order): AcquisitionDateTime;
    AcquisitionDate + AcquisitionTime; AcquisitionTime only (epoch day);
    SeriesNumber proxy; file mtime fallback.
    """
    s = meta.get("AcquisitionDateTime")
    dt = parse_datetime_any(s) if s else None
    if dt:
        return dt.timestamp()

    d = parse_date(meta.get("AcquisitionDate"))
    t = parse_time_any(meta.get("AcquisitionTime"))
    if d and t:
        try:
            return datetime.combine(d, t).timestamp()
        except Exception:
            pass

    if t:
        try:
            return datetime.combine(date(1970, 1, 1), t).timestamp()
        except Exception:
            pass

    try:
        s_num = float(meta.get("SeriesNumber"))
        return 1_000_000.0 + s_num * 60.0
    except Exception:
        pass

    try:
        return path.stat().st_mtime
    except Exception:
        return 0.0

# ---------------- name helpers ----------------

def strip_echo_and_part(basename: str) -> str:
    """Drop _echo-# and _part-(mag|phase) to form a run key across echoes/parts."""
    no_echo = re.sub(r"_echo-\d+\b", "", basename)
    return re.sub(r"_part-(mag|phase)\b", "", no_echo)

def opposite_pe(pe: str):
    if not pe:
        return None
    return pe[:-1] if pe.endswith("-") else pe + "-"

def approx_equal(a, b, tol=FLOAT_TOL):
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return a == b

def listify(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]

# ---------------- geometry + shim ----------------

def geom_signature(meta: dict):
    return {
        "BaseResolution": meta.get("BaseResolution"),
        "AcquisitionMatrixPE": meta.get("AcquisitionMatrixPE"),
        "ReconMatrixPE": meta.get("ReconMatrixPE"),
        "TotalReadoutTime": meta.get("TotalReadoutTime"),
        "EffectiveEchoSpacing": meta.get("EffectiveEchoSpacing"),
        "ParallelReductionFactorInPlane": meta.get("ParallelReductionFactorInPlane"),
        "MultibandAccelerationFactor": meta.get("MultibandAccelerationFactor"),
        "SliceThickness": meta.get("SliceThickness"),
        "SpacingBetweenSlices": meta.get("SpacingBetweenSlices"),
        "ImageOrientationPatientDICOM": meta.get("ImageOrientationPatientDICOM"),
        "PhaseEncodingDirection": meta.get("PhaseEncodingDirection"),
    }

def geom_compatible(fmap_meta: dict, func_meta: dict) -> bool:
    A = geom_signature(fmap_meta)
    B = geom_signature(func_meta)

    if A.get("PhaseEncodingDirection") and B.get("PhaseEncodingDirection"):
        if A["PhaseEncodingDirection"] != opposite_pe(B["PhaseEncodingDirection"]):
            return False

    scalar_keys = [
        "BaseResolution",
        "AcquisitionMatrixPE",
        "ReconMatrixPE",
        "TotalReadoutTime",
        "EffectiveEchoSpacing",
        "ParallelReductionFactorInPlane",
        "MultibandAccelerationFactor",
        "SliceThickness",
        "SpacingBetweenSlices",
    ]
    for k in scalar_keys:
        av = A.get(k); bv = B.get(k)
        if av is None or bv is None:
            continue
        tol = 1e-5 if ("Time" in k or "Spacing" in k) else 1e-3
        if not approx_equal(av, bv, tol=tol):
            return False

    a_ori = listify(A.get("ImageOrientationPatientDICOM"))
    b_ori = listify(B.get("ImageOrientationPatientDICOM"))
    if a_ori and b_ori:
        if len(a_ori) != len(b_ori):
            return False
        for av, bv in zip(a_ori, b_ori):
            if not approx_equal(av, bv, tol=1e-4):
                return False

    return True

def shim_key(meta: dict):
    """Return ShimSetting as an immutable tuple (or None if missing/invalid)."""
    ss = meta.get("ShimSetting")
    if isinstance(ss, (list, tuple)) and len(ss) > 0:
        try:
            return tuple(int(round(float(x))) for x in ss)
        except Exception:
            try:
                return tuple(ss)
            except Exception:
                return None
    return None

# ---------------- discovery ----------------

def _normalize_label_items(items, prefix):
    if not items:
        return None
    out = set()
    for it in items:
        name = it
        try:
            p = Path(it)
            parts = [part for part in p.parts if part.startswith(prefix)]
            if parts:
                name = parts[-1]
            else:
                name = p.name
        except Exception:
            pass
        if not name.startswith(prefix):
            name = f"{prefix}{name}"
        out.add(name)
    return out or None

def find_files(bids_root: Path, sub_filter=None, ses_filter=None):
    """
    Return dict keyed by (sub, ses) with lists of fmap jsons and *all* func jsons (filter later).
    ses may be None for subject-level datasets without sessions.
    """
    result = defaultdict(lambda: {"fmap_jsons": [], "func_jsons": []})

    subs = [p for p in bids_root.glob("sub-*") if p.is_dir()]
    if sub_filter:
        subs = [p for p in subs if p.name in sub_filter]

    for sub_path in subs:
        ses_dirs = list(sub_path.glob("ses-*"))
        ses_paths = ses_dirs if ses_dirs else [sub_path]

        if ses_filter and ses_dirs:
            ses_paths = [p for p in ses_paths if p.name in ses_filter]

        for ses_path in ses_paths:
            key = (sub_path.name, ses_path.name if ses_dirs else None)
            for j in ses_path.glob("fmap/*_epi.json"):
                result[key]["fmap_jsons"].append(j)
            for j in ses_path.glob("func/*_bold.json"):
                result[key]["func_jsons"].append(j)

    return result

# ---------------- selection helpers ----------------

def select_func_jsons_for_session(json_paths):
    """
    Preference:
      1) Use ONLY original, non-NORDIC magnitude BOLDs (fname has '_part-mag_' and NOT 'NORDIC')
      2) Else use any BOLD that is NOT a phase image (exclude 'part-phase')  covers post-NORDIC layouts
    """
    json_paths = sorted(json_paths)
    raw_mag = [p for p in json_paths if ("_part-mag_" in p.name) and ("NORDIC" not in p.name)]
    if raw_mag:
        return raw_mag
    return [p for p in json_paths if "part-phase" not in p.name]

# ---------------- assignment primitives ----------------

def median_abs_deltas(times, ref):
    if not times:
        return float("inf")
    deltas = sorted(abs(t - ref) for t in times)
    n = len(deltas)
    mid = n // 2
    if n % 2 == 1:
        return deltas[mid]
    return 0.5 * (deltas[mid - 1] + deltas[mid])

def drop_subject_prefix(path_str: str) -> str:
    if path_str.startswith("sub-") and "/" in path_str:
        return path_str.split("/", 1)[1]
    return path_str

def intended_rel_without_sub(nii_path: Path, bids_root: Path) -> str:
    try:
        rel = nii_path.relative_to(bids_root).as_posix()
    except Exception:
        rel = nii_path.as_posix()
    return drop_subject_prefix(rel)

DIR_RE = re.compile(r"_dir-[^_]+")

def pair_key_from_name(fname: str) -> str:
    base = fname[:-5] if fname.endswith(".json") else fname
    return DIR_RE.sub("", base)

# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bids_root", type=Path, help="Path to BIDS root (directory containing sub-*/)")
    ap.add_argument("--write", action="store_true", help="Write IntendedFor into fmap jsons (default: dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="Print mapping only (default if --write not given)")
    ap.add_argument("--sub", dest="subs", action="append", help="Limit to specific subject(s): 'sub-01' or path to sub-01")
    ap.add_argument("--ses", dest="sess", action="append", help="Limit to specific session(s): 'ses-7T1' or path to ses-7T1")
    ap.add_argument("--backup", action="store_true", help="Also write .bak alongside modified JSONs (default: off)")
    ap.add_argument("--assign-mode", choices=["auto", "nearest", "lookback", "lookforward"], default="auto",
                    help="auto=block-aware; nearest=closest fmap; lookback=use previous fmap; lookforward=use next fmap.")
    ap.add_argument("--ignore-shim", action="store_true",
                    help="Do not gate by ShimSetting; allow cross-shim matching (not recommended for ses-combined).")
    args = ap.parse_args()

    if not args.write:
        args.dry_run = True

    root = args.bids_root
    if not root.exists():
        print(f"[ERROR] {root} does not exist", file=sys.stderr)
        sys.exit(1)

    sub_filter = _normalize_label_items(args.subs, "sub-")
    ses_filter = _normalize_label_items(args.sess, "ses-")

    inventory = find_files(root, sub_filter=sub_filter, ses_filter=ses_filter)

    total_links = 0
    for (sub, ses), lists in sorted(inventory.items()):
        if not lists["fmap_jsons"]:
            continue

        hdr = f"{sub} {ses or ''}".strip()
        print(f"\n=== {hdr} ===")

        # Load fmaps with metadata/time/shim
        fmap_entries = []
        for jpath in sorted(lists["fmap_jsons"]):
            meta = read_json(jpath)
            nifti = jpath.with_suffix("").with_suffix(".nii.gz")
            fmap_entries.append({
                "json": jpath,
                "nii": nifti,
                "meta": meta,
                "time": get_timestamp(meta, jpath),
                "shim": shim_key(meta),
            })

        # Select func JSONs per preference, then load with time/shim
        chosen_func_jsons = select_func_jsons_for_session(lists["func_jsons"])
        if not chosen_func_jsons:
            print("[INFO] No usable functional JSONs (none or only phase). Skipping session.")
            continue

        raw_func_entries = []
        for jpath in sorted(chosen_func_jsons):
            meta = read_json(jpath)
            nifti = jpath.with_suffix("").with_suffix(".nii.gz")
            raw_func_entries.append({
                "json": jpath,
                "nii": nifti,
                "meta": meta,
                "time": get_timestamp(meta, jpath),
                "shim": shim_key(meta),
            })

        # Group func echoes by run
        func_groups = defaultdict(list)
        for fe in raw_func_entries:
            key = strip_echo_and_part(fe["json"].name)
            func_groups[key].append(fe)

        # Representative per run: earliest timestamp, tie-break EchoNumber
        run_reps = []
        for gkey, files in func_groups.items():
            rep = min(files, key=lambda x: (x["time"], x["meta"].get("EchoNumber", 0)))
            run_reps.append({"gkey": gkey, "rep": rep})
        if not run_reps:
            print("No functional runs found after selection.")
            continue

        # Sort fmaps/runs by time
        fmap_entries.sort(key=lambda x: x["time"])
        run_reps.sort(key=lambda x: x["rep"]["time"])

        # Build AP/PA pair index for mirroring later
        pair_members = defaultdict(list)
        for fm in fmap_entries:
            pk = pair_key_from_name(fm["json"].name)
            pair_members[pk].append(fm["json"])

        # Group by shim
        if args.ignore_shim:
            fmaps_by_shim = {None: fmap_entries}
            runs_by_shim  = {None: run_reps}
            shim_keys = {None}
        else:
            fmaps_by_shim = defaultdict(list)
            for fm in fmap_entries:
                fmaps_by_shim[fm["shim"]].append(fm)
            runs_by_shim = defaultdict(list)
            for rr in run_reps:
                runs_by_shim[rr["rep"]["shim"]].append(rr)
            shim_keys = set(runs_by_shim.keys())

        fmap_to_intended = defaultdict(set)

        def add_run_to_fmap(fmap_obj, group_key):
            for fe in sorted(func_groups[group_key], key=lambda x: x["meta"].get("EchoNumber", 0)):
                rel_no_sub = intended_rel_without_sub(fe["nii"], root)
                fmap_to_intended[fmap_obj["json"]].add(rel_no_sub)

        for sk in sorted(shim_keys, key=lambda x: (str(type(x)), x)):
            group_fmaps = fmaps_by_shim.get(sk, [])
            group_runs  = runs_by_shim.get(sk, [])
            if not group_runs:
                continue

            pool_fmaps = group_fmaps if group_fmaps else fmap_entries
            if not group_fmaps:
                print(f"[WARN] No fmap with matching ShimSetting for shim={sk}; "
                      f"falling back to global pool for {len(group_runs)} run(s).")

            pool_fmaps = sorted(pool_fmaps, key=lambda x: x["time"])
            group_runs = sorted(group_runs,  key=lambda x: x["rep"]["time"])

            fm_times = [fm["time"] for fm in pool_fmaps]
            run_times = [r["rep"]["time"] for r in group_runs]

            # pre/post label per fmap (block-aware)
            fm_labels = []
            for j, fm in enumerate(pool_fmaps):
                if args.assign_mode == "lookback":
                    fm_labels.append("post")
                    continue
                if args.assign_mode == "lookforward":
                    fm_labels.append("pre")
                    continue
                if args.assign_mode == "nearest":
                    fm_labels.append("pre")  # ignored in nearest mode
                    continue

                left_start  = fm_times[j - 1] if j > 0 else float("-inf")
                left_end    = fm_times[j]
                right_start = fm_times[j]
                right_end   = fm_times[j + 1] if j + 1 < len(fm_times) else float("inf")

                left_runs  = [t for t in run_times if (t > left_start and t <= left_end)]
                right_runs = [t for t in run_times if (t > right_start and t <= right_end)]

                lc, rc = len(left_runs), len(right_runs)
                if rc > lc:
                    fm_labels.append("pre")
                elif lc > rc:
                    fm_labels.append("post")
                else:
                    mleft  = median_abs_deltas(left_runs,  fm["time"])
                    mright = median_abs_deltas(right_runs, fm["time"])
                    fm_labels.append("pre" if mright <= mleft else "post")

            for r in group_runs:
                rep = r["rep"]
                rt  = rep["time"]

                # Candidate set based on mode
                if args.assign_mode == "nearest":
                    candidates = pool_fmaps[:]
                else:
                    candidates = []
                    for j, fm in enumerate(pool_fmaps):
                        lbl = fm_labels[j]
                        if lbl == "post":
                            start = fm_times[j - 1] if j > 0 else float("-inf")
                            end   = fm_times[j]
                            in_window = (rt > start and rt <= end)
                        else:
                            start = fm_times[j]
                            end   = fm_times[j + 1] if j + 1 < len(fm_times) else float("inf")
                            in_window = (rt > start and rt <= end)
                        if in_window:
                            candidates.append(fm)
                    if not candidates:
                        candidates = pool_fmaps[:]

                # Opposite PE + geometry preference
                pe = rep["meta"].get("PhaseEncodingDirection")
                want_pe = opposite_pe(pe) if pe else None
                cands = []
                if want_pe:
                    for fm in candidates:
                        if fm["meta"].get("PhaseEncodingDirection") == want_pe and geom_compatible(fm["meta"], rep["meta"]):
                            cands.append(fm)
                if not cands and want_pe:
                    cands = [fm for fm in candidates if fm["meta"].get("PhaseEncodingDirection") == want_pe]
                if not cands:
                    cands = candidates

                chosen = min(cands, key=lambda fm: abs(rt - fm["time"]))
                add_run_to_fmap(chosen, r["gkey"])

        # ---- MIRROR: union IntendedFor across AP/PA pairs ----
        pair_to_union = defaultdict(set)
        for fmap_json, targets in fmap_to_intended.items():
            pk = pair_key_from_name(fmap_json.name)
            pair_to_union[pk].update(targets)

        final_targets_per_json = {}
        for pk, union_targets in pair_to_union.items():
            for member_json in pair_members.get(pk, []):
                final_targets_per_json[member_json] = sorted(union_targets)

        # Emit + write
        for jpath in sorted(final_targets_per_json.keys(), key=lambda p: p.name):
            meta = read_json(jpath)
            new_list = final_targets_per_json[jpath]
            meta["IntendedFor"] = new_list
            total_links += len(new_list)

            try:
                relp = jpath.relative_to(root)
            except Exception:
                relp = jpath
            print(f"\n[fmap] {relp}")
            for t in new_list:
                print(f"  - {t}")

            if args.write:
                write_json(jpath, meta, backup=args.backup)

    print(f"\nDone. {'Wrote' if not args.dry_run else 'Planned'} {total_links} IntendedFor links.")

if __name__ == "__main__":
    main()
# #!/usr/bin/env python3
# """
# IntendedFor_rawmagfirst.py

# Populate fmap/*.json "IntendedFor" by assigning each functional run (grouped across echoes)
# to the closest-in-time, opposite-PE EPI fieldmap in the same session, requiring compatible
# geometry/readout. Also mirrors IntendedFor lists across AP/PA pairs if both exist.

# This version is robust to:
# - Pre-NORDIC layout with ME-P-BOLD split into part-mag / part-phase
# - Post-cleanup NORDIC layout without part-* suffixes

# Preference rule:
# 1) If original (non-NORDIC) part-mag *_bold.json exist -> use ONLY those
# 2) Else -> use any non-phase *_bold.json (e.g., post-NORDIC), skipping part-phase

# IntendedFor entries are written WITHOUT the leading subject folder, e.g.:
#   "ses-7T1/func/sub-XYZ_ses-7T1_task-rest_run-01_echo-1_part-mag_bold.nii.gz"

# Usage examples:
#   python IntendedFor_rawmagfirst.py /path/to/bids --sub sub-01 --ses ses-7T1                     # dry-run
#   python IntendedFor_rawmagfirst.py /path/to/bids --sub sub-01 --ses ses-7T1 --write --backup    # write
# """

# import argparse
# import json
# import re
# import sys
# from pathlib import Path
# from datetime import datetime
# from collections import defaultdict

# FLOAT_TOL = 1e-6

# # ---------------- I/O helpers ----------------

# def read_json(p: Path):
#     try:
#         with p.open("r") as f:
#             return json.load(f)
#     except Exception as e:
#         print(f"[WARN] Failed to read {p}: {e}", file=sys.stderr)
#         return {}

# def write_json(p: Path, obj, backup=False):
#     try:
#         if backup and p.exists():
#             bak = p.with_suffix(p.suffix + ".bak")
#             bak.write_text(p.read_text())
#         with p.open("w") as f:
#             json.dump(obj, f, indent=4)
#             f.write("\n")
#     except Exception as e:
#         print(f"[ERROR] Failed to write {p}: {e}", file=sys.stderr)

# # ---------------- time / name helpers ----------------

# def seconds_of_day(acq_time: str):
#     if not acq_time:
#         return None
#     try:
#         if "." in acq_time:
#             base, frac = acq_time.split(".")
#             frac = (frac + "000000")[:6]
#             acq_time = f"{base}.{frac}"
#             t = datetime.strptime(acq_time, "%H:%M:%S.%f")
#         else:
#             t = datetime.strptime(acq_time, "%H:%M:%S")
#         return t.hour * 3600 + t.minute * 60 + t.second + (t.microsecond / 1e6)
#     except Exception:
#         return None

# def strip_echo(basename: str) -> str:
#     return re.sub(r"_echo-\d+\b", "", basename)

# def opposite_pe(pe: str):
#     if not pe:
#         return None
#     return pe[:-1] if pe.endswith("-") else pe + "-"

# def approx_equal(a, b, tol=FLOAT_TOL):
#     try:
#         return abs(float(a) - float(b)) <= tol
#     except Exception:
#         return a == b

# def listify(x):
#     if x is None:
#         return []
#     return x if isinstance(x, list) else [x]

# # ---------------- geometry matching ----------------

# def geom_signature(meta: dict):
#     return {
#         "BaseResolution": meta.get("BaseResolution"),
#         "AcquisitionMatrixPE": meta.get("AcquisitionMatrixPE"),
#         "ReconMatrixPE": meta.get("ReconMatrixPE"),
#         "TotalReadoutTime": meta.get("TotalReadoutTime"),
#         "EffectiveEchoSpacing": meta.get("EffectiveEchoSpacing"),
#         "ParallelReductionFactorInPlane": meta.get("ParallelReductionFactorInPlane"),
#         "MultibandAccelerationFactor": meta.get("MultibandAccelerationFactor"),
#         "SliceThickness": meta.get("SliceThickness"),
#         "SpacingBetweenSlices": meta.get("SpacingBetweenSlices"),
#         "ImageOrientationPatientDICOM": meta.get("ImageOrientationPatientDICOM"),
#         "PhaseEncodingDirection": meta.get("PhaseEncodingDirection"),
#     }

# def geom_compatible(fmap_meta: dict, func_meta: dict) -> bool:
#     A = geom_signature(fmap_meta)
#     B = geom_signature(func_meta)

#     if A.get("PhaseEncodingDirection") and B.get("PhaseEncodingDirection"):
#         if A["PhaseEncodingDirection"] != opposite_pe(B["PhaseEncodingDirection"]):
#             return False

#     scalar_keys = [
#         "BaseResolution",
#         "AcquisitionMatrixPE",
#         "ReconMatrixPE",
#         "TotalReadoutTime",
#         "EffectiveEchoSpacing",
#         "ParallelReductionFactorInPlane",
#         "MultibandAccelerationFactor",
#         "SliceThickness",
#         "SpacingBetweenSlices",
#     ]
#     for k in scalar_keys:
#         av = A.get(k); bv = B.get(k)
#         if av is None or bv is None:
#             continue
#         tol = 1e-5 if "Time" in k or "Spacing" in k else 1e-3
#         if not approx_equal(av, bv, tol=tol):
#             return False

#     a_ori = listify(A.get("ImageOrientationPatientDICOM"))
#     b_ori = listify(B.get("ImageOrientationPatientDICOM"))
#     if a_ori and b_ori:
#         if len(a_ori) != len(b_ori):
#             return False
#         for av, bv in zip(a_ori, b_ori):
#             if not approx_equal(av, bv, tol=1e-4):
#                 return False

#     return True

# # ---------------- discovery ----------------

# def _normalize_label_items(items, prefix):
#     """
#     Accept entries like 'ses-7T1', '7T1', '/path/.../ses-7T1', and return a set of canonical names.
#     For subs, prefix='sub-'; for sessions, prefix='ses-'.
#     """
#     if not items:
#         return None
#     out = set()
#     for it in items:
#         name = it
#         try:
#             p = Path(it)
#             parts = [part for part in p.parts if part.startswith(prefix)]
#             if parts:
#                 name = parts[-1]
#             else:
#                 name = p.name
#         except Exception:
#             pass
#         if not name.startswith(prefix):
#             name = f"{prefix}{name}"
#         out.add(name)
#     return out or None

# def find_files(bids_root: Path, sub_filter=None, ses_filter=None):
#     """
#     Return dict keyed by (sub, ses) with lists of fmap jsons and *all* func jsons (we'll filter later).
#     - sub_filter/ses_filter are sets like {'sub-01', ...} / {'ses-7T1', ...}
#     """
#     result = defaultdict(lambda: {"fmap_jsons": [], "func_jsons": []})

#     subs = [p for p in bids_root.glob("sub-*") if p.is_dir()]
#     if sub_filter:
#         subs = [p for p in subs if p.name in sub_filter]

#     for sub_path in subs:
#         ses_dirs = list(sub_path.glob("ses-*"))
#         ses_paths = ses_dirs if ses_dirs else [sub_path]

#         if ses_filter and ses_dirs:
#             ses_paths = [p for p in ses_paths if p.name in ses_filter]

#         for ses_path in ses_paths:
#             key = (sub_path.name, ses_path.name if ses_dirs else None)
#             for j in ses_path.glob("fmap/*_epi.json"):
#                 result[key]["fmap_jsons"].append(j)
#             # collect all bold jsons; selection happens in main()
#             for j in ses_path.glob("func/*_bold.json"):
#                 result[key]["func_jsons"].append(j)

#     return result

# # ---------------- selection helpers ----------------

# def select_func_jsons_for_session(json_paths):
#     """
#     Preference:
#       1) Use ONLY original, non-NORDIC part-mag bolds (fname has '_part-mag_'
#          and NOT 'NORDIC')
#       2) Else use any bold that is NOT a phase image (exclude 'part-phase')
#          (this covers post-NORDIC layouts with no 'part-*' segments)
#     """
#     json_paths = sorted(json_paths)
#     raw_mag = [p for p in json_paths
#                if ("_part-mag_" in p.name) and ("NORDIC" not in p.name)]
#     if raw_mag:
#         return raw_mag
#     # fallback: non-phase only
#     return [p for p in json_paths if "part-phase" not in p.name]

# # ---------------- assignment ----------------

# def choose_nearest_fmap(func_meta, fmap_candidates):
#     func_time = seconds_of_day(func_meta.get("AcquisitionTime"))
#     func_series = func_meta.get("SeriesNumber")
#     best = None
#     best_key = (float("inf"), float("inf"))
#     for fm in fmap_candidates:
#         fm_time = seconds_of_day(fm["meta"].get("AcquisitionTime"))
#         fm_series = fm["meta"].get("SeriesNumber")
#         dt = abs(func_time - fm_time) if (func_time is not None and fm_time is not None) else float("inf")
#         ds = abs(int(func_series) - int(fm_series)) if (func_series is not None and fm_series is not None) else float("inf")
#         key = (dt, ds)
#         if key < best_key:
#             best_key = key
#             best = fm
#     return best

# # ---- IntendedFor path helpers ----

# def drop_subject_prefix(path_str: str) -> str:
#     """Remove leading 'sub-.../' from a POSIX path string if present."""
#     if path_str.startswith("sub-") and "/" in path_str:
#         return path_str.split("/", 1)[1]
#     return path_str

# def intended_rel_without_sub(nii_path: Path, bids_root: Path) -> str:
#     """Return subject-relative path like 'ses-XXX/func/...nii.gz' (no leading subject)."""
#     try:
#         rel = nii_path.relative_to(bids_root).as_posix()
#     except Exception:
#         rel = nii_path.as_posix()
#     return drop_subject_prefix(rel)

# # ---- Pairing helpers (AP/PA mirroring) ----

# DIR_RE = re.compile(r"_dir-[^_]+")

# def pair_key_from_name(fname: str) -> str:
#     """
#     Build a pairing key for fmap filenames by removing the '_dir-XXX' segment.
#     Works on the basename string (with or without extension).
#     """
#     base = fname
#     if base.endswith(".json"):
#         base = base[:-5]
#     return DIR_RE.sub("", base)

# # ---------------- main ----------------

# def main():
#     ap = argparse.ArgumentParser()
#     ap.add_argument("bids_root", type=Path, help="Path to BIDS root (directory containing sub-*/)")
#     ap.add_argument("--write", action="store_true", help="Write IntendedFor into fmap jsons (default: dry-run)")
#     ap.add_argument("--dry-run", action="store_true", help="Print mapping only (default if --write not given)")
#     ap.add_argument("--sub", dest="subs", action="append", help="Limit to specific subject(s): 'sub-01' or path to sub-01")
#     ap.add_argument("--ses", dest="sess", action="append", help="Limit to specific session(s): 'ses-7T1' or path to ses-7T1")
#     ap.add_argument("--backup", action="store_true", help="Also write .bak alongside modified JSONs (default: off)")
#     args = ap.parse_args()

#     if not args.write:
#         args.dry_run = True

#     root = args.bids_root
#     if not root.exists():
#         print(f"[ERROR] {root} does not exist", file=sys.stderr)
#         sys.exit(1)

#     sub_filter = _normalize_label_items(args.subs, "sub-")
#     ses_filter = _normalize_label_items(args.sess, "ses-")

#     inventory = find_files(root, sub_filter=sub_filter, ses_filter=ses_filter)

#     total_links = 0
#     for (sub, ses), lists in sorted(inventory.items()):
#         if not lists["fmap_jsons"]:
#             continue

#         hdr = f"{sub} {ses or ''}".strip()
#         print(f"\n=== {hdr} ===")

#         # Load fmap entries
#         fmap_entries = []
#         for jpath in sorted(lists["fmap_jsons"]):
#             meta = read_json(jpath)
#             nifti = jpath.with_suffix("").with_suffix(".nii.gz")
#             fmap_entries.append({"json": jpath, "nii": nifti, "meta": meta})

#         # Select appropriate functional jsons for this session
#         selected_func_jsons = select_func_jsons_for_session(lists["func_jsons"])
#         if not selected_func_jsons:
#             print("[INFO] No functional JSONs selected (none or only phase images). Skipping session.")
#             continue

#         # Load func entries
#         func_entries = []
#         for jpath in sorted(selected_func_jsons):
#             meta = read_json(jpath)
#             nifti = jpath.with_suffix("").with_suffix(".nii.gz")
#             func_entries.append({"json": jpath, "nii": nifti, "meta": meta})

#         # Group func echoes by run key (basename without echo)
#         func_groups = defaultdict(list)
#         for fe in func_entries:
#             key = strip_echo(fe["json"].name)
#             func_groups[key].append(fe)

#         # Index fmaps by PE and also build AP/PA "pairs"
#         fmap_by_dir = defaultdict(list)
#         pair_members = defaultdict(list)  # pair_key -> list[Path to json]
#         for fm in fmap_entries:
#             pe = fm["meta"].get("PhaseEncodingDirection")
#             if pe:
#                 fmap_by_dir[pe].append(fm)
#             pk = pair_key_from_name(fm["json"].name)
#             pair_members[pk].append(fm["json"])

#         # Assign runs -> chosen fmap
#         fmap_to_intended = defaultdict(set)

#         for gkey, group_files in sorted(func_groups.items()):
#             # representative echo (first echo)
#             rep = sorted(group_files, key=lambda x: x["meta"].get("EchoNumber", 0))[0]
#             func_pe = rep["meta"].get("PhaseEncodingDirection")
#             want_pe = opposite_pe(func_pe) if func_pe else None

#             # geometry-compatible candidates, then relax if needed
#             candidates = []
#             if want_pe and want_pe in fmap_by_dir:
#                 for fm in fmap_by_dir[want_pe]:
#                     if geom_compatible(fm["meta"], rep["meta"]):
#                         candidates.append(fm)
#             if not candidates and want_pe and want_pe in fmap_by_dir:
#                 candidates = fmap_by_dir[want_pe][:]
#             if not candidates:
#                 candidates = fmap_entries[:]

#             chosen = choose_nearest_fmap(rep["meta"], candidates)
#             if not chosen:
#                 print(f"[WARN] No fmap choice for run {gkey} (func {rep['json'].name})")
#                 continue

#             # add all echoes of this run
#             for fe in sorted(group_files, key=lambda x: x["meta"].get("EchoNumber", 0)):
#                 rel_no_sub = intended_rel_without_sub(fe["nii"], root)
#                 fmap_to_intended[chosen["json"]].add(rel_no_sub)

#             ft = seconds_of_day(rep["meta"].get("AcquisitionTime"))
#             ct = seconds_of_day(chosen["meta"].get("AcquisitionTime"))
#             dt_str = f" (dt={abs(ft-ct):.1f}s)" if (ft is not None and ct is not None) else ""
#             print(f"Map {gkey} -> {chosen['json'].name}{dt_str}")

#         # ---- MIRROR: union IntendedFor across AP/PA pairs ----
#         pair_to_union = defaultdict(set)
#         for fmap_json, targets in fmap_to_intended.items():
#             pk = pair_key_from_name(fmap_json.name)
#             pair_to_union[pk].update(targets)

#         # Prepare final write set per fmap json
#         final_targets_per_json = {}
#         for pk, union_targets in pair_to_union.items():
#             for member_json in pair_members.get(pk, []):
#                 final_targets_per_json[member_json] = sorted(union_targets)

#         # Show + write
#         for jpath in sorted(final_targets_per_json.keys(), key=lambda p: p.name):
#             meta = read_json(jpath)
#             new_list = final_targets_per_json[jpath]
#             meta["IntendedFor"] = new_list
#             total_links += len(new_list)

#             print(f"\n[fmap] {jpath.relative_to(root)}")
#             for t in new_list:
#                 print(f"  - {t}")

#             if args.write:
#                 write_json(jpath, meta, backup=args.backup)

#     print(f"\nDone. {'Wrote' if not args.dry_run else 'Planned'} {total_links} IntendedFor links.")

# if __name__ == "__main__":
#     main()