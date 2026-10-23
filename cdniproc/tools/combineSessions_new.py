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
import glob, argparse, json
import pandas as pd
import shutil


#%%
#mainDir = '/projects/standard/nardosr/shared/projects/mindfulness/'
#bids = 'sub-01'
#mainDir = '/projects/standard/jboisson/shared/projects/AAR01/bids_test'
#bids = 'AA004'

#%%
parser = argparse.ArgumentParser()

parser.add_argument("-b", "--bidssubj", type=str, help="subID")
args = parser.parse_args()
if args.bidssubj:
    bids = args.bidssubj

mainDir = os.getcwd()
mainDir = os.path.join(mainDir, 'derivatives/nordic')
#mainDir = os.path.join(mainDir, 'bids_test','bids%s'%bids)


#%%

source = os.path.join(mainDir,'sub-'+bids)
if not os.path.exists(source):
    raise Exception(source, ' does not exist! What do you want to combine?')
if 'sub-' not in source:
    raise Exception("I only work on single subject bids folders! The input folder must start with sub-")
else:
    print('combining sessions in %s...'%bids)
#gather the files 
session_list = []
session_list = glob.glob(os.path.join(mainDir, bids, '*'))
if 'tmp_dcm2bids' in session_list:
    session_list.remove('tmp_dcm2bids')
#%%      
#delete ses-combined and start over
combinedfolder = os.path.join(source,'ses-combined')
if os.path.exists(combinedfolder):
    shutil.rmtree(combinedfolder) 
    
session_list = []
session_list = glob.glob(os.path.join(source,'ses-*'))
session_list.sort()
print('making... ',combinedfolder)
os.mkdir(combinedfolder)

df = pd.DataFrame()

subjlist = []
file_list = []
for i,folder in enumerate(session_list):
    #print(folder)
    session = i + 1
    file_list = glob.glob(os.path.join(session_list[i], '[!tmp]*','*'))
    file_list.sort()
    #print(file_list)
    
        
#%%
    for i,filepath in enumerate(file_list):
        filelist = []
        fname = os.path.split(filepath)[1]
        #print(fname)
        seqtype = os.path.split(os.path.split(filepath)[0])[1]
        try:
            modtype = fname.split('_')[-1]
            modtype = modtype.split('.')[0]
        except:
            modtype = ''
    
        try:
            pestart = fname.index('dir-',) + 4
            peend = fname.index('_',pestart)
            pename = fname[pestart:peend]
            pedir = 'PEdir-' + pename
        except:
            pedir = ''
                    
        try:
            substart = fname.index('sub-',) + 4
            subend = fname.index('_',substart)
            subname = fname[substart:subend]
            sub = 'sub-' + subname
        except:
            sub = ''
            
        try:
            echostart = fname.index('echo-',) + 5
            echoend = fname.index('_',echostart)
            echonum = fname[echostart:echoend]
            echo = 'echo-' + echonum
        except:
            echo = ''
            
        try:
            acqstart = fname.index('acq-',) + 4
            acqend = fname.index('_',acqstart)
            acqnum = fname[acqstart:acqend]
            acq = 'acq-' + acqnum
        except:
            acq = ''
            
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
            run = 'run-01'
            runNum = 1
        
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
        filelist.append(str(pedir))
        filelist.append(str(task))
        filelist.append(str(tasktype))
        filelist.append(str(modtype))
        try:
            filelist.append(str(int(echo)))
        except:
            filelist.append(str(echo))
        filelist.append(str(filetype))
        subjlist.append(filelist)
    #%%
    #print(subjlist)
    df = pd.DataFrame()
    cols = ['filename', 'sub','session','seqtype','ses','run','runNum','PEdir','task','tasktype','modtype','echo','filetype']
    df = df.reindex(df.columns.union(cols), axis=1)   
    for i in range(len(subjlist)):
        #print(dcmlist2[i])
        df.loc[i] = subjlist[i]
    
    #df['combRun'] = df.groupby(['sub','PEdir','tasktype','seqtype','modtype','filetype']).cumcount().add(1)
    df['combRun'] = df.groupby(['sub','PEdir','echo','tasktype','seqtype','modtype','filetype']).cumcount().add(1)
    df['combRun'] = df['combRun'].astype(str)
    df['combRun'] = df['combRun'].str.zfill(2)
    df['newRun'] = 'run-' + df['combRun'].astype(str)
    df['newSes'] = 'ses-combined'
    #print(df[['session','seqtype','tasktype','anattype','filetype','run','runNum','newRun','newSes']])
    print(df[['session','seqtype','tasktype','filetype','run','runNum','combRun','echo','newRun']])
#%%
newDict = df.T.to_dict()

#print(newDict)
for i in newDict:
    fname = newDict[i]['filename']
    seqtype = newDict[i]['seqtype']
    func_ses = newDict[i]['session']
            
    if '_run-' in fname:
        newfname = fname.replace(newDict[i]['run'],newDict[i]['newRun'])
    else:
        newfname = fname[:fname.index(modtype)] + newDict[i]['newRun'] + '_' + fname[fname.index(modtype):]
    
    newfname = newfname.replace(newDict[i]['ses'],newDict[i]['newSes'])
    srcpath = os.path.join(source,newDict[i]['ses'],newDict[i]['seqtype'],newDict[i]['filename'])
    
    #I want to preserve the orginial session number in the json sidecar
    if 'json' in fname:
        #print(srcpath)
        with open(srcpath, 'r') as g:
            func_json = json.load(g)
            g.close()
        
        #insert orig session
        entry = {"OriginalSession": newDict[i]['ses']}
        func_json.update(entry)
        
        #insert old run entry
        try:
            entry = {'OrginalRun': newDict[i]['run']}
            func_json.update(entry)
        except:
            entry = {'OrginalRun': ''}
            func_json.update(entry)
            
        #insert orig filename
        entry = {"OriginalFilename": fname}
        func_json.update(entry)
        
        #insert new run entry
        entry = {"NewRun": newDict[i]['newRun']}
        func_json.update(entry)
        
        with open(srcpath, 'w') as f:
            json.dump(func_json, f, indent = 4)
            #print(func_json)
            f.close()
    
    if not os.path.exists(os.path.join(combinedfolder,newDict[i]['seqtype'])):
        os.mkdir(os.path.join(combinedfolder,newDict[i]['seqtype']))   
    destpath = os.path.join(combinedfolder,newDict[i]['seqtype'])
    shutil.copy(srcpath, destpath)
    newpatholdname = os.path.join(destpath,fname)
    print('old name in %s/%s    : '%(newDict[i]['ses'],newDict[i]['seqtype']), fname)
    newpathnewname = os.path.join(destpath,newfname)
    print('new name in ses-combined/%s: '%newDict[i]['seqtype'], newfname)
    os.rename(newpatholdname,newpathnewname)
    
