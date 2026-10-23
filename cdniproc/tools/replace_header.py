#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 11:50:38 2026

@author: kweldon
"""

import os
import csv

# 1. Update your folder paths
input_dir = '/scratch.global/kweldon/subpoptest/release/phenotype/'
output_dir = os.path.join(input_dir, 'standardized_tsvs')

# Create the output folder if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(input_dir):
    if filename.endswith(".tsv"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        try:
            with open(input_path, 'r', encoding='utf-8', newline='') as infile, \
                 open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                
                # Using csv module with tab delimiter for reliability
                reader = csv.reader(infile, delimiter='\t')
                writer = csv.writer(outfile, delimiter='\t')
                
                for row in reader:
                    if row:  # Skip empty lines
                        # Check ONLY the first column (index 0)
                        if row[0] == "record_id":
                            row[0] = "participant_id"
                        
                        writer.writerow(row)
            
            print(f"Processed: {filename}")
            
        except Exception as e:
            print(f"Skipped {filename} due to error: {e}")

print(f"\nTask complete. Check the '{output_dir}' folder.")