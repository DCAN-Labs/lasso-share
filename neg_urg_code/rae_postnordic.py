#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Updated code 7/10/25

Original Author: kweldon
Updated Code Author: rae mccollum
"""

"""
I will make 3 bids directories from one subj:
    
    -bids
        -sub-subID
        
    becomes...
    
    -bids
        -sub-subID
    -derivatives   
        -nordic
            -sub-subID

Usage:
    python postnordic.py -s sub-01

"""

import os
import glob, argparse
import shutil

def movefile(source,destination):
    # print("mvfile src",source)
    print("mvfile dst",destination)
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

parser.add_argument("-b", "--subject", required=True, type=str, help="subject ID to clean. Include sub- prefix")

mainDir = os.getcwd()
args = parser.parse_args()

if args.subject:
    subj = args.subject
   
source = os.path.join(mainDir,'bids',subj)
if not os.path.exists(source):
    print(source)
    raise Exception(source, ' does not exist')

nordic = os.path.join(mainDir,'derivatives','nordic')
derivatives = os.path.join(mainDir,'derivatives')

nordicdest = os.path.join(nordic, subj)

if not os.path.exists(derivatives):
    print('making... ',derivatives)
    os.mkdir(derivatives)
if not os.path.exists(nordic):
    print('making... ',nordic)
    os.mkdir(nordic)

FlagRaw = ['part-mag','part-phase']
FlagNordic = ['MENORDIC_','MEN_', 'NORDIC']

 #%%   
sessions = glob.glob(os.path.join(source, '*'))
sessions.sort()
for ses in sessions:
    funcdir = os.path.join(source,ses,'func','*')
    files = glob.glob(funcdir)
    files.sort()
    rawfiles = []
    nordicfiles = []
    #check that nordic has been run correctly by comparing the number of 
    #NORDIC runs to raw
    for file in files:
        if any(filetype in file for filetype in FlagNordic):
            nordicfiles.append(file)
        elif 'part-mag' in file and 'NORDIC' not in file:
            rawfiles.append(file)
        else:
            pass
    print(len(rawfiles), 'raw files')
    print(len(nordicfiles), 'nordic files')
    if len(rawfiles) == len(nordicfiles):
        print("NORDIC COMPLETE")
    else:
        raise Exception('NORDIC FAILED for ' + ses)

# Grab modality folders for each session
modalities = glob.glob(os.path.join(source,'ses-*','*'))
modalities.sort()
for mod in modalities:
    print("Cleaning this folder:", mod)
    ses_nordic = mod.replace('bids','derivatives/nordic')
    # Copy over anat and fmap folders
    if 'func' not in os.path.split(mod)[1]:
        if not os.path.exists(ses_nordic):
            print('cp to %s'%ses_nordic)
            shutil.copytree(mod,ses_nordic)
    # Clean up func folder
    else:
        print('cleaning up func...')
        if not os.path.exists(ses_nordic):
            os.mkdir(ses_nordic)
        files = glob.glob(os.path.join(mod,'*'))
        files.sort()
        for file in files:
            file_nordic = file.replace('bids','derivatives/nordic')
            file_nordic = file_nordic.replace('_part-mag_','_')
            if any(filetype in file for filetype in rawfiles):
                pass
            elif any(filetype in file for filetype in nordicfiles):
                movefile(file,file_nordic)           
            else:
                #pass
                if os.path.isdir(file):
                    shutil.rmtree(file)

# Move rawdata back to bids
# bids = os.path.join(mainDir,'bids')
# if not os.path.exists(source):
#     shutil.move(rawdest, source)
