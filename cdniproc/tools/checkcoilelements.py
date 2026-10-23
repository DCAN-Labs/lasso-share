#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 16:04:19 2025

@author: kweldon
"""

import os
import json

# Starting directory (parent of all subfolders with jsons)
parent_dir = "/scratch.global/kweldon/washtest/derivatives/nordic"

# Key you want to extract
target_key = "ReceiveCoilActiveElements"

for root, _, files in os.walk(parent_dir):
    for file in files:
        if file.endswith(".json"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                # If key is top-level only
                if target_key in data:
                    if 'HC1-' not in data[target_key]:
                        if 'combined' not in file_path:
                            print(f"{file_path}")
                            print(f"{data[target_key]}")
                else:
                    print(f"{file_path}: Key not found")

            except Exception as e:
                print(f"Error reading {file_path}: {e}")