#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 22:45:48 2026

@author: kweldon
"""

import pandas as pd
import glob
import os

# 1. Update your paths
input_dir = '/scratch.global/kweldon/subpoptest/release/phenotype/'
output_dir = os.path.join(input_dir, 'new')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.endswith(".tsv"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        updated_lines = []
        
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                # Split by COMMA instead of TAB
                parts = line.split(',')
                
                if parts:
                    # Clean the first part (remove quotes/spaces) to check it
                    first_val = parts[0].strip().replace('"', '')
                    
                    if first_val.lower() == "record_id":
                        parts[0] = "participant_id"
                
                # Re-join using the comma
                updated_lines.append(','.join(parts))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
            
        print(f"Fixed CSV-formatted TSV: {filename}")

print(f"\nDone! Files are in: {output_dir}")


# # Update this to your actual folder path
# directory = '/scratch.global/kweldon/subpoptest/release/phenotype/'

# print(f"{'FILENAME':<30} | {'FIRST CELL CONTENT'}")
# print("-" * 60)

# for filename in os.listdir(directory):
#     if filename.endswith(".tsv"):
#         filepath = os.path.join(directory, filename)
        
#         try:
#             # We use 'utf-8-sig' to catch hidden Windows/Excel markers
#             with open(filepath, 'r', encoding='utf-8-sig') as f:
#                 first_line = f.readline()
                
#                 if first_line:
#                     # Split by tab and take the first element
#                     cells = first_line.split('\t')
#                     first_cell = cells[0]
                    
#                     # repr() shows the "true" string, including hidden quotes or spaces
#                     print(f"{filename:<30} | {repr(first_cell)}")
#                 else:
#                     print(f"{filename:<30} | [File is empty]")
                    
#         except Exception as e:
#             print(f"{filename:<30} | Error: {e}")
# # --- Configuration ---
# input_dir = '/scratch.global/kweldon/subpoptest/release/phenotype/'  # Path to your files
# new_header_name = "participant_id"      # The new string for the first cell
# output_dir = '/scratch.global/kweldon/subpoptest/release/phenotype/new/'   # Where to save the fixed files


# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# for filename in os.listdir(input_dir):
#     if filename.endswith(".tsv"):
#         input_path = os.path.join(input_dir, filename)
#         output_path = os.path.join(output_dir, filename)
        
#         updated_lines = []
        
#         # 'utf-8-sig' is the magic fix for hidden 'record_id' markers at the start of files
#         with open(input_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
#             for line in f:
#                 columns = line.split('\t')
                
#                 if len(columns) > 0:
#                     # Clean the first column for the CHECK only
#                     # This removes quotes, spaces, and makes it lowercase
#                     check_val = columns[0].strip().replace('"', '').lower()
                    
#                     if check_val == "record_id":
#                         columns[0] = "participant_id"
                
#                 # Re-join with tabs and save the line
#                 updated_lines.append('\t'.join(columns))
        
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.writelines(updated_lines)
            
#         print(f"Fixed: {filename}")

# print(f"\nDone! Check the folder: {output_dir}")