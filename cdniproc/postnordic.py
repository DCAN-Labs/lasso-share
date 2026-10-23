#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""

"""
#import os, datetime, glob, sys, json
#import numpy as np

import os, sys
import glob, argparse
import shutil

def movefile(source,destination):
    #print(source)
    #print(destination)
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    try:
        #shutil.copy(source, destination)
        shutil.move(source, destination)
        #print("File copied successfully.")

    # If source and destination are same
    except shutil.SameFileError:
        print("Source and destination represents the same file.")

    # If there is any permission issue
    except PermissionError:
        print("Permission denied.")

    # For other errors
    except:
        print("Error occurred while copying file.")

#%%
parser = argparse.ArgumentParser()
parser.add_argument('funcDir', help='/bids/sub-/ses-/func input to run')
parser.add_argument('--overwrite', action='store_true', help='Overwrite failed_nordic.txt instead of appending to it')
args = parser.parse_args()
funcDir = args.funcDir
    
funcDir = funcDir.rstrip('/')

#%%
#funcDir = '/projects/standard/lewi1538/shared/projects/neg_urg/bids/sub-NU001/ses-1/func'
#funcDir = '/scratch.global/kweldon/attune/bids/sub-GPA39/ses-02'
# mainDir = '/projects/standard/faird/shared/projects/subpop/'
# subj = 'sub-1020001'
     
source = os.path.split(funcDir)[0].split('ses-')[0]
if not os.path.exists(source):
    raise Exception(source, ' does not exist')

sessions =[]   
if "ses-" in funcDir:
    print('You gave me a session as input so I will work on one session')
    if 'func' in funcDir:
        funcDir = os.path.split(funcDir)[0]
    sessions = glob.glob(funcDir)
    sessions.sort()
    mainDir = os.path.split(funcDir)[0].split('bids')[0]
    subj = 'sub-' + os.path.split(funcDir)[0].split('sub-')[1]
else:
    print('You gave me a subject as input so I will only work on all sessions')
    sessions = glob.glob(os.path.join(funcDir, 'ses-*'))
    sessions.sort()
    mainDir = os.path.split(funcDir)[0].split('bids')[0]
    subj = os.path.split(funcDir)[1]
    

print('main dir: ', mainDir)
print('subj: ',subj)
print('sessions: ',sessions)
#%%    

#print(mainDir)
#print(subj)
rawdata = os.path.join(mainDir,'rawdata')
nordic = os.path.join(mainDir,'derivatives','nordic')
derivatives = os.path.join(mainDir,'derivatives')

rawdest = os.path.join(rawdata, subj)
nordicdest = os.path.join(nordic, subj)

FlagRaw = ['ME_','MEph_']
FlagNordic = ['MENORDIC_','MEN_','NORDIC']
FlagTrimmed = ['MErmnoisevols_','MEt_','MEtrimmed_']
FlagNordicTrimmed = ['MENORDICrmnoisevols_','MEtN_','MENORDICtrimmed','MEpassNORDICrmnoisevols_','MEpassNORDICtrimmed_','NORDIC']

#%%
failed_nordic_file = os.path.join(mainDir, 'failed_nordic.txt')
if args.overwrite:
    open(failed_nordic_file, 'w').close()

existing_failures = set()
if os.path.exists(failed_nordic_file):
    with open(failed_nordic_file, 'r') as f:
        existing_failures = {line.strip() for line in f if line.strip()}

for ses in sessions:
    funcdir = os.path.join(ses,'func','*')
    files = glob.glob(funcdir)
    files.sort()

    ses_nordic = ses.replace('bids','derivatives/nordic')
    nordic_funcdir = os.path.join(ses_nordic,'func','*')
    nordic_files_already_moved = glob.glob(nordic_funcdir)

    raw = []
    nordic = []
    #check that nordic has been run correctly by comparing the number of
    #NORDIC runs to raw; also count files already moved to derivatives/nordic
    for file in files:
        if any(filetype in file for filetype in FlagNordicTrimmed):
              nordic.append(file)
        elif 'part-mag' in file:
            raw.append(file)
        else:
            pass
    for file in nordic_files_already_moved:
        if any(filetype in file for filetype in FlagNordicTrimmed):
            nordic.append(file)
    if len(raw) == len(nordic):
        print("NORDIC COMPLETE FOR SESSION", ses)
        parts = ses.replace('\\', '/').split('/')
        sub_part = next((p for p in parts if p.startswith('sub-')), '').replace('sub-', '', 1)
        ses_part = next((p for p in parts if p.startswith('ses-')), '').replace('ses-', '', 1)
        entry = f"{sub_part} {ses_part}"
        if entry in existing_failures:
            existing_failures.discard(entry)
            with open(failed_nordic_file, 'w') as f:
                f.write('\n'.join(sorted(existing_failures)) + ('\n' if existing_failures else ''))
            print(f"Removed {entry} from failed_nordic.txt")
        for file in files:
            file_nordic = file.replace('bids','derivatives/nordic')
            nordicdest = os.path.split(file_nordic)[0]
            if any(filetype in file for filetype in FlagNordicTrimmed):
                movefile(file,file_nordic)
    else:
        print('NORDIC FAILED for ' + ses)
        parts = ses.replace('\\', '/').split('/')
        sub_part = next((p for p in parts if p.startswith('sub-')), '').replace('sub-', '', 1)
        ses_part = next((p for p in parts if p.startswith('ses-')), '').replace('ses-', '', 1)
        entry = f"{sub_part} {ses_part}"
        if entry not in existing_failures:
            with open(failed_nordic_file, 'a') as f:
                f.write(entry + "\n")
            existing_failures.add(entry)
        #for file in files:
            #if 'NORDIC' in os.path.basename(file):
                #print(f"Deleting partial NORDIC file: {file}")
                #os.remove(file)
        continue

#copy non-func directories
for ses in sessions:
    folders = glob.glob(os.path.join(ses,'*'))
    ses_nordic = ses.replace('bids','derivatives/nordic')
    for folder in folders:
        #print(folder)
        if 'func' not in os.path.split(folder)[1]:
            print(folder)
            folder_nordic = folder.replace('bids','derivatives/nordic')
            if not os.path.exists(folder_nordic):
                shutil.copytree(folder,folder_nordic)
