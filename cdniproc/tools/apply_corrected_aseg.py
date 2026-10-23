#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
I will copy files needed for temp matching into an input folder!

"""
#import os, datetime, glob, sys, json
#import numpy as np

import os
import glob, argparse
import pandas as pd
import shutil

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return 

#%%
mainDir = '/projects/standard/csandova/shared/projects/neonatal/'
correctedDir = os.path.join(mainDir, 'corrected')
bibsDir = os.path.join(mainDir,'derivatives/bibsnet/output')
subjID = 's009post'
outputDir = os.path.join(bibsDir,subjID,'bibsnet','sub-'+subjID,'ses-1','anat/')
#%%
# parser = argparse.ArgumentParser()
# parser.add_argument("-s", "--subjID", type=str, help="subID")

# mainDir = os.getcwd()
# correctedDir = os.path.join(mainDir, 'corrected')
# bibsDir = os.path.join(mainDir,'derivatives/bibsnet/output')

# args = parser.parse_args()
# if args.subjID:
#     subjID = args.subjID
    
# outputDir = os.path.join(bibsDir,subjID,'bibsnet','sub-'+subjID,'ses-01','anat/')

#%%
#incorrect_aseg_in = os.path.join(outputDir,'sub-'+subjID+'_ses-1_space-T1w_desc-aseg_dseg.nii.gz')
#incorrect_aseg_out = os.path.join(outputDir,'sub-'+subjID+'_ses-1_space-T1w_desc-aseg_dseg_old.nii.gz')
#corrected_file_in = os.path.join(correctedDir,'corrected_sub-s003_ses-01_optimal_resized_final.nii.gz')
#corrected_file_out = incorrect_aseg_in

#gather the files 
input_list = []
input_list = glob.glob(os.path.join(outputDir, '*aseg_dseg.nii.gz'))

#print(input_list)

for file in input_list:
    incorrect_aseg_in = file
    incorrect_aseg_out_name = os.path.split(file)[1].split('.')[0] + '_old.nii.gz'
    incorrect_aseg_out = os.path.join(outputDir,incorrect_aseg_out_name)
    corrected_file_in = os.path.join(correctedDir,'corrected_sub-s009_ses-2_optimal_resized_final.nii.gz')
    corrected_file_temp = os.path.join(outputDir,'corrected_sub-s009_ses-2_optimal_resized_final.nii.gz')
    corrected_file_final = incorrect_aseg_in
    
    cmd = 'mv %s %s'%(incorrect_aseg_in,incorrect_aseg_out)
    print(cmd)
    run_shell_cmd(cmd)
    
    cmd = 'cp %s %s'%(corrected_file_in,outputDir)
    print(cmd)
    run_shell_cmd(cmd)
    
    cmd ='mv %s %s'%(corrected_file_temp,corrected_file_final)
    print(cmd)
    run_shell_cmd(cmd)
