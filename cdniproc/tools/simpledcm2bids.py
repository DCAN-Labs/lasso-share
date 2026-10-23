import os
import pydicom
import subprocess
import argparse
from datetime import datetime

def is_dicom(file_path):
    """Check if a file is a valid DICOM using pydicom."""
    try:
        pydicom.dcmread(file_path, stop_before_pixels=True)
        return True
    except:
        return False

def get_dicom_dir_status(root_dir):
    """Walk through directories and classify them as valid or skipped."""
    valid_dirs = []
    skipped_dirs = []

    for dirpath, _, filenames in os.walk(root_dir):
        if not filenames:
            skipped_dirs.append(dirpath)
            continue

        has_dicom = "PhoenixZIP" not in dirpath and \
                any(is_dicom(os.path.join(dirpath, f)) for f in filenames)
        
        if has_dicom:
            print(dirpath)
            valid_dirs.append(dirpath)
        else:
            skipped_dirs.append(dirpath)

    return list(set(valid_dirs)), list(set(skipped_dirs))

def main():
    parser = argparse.ArgumentParser(description="Safe DICOM-to-BIDS converter using dcm2bids.")
    parser.add_argument("-d", "--dicom_dir", required=True, help="Root directory containing DICOM folders")
    parser.add_argument("-p", "--participant_label", required=True, help="Participant label (e.g., 1009101)")
    parser.add_argument("-s", "--session_label", required=True, help="Session label (e.g., 01)")
    parser.add_argument("-c", "--config", required=True, help="Path to dcm2bids config JSON")
    parser.add_argument("-o", "--output_dir", required=True, help="BIDS output directory")
    parser.add_argument("--log", help="Optional log file path", default=None)

    args = parser.parse_args()

    dicom_root = args.dicom_dir
    output_dir = args.output_dir
    config_file = args.config
    participant_label = args.participant_label
    session_label = args.session_label
    log_file = args.log or f'dcm2bids_skip_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

    valid_dirs, skipped_dirs = get_dicom_dir_status(dicom_root)
    valid_dirs.sort()

    # Log results
    with open(log_file, 'w') as log:
        log.write("Dcm2Bids Directory Check Log\n")
        log.write("=" * 40 + "\n\n")
        log.write(f"Valid DICOM directories ({len(valid_dirs)}):\n")
        for d in valid_dirs:
            log.write(f"{d}\n")

        log.write(f"\nSkipped (no valid DICOMs) directories ({len(skipped_dirs)}):\n")
        for d in skipped_dirs:
            log.write(f"{d}\n")

    print(f"\nLog written to: {log_file}")
    print(f"Found {len(valid_dirs)} valid DICOM directories.\n")

    # Run dcm2bids on each valid directory
    for dicom_dir in valid_dirs:
        print(f"Running dcm2bids on: {dicom_dir}")
        subprocess.run([
            "dcm2bids",
            "-d", dicom_dir,
            "-p", participant_label,
            "-s", session_label,
            "-c", config_file,
            "-o", output_dir,
            "--force_dcm2bids"
#
        ])

if __name__ == "__main__":
    main()