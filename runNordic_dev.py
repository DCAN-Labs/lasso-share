#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess as sub
import pandas as pd
import numpy as np
import nibabel as nib
"""
This script is designed to run nordic with one input: csv file
"""
def run_shell_cmd(cmd):
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return


def count_noise_volumes(nifti_file, percentile=90, threshold_ratio=0.5):
    # Load the NIfTI file
    print("Loading this file:", nifti_file)
    img = nib.load(nifti_file)
    data = img.get_fdata()

    # Check the shape of the data (X, Y, Z, T) -> T is the number of frames (time points)
    num_frames = data.shape[-1]
    
    # Step 1: Calculate the average of the percentile intensities of the first 5 frames
    first_5_frames = data[..., :5]  # Extract the first 5 frames
    percentile_intensities = []

    for i in range(5):
        frame_data = first_5_frames[..., i]
        nonzero_voxels = frame_data[frame_data > 0]  # Only consider nonzero voxels
        percentile_intensity = np.percentile(nonzero_voxels, percentile)
        percentile_intensities.append(percentile_intensity)
    
    avg_percentile_first_5 = np.mean(percentile_intensities)
    
    # Print the average percentile intensity from the first 5 frames
    print(f"Average {percentile}th percentile intensity of the first 5 frames: {avg_percentile_first_5}")

    # Step 2: Define the threshold as threshold_ratio of the average percentile intensity from step 1
    threshold = avg_percentile_first_5 * threshold_ratio
    
    # Print the threshold intensity
    print(f"Threshold intensity (threshold ratio = {threshold_ratio}): {threshold}")

    # Step 3: Work backwards from the last frame, flagging frames where the percentile intensity is below the threshold
    outlier_count = 0
    print(f"\n{percentile}th percentile intensities of the frames at the end of the run:")
    for i in range(num_frames - 1, -1, -1):
        frame_data = data[..., i]
        nonzero_voxels = frame_data[frame_data > 0]
        percentile_intensity = np.percentile(nonzero_voxels, percentile)

        # Print the percentile intensity of the current frame
        print(f"Frame {i+1}: {percentile}th percentile intensity = {percentile_intensity}")

        if percentile_intensity < threshold:
            outlier_count += 1
        else:
            break  # Stop once a non-outlier frame is found

    return outlier_count

#%%
parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fileToParse", help="the .csv")

args = parser.parse_args()
if args.fileToParse:
    filename = args.fileToParse
else:
    print('I need a config file if you want to run nordic on a func dataset!')
mainDir = os.getcwd()
print(mainDir)

splitPath = mainDir.split('/')
for i in splitPath:
    try:
        int(i)
        newPath = '/home' + mainDir[mainDir.index(i)+len(i):]
        mainDir = newPath
    except:
        pass

bids = os.path.join(mainDir,'bids')
    
sbatch = os.path.join(mainDir,'code','nordicsbatch.sh')
lowsbatch = os.path.join(mainDir,'code','lowsbatch.sh')
niftiNordic = os.path.join(mainDir,'code','NIFTI_NORDIC.m')
runNordic = os.path.join(mainDir,'code','runnordic.m')

if not os.path.exists(sbatch):
    raise Exception("please copy code/nordicsbatch.sh into code")
if not os.path.exists(lowsbatch):
    raise Exception("please copy code/lowsbatch.sh into code")
if not os.path.exists(niftiNordic):
    raise Exception("please copy code/NIFTI_NORDIC.m into code")
if not os.path.exists(runNordic):
    raise Exception("please copy code/runnordic.m into code")

#%%        
df = pd.read_csv(filename,sep='\t')
#get rid of nans
df = df.replace(np.nan, '', regex=True)
    
mag_paths = []
phase_paths = []

empty = ['']
#labeled = df[['SubID','Session','label','PEdir','nTRs','AcqNumber','ExpectedTRs',\
#              'complete','noise','runNum','MP','nEc']][~df['label'].isin(empty)]
labeled = df[['SubID','Session','label','PEdir','nTRs','AcqNumber','ExpectedTRs',\
              'complete','runNum','MP','nEc']][~df['label'].isin(empty)]
print(labeled)
notFunc = ['T1w','T2w','dwi','fmap','physio','']
#funcOnly = labeled[['SubID','Session','label','PEdir','nTRs','AcqNumber','ExpectedTRs','complete','noise','runNum','MP','nEc']][~df['label'].isin(notFunc)]
funcOnly = labeled[['SubID','Session','label','PEdir','nTRs','AcqNumber','ExpectedTRs','complete','runNum','MP','nEc']][~df['label'].isin(notFunc)]
newDict = funcOnly.T.to_dict()
dicomList = []
for i in newDict:
    dicomList.append(newDict[i])
#print(dicomList)
#%%
anotherDict = []
for i,nii in enumerate(dicomList):
    #print(nii)
    subID = 'sub-'+ str(nii['SubID'])
    #noise = nii['noise']
    ses = str(nii['Session'])
    task = nii['label']
    echo = int(nii['nEc'])
    funcDir = os.path.join(bids,'%s','ses-%s','func/')%(subID,ses)
    print(funcDir)

    for i in range(echo):
        run = nii['runNum']
        if int(run) < 10:
            run = '0' + str(int(run))
        else:
            run = str(int(run))
        dictionary = {
              'magFile': '', 
              'phaseFile': '',
              'nordicHeader': '',
              'noiseVols': '',
              }
        dictionary['nordicHeader'] = 'NORDIC'
        #dictionary['noiseVols'] = noise
        echo = i + 1
        
        if nii['MP'] == 'M':
            # magName = subID + '_ses-' + str(ses) + '_task-' + task + 'ME' + '_run-' + run + '_echo-' + str(echo) + '_bold.nii.gz'
            # phName = subID + '_ses-' + str(ses) + '_task-' + task + 'MEph' + '_run-' + run + '_echo-' + str(echo) + '_bold.nii.gz'
            magName = subID + '_ses-' + str(ses) + '_task-' + task + '_run-' + run + '_echo-' + str(echo) + '_part-mag_bold.nii.gz'
            phName = subID + '_ses-' + str(ses) + '_task-' + task + '_run-' + run + '_echo-' + str(echo) + '_part-phase_bold.nii.gz'
            #print(magName)
            #print(phName)
            nordicHeader = subID + '_ses-' + str(ses) + '_task-' + task + 'MENORDIC' + '_run-' + run + '_echo-' + str(echo) + '_bold'
            dictionary['nordicHeader'] = nordicHeader
            dictionary['phaseFile'] = phName
            dictionary['magFile'] = magName
            if os.path.exists(os.path.join(funcDir,magName)) and os.path.exists(os.path.join(funcDir,phName)):
                noise = count_noise_volumes(os.path.join(funcDir,magName))
                dictionary['noiseVols'] = noise
                anotherDict.append(dictionary)

#print('dictionary; ', anotherDict)
#%%    
print('copying relevant files to funcDir...')
cmd_list = []
os.chdir(funcDir)
cmd = 'mkdir -p output_logs'
run_shell_cmd(cmd)
cmd = 'cp -n %s .'%niftiNordic
run_shell_cmd(cmd)
cmd = 'cp -n %s .'%runNordic
run_shell_cmd(cmd)


#%%
for m,mag in enumerate(anotherDict):
    magFile = anotherDict[m]['magFile']
    phaseFile = anotherDict[m]['phaseFile']
    #magFile = os.path.join(funcDir,anotherDict[m]['magFile'])
    #phaseFile = os.path.join(funcDir,anotherDict[m]['phaseFile'])
    nordicHeader = anotherDict[m]['nordicHeader']
    noiseVols = str(int(anotherDict[m]['noiseVols']))
    cmd = 'sbatch %s %s %s %s %s %s %s'%(sbatch, funcDir, magFile, phaseFile, nordicHeader, noiseVols, lowsbatch)
    #print(sbatch)
    #print(funcDir)
    #print(anotherDict[m]['magFile'])
    #print(anotherDict[m]['phaseFile'])
    #print(nordicHeader)
    #print(noiseVols)
    #print(cmd)
    cmd_list.append(cmd)

for cmd in cmd_list:
    print(cmd)
    run_shell_cmd(cmd)
