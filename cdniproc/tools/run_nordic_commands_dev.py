#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess as sub
import pandas as pd
import numpy as np
import nibabel as nib
import sys
"""
This script is designed to run nordic with one input
"""
def run_shell_cmd(cmd):
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return


#%%
if len(sys.argv) > 1:
    file = sys.argv[1]
else:
    print('I need an input to run the nordic commands!')

mainDir = os.path.split(file)[0].split('summaries')[0]
filename = file
subjid = os.path.split(filename)[1].split('_')[2]
sess = os.path.split(filename)[1].split('_')[3]

cmd_list = []
with open(filename, 'r') as file:
    for line in file:
        #print(line)
        cmd_list.append(line)
        
#print(cmd_list)
for cmd in cmd_list:
    #print(cmd)
    run_shell_cmd(cmd)
print(os.getcwd())