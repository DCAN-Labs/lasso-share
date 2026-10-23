#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 17 19:05:15 2025

@author: kweldon
"""

import os
import json

def find_invalid_json_files(directory):
    invalid_files = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError, OSError):
                invalid_files.append(filename)

    return invalid_files

# Example usage
if __name__ == "__main__":
    dir_path = "/projects/standard/faird/shared/projects/subpop_v2/summaries"
    bad_files = find_invalid_json_files(dir_path)
    bad_files.sort()
    if bad_files:
        print("Invalid JSON files:")
        for file in bad_files:
            print(file)
    else:
        print("All JSON files are valid.")