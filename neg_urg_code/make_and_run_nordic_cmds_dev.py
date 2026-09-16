#!/usr/bin/env python3

import os, glob
#import glob
#import argparse
import subprocess as sub
#import pandas as pd
import numpy as np
import nibabel as nib
import argparse
import sys
"""
This script is designed to run nordic with one input: path to func dir
"""
def run_shell_cmd(cmd):
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return

def count_noise(nifti_file,percentile=90, threshold_ratio=0.5):
    # Load the NIfTI file
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
    #print(f"Average {percentile}th percentile intensity of the first 5 frames: {avg_percentile_first_5}")

    # Step 2: Define the threshold as threshold_ratio of the average percentile intensity from step 1
    threshold = avg_percentile_first_5 * threshold_ratio
    
    # Print the threshold intensity
    #print(f"Threshold intensity (threshold ratio = {threshold_ratio}): {threshold}")

    # Step 3: Work backwards from the last frame, flagging frames where the percentile intensity is below the threshold
    outlier_count = 0
    #print(f"\n{percentile}th percentile intensities of the frames at the end of the run:")
    for i in range(num_frames - 1, -1, -1):
        frame_data = data[..., i]
        nonzero_voxels = frame_data[frame_data > 0]
        percentile_intensity = np.percentile(nonzero_voxels, percentile)

        # Print the percentile intensity of the current frame
        #print(f"Frame {i+1}: {percentile}th percentile intensity = {percentile_intensity}")

        if percentile_intensity < threshold:
            outlier_count += 1
        else:
            break  # Stop once a non-outlier frame is found
    del img
    return num_frames, outlier_count

def count_volumes(nifti_file):
    # Load the NIfTI file
    img = nib.load(nifti_file)
    data = img.get_fdata()
    # Check the shape of the data (X, Y, Z, T) -> T is the number of frames (time points)
    num_frames = data.shape[-1]
    del img
    return num_frames

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--funcdir", type=str, required=True, help="Path to func directory to run NORDIC on")
args = parser.parse_args()

funcDir = args.funcdir

print('funcdir: ', funcDir)

mainDir = os.path.split(funcDir)[0].split('bids')[0]
nordicDir = os.path.join(mainDir,'derivatives','nordic')
sbatch = '/projects/standard/lewi1538/shared/projects/neg_urg/code/nordicsbatch_new.sh'

magfiles = []
magfiles = glob.glob(os.path.join(funcDir,'*part-mag*nii.gz'))
phfiles = []
phfiles = glob.glob(os.path.join(funcDir,'*part-phase*nii.gz'))

# print(magfiles)


#%%
nordicDict = []
passDict = []
cmd_list_nordic = []
cmd_list_pass = []
for i,nii in enumerate(magfiles):
    dictionary = {
          'magFile': '', 
          'phFile': '',
          'nordicHeader': '',
          'noiseVols': '',
          }
    
    funcDir=os.path.split(nii)[0]
    magName=os.path.split(nii)[1]
    magHead=magName.split('.')[0]
    elements = os.path.split(nii)[1].split('_')
    #print(elements)
    for e in elements:
        if e.startswith('task-'):
             task = e
        if e.startswith('sub-'):
             subID = e
        if e.startswith('ses-'):
             ses = e
    
    phtask=task 
    phName=magName.replace('part-mag','part-phase')
    phName=phName.replace(task,phtask)
    phFile=os.path.join(funcDir,phName)
    
    nordictask = task + 'NORDIC'
    nordicHeader= magName.replace(task,nordictask)
    nordicHeader=nordicHeader.replace('.nii.gz','')
#%%    
    read_mag = count_noise(nii)
    mag_count = read_mag[0]
    noise = read_mag[1]
    print(magName, ' exists')
    #print(read_mag)
    if os.path.exists(phFile):
         print(phName, ' exists')
         cmd = 'sbatch %s %s %s %s %s %s %s'%(sbatch, funcDir, nii, phFile, nordicHeader, noise, nordicDir)
         cmd_list_nordic.append(cmd)
    else:
         cmd = 'sbatch %s %s %s %s %s %s %s'%(sbatch, funcDir, nii, phFile, nordicHeader, noise, nordicDir)
         cmd_list_pass.append(cmd)
         print(phName, ' does not exist')

    
# Run commands
for cmd in cmd_list_nordic:
    run_shell_cmd(cmd)
    print(cmd)

# Write out commands 
cmd_listFileName = 'nordic_cmd_' + subID + '_' + ses + '.sh'
cmd_listFilePath = os.path.join(mainDir,cmd_listFileName)
print(cmd_listFilePath)
with open(cmd_listFilePath, 'w') as f:
    for cmd in cmd_list_nordic:
        f.write("%s\n" % cmd)
    for cmd in cmd_list_pass:
        f.write("%s\n" % cmd)
f.close()
