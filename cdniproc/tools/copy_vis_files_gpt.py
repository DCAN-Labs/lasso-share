#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
I will copy files needed for temp matching into an input folder!

"""
#import os, datetime, glob, sys, json
#import numpy as np

import os
import sys
import glob
import pandas as pd
import shutil

# --- Utility Functions (Simplified) ---
def read_txt_to_dict(file_path):
    """Reads a text file with three columns into a dictionary.

    Args:
        file_path: The path to the text file.

    Returns:
        A dictionary where the keys are from the first column and the values
        are lists containing the second and third column values.
        Returns an empty dictionary if the file is empty or an error occurs.
    """
    data_dict = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Skip empty lines
                    columns = line.split()
                    if len(columns) == 3:
                        key = columns[0]
                        value1 = columns[1]
                        value2 = columns[2]

                        if key in data_dict:
                            # Appending as a tuple is safer than a list
                            data_dict[key].append((value1, value2))
                        else:
                            data_dict[key] = [(value1, value2)]
                    else:
                        print(f"Skipping line with invalid number of columns: {line}")
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
    return data_dict

# --- Path Setup ---
#pipeline = '/path/fmriprep-24.1.1-xcpd-0.9.1/GPA52/'

if len(sys.argv) > 1:
    pipeline = sys.argv[1]
else:
    # Exit if no argument is provided
    print("Error: Pipeline path required as command-line argument.")
    sys.exit(1)

# strip trailing slash (using rstrip is cleaner)
pipeline = pipeline.rstrip(os.sep)

subjID = os.path.split(pipeline)[1]
print(f"Subject ID: {subjID}")
pipelineoutput = os.path.split(pipeline)[0]
pipelinebase = os.path.basename(pipelineoutput) # Cleaner way to get base name

# Defensive splitting for version extraction
parts = pipelinebase.split('-')
if len(parts) >= 4:
    xcpdversion = f"{parts[2]}-{parts[3]}"
    fmriprepversion = f"{parts[0]}-{parts[1]}"
else:
    print(f"Warning: Could not reliably parse pipeline versions from {pipelinebase}")
    xcpdversion = os.path.split(pipelineoutput)[0]
    fmriprepversion = os.path.split(pipelineoutput)[0]

derivatives = os.path.split(pipelineoutput)[0]
print(f"Derivatives directory: {derivatives}")

# Hardcoded paths (as requested)
#abcd_atlas_dir = '/path/shared/projects/ABCD_net_template_matching_2.0/results/probabilistic_maps/'
pcm_dir = os.path.join(pipeline, 'PCM/ExpData-fullm/figures/Percent_Holdout-100/ciftis/')
inputDir = os.path.join(pipeline, 'visualization_files') # Removed trailing slash in definition

#print(pcm_dir)
#print(inputDir)

# --- File Gathering and Filtering (Improved) ---
input_list = []

# Gather anat files using glob.glob
xcpd_files = glob.glob(os.path.join(derivatives, 'xcpd*', 'output', subjID, 'sub-*/ses-*/anat', '*surf*'))
xcpd_files += glob.glob(os.path.join(derivatives, 'xcpd*', 'output', subjID, 'sub-*/ses-*/anat', '*preproc*'))
fmriprep_files = glob.glob(os.path.join(derivatives, 'fmriprep*', 'output', subjID, 'sub-*/ses-*/anat', '*preproc*nii.gz'))

all_anat_files = xcpd_files + fmriprep_files

#print('all_anat_files: ', all_anat_files)

# Remove non-native resolutions using list comprehension
input_list = [f for f in all_anat_files if 'res-' not in f]

# --- Copy Core Files (Replaced Shell with shutil) ---
print(f"Target directory: {inputDir}")

# Create the directory using os.makedirs (safer, portable)
try:
    os.makedirs(inputDir, exist_ok=True)
    print(f"Directory ensured: {inputDir}")
except Exception as e:
    print(f"Error creating directory {inputDir}: {e}")
    sys.exit(1)

print("Copying core anatomical files...")
for file_path in input_list:
    try:
        # Use shutil.copy2 for robust file copying (preserves metadata)
        shutil.copy2(file_path, inputDir)
        print(f"Copied: {os.path.basename(file_path)}")
    except FileNotFoundError:
        print(f"Warning: Source file not found, skipping: {file_path}")
    except Exception as e:
        print(f"Error copying {file_path}: {e}")


# --- Copy Network Atlas and PCM Files (Revised to use glob) ---

# NOTE: The 'network_dict' variable (currently ['SCAN', 'CO']) is now unused for copying files,
# but remains defined earlier in the script as per your previous instruction.

print("\nCopying network atlas files via glob...")

# # 1. Copy Probabilistic Atlas Files
# # Search for all files matching the pattern in the atlas directory
# atlas_files_to_copy = glob.glob(os.path.join(abcd_atlas_dir, '*_network_thres.dscalar.nii'))

# if atlas_files_to_copy:
#     for file_in_atlas in atlas_files_to_copy:
#         # Extract the base filename to use in the output path
#         base_name = os.path.basename(file_in_atlas)
#         file_out_atlas = os.path.join(inputDir, f'abcd_{base_name}')

#         try:
#             print(f'Copying atlas: {base_name}')
#             shutil.copy2(file_in_atlas, file_out_atlas)
#             print('-> Success')
#         except Exception as e:
#             print(f'Error copying atlas file {base_name}: {e}')
# else:
#     print(f'No atlas files found matching *_network_thres.dscalar.nii in: {abcd_atlas_dir}')


# 2. Copy PCM Files (Applying the same glob logic)
print("\nCopying PCM probability files via glob...")

if os.path.exists(pcm_dir):
    # Search for all files matching the pattern in the PCM directory
    pcm_pattern = 'Probability_Maps_across_perms_TM_Percent_holdout_*_network_probability.dscalar.nii'
    pcm_pattern2 = 'Mode_of_Shuffled_dscalars_Percent_holdout_population_mode.dlabel.nii'
    pcm_files_to_copy = glob.glob(os.path.join(pcm_dir, pcm_pattern))
    pcm_files_to_copy += glob.glob(os.path.join(pcm_dir, pcm_pattern2))

    if pcm_files_to_copy:
        for file_in_pcm in pcm_files_to_copy:
            base_name = os.path.basename(file_in_pcm)
            file_out_pcm = os.path.join(inputDir, base_name)
            
            try:
                print(f'Copying PCM: {base_name}')
                shutil.copy2(file_in_pcm, file_out_pcm)
                print('-> Success')
            except Exception as e:
                print(f'Error copying PCM file {base_name}: {e}')
    else:
        print(f'No PCM files found matching the pattern in: {pcm_dir}')
else:
    print(f'PCM directory not found: {pcm_dir}')