import csv
import re
from collections import defaultdict
import shutil
import os
import json
import argparse
import sys
from pathlib import Path

# --- BIDS REGEX PATTERNS DEFINITION ---
# The patterns are designed to capture BIDS entities AND the entire 'run-XX' string 
# for accurate replacement, regardless of padding.
BIDS_PATTERNS = {
    # Functional: Captures run, echo (optional), part (optional), and task. Captures 'run-XX' explicitly.
    'func': re.compile(
        r"(?:ses-(?P<ses>[^_]+)_)?"
        r"task-(?P<task>[^_]+)_"
        r"(?:acq-(?P<acq>[^_]+)_)?"
        r"(?:dir-(?P<dir>[^_]+)_)?"
        r"(run-(?P<run>\d+))_"         # Captures 'run-XX'
        r"(?:echo-(?P<echo>\d+)_)?"
        r"(?:part-(?P<part>[^_]+)_)?"
        r".*(?P<ext>\.nii|\.nii\.gz|\.json)",
        re.IGNORECASE
    ),
    # Anatomical: Captures run and acquisition type (T1w/T2w). Captures 'run-XX' explicitly.
    'anat': re.compile(
        r"(?:ses-(?P<ses>[^_]+)_)?"
        r"(?:acq-(?P<acq>[^_]+)_)?"
        r"(run-(?P<run>\d+))_"         # Captures 'run-XX'
        r".*(?P<suffix>T1w|T2w|QALAS)\.(?P<ext>nii|nii\.gz|json)",
        re.IGNORECASE
    ),
    # Fieldmap: Captures run, direction (dir). Captures 'run-XX' explicitly.
    'fmap': re.compile(
        r"(?:ses-(?P<ses>[^_]+)_)?"
        r"(?:acq-(?P<acq>[^_]+)_)?"
        r"(?:dir-(?P<dir>[^_]+)_)?"
        r"(run-(?P<run>\d+))_"         # Captures 'run-XX'
        r".*(?P<suffix>epi|fieldmap|dwi|TB1TFL)\.(?P<ext>nii|nii\.gz|json|bval|bvec)",
        #r".*(?P<suffix>dwi)\.(?P<ext>nii|nii\.gz|json|bval|bvec)",
        re.IGNORECASE
        
    ),
    # Diffusion: Captures run, direction (dir), and acquisition (acq). Captures 'run-XX' explicitly.
    # Also includes .bval and .bvec files which are typical for dwi.
    'dwi': re.compile(
        r"(?:ses-(?P<ses>[^_]+)_)?"
        r"(?:acq-(?P<acq>[^_]+)_)?"
        r"(?:dir-(?P<dir>[^_]+)_)?"
        r"(run-(?P<run>\d+))_"           # Captures 'run-XX'
        r".*(?P<suffix>dwi)\.(?P<ext>nii|nii\.gz|json|bval|bvec)",
        re.IGNORECASE
    )
}


def flatten_sessions(ses_combined_path):
    """
    Flattens nested session folders inside ses-combined so that:
        ses-combined/ses-01/anat/file.nii.gz    ses-combined/anat/file.nii.gz
        ses-combined/ses-02/func/file.nii.gz    ses-combined/func/file.nii.gz

    Moves only top-level files (not recursive).
    Raises FileExistsError if a file already exists in the destination.
    Deletes empty directories after moving files.
    Prints each move operation.
    """
    ses_combined = Path(ses_combined_path)
    if not ses_combined.is_dir():
        raise NotADirectoryError(f"{ses_combined} is not a valid directory")

    print(f"Flattening nested sessions inside: {ses_combined}")

    # Find session directories inside ses-combined (e.g., ses-01, ses-02)
    for ses_dir in ses_combined.glob("ses-0*"):
        if not ses_dir.is_dir():
            continue

        print(f"\nProcessing {ses_dir.name}")

        # For each modality directory (anat, func, fmap, etc.)
        for modality_dir in ses_dir.iterdir():
            if not modality_dir.is_dir():
                continue

            combined_modality = ses_combined / modality_dir.name
            combined_modality.mkdir(parents=True, exist_ok=True)

            for file in modality_dir.iterdir():
                if file.is_file():
                    target = combined_modality / file.name
                    if target.exists():
                        raise FileExistsError(f"File already exists: {target}")
                    #print(f"Moving {file.relative_to(ses_combined)}  {target.relative_to(ses_combined)}")
                    shutil.move(str(file), str(target))

            # Remove modality directory if empty
            try:
                modality_dir.rmdir()
                #print(f"Removed empty directory: {modality_dir.relative_to(ses_combined)}")
            except OSError:
                print(f"Could not remove {modality_dir.relative_to(ses_combined)} (not empty)")

        # Remove session directory if empty
        try:
            ses_dir.rmdir()
            #print(f"Removed empty session directory: {ses_dir.relative_to(ses_combined)}")
        except OSError:
            print(f"Could not remove {ses_dir.relative_to(ses_combined)} (not empty)")

    print("\nFlattening complete.")


def get_original_run_string(match_obj):
    """Finds the captured 'run-XX' string from the match object's groups."""
    for group_val in match_obj.groups():
        if group_val and group_val.startswith('run-'):
            # The captured group might include a trailing underscore from the regex definition
            return group_val.rstrip('_') 
    return None

def renumber_bids_runs_preserve_structure(sub_path, output_dir, preview=True, output_csv=None):
    """
    Renumber runs and copy BIDS files to a 'ses-combined' session,
    preserving folder structure relative to sub_path and updating 'ses-' in filenames.
    """
    if not preview and os.path.exists(output_dir):
        print(f"Deleting existing '{output_dir}'...")
        shutil.rmtree(output_dir)
    
    # 1. Find all relevant files recursively
    exclude_dirs = ["ses-combined"] if preview else []
    files = []

    for root, dirs, filenames in os.walk(sub_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in filenames:
            if f.endswith(('.nii', '.nii.gz', '.json', '.bval', '.bvec')):
                files.append(os.path.join(root, f))

    # grouped: Keyed by (MODALITY, BIDS_GROUPING_KEY, ORIGINAL_SES_ID, ORIGINAL_RUN_ID)
    grouped = defaultdict(list)
    modalities_found = set()

    # 2. Pre-process: Group files by acquisition type for sequential numbering
    for fpath in files:
        fname = os.path.basename(fpath)
        lower_path = fpath.lower()
        
        # --- Modality Detection (UPDATED with dwi) ---
        modality = None
        if '/func/' in lower_path:
            modality = 'func'
        elif '/anat/' in lower_path:
            modality = 'anat'
        # Check for dwi/ before fmap/ as 'dwi' contains 'i' and could potentially be confused 
        # if using complex path logic, though here it's safe.
        elif '/dwi/' in lower_path:
            modality = 'dwi'
        elif '/fmap/' in lower_path:
            modality = 'fmap'
        
        if not modality:
            continue

        pattern = BIDS_PATTERNS.get(modality)
        m = pattern.search(fname)

        if m:
            groups = m.groupdict(default="")
            
            # Entities used for internal sorting/provenance:
            run_id = groups.get('run') or "1"
            ses_id = groups.get('ses') or ""
            echo_id = groups.get('echo') or "1"
            
            # The key is what defines a unique run series that needs its own counter.
            # E.g., for anat, T1w and T2w are separate series. For fmap, AP and PA are separate.
            bids_grouping_key = (
                modality,
                groups.get('acq') or "",
                groups.get('dir') or "",
                groups.get('task') or "",
                groups.get('suffix') or "", # Key for anat (T1w vs T2w) and fmap (epi/fieldmap)
                groups.get('part') or "", # Key for func (mag/phase)
            )
            
            # Full key includes the session and run for correct ordering/sorting
            # (MODALITY, BIDS_GROUPING_KEY, ORIGINAL_SES_ID, ORIGINAL_RUN_ID)
            full_key = (modality, bids_grouping_key, ses_id, run_id)
            
            modalities_found.add(modality)
            
            grouped[full_key].append({
                'fpath': fpath, 
                'fname': fname, 
                'echo': int(echo_id),
                'modality': modality,
                'run_id': run_id,
                'original_run_str_in_file': get_original_run_string(m)
            })
    
    # --- Print Modalities Found ---
    print(f'Combining sessions for {os.path.basename(sub_path)}...')
    print("\n--- Modalities Found for Combination ---")
    if modalities_found:
        for mod in sorted(list(modalities_found)):
            print(f"- {mod}")
    else:
        print("No BIDS files matched the modality-specific patterns for combination.")
        return 
    print("------------------------------------------\n")

    # 3. Renumbering and Processing
    
    # Sort groups first by modality, then by session ID (ses-01 < ses-02), then by original run ID
    sorted_groups = sorted(grouped.items(), key=lambda x: (x[0][0], x[0][2], x[0][3]))

    # Dictionary to hold the next available run number for each unique BIDS group key
    modality_run_counters = defaultdict(lambda: 1)
    csv_rows = []

    for full_key, items in sorted_groups:
        modality = full_key[0]
        bids_grouping_key = full_key[1]
        original_ses = full_key[2]
        original_run = full_key[3]
        
        # Get the next sequential run number for this specific acquisition type (e.g., T1w run counter, AP fmap run counter)
        new_run_num = modality_run_counters[bids_grouping_key]

        # Sort items within the group primarily by echo number (to keep echo-1 files together)
        for item in sorted(items, key=lambda x: x['echo']):
            fpath = item['fpath']
            fname = item['fname']
            original_run_str_in_file = item['original_run_str_in_file'] # e.g., 'run-01' or None
            
            rel_dir = os.path.relpath(os.path.dirname(fpath), sub_path)

            new_run_str = f"run-{new_run_num:02d}"
            new_fname = fname
            
            # 1. Replace run- entity (using the captured string for robustness)
            if original_run_str_in_file:
                new_fname = new_fname.replace(original_run_str_in_file, new_run_str)
            else:
                # This should only happen if the regex failed to capture run- but found the file
                print(f"Warning: Could not find 'run-' entity for renumbering in {fname}. Skipping run renumbering.")

            # 2. Replace ses- entity (using direct string replacement for robustness)
            if original_ses:
                original_ses_str = f"ses-{original_ses}"
                new_fname = new_fname.replace(original_ses_str, "ses-combined")
            
            # Determine new path
            new_fpath = os.path.join(output_dir, rel_dir, new_fname)

            print(f"Original ({modality} ses-{original_ses} run-{original_run}): {fname}")
            print(f"New ({modality} ses-combined {new_run_str}): {new_fname}")
            print("-" * 20)
            csv_rows.append({
                "modality":          modality,
                "original_ses":      f"ses-{original_ses}" if original_ses else "",
                "original_run":      f"run-{original_run}",
                "original_filename": fname,
                "new_run":           new_run_str,
                "new_filename":      new_fname,
            })
            if not preview:
                os.makedirs(os.path.dirname(new_fpath), exist_ok=True)
                shutil.copy2(fpath, new_fpath)
                if new_fname.lower().endswith('.json'):
                    with open(new_fpath, 'r') as g:
                        func_json = json.load(g)
                    func_json["OriginalSession"] = f"ses-{original_ses}" if original_ses else "N/A"
                    func_json["OriginalRun"] = f"run-{original_run}"
                    func_json["OriginalFilename"] = fname
                    func_json["NewRun"] = new_run_str
                    with open(new_fpath, 'w') as g:
                        json.dump(func_json, g, indent=4)
                

        # Increment the counter for this specific acquisition type
        modality_run_counters[bids_grouping_key] += 1
    
    if output_csv:
        fieldnames = ["modality", "original_ses", "original_run", "original_filename", "new_run", "new_filename"]
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"\nRename mapping saved to: {output_csv}")

    if not preview:
        print("\nFinalizing 'ses-combined'...")
        flatten_sessions(output_dir)


#%% Main Execution

parser = argparse.ArgumentParser(
    description="Combine BIDS sessions for a single subject into 'ses-combined' with independent run counters per modality type."
)
parser.add_argument("-b", "--bidssubj", type=str, required=True, help="Subject ID (e.g., 2008101 for sub-2008101)")
parser.add_argument("-p", "--preview", action="store_true", help="Run in preview mode (do not write files).")
parser.add_argument("-o", "--output", type=str, default=None, help="Path to save rename mapping as CSV.")
parser.add_argument("-d", "--bidsdir", type=str, default=None, help="Path to BIDS derivatives directory containing sub-* folders. Defaults to derivatives/nordic relative to cwd.")
args = parser.parse_args()

bids_id = args.bidssubj
sub_folder = 'sub-' + bids_id

mainDir = args.bidsdir if args.bidsdir else os.path.join(os.getcwd(), 'derivatives/nordic')
source = os.path.join(mainDir, sub_folder)
out = os.path.join(source, 'ses-combined')

# Validation
if not os.path.exists(source):
    sys.exit(f"Error: Source folder '{source}' does not exist. Please check the 'mainDir' definition.")
    
# Preparation
combinedfolder = os.path.join(source,'ses-combined')
if not args.preview and os.path.exists(combinedfolder):
    print(f"Deleting existing '{combinedfolder}'...")
    shutil.rmtree(combinedfolder)  

# Execute the renumbering function
renumber_bids_runs_preserve_structure(source, output_dir=out, preview=args.preview, output_csv=args.output)
