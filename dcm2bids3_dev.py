#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 21:16:19 2023

@author: kweldon
"""
import os, sys
import importlib
import argparse
import pandas as pd
import numpy as np
import json
import glob

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return 

realPath = os.path.realpath('.')
splitPath = realPath.split('/')
for i in splitPath:
    try:
        int(i)
        realPath = '/home' + realPath[realPath.index(i)+len(i):]
    except:
        pass

print(realPath)

#%%
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fileToParse", help="the .csv")
parser.add_argument("--noforce", action='store_true', help="force dcm2bids")
parser.add_argument("-d", "--dicomdir", help="optional dicompath")
parser.add_argument("--all", action='store_true', help="run one dcm2bids command")
parser.add_argument("--outdir", type=str, help="bids output directory")

args = parser.parse_args()
if args.fileToParse:
    filename = args.fileToParse
else:
    print('I need a config file if you want to run dcm2bids on a dataset!')

if args.noforce:
    force = 0
else:
    force = 1
    
if args.all:
    alldcm = 1
else:
    alldcm = 0
    
if args.dicomdir:
    #dicoms = os.path.split(filename)[1][:-4]
    dicomPath = args.dicomdir
    dFlag = dicomPath
else:
    pass

if args.outdir:
    bids = args.outdir
else:
    bids = 'bids'
    
mainDir = realPath
filepath = os.path.join(mainDir,filename)
dicoms = os.path.split(filename)[1][:-4]
dicomPath = os.path.join(mainDir,'dicoms',dicoms)
bids = os.path.join(mainDir,bids)
oFlag = bids
#%%
df = pd.read_csv(filepath,sep='\t')
print('reading from ... ', filename)
#get rid of nans
df = df.replace(np.nan, '', regex=True)

#%%
#build dictionary -- put fmaps first
newDict = df.T.to_dict()
dicomList = []
for i in newDict:
    if newDict[i]['label'] == 'fmap':
        dicomList.append(newDict[i])
    else:
        pass
for i in newDict:
    if newDict[i]['label'] != 'fmap':
        dicomList.append(newDict[i])
    else:
        pass

#%%

if alldcm:
    dcm = dicomList[0]
    configname = filename.split('.')[0] + '.json'
    try: 
        dFlag
    except:
        dFlag = os.path.join(mainDir,'dicoms',dcm['dicomDir'])
    cFlag = os.path.join(mainDir,configname)
    print("config file:",cFlag)
    if not os.path.exists(cFlag):
        print('config file needs to be in a summaries folder!')
        #cFlag = os.path.join(mainDir,configname)
    
    pFlag = str(dcm['SubID'])
    if 'combine' in filename:
        sFlag = 'combined'
    else:
        sFlag = str(dcm['Session'])
    if force:
        cmd = 'dcm2bids -d %s -p %s -s %s -c %s -o %s --force'\
        %(dFlag, pFlag, sFlag, cFlag, oFlag)
        #print('running %s'%dcmName)
        print(cmd)
        run_shell_cmd(cmd) 
        
    else:
        cmd = 'dcm2bids -d %s -p %s -s %s -c %s -o %s'\
        %(dFlag, pFlag, sFlag, cFlag, oFlag)
        #print('running %s'%dcmName)
        print(cmd)
        run_shell_cmd(cmd)  
    
else:
    for iD, dcm in enumerate(dicomList):
        #print(dicomList)
        if len(dcm['label'])>0: 
            configname = filename.split('.')[0] + '.json'
            # try: 
            #     dFlag
            # except:
            #     dFlag = os.path.join(mainDir,'dicoms',dcm['dicomDir'])
            cFlag = os.path.join(mainDir,configname)
            print(cFlag)
            if not os.path.exists(cFlag):
                print('config file needs to be in a summaries folder!')
                #cFlag = os.path.join(mainDir,configname)
            
            pFlag = str(dcm['SubID'])
            if 'combine' in filename:
                sFlag = 'combined'
            else:
                sFlag = str(dcm['Session'])
                dcmName = os.path.join(dFlag,dcm['Name'])
                folder = 'sub-'+ pFlag + '_ses-' + sFlag
                tmpDir = os.path.join(oFlag,'tmp_dcm2bids',folder)
                if force == 1:
                    cmd = 'dcm2bids -d %s -p %s -s %s -c %s -o %s --force'\
                    %(dcmName, pFlag, sFlag, cFlag, oFlag)
                    #print('running %s'%dcmName)
                    print(cmd)
                    run_shell_cmd(cmd)
                    if not os.listdir(tmpDir):
                        print('SUCCESS!!!')
                else:
                    cmd = 'dcm2bids -d %s -p %s -s %s -c %s -o %s'\
                    %(dcmName, pFlag, sFlag, cFlag, oFlag)
                    #print('running %s'%dcmName)
                    print(cmd)
                    run_shell_cmd(cmd)
                    if not os.listdir(tmpDir):
                        print('SUCCESS!!!')
