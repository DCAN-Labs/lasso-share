#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
I will combined sessions of a single subject's bids data

Usage:
    python /path/to/combineSessions.py -b sub-01
    
Note:
    I will combined every modality! 

"""
#import os, datetime, glob, sys, json
#import numpy as np

import os
import glob, argparse
import pandas as pd
import shutil


#%%
#mainDir = '/projects/standard/nardosr/shared/projects/mindfulness/'
#bids = 'sub-01'
#mainDir = '/projects/standard/faird/shared/projects/subpop/bids'
#bids = 'sub-1005401'

#%%
parser = argparse.ArgumentParser()

parser.add_argument("-b", "--bidssubj", type=str, help="subID")

mainDir = os.getcwd()
args = parser.parse_args()

if args.bidssubj:
    bids = args.bidssubj

#%%

if 'sub-' not in bids:
    raise Exception("I only work on single subject bids folders! The input folder must start with sub-")
else:
    print('combining sessions in %s...'%bids)
#gather the files 
session_list = []
session_list = glob.glob(os.path.join(mainDir, bids, '*'))
if 'tmp_dcm2bids' in session_list:
    session_list.remove('tmp_dcm2bids')
#%%      
combinedfolder = os.path.join(mainDir, bids,'ses-combined')
if os.path.exists(combinedfolder):
    shutil.rmtree(combinedfolder) 
session_list = []
session_list = glob.glob(os.path.join(mainDir, bids, '*'))
session_list.sort()
print('making... ',combinedfolder)
os.mkdir(combinedfolder)

df = pd.DataFrame()

subjlist = []
file_list = []
for i,folder in enumerate(session_list):
    print(folder)
    session = i + 1
    file_list = glob.glob(os.path.join(session_list[i], '*','*'))
    file_list.sort()
        
#%%
    for i,filepath in enumerate(file_list):
        filelist = []# copying the files to the destination directory
        #fname = os.path.split(file_list[0])[1]
        fname = os.path.split(filepath)[1]
        
        
        seqtype = os.path.split(os.path.split(filepath)[0])[1]
        
        if seqtype == 'anat':
            try:
                anatend = fname.index('.')
                anattype = fname[anatend-3:anatend]
            except:
                anattype = ''
        else: 
            anattype = ''
            
        # if seqtype == 'fmap':
        #     try:
        #         anatend = fname.index('.')
        #         anattype = fname[anatend-3:anatend]
        #     except:
        #         anattype = ''
        # else: 
        #     anattype = ''
                    
        try:
            substart = fname.index('sub-',) + 4
            subend = fname.index('_',substart)
            subname = fname[substart:subend]
            sub = 'sub-' + subname
        except:
            ses = ''
            
        # try:
        #     echostart = fname.index('echo-',) + 5
        #     echoend = fname.index('_',echostart)
        #     echonum = fname[echostart:echoend]
        #     echo = 'echo-' + echonum
        # except:
        #     echo = ''
            
        try:
            sesstart = fname.index('ses-',) + 4
            sesend = fname.index('_',sesstart)
            sesNum = fname[sesstart:sesend]
            ses = 'ses-' + sesNum
        except:
            ses = ''
        
        try:
            runstart = fname.index('run-') + 4
            runend = fname.index('_',runstart)
            runNum = fname[runstart:runend] 
            run = 'run-' + runNum
        except:
            run = ''
            runNum = ''
        
        try:
            taskstart = fname.index('task-') + 5
            taskend = fname.index('_',taskstart)
            tasktype = fname[taskstart:taskend]
            task = 'task-' + tasktype
        except:
            task = ''
            tasktype = ''
    
        filetype = fname.split('.')[1]
        
        filelist.append(str(fname))
        filelist.append(str(sub))
        filelist.append(str(session))
        filelist.append(str(seqtype))
        filelist.append(str(ses))
        filelist.append(str(run))
        try:
            filelist.append(str(int(runNum)))
        except:
            filelist.append(str(runNum))
        filelist.append(str(task))
        filelist.append(str(tasktype))
        filelist.append(str(anattype))
        # try:
        #     filelist.append(str(int(echo)))
        # except:
        #     filelist.append(str(echo))
        filelist.append(str(filetype))
        subjlist.append(filelist)
#%%
#print(subjlist)
df = pd.DataFrame()
cols = ['filename', 'sub','session','seqtype','ses','run','runNum','task','tasktype','anattype','filetype']
df = df.reindex(df.columns.union(cols), axis=1)   
for i in range(len(subjlist)):
    #print(dcmlist2[i])
    df.loc[i] = subjlist[i]

df['combRun'] = df.groupby(['sub','tasktype','seqtype','anattype','filetype']).cumcount().add(1)

#df['combRun'] = df.groupby(['session','sub','tasktype','seqtype','anattype','filetype','run']).cumcount().add(1)
df['combRun'] = df['combRun'].astype(str)
df['combRun'] = df['combRun'].str.zfill(2)
df['newRun'] = 'run-' + df['combRun'].astype(str)
df['newSes'] = 'ses-combined'
#print(df[['session','seqtype','tasktype','anattype','filetype','run','runNum','newRun','newSes']])
print(df[['session','seqtype','tasktype','filetype','run','runNum','combRun','newRun']])
#%%
newDict = df.T.to_dict()
dicomList = []
for i in newDict:
    dicomList.append(newDict[i])
    fname = newDict[i]['filename']
    newfname = fname.replace(newDict[i]['ses'],newDict[i]['newSes'])
    newfname = newfname.replace(newDict[i]['run'],newDict[i]['newRun'])
    srcpath = os.path.join(mainDir, newDict[i]['sub'],newDict[i]['ses'],newDict[i]['seqtype'],newDict[i]['filename'])
    if not os.path.exists(os.path.join(combinedfolder,newDict[i]['seqtype'])):
        os.mkdir(os.path.join(combinedfolder,newDict[i]['seqtype']))
    destpath = os.path.join(combinedfolder,newDict[i]['seqtype'])
    shutil.copy(srcpath, destpath)
    newpatholdname = os.path.join(destpath,fname)
    print('old name in %s    : '%newDict[i]['ses'], fname)
    newpathnewname = os.path.join(destpath,newfname)
    print('new name in ses-combined: ', newfname)
    os.rename(newpatholdname,newpathnewname)
    
