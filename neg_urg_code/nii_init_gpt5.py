#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 10:49:32 2025

@author: kweldon


how it labels series:
Anatomy:   	Checks for NORM in ImageTypeText and specific strings in SeriesDescription.
Functional	Matches "rest" or "task" in SeriesDescription, excludes SBRef. 
MP2RAGE: 	Specialized logic for INV1, INV2, and UNI images.
Fieldmaps (topup):	 Looks for fieldmap, fmap, revPE, or PE_ in SeriesDescription
DWI:        Looks for DIFFUSION and ORIGINAL in ImageTypeText
QALAS:      Matches "qalas" in SeriesDescription
TB1FTL:     Matches "TB1TFL" in SeriesDescription and FLIP ANGLE MAP in ImageTypeText

need to add:
ASL
DWI fmaps (ABCD style)

usage: python /path/to/nii_init_gpt5.py folderOfNiiAndJSONs -p subID -s ses


maybe to add later: 
    #get basic elements
    StudyYear = int(ds.StudyDate[:4])
    BirthYear = int(ds.PatientBirthDate[:4])
    subAge = str(StudyYear-BirthYear) + "Y"
    subSex = ds.PatientSex
mv /.../tmp_dcm2bids/helper/* /.../bids/tmp_dcm2bids/sub-conTCB10_ses-01/.
"""

import argparse
import json
import subprocess
import pandas as pd
import numpy as np
from pathlib import Path



# --- ImageType Helper Function ---
def check_image_tag(df, search_pattern):
    """
    Search for a pattern in both ImageType and ImageTypeText.
    Handles lists, strings, and missing columns gracefully.
    """
    def clean_col(col_name):
        series = df.get(col_name, pd.Series([''] * len(df)))
        return series.apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x)).fillna('')

    combined_text = clean_col('ImageType') + " " + clean_col('ImageTypeText')
    return combined_text.str.contains(search_pattern, case=False, na=False, regex=True)

# --- FSL Helper Function ---
def get_fslinfo_data(nii_path: Path) -> dict:
    """
    Checks the dimensions of the nii files so you can confirm 
    they are the expected size. 
    Runs the fslinfo command and parses the output 
    into a dictionary of key parameters.
    """
    if not nii_path.exists():
        return {'fsl_status': 'NII_MISSING'}

    try:
        # Execute fslinfo command
        result = subprocess.run(
            ['fslinfo', str(nii_path)],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        
        # Parse the output
        fsl_data = {'fsl_status': 'OK'}
        #for line in result.stdout.splitlines():
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue

            # CRITICAL FIX: Use line.split(None, 1) to split by any whitespace (tabs or spaces) 
            # into exactly two parts (key, value).
            parts = line.split(None, 1)
            
            if len(parts) == 2:
                key, value = parts
                key = key.strip().replace(' ', '_')
                value = value.strip()
                
                # Standardize key names
                if key == 'data_size':
                    fsl_data['dim_size'] = value
                elif key == 'voxel_size':
                    fsl_data['voxel_size_mm'] = value
                elif key.startswith('dim') and key[-1].isdigit(): 
                    try:
                        fsl_data[f'fsl_{key}'] = int(value)
                    except ValueError:
                        fsl_data[f'fsl_{key}'] = value
                else:
                    fsl_data[f'fsl_{key}'] = value
        
        return fsl_data

    except FileNotFoundError:
        print("ERROR: 'fslinfo' command not found. Be sure you have loaded fsl.")
        return {'fsl_status': 'FSL_MISSING'}
    except subprocess.CalledProcessError:
        return {'fsl_status': 'FSL_ERROR'}
    except Exception:
        return {'fsl_status': 'UNEXPECTED_ERROR'}
    
def map_pe_dir(val):
    """
    Maps PhaseEncodingDirection codes to BIDS labels.
    """
    if not val or pd.isna(val):
        return ""
    
    mapping = {
        'j': 'PA',
        'j-': 'AP',
        'i': 'RL',
        'i-': 'LR',
        'k': 'IS',
        'k-': 'SI'
    }
    return mapping.get(val, val) # Returns the BIDS label or the original if not found

def process_json_files(input_dir: Path, output_file: Path, subID: str = None, ses: str = None):
    data_list = []
    
    # 1. Gather all .json files
    json_files = list(input_dir.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {input_dir}")
        return

    print(f"Found {len(json_files)} JSON files. Processing...")

    # 2. Read files and collect FSL info
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    data = data[0] if data else {}

                # Add filename for tracking
                data['filename'] = file_path.name
                
                # nifti file must have the same name as the JSON file but with .nii.gz suffix
                nii_path = file_path.with_suffix('.nii.gz')
                fsl_info = get_fslinfo_data(nii_path)
                data.update(fsl_info)
                data_list.append(data)
                
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

    if not data_list:
        print("No valid data extracted.")
        return

    # Convert to DataFrame
    df = pd.json_normalize(data_list)

    #make some columns    
    if 'SeriesDescription' in df.columns:
        #df['AcquisitionTime'] = ''
        df['subID'] = ''
        df['ses'] = ''
        df['label'] = '' 
        df['acq'] = ''
        df['MP'] = '' 
        df['PEdir'] = ''
        df['inv'] = ''
    
    #make sure everthing in the same series has the same dimensions
    dims = ['fsl_dim1', 'fsl_dim2', 'fsl_dim3', 'fsl_dim4']
    if 'SeriesNumber' in df.columns and all(d in df.columns for d in dims):
        if 'EchoNumber' in df.columns:
            df['EchoNumber'] = pd.to_numeric(df['EchoNumber'], errors='coerce').fillna(1)
        
            # 1. Calculate uniqueness per SeriesNumber
            series_dim_counts = df.groupby('SeriesNumber')[dims].apply(lambda x: len(x.drop_duplicates()))
            consistent_series_ids = series_dim_counts[series_dim_counts == 1].index
            
            # 2. Split and tag
            df_consistent = df[df['SeriesNumber'].isin(consistent_series_ids)].copy()
            df_mismatched = df[~df['SeriesNumber'].isin(consistent_series_ids)].copy()
            
            # Tagging for clarity in the TSV
            df_consistent['consistent'] = '1'
            df_mismatched['consistent'] = '0'
            
            # 3. Only drop duplicates for the "Yes" (consistent) group
            if not df_consistent.empty:
                df_consistent = df_consistent.sort_values(by=['SeriesNumber', 'EchoNumber'], ascending=True)
                df_consistent = df_consistent.drop_duplicates(subset=['SeriesNumber'], keep='last')
            
            # 4. Recombine
            df = pd.concat([df_consistent, df_mismatched]).reset_index(drop=True)
            print("Conditional filtering complete. Tags added to 'consistent' column.")
        else:
            df['consistent'] = '' 
            df['EchoNumber'] = '' 
    
    ####
    #deal with mosaics and setters (only contain one row)
    contains_mosaic = check_image_tag(df, 'MOSAIC')
    is_setter = df['SeriesDescription'].str.contains('setter', case=False, na=False)
    
    # Identify rows that meet BOTH conditions
    mosaic_setter_mask = contains_mosaic & is_setter
    
    # Find duplicates within that specific group (keeping the first occurrence)
    # .duplicated() flags all occurrences after the first one as True
    is_duplicate_mosaic_setter = mosaic_setter_mask & df.duplicated(subset=['SeriesDescription'], keep='first')
    
    # Invert the mask to drop only the duplicates, leaving the first entry completely intact
    df = df[~is_duplicate_mosaic_setter].reset_index(drop=True)
    
    #contains_mosaic = check_image_tag(df, 'MOSAIC')
    # Keep only rows that are NOT mosaics
    #df = df[~contains_mosaic].reset_index(drop=True)
    ####
    
    # make sure RetroRecon are at the end of the list
    if 'SeriesDescription' in df.columns and 'SeriesNumber' in df.columns:
        # 1. Check if the description contains "_RR_" (case-sensitive)
        contains_rr = df['SeriesDescription'].str.contains('_RR', case=True, na=False)
        # Ensure SeriesNumber is numeric before modification, converting errors to NaN
        df['SeriesNumber'] = pd.to_numeric(df['SeriesNumber'], errors='coerce')
        # Add 1000 to the SeriesNumber for all rows where the condition is True (loc is used for safe assignment)
        df.loc[contains_rr, 'SeriesNumber'] = df['SeriesNumber'] + 1000

    # ---------------------------------------------------------
    # Labeling Series
    # ---------------------------------------------------------
    #print(df)  

    # 1. Pre-calculate all masks once to save time and lines of code
    is_norm = check_image_tag(df, 'NORM')
    is_ph1 = check_image_tag(df, 'P')  # Phase
    is_ph2 = check_image_tag(df, 'PHASE')  # Phase
    #is_mag = check_image_tag(df, 'M')  # Magnitude
    is_mag = ~is_ph1 | ~is_ph2
    is_uni = check_image_tag(df, 'UNI')
    is_dis2d = check_image_tag(df, 'DIS2D')
    is_dwi = check_image_tag(df, 'DIFFUSION')
    is_orig = check_image_tag(df, 'ORIGINAL')
    is_famap = check_image_tag(df, 'FLIP ANGLE MAP')
    

    if 'SeriesNumber' in df.columns:
        if subID:
            df['subID'] = subID  
        if ses:
            df['ses'] = ses
        
        #rest/task
        #common conditions
        is_rest = df['SeriesDescription'].str.contains('rest', case=False, na=False)
        is_task = df['SeriesDescription'].str.contains('task', case=False, na=False)
        is_sbref = df['SeriesDescription'].str.contains('SBRef', case=False, na=False)
        
        rest_condition = is_rest & ~is_sbref
        task_condition = is_task & ~is_sbref
        df.loc[rest_condition, 'label'] = 'rest'
        df.loc[task_condition, 'label'] = 'task'

        # --- anats ---
        is_setter = df['SeriesDescription'].str.contains('setter', case=False, na=False)
        is_mrs = df['SeriesDescription'].str.contains('mrs', case=False, na=False)
        is_inv1 = df['SeriesDescription'].str.contains('_INV1', case=False, na=False)
        is_inv2 = df['SeriesDescription'].str.contains('_INV2', case=False, na=False)
        
        # t1w
        is_t1w = df['SeriesDescription'].str.contains('t1w', case=False, na=False)
        t1w_condition = is_t1w & is_norm & ~is_setter & ~is_inv1 & ~is_inv2
        df.loc[t1w_condition, 'label'] = 't1w'
        
        # t2w
        is_t2w = df['SeriesDescription'].str.contains('t2w', case=False, na=False)
        t2w_condition = is_t2w & ~is_setter & is_norm & ~is_mrs
        df.loc[t2w_condition, 'label'] = 't2w'
        
        # mp2rage
        is_mp2 = df['SeriesDescription'].str.contains('mp2rage', case=False, na=False)
        inv1_condition = is_mp2 & is_norm & is_inv1 & is_orig
        inv2_condition = is_mp2 & is_norm & is_inv2 & is_orig
        uni_condition = is_mp2 & (is_dis2d | is_norm) & is_uni
        df.loc[inv1_condition, 'inv'] = '1'
        df.loc[inv2_condition, 'inv'] = '2'
        df.loc[inv1_condition, 'label'] = 'mp2rage'
        df.loc[inv2_condition, 'label'] = 'mp2rage'
        df.loc[uni_condition, 'label'] = 'unit1'
        
        # qalas
        is_qalas = df['SeriesDescription'].str.contains('qalas', case=False, na=False)
        qalas_condition = is_qalas
        df.loc[qalas_condition, 'label'] = 'qalas'
        
        # dwi 
        dwi_condition = is_dwi & is_orig
        df.loc[dwi_condition, 'label'] = 'dwi'
        
        # fmaps 
        pattern = 'FieldMap|fieldmap|fmap|revPE|PE_|DistortionMap'
        dMRI = 'dMRI'
        b1map = 'TB1TFL'
        is_fmap = df['SeriesDescription'].str.contains(pattern, case=False, na=False)
        is_b1 = df['SeriesDescription'].str.contains(b1map, case=False, na=False)
        is_dwi = df['SeriesDescription'].str.contains(dMRI, case=False, na=False)
        
        fmap_mag_condition = is_fmap & is_mag & ~is_sbref & ~is_b1
        fmap_dwi_condition = is_dwi & is_fmap & is_mag & ~is_sbref & ~is_b1
        
        b1_condition = is_b1
        b1_anat_condition = is_b1 & ~is_famap
        b1_famp_condition = is_b1 & is_famap
        df.loc[fmap_dwi_condition, 'label'] = 'fmapDWI'
        df.loc[fmap_mag_condition, 'label'] = 'fmap'
        df.loc[b1_condition, 'label'] = 'tb1tfl'
 
        #flip angle map & anat for tb1tfl
        df.loc[b1_anat_condition, 'acq'] = 'anat'
        df.loc[b1_famp_condition, 'acq'] = 'famp'

        # --- mag or phase? --- 
        #df.loc[label_exists & is_m, 'MP'] = 'M'
        #df.loc[label_exists & is_p, 'MP'] = 'P'
        df.loc[is_mag, 'MP'] = 'M'
        df.loc[~is_mag, 'MP'] = 'P'

        #PEdir Assignment 
        if 'PhaseEncodingDirection' in df.columns:
            # 1. Map the codes (j -> PA, etc.)
            df['PEdir'] = df['PhaseEncodingDirection'].apply(map_pe_dir)
        else:
            df['PEdir'] = ""
        
    # ---------------------------------------------------------
    # cleanup for readability
    # ---------------------------------------------------------
    
    # Identify all columns created by the FSL helper function
    #fsl_cols_to_clear = [col for col in df.columns if col.startswith('fsl_') or col in ['dim_size', 'voxel_size_mm']]
    # # Create a mask for rows that still have the empty label
    # unlabeled_mask = (df['label'] == '')

    # if unlabeled_mask.any():
    #     # Set FSL columns to NaN for unlabeled rows
    #     df.loc[unlabeled_mask, fsl_cols_to_clear] = np.nan
    #     # Update status
    #     df.loc[unlabeled_mask, 'fsl_status'] = ''
    #     #print("FSL data cleared for unlabeled series.")
        
    # ---------------------------------------------------------
    # sort order
    # --------------------------------------------------------- 
    df = df.sort_values(by='SeriesNumber', ascending=True, na_position='last') #print("Final DataFrame sorted by 'SeriesNumber'.")
    
    # ---------------------------------------------------------
    # Run Number Assignment (runNum)
    # ---------------------------------------------------------
    
    # 1. Calculate sequential run number for series sharing the same BIDS keys
    df['runNum'] = df.groupby(['label','EchoNumber','MP','PEdir','inv']).cumcount().add(1)
    
    # 2. Clear run number if the series has no BIDS label, otherwise keep the calculated number
    df['runNum'] = np.where(df['label'] != '', df['runNum'], '')
    
    # 3. Ensure runNum is treated as a string for consistent TSV output (empty string or number)
    df['runNum'] = df['runNum'].astype(str)
    
    # ---------------------------------------------------------
    # reorder, filter columns
    # ---------------------------------------------------------
    priority_cols = [
        'subID', 'ses', 'SeriesNumber', 'label', 'MP', 'acq',
        'PEdir', 'runNum','EchoNumber', 'consistent',
        'fsl_dim1', 'fsl_dim2', 'fsl_dim3', 'fsl_dim4', 'inv', 'voxel_size_mm', 
        'SeriesDescription', 'AcquisitionTime', 
        'ImageType', 'ImageTypeText', 
        'ShimSetting','SoftwareVersions',
        'InPlanePhaseEncodingDirectionDICOM',
        'ReceiveCoilName', 'ReceiveCoilActiveElements','filename'
    ]

    # Filter to include only columns that actually exist
    df_cols = [col for col in priority_cols if col in df.columns]
    df = df[df_cols]
    df = df.sort_values(by=['SeriesNumber', 'AcquisitionTime', 'EchoNumber'])
    
    # ---------------------------------------------------------
    # save tsv
    # ---------------------------------------------------------
    df.to_csv(output_file, sep='\t', index=False)
    print(f"Summary saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Create a summary TSV file based on dcm2bids_helper output. Be sure to module load fsl first.")
    parser.add_argument("input_dir", type=Path, help="Drectory containing .json and .nii.gz files from dcm2bids_helper output")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output TSV filename. Will be assumed from -p and -s flags if not assigned with this flag.")    
    parser.add_argument("-p", "--participant_id", type=str, default=None, 
                        help="Optional participant ID to be included in the output filename.")
    parser.add_argument("-s", "--session_id", type=str, default=None, 
                        help="Optional session ID to be included in the output filename.")
    
    args = parser.parse_args()
    input_dir = args.input_dir.resolve()
    input_dir_name = args.input_dir.resolve()
    
    subID = None
    if args.participant_id:
        subID = args.participant_id
        print(subID)
    if args.session_id:
        ses = args.session_id
        print(ses)
    else:
        ses = '01'
        
    #check dir exists
    if not input_dir.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")
        
    #check dir has jsons in it
    if not any(input_dir.glob("*.json")):
        try:
            helper_path = input_dir / "tmp_dcm2bids" / "helper"
            if helper_path.exists() and any(helper_path.glob("*.json")):
                print(f"Redirecting to: {helper_path}")
                input_dir = helper_path
            else:
                # If the helper path doesn't have them either, we stick to root 
                # so the existing error handling catches it.
                pass 
        except Exception as e:
            print(f"Search for helper directory failed: {e}")

    #set output path
    if args.output:
        output_filename = str(args.output.resolve()) 
        if not output_filename.lower().endswith(".tsv"):
            output_filename += ".tsv"
        output_file = Path(output_filename) # Convert back to a Path object
    elif args.participant_id and args.session_id:
        # no -o flag, but BOTH participant_id AND session_id are provided.
        parts = [str(args.participant_id), str(args.session_id)]
        output_filename = "_".join(parts)
        output_filename += ".tsv"
        output_file = Path.cwd() / output_filename
    else:
        output_file = Path.cwd() / (input_dir_name.name + ".tsv")

    process_json_files(input_dir, output_file, subID=subID, ses=ses)

if __name__ == "__main__":
    main()
    
