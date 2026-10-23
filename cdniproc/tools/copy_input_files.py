#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
I will copy files needed for postprocessing into an input folder!

"""
#import os, datetime, glob, sys, json
#import numpy as np

import os, sys
import glob
import pandas as pd
import shutil

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return 

#%%
#xcpdDir = '/scratch.global/kweldon/attune/derivatives/xcpd-0.10.7/output/GPA54'

#%%
if len(sys.argv) < 3:
    sys.exit("Usage: copy_input_files.py <xcpd_subject_dir> <project_root> [output_dir]")

xcpdDir = sys.argv[1]
project_root = sys.argv[2].rstrip('/')
output_dir = sys.argv[3].rstrip('/') if len(sys.argv) > 3 else os.path.join(project_root, 'derivatives', 'analysis')

#strip trailing slash
if os.path.split(xcpdDir)[1] == '':
    xcpdDir = xcpdDir[:-1]

#%%
subjID = os.path.split(xcpdDir)[1]
xcpdoutput = os.path.split(xcpdDir)[0]
xcpdbase = os.path.split(xcpdoutput)[0]

print('running')
xcpd_version = os.path.split(xcpdbase)[1]
derivatives = output_dir


#derivatives = xcpdbase.split('derivatives')[0] + 'derivatives' + '/fmriprep-24.1.1-' + os.path.split(xcpdbase)[1] + '/' + subjID
funcDir = os.path.join(xcpdDir,'sub-*/ses-*/func/')
anatDir = os.path.join(xcpdDir,'sub-*/ses-*/anat/')
anatDir2 = os.path.join(xcpdDir,'sub-*/anat/')
inputDir = os.path.join(derivatives, 'analysis_input_files', subjID)

print(funcDir)
print(anatDir)
print(anatDir2)
#gather the files 
input_list = []
input_list = glob.glob(os.path.join(funcDir, '*FD_only.mat'))
input_list += glob.glob(os.path.join(funcDir, '*inter*'))
input_list += glob.glob(os.path.join(anatDir, '*midthick*'))
input_list += glob.glob(os.path.join(anatDir2, '*midthick*'))
print(input_list)

#%%      
cmd_list = []
print(inputDir)
if not os.path.exists(inputDir):
    cmd = 'mkdir -p %s'%inputDir
    print(cmd)
    run_shell_cmd(cmd)
else:
    print('wiping directory and starting over')
    cmd = 'rm -rf %s'%inputDir
    print(cmd)
    run_shell_cmd(cmd)
    cmd = 'mkdir -p %s'%inputDir
    print(cmd)
    run_shell_cmd(cmd)
    
    
for i in input_list:
    cmd = 'cp %s %s/.'%(i,inputDir)
    cmd_list.append(cmd)
    #print(cmd)

for i in cmd_list:
    print(i)
    run_shell_cmd(i)
    
##rename files
    
