#!/usr/bin/env python3
import os
import re
import json
import argparse
import csv
from glob import glob
import sys

"""
Assigns fieldmaps to fMRI scans by matching ShimSettings, prioritizing:
  1. Non-GE fmaps
  2. GE fmaps
  3. Fallback by OriginalSession (if no Shim match)
Ensures each func run is assigned to only one fmap pair.
Logs all pairing decisions, including unmatched fmaps and funcs.
"""

# ----------------------------
# Helper functions
# ----------------------------
def extract_bids_key(fname):
    """Extracts BIDS entities for AP/PA pairing."""
    entities = {}
    pattern = r'(?P<key>sub|ses|run|acq|rec)-(?P<val>[^_]+)'
    for match in re.finditer(pattern, fname):
        entities[match.group("key")] = match.group("val")
    bids_order = ["sub", "ses", "acq", "rec", "run"]
    key_parts = [f"{k}-{entities[k]}" for k in bids_order if k in entities]
    return "_".join(key_parts)

def deprioritize_acq_ge(keys):
    """Sort keys so acq-GE fmaps are handled last."""
    return sorted(keys, key=lambda k: "acq-GE" in k)

def get_bids_relative_path(full_path):
    """Return relative BIDS path starting at ses-* or func/."""
    parts = full_path.split('/')
    for i, part in enumerate(parts):
        if part.startswith('ses-'):
            return '/'.join(parts[i:])
    for i, part in enumerate(parts):
        if part == 'func':
            return '/'.join(parts[i:])
    raise ValueError("Cannot find 'ses-*' or 'func' in path: " + full_path)

# ----------------------------
# Parse arguments
# ----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("ses_path", help="Full path to BIDS sub/ses directory")
args = parser.parse_args()

subject_path = args.ses_path.rstrip(os.path.sep) + os.path.sep
print(f"***** {subject_path}")

if not os.path.isabs(subject_path):
    sys.exit("Error: Please provide an absolute path to the session directory.")

# ----------------------------
# Extract subject ID and session ID
# ----------------------------
match = re.search(r"(sub-[a-zA-Z0-9]+)", subject_path)
if not match:
    sys.exit("Error: Could not extract subject ID from path.")
subject_id = match.group(1)

# Extract session ID (optional depending on directory structure)
match_ses = re.search(r"(ses-[a-zA-Z0-9]+)", subject_path)
session_id = match_ses.group(1) if match_ses else None

# ----------------------------
# Load func and fmap files
# ----------------------------
func_all = sorted(glob(subject_path + '/func/*bold.json'))
fmap_jsons = sorted(glob(subject_path + '/fmap/*.json'))
fmap_runs = {}
used_shim_settings = set()
assigned_funcs = set()  # Keep track of funcs already assigned
log_rows = []

if not fmap_jsons:
    print(f"Warning: No fmap JSONs found in {subject_path}/fmap/")
if not func_all:
    print(f"Warning: No functional JSONs found in {subject_path}/func/")

# Step 0: Clear any existing IntendedFor fields
for fmap_json in fmap_jsons:
    with open(fmap_json, 'r') as f:
        fmap_data = json.load(f)
    if "IntendedFor" in fmap_data:
        print(f"Clearing IntendedFor from: {fmap_json}")
        del fmap_data["IntendedFor"]
    with open(fmap_json, 'w') as f:
        json.dump(fmap_data, f, indent=4, sort_keys=True)

# Step 1: Group fmaps by key (ignoring dir-AP/PA)
for fmap in fmap_jsons:
    key = extract_bids_key(os.path.basename(fmap))
    fmap_runs.setdefault(key, []).append(fmap)

# Step 2: Process fmaps by priority
for key in deprioritize_acq_ge(fmap_runs):
    fmap_pair = fmap_runs[key]

    def log(key_suffix, shim, matched, reason):
        full_key = key_suffix if key_suffix.startswith("sub-") else f"{subject_id}_{key_suffix}"
        log_rows.append([full_key, shim, matched, reason])

    if len(fmap_pair) != 2:
        shim_val = "N/A"
        try:
            with open(fmap_pair[0], 'r') as f:
                j = json.load(f)
                shim_val = j.get("ShimSetting", "N/A")
        except Exception:
            pass
        log(key, shim_val, "None", f"Unpaired fmap (found {len(fmap_pair)} images)")
        continue

    # Load both fmap JSONs
    with open(fmap_pair[0]) as f1, open(fmap_pair[1]) as f2:
        fmap_json1 = json.load(f1)
        fmap_json2 = json.load(f2)

    shim1 = fmap_json1.get("ShimSetting")
    shim2 = fmap_json2.get("ShimSetting")

    if shim1 is None or shim2 is None:
        log(key, shim1 or shim2 or "N/A", "None", "Missing ShimSetting")
        continue

    if shim1 != shim2:
        log(key, f"{shim1} vs {shim2}", "None", "Shim mismatch in pair")
        continue

    shim_setting = tuple(shim1)
    fmap_orig_session = fmap_json1.get("OriginalSession")

    if shim_setting in used_shim_settings:
        log(key, shim_setting, "None", "Duplicate shim setting used")
        continue

# Step 3: Try to match to func (only unassigned funcs)
    func_list = []
    for func in func_all:
        if func in assigned_funcs:
            continue
        with open(func) as g:
            func_json = json.load(g)
        shim_func = func_json.get("ShimSetting")
        
        # Match by ShimSetting
        if shim_func and tuple(shim_func) == shim_setting:
            func_nii_candidates = glob(func.replace('.json', '.nii*'))
            if func_nii_candidates:
                func_nii = func_nii_candidates[0]
                func_nii_rel = get_bids_relative_path(func_nii).replace('//', '/')
                func_list.append(func_nii_rel)
                assigned_funcs.add(func)  # mark as assigned

    # Step 3b: Fallback by OriginalSession if no Shim match (CORRECTED LOGIC)
    if fmap_orig_session:
    #if not func_list and fmap_orig_session:
        fallback_assigned = []
        for func in func_all:
            if func in assigned_funcs:
                continue
            with open(func) as g:
                func_json = json.load(g)
            
            # Match by OriginalSession
            if func_json.get("OriginalSession") == fmap_orig_session:
                func_nii_candidates = glob(func.replace('.json', '.nii*'))
                if func_nii_candidates:
                    func_nii = func_nii_candidates[0]
                    func_nii_rel = get_bids_relative_path(func_nii).replace('//', '/')
                    
                    # DO NOT break. Collect all matching unassigned funcs.
                    func_list.append(func_nii_rel)
                    assigned_funcs.add(func)
                    fallback_assigned.append(func_nii_rel) 

        # Log all fallback assignments ONCE
        if fallback_assigned:
            log(key, shim_setting, ";".join(fallback_assigned), "Fallback: OriginalSession match")

    # Step 4: Assign to fmap JSON if matches found
    if func_list:
        for fmap_json_path in fmap_pair:
            with open(fmap_json_path, 'r') as f:
                fmap_json = json.load(f)
            fmap_json["IntendedFor"] = func_list
            with open(fmap_json_path, 'w') as f:
                json.dump(fmap_json, f, indent=4, sort_keys=True)
        used_shim_settings.add(shim_setting)
        
        # Log 'Assigned' ONLY if it was a SHIM match (i.e., not already logged by fallback)
        if not any(r[0].endswith(key) for r in log_rows):
            log(key, shim_setting, ";".join(func_list), "Assigned")
    else:
        log(key, shim_setting, "None", "No matching func found")

# Step 5: Log func files with no matching fmap
for func in func_all:
    if func in assigned_funcs:
        continue
    func_nii_candidates = glob(func.replace('.json', '.nii*'))
    if not func_nii_candidates:
        continue
    func_nii_rel = get_bids_relative_path(func_nii_candidates[0])
    with open(func) as f:
        func_json = json.load(f)
    shim_func = func_json.get("ShimSetting", "N/A")
    log_rows.append([
        f"{subject_id}_{os.path.basename(func)}",
        shim_func,
        func_nii_rel,
        "Func has no matching fmap"
    ])

# ----------------------------
# Write CSV log
# ----------------------------
#log_file = os.path.join(subject_path, f"{subject_id}_fmap_matching_log.csv")
#log_file = os.path.join(os.getcwd(), f"{subject_id}_fmap_matching_log.csv")

# Build filename: sub-01_ses-01_fmap_matching_log.csv (or sub-01_fmap_matching_log.csv if no ses found)
if session_id:
    log_name = f"{subject_id}_{session_id}_fmap_matching_log.csv"
else:
    log_name = f"{subject_id}_fmap_matching_log.csv"

log_file = os.path.join(os.getcwd(), log_name)

with open(log_file, 'w', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["FmapKey", "ShimSetting", "MatchedFuncs", "Reason"])
    writer.writerows(log_rows)

print(f"\nLog written to: {log_file}")
