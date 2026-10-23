#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 09:50:24 2023

@author: kweldon

Notes: 
    ds.private_creators(0x0021) returns private creator


Get a specific value: python checkheader.py ./my_dicom_dir -e PatientName
Output: Just the PatientName.

Save the header to a file: python checkheader.py ./my_dicom_dir -s
Output: Creates my_dicom_dir.txt and prints a confirmation.

Quick check in terminal (Default): python checkheader.py ./my_dicom_dir
Output: Dumps the entire DICOM header directly to your terminal window.

"""

import os, argparse
from pydicom import dcmread

def get_target_file(input_path):
    abs_path = os.path.abspath(input_path)
    if os.path.isdir(abs_path):
        # Filter for files and sort
        files = sorted([f for f in os.listdir(abs_path) if os.path.isfile(os.path.join(abs_path, f))])
        if not files:
            return None
        return os.path.join(abs_path, files[0])
    return abs_path

#%% Parser Setup
parser = argparse.ArgumentParser(description="DICOM Header Tool")
# Removing the '-' makes this a positional argument (the 'input')
parser.add_argument("path", help="Path to a DICOM file or directory")
parser.add_argument("-e", "--element", help="Specific DICOM tag to print (e.g., SeriesDescription)")
parser.add_argument("-s", "--save", action="store_true", help="Save header to .txt file")
args = parser.parse_args()

# Resolve path
target = get_target_file(args.path)
if not target or not os.path.exists(target):
    print(f"Error: Could not find valid file at {args.path}")
    exit()

dicom_dir_name = os.path.basename(os.path.dirname(target))

try:
    ds = dcmread(target, force=True)

    # 1. Handle specific element request
    if args.element:
        if hasattr(ds, args.element):
            print(getattr(ds, args.element))
        else:
            print(f"Element '{args.element}' not found.")

    # 2. Handle saving to file
    if args.save:
        output_name = f"{dicom_dir_name}.txt"
        with open(output_name, 'w') as f:
            f.write(str(ds))
        print(f"Header saved to {output_name}")

    # 3. Default behavior: if no element is requested and save isn't flagged, print full header
    if not args.element and not args.save:
        print(str(ds))

except Exception as e:
    print(f"Error reading DICOM: {e}")