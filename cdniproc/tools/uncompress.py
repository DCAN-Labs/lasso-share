#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 09:49:38 2026

@author: kweldon
"""

import argparse
import subprocess
import shutil
from pathlib import Path

def decompress_with_dcmtk(input_path: Path):
    """
    Uses DCMTK's dcmdjpeg to decompress DICOM files in place.
    Reports progress every 100 files.
    """
    if not shutil.which("dcmdjpeg"):
        print("ERROR: 'dcmdjpeg' command not found. Please install DCMTK.")
        return

    # Gather all files in the directory tree
    all_files = [f for f in input_path.rglob("*") if f.is_file()]
    total_files = len(all_files)
    
    print(f"Total files found: {total_files}")
    print(f"Scanning and decompressing...")

    decompressed_count = 0

    for index, f in enumerate(all_files, start=1):
        temp_file = f.with_suffix(f.suffix + ".tmp")
        
        try:
            # dcmdjpeg [options] inputfile outputfile
            result = subprocess.run(
                ['dcmdjpeg', str(f), str(temp_file)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Replace original with decompressed version
                temp_file.replace(f)
                decompressed_count += 1
            
            # Print progress every 100 files
            if index % 100 == 0:
                print(f"Progress: {index}/{total_files} files processed...")

        except Exception as e:
            print(f"\nError processing {f.name}: {e}")
        finally:
            # Clean up temp file if it exists (in case of dcmdjpeg error)
            if temp_file.exists():
                temp_file.unlink()

    print(f"\nFinished!")
    print(f"Total files checked: {total_files}")
    print(f"Total files decompressed: {decompressed_count}")

def main():
    parser = argparse.ArgumentParser(description="Decompress DICOMs using DCMTK's dcmdjpeg.")
    parser.add_argument("input_dir", type=Path, help="Path to the folder containing DICOMs")
    
    args = parser.parse_args()

    if not args.input_dir.exists():
        print(f"Error: Path {args.input_dir} does not exist.")
        return

    decompress_with_dcmtk(args.input_dir)

if __name__ == "__main__":
    main()