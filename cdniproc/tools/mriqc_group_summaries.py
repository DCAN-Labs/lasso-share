#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
INTENDED FOR PARTICIPANTS > 1 YR

"""
#import os, datetime, glob, sys, json
#import numpy as np

import os, datetime, shutil 
import glob, argparse, json, ast, math
import pandas as pd
from pydicom import dcmread
import numpy as np
import warnings

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return


#%%
#mainDir = '/scratch.global/kweldon/subpop'
mainDir = '/projects/standard/faird/shared/projects/turing/'
#folder = ''
folder = 'mriqc'
mriqcPath = os.path.join(mainDir, folder)
#%%
# parser = argparse.ArgumentParser()

# parser.add_argument("-d", "--mriqc directory", help="MRIqc directory path")

# mainDir = os.getcwd()
# args = parser.parse_args()

# discard = ''
# mriqcPath = args.mriqc


#%%

print('Reading from mriqc dir: ', mriqcPath)

#%%

if os.path.isdir(mriqcPath):
    contents = glob.glob(os.path.join(mriqcPath,'output','sub-*','*','*','*','*.csv'))
    contents.sort()
    print(contents)
cmd_list = []
for file in contents:
    cmd = 'cp %s %s'%(file,os.path.join(mriqcPath, 'output/.'))
    cmd_list.append(cmd)
for cmd in cmd_list:
    print(cmd)
    run_shell_cmd(cmd)
    



    
