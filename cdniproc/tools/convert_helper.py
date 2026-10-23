#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 14:12:56 2026

@author: kweldon
"""

import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Direct DICOM to NIfTI conversion.")

    # Input Flags
    parser.add_argument("-d", "--dicom_dir", required=True, help="Path to input DICOMs")
    parser.add_argument("-p", "--participantID", required=True, help="Participant ID")
    parser.add_argument("-s", "--sessionID", required=True, help="Session ID")
    parser.add_argument("-b", "--bids_dir", required=True, help="Abs or relative path to bids dir")

    args = parser.parse_args()

    participantID = args.participantID
    #sessionID = args.sessionID
    sessionID = args.sessionID.zfill(2) if args.sessionID.isdigit() else args.sessionID
    
    # Resolve absolute paths
    dicom_input = os.path.abspath(args.dicom_dir)
    bids_path = os.path.abspath(args.bids_dir)
    # output path for dcm2bids: base/tmp_dcm2bids/sub-ID_ses-ID
    output_path = os.path.join(bids_path, 'tmp_dcm2bids', f'sub-{participantID}_ses-{sessionID}')
    
    # Make the output directory if it doesn't exist
    if not os.path.exists(output_path):
        print(f"Creating directory: {output_path}")
        os.makedirs(output_path, exist_ok=True)

    # Construct the dcm2niix command exactly as requested
    command = [
        "dcm2niix",
	   "-w", "0",
        "-b", "y",
        "-ba", "y",
        "-z", "y",
        "-f", "%3s_%f_%p_%t",
        "-o", output_path,
        dicom_input
    ]

    print("--- executing ---")
    print(" ".join(command))
    try:
        # Running the command
        subprocess.run(command, check=True)
        print(f"\nConversion complete. Files saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: dcm2niix failed with return code {e.returncode}.")
    except FileNotFoundError:
        print("Error: 'dcm2niix' command not found in your system PATH.")

if __name__ == "__main__":
    main()
