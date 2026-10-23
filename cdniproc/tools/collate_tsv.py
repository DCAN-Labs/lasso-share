#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 14:56:17 2025

@author: kweldon
"""

import csv
import glob
import os
import argparse


def extract_columns(directory: str, file_pattern: str):
    """
    Reads all flat files matching the pattern inside the specified directory.
    Automatically detects delimiters with a strict fallback hierarchy:
    1. If a tab is in the header line -> Explicitly Tab-delimited.
    2. If a comma is in the header line (and no tab) -> Explicitly Comma-delimited.
    3. Otherwise -> Use csv.Sniffer() to handle anomalies.
    """
    columns_map = {}
    headers = []

    search_path = os.path.join(directory, file_pattern)
    tsv_files = sorted(glob.glob(search_path))

    if not tsv_files:
        print(f"Warning: No files found matching '{file_pattern}' in '{directory}'.")
        return [], {}

    print(f"Found {len(tsv_files)} file(s) to process.")

    for file_path in tsv_files:
        seen = set()
        col_data = []
        filename = os.path.basename(file_path)

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as f:
                # Read a sample to analyze the text structure
                sample = f.read(2048)
                f.seek(0)

                if not sample.strip():
                    print(f"Warning: File '{filename}' is empty. Skipping.")
                    continue

                # Grab the raw header text string
                first_line = sample.splitlines()[0] if sample.splitlines() else ""

                # --- Strict Delimiter Resolution Logic ---
                if "\t" in first_line:
                    input_delimiter = "\t"
                elif "," in first_line:
                    input_delimiter = ","
                else:
                    # If neither/or simple single column structure, try Sniffer
                    try:
                        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t"])
                        input_delimiter = dialect.delimiter
                    except csv.Error:
                        input_delimiter = "\t"  # Ultimate safety default

                reader = csv.reader(f, delimiter=input_delimiter)
                try:
                    header_row = next(reader)
                except StopIteration:
                    print(f"Warning: File '{filename}' is empty. Skipping.")
                    continue

                try:
                    # Target column matching
                    record_idx = header_row.index("participant_id")
                except ValueError:
                    print(f"ERROR: File '{filename}' does not contain 'participant_id'. Skipping.")
                    continue

                for row in reader:
                    if row and len(row) > record_idx:
                        val = row[record_idx].strip()
                        if val and val not in seen:
                            col_data.append(val)
                            seen.add(val)

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue

        headers.append(filename)
        columns_map[filename] = {"list": col_data, "set": seen}

    return headers, columns_map


def align_columns_preserve_first(headers, columns_map):
    """
    Align columns so that each row contains the same participant_id values across columns.
    """
    if not headers:
        return [], {}

    first_col = columns_map[headers[0]]["list"]
    master_order = list(first_col)
    master_set = set(master_order)

    for header in headers[1:]:
        for val in columns_map[header]["list"]:
            if val not in master_set:
                master_order.append(val)
                master_set.add(val)

    aligned_columns = {}
    for header in headers:
        col_set = columns_map[header]["set"]
        aligned_col = []

        for val in master_order:
            if val in col_set:
                aligned_col.append(val)
            else:
                aligned_col.append("")

        aligned_columns[header] = aligned_col

    return master_order, aligned_columns


def write_collated_file(headers, aligned_columns, master_order, output_file, output_delimiter):
    """
    Write aligned columns to the final output file.
    """
    print(f"\nWriting {len(master_order)} rows to {output_file}...")
    try:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=output_delimiter)
            writer.writerow(headers)

            for i in range(len(master_order)):
                row = [aligned_columns[h][i] for h in headers]
                writer.writerow(row)

        print(f"Successfully created '{output_file}'.")
    except Exception as e:
        print(f"Error writing output file: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="Collate flat file columns with row alignment")
    parser.add_argument("--input-dir", "-i", default="input_data", help="Input directory")
    parser.add_argument("--pattern", "-p", default="*.tsv", help="Glob pattern for input files")
    parser.add_argument("--output", "-o", default="collated_columns.csv", help="Output file")
    parser.add_argument("--output-delim", default=",", help="Output file delimiter")
    return parser.parse_args()


def main():
    args = parse_args()
    output_delim = "\t" if args.output_delim == "\\t" else args.output_delim

    headers, columns_map = extract_columns(
        directory=args.input_dir,
        file_pattern=args.pattern
    )

    if not headers:
        print("No files to process. Exiting.")
        return

    master_order, aligned_columns = align_columns_preserve_first(headers, columns_map)

    write_collated_file(
        headers=headers,
        aligned_columns=aligned_columns,
        master_order=master_order,
        output_file=args.output,
        output_delimiter=output_delim
    )

    print("\nScript execution complete.")


if __name__ == "__main__":
    main()