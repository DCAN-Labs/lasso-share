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
#xcpdDir = '/scratch.global/kweldon/attune/derivatives/xcpd-0.10.7/output/GPA22'

#%%
if len(sys.argv) > 1:
    xcpdDir = sys.argv[1]

#%%
subjID = os.path.split(xcpdDir)[1]
xcpdoutput = os.path.split(xcpdDir)[0]
xcpdbase = os.path.split(xcpdoutput)[0]
derivatives = os.path.split(xcpdbase)[0]

#%%

funcDir = os.path.join(xcpdDir,'sub-*/ses-*/func/')
anatDir = os.path.join(xcpdDir,'sub-*/ses-*/anat/')
inputDir = os.path.join(derivatives, 'postprocessing', subjID, 'tempmatch', 'input')
print(funcDir)

#gather the files 
input_list = []
input_list = glob.glob(os.path.join(funcDir, '*FD_only.mat'))
input_list += glob.glob(os.path.join(funcDir, '*inter*'))
input_list += glob.glob(os.path.join(anatDir, '*midthick*'))
print(input_list)

#%%      
cmd_list = []
print(inputDir)
if not os.path.exists(inputDir):
    cmd = 'mkdir -p %s'%inputDir
    print(cmd)
    run_shell_cmd(cmd)
    
for i in input_list:
    cmd = 'cp %s %s/.'%(i,inputDir)
    cmd_list.append(cmd)
    print(cmd)

for i in cmd_list:
    print(i)
    run_shell_cmd(i)
    


