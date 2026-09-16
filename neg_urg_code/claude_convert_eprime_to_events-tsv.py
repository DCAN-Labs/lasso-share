# import re
from datetime import datetime, timedelta
# import io
import os
import glob
import json
import pandas as pd
import numpy as np

## First, verify that the fMRI aquisition times line up from the event log and NIFTI 

def get_run_start_times(file_path_or_content, run_identifier="RunTitle", encoding='utf-16'):
    """
    Parses an E-Prime text log to find absolute start times for specific runs.
    
    This version is "Hierarchy Aware". It detects when a Run finishes (e.g., RunProc)
    and looks backwards to find the earliest 'OnsetTime' of any event (Level 3+) 
    that occurred within that run.
    
    Args:
        file_path_or_content (str): Path to .txt file OR raw string content.
        run_identifier (str): The variable that names the run (e.g. "RunTitle").
                              If this variable is found in a LogFrame, that Frame is considered the "End of Run".
        encoding (str): 'utf-16' (default) or 'utf-8'.
        
    Returns:
        list of dicts: [{'run_index': 1, 'label': 'Run1', 'absolute_time': '14:30:05', 'onset_ms': 43705}]
    """
    
    # --- 1. Load Content ---
    if isinstance(file_path_or_content, str) and ("\n" not in file_path_or_content) and ("\r" not in file_path_or_content):
        try:
            with open(file_path_or_content, 'r', encoding=encoding) as f:
                content = f.read()
        except FileNotFoundError:
            return "Error: File not found."
        except UnicodeError:
            return f"Error: Encoding issue. Try changing encoding from '{encoding}' to 'utf-8' or 'latin-1'."
    else:
        content = file_path_or_content

    lines = content.splitlines()
    
    # --- 2. Extract Session Start Time ---
    session_date_str = None
    session_time_str = None
    
    for line in lines[:50]:
        if "SessionDate:" in line:
            session_date_str = line.split(":", 1)[-1].strip()
        if "SessionTime:" in line:
            session_time_str = line.split(":", 1)[-1].strip()
            
    if not session_date_str or not session_time_str:
        return "Error: Could not find SessionDate or SessionTime in header."

    full_time_str = f"{session_date_str} {session_time_str}"
    start_dt = None
    date_formats = ["%m-%d-%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S"]
    
    for fmt in date_formats:
        try:
            start_dt = datetime.strptime(full_time_str, fmt)
            break
        except ValueError:
            continue
            
    if start_dt is None:
        return f"Error: Could not parse date/time string '{full_time_str}'."

    print(f"Session Started at: {start_dt}")

    # --- 3. Scan Frames ---
    run_times = []
    
    current_level = 0
    
    # We collect all OnsetTimes found since the last run ended.
    # format: list of (level, onset_value)
    pending_onsets = [] 
    
    current_frame = {}
    inside_frame = False

    for line in lines:
        line = line.strip()
        
        # Track Level (Hierarchy)
        # Lines usually look like: "    Level: 3"
        if line.startswith("Level:"):
            try:
                current_level = int(line.split(":")[-1].strip())
            except ValueError:
                pass
            continue

        if line == "*** LogFrame Start ***":
            inside_frame = True
            current_frame = {}
            continue
            
        if line == "*** LogFrame End ***":
            if inside_frame:
                # 1. Did we find an OnsetTime in this frame?
                # We look for ANY key ending in .OnsetTime (e.g. PrepStim.OnsetTime, Stimulus.OnsetTime)
                # We ignore 0 because E-Prime often initializes values to 0.
                for k, v in current_frame.items():
                    if k.endswith(".OnsetTime"):
                        try:
                            val = float(v)
                            if val > 0:
                                pending_onsets.append((current_level, val))
                        except ValueError:
                            pass

                # 2. Is this the "Run Summary" frame? (End of the run)
                # We check if the unique run identifier (e.g., "RunTitle") is present.
                if run_identifier in current_frame:
                    run_label = current_frame[run_identifier]
                    frame_level = current_level
                    
                    # Logic: The run *content* must be at a deeper level (higher number) than the run frame
                    # OR we just take the minimum of all valid onsets seen since the last run.
                    # Given the structure (RunProc Level 2, Content Level 3), filtering by level > frame_level is safest.
                    
                    valid_child_onsets = [t for (lvl, t) in pending_onsets if lvl > frame_level]
                    
                    # If strictly hierarchical structure isn't followed, fallback to all collected onsets
                    if not valid_child_onsets and pending_onsets:
                         valid_child_onsets = [t for (lvl, t) in pending_onsets]

                    if valid_child_onsets:
                        # The start of the run is the Earliest timestamp found in its children
                        start_ms = min(valid_child_onsets)
                        abs_time = start_dt + timedelta(milliseconds=start_ms)
                        
                        run_times.append({
                            "run_index": len(run_times) + 1,
                            "label": run_label,
                            "onset_ms": start_ms,
                            "absolute_time": abs_time.strftime("%H:%M:%S.%f")[:-3]
                        })
                    
                    # RESET: Clear the pending onsets to prepare for the next run
                    pending_onsets = []
            
            inside_frame = False
            continue

        if inside_frame:
            if ": " in line:
                key, val = line.split(": ", 1)
                current_frame[key] = val

    return run_times

# input_bids_dir = '/projects/standard/lewi1538/shared/projects/neg_urg/bids/'
# task_data_dir = '/projects/standard/lewi1538/shared/projects/neg_urg/task_files/'
# os.chdir(input_bids_dir)
# subjects = glob.glob('sub-*')
# for temp_sub in subjects:
#     print('{}'.format(temp_sub))
#     func_jsons = glob.glob(os.path.join(input_bids_dir, temp_sub,'ses-*', 'func', '*echo-1_part-mag*json'))
#     out = get_run_start_times(os.path.join(task_data_dir, temp_sub + '_' + func_jsons[-1].split('/')[-1].split('_')[1] + '_event_log.txt'))
#     for temp_dict in out:
#         if type(temp_dict) != dict:
#             print('   Skipping - temp_dict is not actually a dict')
#             continue
#         print('   Run:      {},  Absolute Time: {} (EPRIME)'.format(temp_dict['run_index'], temp_dict['absolute_time']))
#     for temp_json in func_jsons:
#         with open(temp_json, 'r') as f:
#             content = json.load(f)
#         print('   Run: {},  Acq Time:      {} (NIFTI)'.format(temp_json.split('/')[-1].split('_')[3], content['AcquisitionTime']))
    
#     print('MRI Session: ')
#     print('')

## Then convert code from eprime log to event tsv 
import warnings

# Suppress warnings for cleaner notebook output
warnings.filterwarnings('ignore')

def _parse_eprime_txt(filepath):
    """
    Internal Helper: Parses an E-Prime text recovery file into a Pandas DataFrame.
    """
    try:
        with open(filepath, 'r', encoding='utf-16') as f:
            lines = f.readlines()
    except UnicodeError:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

    frames = []
    current_frame = {}
    
    for line in lines:
        line = line.strip()
        if line == "*** LogFrame Start ***":
            current_frame = {}
        elif line == "*** LogFrame End ***":
            frames.append(current_frame)
        else:
            if ": " in line:
                key, val = line.split(": ", 1)
                if key == "LevelName": key = "Eprime.LevelName"
                if key == "FrameNumber": key = "Eprime.FrameNumber"
                current_frame[key] = val
    
    df = pd.DataFrame(frames)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').where(lambda x: x.notna(), df[col])
    return df

def _process_run_data_bids(run_df, original_run_name, bids_run_num, sub_str, ses_str, output_root):
    """
    Internal Helper: Processes a specific run and writes a BIDS events.tsv file.
    Groups trials into contiguous blocks by BlockType and computes per-block
    onset (first stimulus onset) and duration (last stimulus offset - first onset).
    """
    if run_df.empty:
        return

    # Reference time = PrepStim onset of the run's prep screen (scanner trigger reference)
    first_onset = run_df['onset.final'].iloc[0]

    # ---------------------------------------------------------
    # 1. Filter to emotion block trials only (Running == 'BlockList')
    # ---------------------------------------------------------
    EMOTION_TYPES = {'Positive', 'Negative', 'Neutral', 'Scrambled'}

    block_trials = run_df[
        (run_df['Running'] == 'BlockList') &
        (run_df['BlockType'].isin(EMOTION_TYPES))
    ].copy()

    if block_trials.empty:
        print(f"WARNING: No emotion block trials found for Run #{bids_run_num} ({original_run_name})")
        return

    # ---------------------------------------------------------
    # 2. Identify contiguous blocks (each block = a run of same BlockType)
    # ---------------------------------------------------------
    block_trials['block_id'] = (
        block_trials['BlockType'] != block_trials['BlockType'].shift()
    ).cumsum()

    # ---------------------------------------------------------
    # 3. Compute onset and duration for each contiguous block
    # ---------------------------------------------------------
    rows = []
    for _, block_df in block_trials.groupby('block_id', sort=True):
        block_type = block_df['BlockType'].iloc[0]

        # Onset: first stimulus onset in the block, zeroed to run start
        first_stim_onset = block_df['stimulus.onset'].dropna().min()
        if pd.isna(first_stim_onset):
            print(f"WARNING: No stimulus onset found for a {block_type} block  skipping.")
            continue
        onset_sec = (first_stim_onset - first_onset) / 1000.0

        # Duration: last stimulus offset - first stimulus onset
        last_stim_offset = block_df['stimulus.offset'].dropna().max()
        if pd.isna(last_stim_offset):
            print(f"WARNING: No stimulus offset found for a {block_type} block  duration will be NaN.")
            duration_sec = np.nan
        else:
            duration_sec = (last_stim_offset - first_stim_onset) / 1000.0

        rows.append({
            'onset': round(onset_sec, 3),
            'duration': round(duration_sec, 3) if not pd.isna(duration_sec) else np.nan,
            'trial_type': block_type,
            '_sort_key': first_stim_onset,
        })

    if not rows:
        print(f"WARNING: No valid blocks for Run #{bids_run_num} ({original_run_name})")
        return

    final_bids_df = (
        pd.DataFrame(rows)
        .sort_values('_sort_key')
        [['onset', 'duration', 'trial_type']]
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # 4. File Writing
    # ---------------------------------------------------------
    task_label = "taskMENORDIC"
    run_label = f"{bids_run_num:02d}"

    bids_func_dir = os.path.join(output_root, f"sub-{sub_str}", f"ses-{ses_str}", "func")
    os.makedirs(bids_func_dir, exist_ok=True)

    filename = f"sub-{sub_str}_ses-{ses_str}_task-{task_label}_run-{run_label}_events.tsv"
    out_path = os.path.join(bids_func_dir, filename)

    print(f"   -> Writing BIDS events (Original: {original_run_name}) to: {out_path}")
    print(final_bids_df.to_string(index=False))

    final_bids_df.to_csv(out_path, sep='\t', index=False)


def convert_eprime_to_bids(input_file, output_dir, sub_id=None, ses_id="01"):
    """
    Main Function to convert E-Prime txt to BIDS events.tsv.
    """

    # 1. Determine Subject ID
    if sub_id is None:
        try:
            filename = os.path.splitext(os.path.basename(input_file))[0]
            splitname = filename.split("-")
            sub_id = splitname[-2]
            print(f"Auto-detected Subject ID: {sub_id}")
        except IndexError:
            print(f"CRITICAL ERROR: Could not parse Subject ID from filename")
            return

    print(f"Processing: {os.path.basename(input_file)} | Sub: {sub_id} | Ses: {ses_id}")

    # 1.5 Determine if output file already exists
    if len(glob.glob(os.path.join(output_dir, f"sub-{sub_id}", f"ses-{ses_id}","func","*events.tsv"))) > 0:
        print(f"Events TSV already exists for this subject/session: {sub_id}")
        return
    
    # 2. Read
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return

    df = _parse_eprime_txt(input_file)
    
    # 3. Clean
    cols_to_keep = [
        "Eprime.LevelName", "Eprime.FrameNumber", "Procedure", "Running",
        "BlockType", "RunTitle", "PrepStim.OnsetDelay", "PrepStim.OnsetTime",
        "PrepIAPS.DurationError", "PrepIAPS.OnsetTime", "Stimulus.DurationError",
        "Stimulus.OnsetTime", "Stimulus.OffsetTime",
        "StimulusNoGo.OnsetTime", "StimulusNoGo.OffsetTime",
        "RestStim.OnsetTime"
    ]
    
    existing_cols = [c for c in cols_to_keep if c in df.columns]
    pruned = df[existing_cols].copy()

    # --- BLOCK FILLING (Backward) ---
    # BlockProc frames (which set BlockType) appear AFTER the trial frames they label,
    # so we must backward-fill to assign the correct type to each preceding trial.
    if 'BlockType' in pruned.columns:
        pruned['BlockType'] = pruned['BlockType'].replace('', np.nan).bfill()
        
    # --- RUN IDENTIFICATION (Critical Logic Change) ---
    # Instead of trusting the text name "Run1", we create a unique ID for each occurrence
    
    # 1. Initialize RunID with NaNs
    pruned['RunID'] = np.nan
    
    # 2. Find rows where RunTitle exists (these are the end-of-run markers)
    # We assign a sequential number (1, 2, 3...) to these markers
    if 'RunTitle' in pruned.columns:
        run_markers = pruned['RunTitle'].notna()
        # Create a sequence 1..N for every True value
        pruned.loc[run_markers, 'RunID'] = range(1, run_markers.sum() + 1)
        
        # 3. Backfill this ID so the trials *above* the marker get the ID
        pruned['RunID'] = pruned['RunID'].bfill()
        
        # 4. Also backfill the textual title just for reference
        pruned['RunTitle'] = pruned['RunTitle'].bfill()

    # --- Standard Onset Calcs ---
    onset_cols = ['PrepStim.OnsetTime', 'PrepIAPS.OnsetTime', 'RestStim.OnsetTime']
    for c in onset_cols: 
        if c not in pruned.columns: pruned[c] = np.nan
    
    pruned['onset.all'] = pruned['PrepStim.OnsetTime'].combine_first(
        pruned['PrepIAPS.OnsetTime']
    ).combine_first(pruned['RestStim.OnsetTime'])
    
    pruned['onset.all'] = pd.to_numeric(pruned['onset.all'], errors='coerce')
    if 'PrepStim.OnsetDelay' in pruned.columns:
        pruned['PrepStim.OnsetDelay'] = pd.to_numeric(pruned['PrepStim.OnsetDelay'], errors='coerce')
    else:
        pruned['PrepStim.OnsetDelay'] = np.nan

    pruned['onset.final'] = np.where(
        pruned['PrepStim.OnsetDelay'].notna(),
        pruned['onset.all'] - pruned['PrepStim.OnsetDelay'],
        pruned['onset.all']
    )

    # --- Stimulus-level onset/offset for block trial duration calculation ---
    # Go trials use Stimulus.OnsetTime / Stimulus.OffsetTime
    # NoGo trials use StimulusNoGo.OnsetTime / StimulusNoGo.OffsetTime
    for c in ['Stimulus.OnsetTime', 'Stimulus.OffsetTime', 'StimulusNoGo.OnsetTime', 'StimulusNoGo.OffsetTime']:
        if c not in pruned.columns:
            pruned[c] = np.nan
        pruned[c] = pd.to_numeric(pruned[c], errors='coerce')

    pruned['stimulus.onset'] = pruned['Stimulus.OnsetTime'].combine_first(pruned['StimulusNoGo.OnsetTime'])
    pruned['stimulus.offset'] = pruned['Stimulus.OffsetTime'].combine_first(pruned['StimulusNoGo.OffsetTime'])

    def calculate_order(row):
        proc = row.get('Procedure', '')
        run_col = row.get('Running', '')
        blk = row.get('BlockType', '')
        if proc == "TrialProc":
            if run_col == "BlockList":
                return blk
            return run_col
        return run_col

    pruned['order'] = pruned.apply(calculate_order, axis=1)

    # 4. Loop through Valid Run IDs
    # If no RunID was created (e.g. older log format), we skip
    if 'RunID' not in pruned.columns or pruned['RunID'].isna().all():
        print("Error: Could not identify any Runs in this file.")
        return

    # Group by the unique ID (1, 2, 3...)
    # This ensures that "Run1" (instance 1) and "Run1" (instance 3) are treated separately
    for run_id, run_data in pruned.groupby('RunID'):
        
        # Determine the original name (e.g. "Run1") just for logging/checking
        original_name = run_data['RunTitle'].iloc[0] if 'RunTitle' in run_data.columns else "Unknown"
        
        # Filter for valid data
        clean_run = run_data.dropna(subset=['onset.final', 'order']).copy()
        
        if clean_run.empty:
            print(f"   Run #{int(run_id)} ({original_name}) - NO DATA, skipping.")
            continue
            
        # Process this run
        # We pass 'run_id' as the integer to use for the BIDS filename (run-01, run-02, run-03)
        _process_run_data_bids(clean_run, original_name, int(run_id), sub_id, ses_id, output_dir)

    print("Done.\n")

output_folder = "/projects/standard/lewi1538/shared/projects/neg_urg/task_files/event_tsvs"
input_folder = "/projects/standard/lewi1538/shared/projects/neg_urg/task_files/event_logs"
task_files = glob.glob(os.path.join(input_folder, '*txt'))
for temp_task in task_files:
    subject_name = temp_task.split('/')[-1].split('_')[0]
    same_name_count = 0
    for temp_task_2 in task_files:
        subject_name_2 = temp_task_2.split('/')[-1].split('_')[0]
        if subject_name == subject_name_2:
            same_name_count += 1
    if same_name_count == 1:
        subject_label = temp_task.split('/')[-1].split('_')[0].split('-')[1]
        session_label = temp_task.split('/')[-1].split('_')[1].split('-')[1]
        convert_eprime_to_bids(temp_task, output_folder, sub_id=subject_label, ses_id=session_label)