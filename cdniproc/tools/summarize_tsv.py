#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 19:27:37 2024

from main directory, '/projects/standard/nardosr/shared/projects/mindfulness/' I will look
in 'derivatives/xcpd/output' and combine all *qc.tsv files into one summary.tsv
@author: kweldon
"""

import os, glob, h5py
import pandas as pd
import argparse

#%%
#mainDir = '/projects/standard/csandova/shared/projects/neonatal/'
mainDir = os.getcwd()

#%%

outputDir = os.path.join(mainDir,'derivatives/xcpd*/output')
#funcDir = os.path.join(outputDir,subjID,'sub-'+subjID,'ses-combined','func')
funcDir = os.path.join(outputDir,'*',"*",'ses-*','func')

#gather the files 
input_list = []
input_list = glob.glob(os.path.join(funcDir, '*qc.tsv'))
input_list2 = glob.glob(os.path.join(funcDir, '*_run*qc.tsv'))
#remove single runs
input_list = set(input_list)-set(input_list2)
input_list = list(input_list)
print(input_list)

#%%    
# for file in input_list:
#     print(file)
#     f = h5py.File(file,'r')
#     group = f['dcan_motion']
#     df = pd.DataFrame(group)
#     for iF,fd in enumerate(group.keys()):
#         #print(iF)
#         #print(fd)
#         for element in group[fd].keys():
#             if element != 'binary_mask':
#                 #df[element] = group[fd][element][()]
#                 df.loc[iF,element] = group[fd][element][()]
#                 #print(df)
#                 #print(element, group[fd][element][()])
    
#     df['remaining_min']=df['remaining_seconds']/60
#     csvname = os.path.split(file)[-1].split('.')[0] + '.tsv'
#     csvpath = os.path.join(funcDir,csvname)
#     df.to_csv(csvpath, sep='\t', index=False)

#%%
#df[df['0'] == 'fd_0.2']
for i,tsv in enumerate(input_list):
    if i == 0:
        df_tsv = pd.read_csv(tsv,sep='\t',header=0)
        df = df_tsv
        df['subID'] = os.path.split(tsv)[1].split('_')[0]
        df['ses'] = os.path.split(tsv)[1].split('_')[1] 
        df['task'] = os.path.split(tsv)[1].split('_')[2]    
        fd = df['0']
    else:
        df_tsv = pd.read_csv(tsv,sep='\t',header=0)
        df_tsv['subID'] = os.path.split(tsv)[1].split('_')[0]
        df_tsv['ses'] = os.path.split(tsv)[1].split('_')[1] 
        df_tsv['task'] = os.path.split(tsv)[1].split('_')[2]  
        df=pd.concat([df, df_tsv], ignore_index=True)

#fd = df['0']

df = df.rename(columns={'0': 'fd'})
column_to_move = df.pop("subID")
df.insert(0, "subID", column_to_move)
column_to_move = df.pop("ses")
df.insert(1, "ses", column_to_move)
column_to_move = df.pop("task")
df.insert(2, "task", column_to_move)
#df_sorted = df.sort_index()
df_sorted = df.sort_values(by=['subID','task','fd'])

name = 'motion_summary.tsv'
csvpath = os.path.join(mainDir, name)
print(csvpath)
df_sorted.to_csv(csvpath, sep='\t', index=False)

# for i in fd:
#     if i == 'fd_0.2' or i == 'fd_0.3':
#         name = i + '.tsv'
#         df2 = df[df['fd'] == i]
#         df2_sorted = df.sort_values(by='subID')
#         csvpath = os.path.join(mainDir + name)
#         print(csvpath)
#         df2_sorted.to_csv(csvpath, sep='\t', index=False)

