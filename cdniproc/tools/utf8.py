#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 16:25:07 2026

@author: kweldon
"""

input_file = '/scratch.global/kweldon/subpoptest/release/phenotype/asr.tsv'
output_file = '/scratch.global/kweldon/subpoptest/release/phenotype/asr2.tsv'

def convert_to_utf8(input_file, output_file):
    # 'utf-8-sig' handles files with or without a BOM (Byte Order Mark)
    # 'errors="replace"' prevents the script from crashing on unrecognized characters
    with open(input_file, 'r', encoding='latin-1', errors='replace') as f:
        content = f.read()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Success! {output_file} has been saved.")

# Usage
convert_to_utf8(input_file, output_file)