#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 14:26:03 2026

@author: kweldon
"""

import os
import csv
import sys
from datetime import datetime

def get_size_format(b):
    """Converts bytes to Gigabytes."""
    return round(b / (1024**3), 2)

def audit_storage(root_path):
    if not os.path.isdir(root_path):
        print(f"Error: {root_path} is not a valid directory.")
        return None

    report_data = []
    print(f"Scanning: {root_path}...")
    print("This process traverses 20TB; performance depends on your disk speed.")

    try:
        # Scan immediate subdirectories (the "Project" or "User" level)
        for entry in os.scandir(root_path):
            if entry.is_dir():
                total_size = 0
                newest_access = 0
                file_count = 0
                
                # Deep walk into the subdirectory
                for root, _, files in os.walk(entry.path):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            stat = os.stat(fp)
                            total_size += stat.st_size
                            file_count += 1
                            if stat.st_mtime > newest_access:
                                newest_access = stat.st_mtime
                        except (PermissionError, FileNotFoundError):
                            continue

                last_mod = datetime.fromtimestamp(newest_access).strftime('%Y-%m-%d') if newest_access > 0 else "N/A"
                
                report_data.append({
                    'Folder Name': entry.name,
                    'Size (GB)': get_size_format(total_size),
                    'File Count': file_count,
                    'Last Modified': last_mod,
                    'Full Path': entry.path
                })
                print(f"  [Checked] {entry.name}: {get_size_format(total_size)} GB")

    except KeyboardInterrupt:
        print("\nScan interrupted by user. Saving partial results...")
    except Exception as e:
        print(f"Critical Error: {e}")

    return report_data

def save_to_csv(data, filename="storage_audit.csv"):
    if not data:
        return
    keys = data[0].keys()
    with open(filename, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print(f"\n--- DONE ---")
    print(f"Report saved to: {os.path.abspath(filename)}")

if __name__ == "__main__":
    # Check if user provided a path as an argument
    if len(sys.argv) < 2:
        print("Usage: python audit.py /path/to/directory")
    else:
        target_path = sys.argv[1]
        results = audit_storage(target_path)
        save_to_csv(results)