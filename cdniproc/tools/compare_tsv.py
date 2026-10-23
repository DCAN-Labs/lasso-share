#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 16:55:14 2026

@author: kweldon
"""

import os
import argparse

# =========================================================
# HARDCODED CONFIGURATION VARIABLES (Your Defaults)
# =========================================================
DEFAULT_FOLDER_1 = "path_to_first_folder"
DEFAULT_FOLDER_2 = "path_to_second_folder"
# =========================================================


def compare_headers(dir1: str, dir2: str):
    """
    Compares the first line of identically named files across two directories
    and summarizes exactly which files match and which ones do not.
    """
    if not os.path.exists(dir1):
        print(f"Error: Directory '{dir1}' does not exist.")
        return
    if not os.path.exists(dir2):
        print(f"Error: Directory '{dir2}' does not exist.")
        return

    files1 = set(os.listdir(dir1))
    files2 = set(os.listdir(dir2))

    # Intersect to find identical filenames present in both folders
    common_files = sorted(list(files1.intersection(files2)))
    common_tsv = [f for f in common_files if f.endswith(".tsv")]

    if not common_tsv:
        print(f"No duplicate filenames found between '{dir1}' and '{dir2}'.")
        return

    print(f"Comparing headers for {len(common_tsv)} identically named file(s)...\n")
    print(f"Folder 1 [A]: {dir1}")
    print(f"Folder 2 [B]: {dir2}")
    print("-" * 60)

    # Lists to keep track of matches and mismatches
    matching_files = []
    mismatching_files = []

    for filename in common_tsv:
        path1 = os.path.join(dir1, filename)
        path2 = os.path.join(dir2, filename)

        try:
            with open(path1, "r", encoding="utf-8") as f1, open(
                path2, "r", encoding="utf-8"
            ) as f2:
                #header1 = f1.readline().strip()
                #header2 = f2.readline().strip()
                header1 = f1.readline().strip().replace('"', '')
                header2 = f2.readline().strip().replace('"', '')

            if header1 == header2:
                print(f" MATCH: '{filename}'")
                matching_files.append(filename)
            else:
                print(f"L MISMATCH: '{filename}'")
                print(f"   [A]: {header1}")
                print(f"   [B]: {header2}\n")
                mismatching_files.append(filename)
        except Exception as e:
            print(f"  Error reading '{filename}': {e}")

    # --- FINAL SUMMARY SECTION ---
    print("\n" + "=" * 60)
    print("                      FINAL SUMMARY                     ")
    print("=" * 60)
    
    print(f"\n=Â TOTAL MATCHING FILES ({len(matching_files)}):")
    if matching_files:
        for f in matching_files:
            print(f"   {f}")
    else:
        print("  (None)")

    print(f"\n=Â TOTAL MISMATCHING FILES ({len(mismatching_files)}):")
    if mismatching_files:
        for f in mismatching_files:
            print(f"   {f}")
    else:
        print("  (None)")
        
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Compare first-line headers of matching files across two folders."
    )
    parser.add_argument(
        "--dir1",
        "-1",
        default=DEFAULT_FOLDER_1,
        help="Path to the first directory",
    )
    parser.add_argument(
        "--dir2",
        "-2",
        default=DEFAULT_FOLDER_2,
        help="Path to the second directory",
    )

    args = parser.parse_args()
    compare_headers(args.dir1, args.dir2)


if __name__ == "__main__":
    main()