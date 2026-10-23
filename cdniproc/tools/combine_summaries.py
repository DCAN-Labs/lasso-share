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

import os
import glob, argparse
import json, ast, math
import pandas as pd

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return


#%%
#mainDir = '/scratch.global/kweldon/subpop'
mainDir = '/projects/standard/kweldon/shared/projects/subpop_v2/'
#mainDir = '/projects/standard/nardosr/shared/projects/sandbox/'
#folder = ''
#folder = 'summaries'
summaries = os.path.join(mainDir)
#%%
# parser = argparse.ArgumentParser()

# parser.add_argument("-d", "--mriqc directory", help="MRIqc directory path")

# mainDir = os.getcwd()
# args = parser.parse_args()

# discard = ''
# mriqcPath = args.mriqc


#%%

print('Reading from summaries dir: ', summaries)

#%%
filename = os.path.join(mainDir,'summaries_combined.tsv')
if os.path.isdir(summaries):
    contents = glob.glob(os.path.join(summaries,'*.tsv'))
    contents.sort()
    print(contents)
    
#df_csv_append = pd.DataFrame()
lst = []
# append the CSV files                # <--- initial list (doesn't have to be empty; 
for file in contents:   #                    could store the initial df)
    data = pd.read_csv(file,sep='\t')
    lst.append(data)                         # <--- enlarge list
df = pd.concat(lst)
                          # <--- concatenate the frames
print('writing...: ', filename)
df.to_csv(filename, encoding='utf-8', index=False,sep="\t")



    
