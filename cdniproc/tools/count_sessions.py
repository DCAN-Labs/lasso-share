#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 14:23:27 2026

@author: kweldon
"""

from collections import defaultdict
import csv
import re
import sys


def count_sessions_per_id(file_path, output_csv_path):
    # Using a nested dictionary: { subject_id: { session_name: count } }
    subject_data = defaultdict(lambda: defaultdict(int))

    # Regex captures the 7-digit ID and the session part
    pattern = re.compile(r"(\d{7})-(ses\d+|ses-\d+)")

    try:
        # 1. Parse and aggregate the log file
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    sub_id, session = match.groups()
                    subject_data[sub_id][session] += 1

        # 2. Export the aggregated data to a CSV file
        with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header row
            writer.writerow(["Subject ID", "Sessions Found", "Total Sessions"])

            # Write data rows sorted by Subject ID
            for sub_id, sessions in sorted(subject_data.items()):
                session_breakdown = ", ".join(sorted(sessions.keys()))
                total_distinct_sessions = len(sessions)
                
                writer.writerow([sub_id, session_breakdown, total_distinct_sessions])

        print(f"Success! Data has been successfully exported to: {output_csv_path}")

    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <path_to_text_file> <path_to_output_csv>")
        sys.exit(1)

    target_file = sys.argv[1]
    output_file = sys.argv[2]
    count_sessions_per_id(target_file, output_file)