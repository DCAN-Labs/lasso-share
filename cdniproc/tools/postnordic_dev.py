#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
I will make 3 bids directories from one subj:
    
    -bids
        -sub-subID
        
    becomes...
    
    -bids
        -rawdata
            -sub-subID
        -derivatives   
            -nordic
                -sub-subID

bids/rawdata has noise vols and ph data
bids/derivatives/trimmed (cleaned) has no noise vols and no ph data
bids/derivatives/nordic has been denoised and has no noise vols and no ph data

Usage:
    python postnordic_dev.py /scratch.global/kweldon/attune/bids/sub-GPA39

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
if len(sys.argv) > 1:
     funcDir = sys.argv[1]
else:
     print('I need an /bids/sub-/ses-/func input to run')
    
#strip trailing slash
if os.path.split(funcDir)[1] == '':
     funcDir = funcDir[:-1]

#%%
#funcDir = '/home/lewi1538/shared/projects/neg_urg/bids/sub-NU001/ses-1/func'
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
for ses in sessions:
    funcdir = os.path.join(ses,'func','*')
    files = glob.glob(funcdir)
    files.sort()
    raw = []
    nordic = []
    #check that nordic has been run correctly by comparing the number of 
    #NORDIC runs to raw
    for file in files:
        if any(filetype in file for filetype in FlagNordicTrimmed):
              nordic.append(file)
        elif 'part-mag' in file:
            raw.append(file)
        else:
            pass
    if len(raw) == len(nordic):
        print("NORDIC COMPLETE FOR SESSION", ses)
        for file in files:
            file_nordic = file.replace('bids','derivatives/nordic')
            nordicdest = os.path.split(file_nordic)[0]
            if any(filetype in file for filetype in FlagNordicTrimmed):
                #print('moving...')
                #print(file)
                #print(ses)
                movefile(file,file_nordic)
    else:
        #funcdir = os.path.join(ses,'func','*')
        #    
        #else:
        print('NORDIC FAILED for ' + ses)
        continue
        #raise Exception('NORDIC FAILED for ' + ses)

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
