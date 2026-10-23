#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess as sub
import pandas as pd
import numpy as np
import nibabel as nib
"""
This script is designed to run nordic with one input: tsv file
"""
def run_shell_cmd(cmd):
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return


#%%
parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fileToParse", help="the .tsv")

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
    except:
        pass
mainDir = newPath

bids = os.path.join(mainDir,'bids')    
sbatchinit = os.path.join(mainDir,'code','run_newinit.sh')


#%%
# mainDir = '/projects/standard/nardosr/shared/projects/sandbox/'
# bids = os.path.join(mainDir,'bids')
# lowsbatch = '/projects/standard/faird/shared/code/internal/utilities/bids_nordic_wrapper/genericsbatch_low_resources.sh'
# sbatch = '/projects/standard/faird/shared/code/internal/utilities/bids_nordic_wrapper/nordicsbatch.sh'
# passnordicsbatch = '/projects/standard/faird/shared/code/internal/utilities/bids_nordic_wrapper/passnordicsbatch.sh'
# filename = os.path.join(mainDir, 'summaries', '1000401-ses4.tsv')#read in csv to dataframe
# funcDir = os.path.join(mainDir,'bids/sub-1000401/ses-4/func')
# niftiNordic = os.path.join(mainDir,'code','NIFTI_NORDIC.m')
# runNordic = os.path.join(mainDir,'code','runnordic.m')
# sbatch = os.path.join(mainDir,'code','nordicsbatch.sh')

#%%        
cmd_list = []
with open(filename, 'r') as file:
    for line in file:
        #print(line)
        subj = line.split('/')[-2].split('-')[0]
        ses = line.split('/')[-2].split('-')[1][-1]
        cmd = 'sbatch %s %s %s'%(sbatchinit, subj, ses)
        print(cmd)
        cmd_list.append(cmd)
#print(cmd_list)
#%%
    

cmd_listFileName = 'init_cmd'
cmd_listFilePath = os.path.join(mainDir,cmd_listFileName)
print(cmd_listFilePath)
with open(cmd_listFilePath, 'w') as f:
    for cmd in cmd_list:
        f.write("%s\n" % cmd)
f.close()