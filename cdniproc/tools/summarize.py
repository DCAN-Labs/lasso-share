#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 15:22:19 2025

@author: kweldon
"""

import argparse
import os
import glob
import csv

def concatenate_tsv_files_in_directory(input_directory, output_file):
    """
    Concatenates all TSV files within a specified directory into a single output TSV file.
    It takes the header from the first TSV file found and skips headers from subsequent files.

    Args:
        input_directory (str): The path to the directory containing the TSV files.
        output_file (str): The path to the output concatenated TSV file.
    """
    # Find all TSV files in the input directory
    search_path = os.path.join(input_directory, '*sv')
    input_paths = sorted(glob.glob(search_path))

    if not input_paths:
        print(f"No .tsv files found in directory: '{input_directory}'. Exiting.")
        return

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    print(f"Concatenating {len(input_paths)} files from '{input_directory}' into '{output_file}'...")

    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile, delimiter='\t')
        header_written = False

        for i, input_path in enumerate(input_paths):
            if not os.path.exists(input_path):
                print(f"Warning: Input file not found, skipping: {input_path}")
                continue

            print(f"Processing: {input_path}")
            with open(input_path, 'r', newline='', encoding='utf-8') as infile:
                csv_reader = csv.reader(infile, delimiter='\t')

                # Read header from the first file and write it
                if not header_written:
                    try:
                        header = next(csv_reader)
                        csv_writer.writerow(header)
                        header_written = True
                    except StopIteration:
                        print(f"Warning: Input file '{input_path}' is empty. Skipping.")
                        continue # Skip empty files

                # For subsequent files, skip their header
                if i > 0:
                    try:
                        next(csv_reader) # Skip the header row of subsequent files
                    except StopIteration:
                        # This means the file only had a header or was empty (already handled)
                        pass

                # Write the remaining rows
                for row in csv_reader:
                    csv_writer.writerow(row)

    print(f"Concatenation complete. Output saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Concatenate all TSV files within a directory into a single output file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--input-directory',
        required=True,
        help="Path to the directory containing TSV files to concatenate."
    )
    parser.add_argument(
        '--output-file',
        required=True,
        help="Path to the output concatenated TSV file (e.g., combined_data.tsv)."
    )

    args = parser.parse_args()

    concatenate_tsv_files_in_directory(args.input_directory, args.output_file)

if __name__ == "__main__":
    main()
