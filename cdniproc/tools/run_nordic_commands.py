#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess as sub
import pandas as pd
import numpy as np
import nibabel as nib
"""
This script is designed to run nordic with one input
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
    
    
args = parser.parse_args()
if args.fileToParse:
    filename = args.fileToParse
else:
    print('I need a filename! e.g. nordic_cmd_1000201_1')

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
nordic_cmd_dir = os.path.join(mainDir,'nordic_cmds')
filename = os.path.join(nordic_cmd_dir, filename)
subjid = os.path.split(filename)[1].split('_')[2]
sess = os.path.split(filename)[1].split('_')[3]
funcDir = os.path.join(mainDir,'bids','sub-%s','ses-%s','func')%(subjid,sess)

#%%        
#mainDir = '/projects/standard/nardosr/shared/projects/sandbox'
#filename = os.path.join(mainDir,'nordic_cmds','nordic_cmd_1000201_1')

#%%

subjid = os.path.split(filename)[1].split('_')[2]
sess = os.path.split(filename)[1].split('_')[3]
funcDir = os.path.join(mainDir,'bids','sub-%s','ses-%s','func')%(subjid,sess)
os.chdir(funcDir)

#print('now in')
print(os.getcwd())
cmd_list = []
with open(filename, 'r') as file:
    for line in file:
        #print(line)
        cmd_list.append(line)
        
#print(cmd_list)
for cmd in cmd_list:
    print(cmd)
    run_shell_cmd(cmd)
print(os.getcwd())