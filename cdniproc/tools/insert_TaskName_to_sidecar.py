#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon


This code inserts "TaskName" key and value into the json sidecar to match the "task" element in the BIDS filename. 

flags:
    -s = subjID
    -b = bids standard directory containing subject directories
    
note: -b can be relative or absolute path

usage: 
    
from /projects/standard/bart/shared/projects/dsmc:
> python code/insert_TaskName_to_sidecar.py -s 01 -b bids
"""

"""


"""
#import os, datetime, glob, sys, json
#import numpy as np

import os
import glob, argparse, json
import pandas as pd
import shutil

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return 

#%%
# mainDir = '/projects/standard/bart/shared/projects/dsmc/'
# subjID = '01'
# bidsDir = 'bids'
#%%
parser = argparse.ArgumentParser()

parser.add_argument("-s", "--subjID", type=str, help="subID")
parser.add_argument("-b", "--bidsDir", type=str, help="bidsDir")

mainDir = os.getcwd()


args = parser.parse_args()
if args.subjID:
    subjID = args.subjID
   
if args.bidsDir:
    bidsDir = args.bidsDir
else:
    print('in which directory are the files you want me to fix?')


#%%

if os.path.isabs(bidsDir):
    ses_list = glob.glob(os.path.join(bidsDir,'sub-'+subjID,'*'))
else:
    ses_list = glob.glob(os.path.join(mainDir,bidsDir,'sub-'+subjID,'*'))

#%%
#funcDir = os.path.join(mainDir,'sub-'+subjID,'ses-etoh','func')


for ses in ses_list:
    print(ses)
    funcDir = os.path.join(ses,'func')
    input_list = []
    input_list = glob.glob(os.path.join(funcDir, '*.json'))
    for j in input_list:
        fname = os.path.split(j)[1]
        print(fname)
        try:
            taskstart = fname.index('task-') + 5
            taskend = fname.index('_',taskstart)
            tasktype = fname[taskstart:taskend]
            task = 'task-' + tasktype
        except:
            task = ''
            tasktype = ''
        
        #print(task)
        with open(j, 'r') as f:
            json_content = json.load(f) 
            json_content["TaskName"] = tasktype
        
        with open(j,'w') as f:
            json.dump(json_content, f, indent=4) # you decide the indentation level

