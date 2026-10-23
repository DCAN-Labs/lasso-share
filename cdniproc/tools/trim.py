#!/usr/bin/env python3

import os
import glob
import argparse
import subprocess as sub
import pandas as pd
import numpy as np
"""
This script is designed to run nordic with one input: csv file
"""
def run_shell_cmd(cmd):
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return

#%%
parser = argparse.ArgumentParser()

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fileToParse", help="the .csv")
parser.add_argument("-d", "--derivativesDir", help="bids derivatives folder")

args = parser.parse_args()
if args.fileToParse:
    filename = args.fileToParse
else:
    print('I need a config file so I know how much to trim!')

if args.derivativesDir:
    derivativesDir = args.derivativesDir
else:
    print('I need a config file so I know how much to trim!')
#mainDir = os.getcwd()
bids = os.path.abspath(derivativesDir)
    
#%%
# mainDir = '/projects/standard/faird/shared/projects/turing/kw/'
# bids = os.path.join(mainDir)
# #bids = os.path.join(mainDir,'sub-1008101')
# #dicoms = 'human-mbme-test-dataset'
# #sbatch = '/projects/standard/darro015/shared/projects/recode/kw/code/nordicsbatch_dev.sh'
# #lowsbatch = '/projects/standard/faird/shared/code/internal/utilities/bids_nordic_wrapper/genericsbatch_low_resources.sh'
# #sbatch = '/projects/standard/faird/shared/code/internal/utilities/bids_nordic_wrapper/nordicsbatch.sh'
# #dicomPath = os.path.join(mainDir,dicoms)
# filename = mainDir + '1008101-ses1.csv'#read in csv to dataframe
# #funcDir = os.path.join(mainDir,'bids/sub-human-mbme-test-dataset/ses-1/func')

#%%        
df = pd.read_csv(filename)
#get rid of nans
df = df.replace(np.nan, '', regex=True)
    
mag_paths = []
phase_paths = []

empty = ['']
labeled = df[['SubID','Session','label','PEdir','nTRs','AcqNumber','ExpectedTRs',\
              'complete','noise','runNum','MP','nEc']][~df['label'].isin(empty)]
print(labeled)
notFunc = ['T1w','T2w','dwi','fmap','physio','QALAS','']
notPH = ['P']
funcOnly = labeled[['SubID','Session','label','PEdir','nTRs','AcqNumber','ExpectedTRs','complete','noise','runNum','MP','nEc']][~df['MP'].isin(notPH)][~df['label'].isin(notFunc)]
newDict = funcOnly.T.to_dict()
dicomList = []
for i in newDict:
    dicomList.append(newDict[i])
#print(newDict)
#%%
anotherDict = []
for i,nii in enumerate(dicomList):
    #print(nii)
    if '-' in str(nii['SubID']):
        subID2 = ''
        subID = 'sub-'+ str(nii['SubID'])
    else:
        subID2 = 'sub-'+ str(nii['SubID']) + '_'
        subID = 'sub-'+ str(nii['SubID'])
    noise = int(nii['noise'])
    AcqNumber = int(nii['AcqNumber'])
    ses = nii['Session']
    task = nii['label']
    echo = int(nii['nEc'])
    funcDir = os.path.join(bids,'%s','ses-%s','func/')%(subID,ses)
    print(funcDir)

    for i in range(echo):
        run = int(nii['runNum'])
        if run < 10:
            run = '0' + str(run)
        else:
            run = str(run)
        dictionary = {
              'magFile': '',
              'trimHeader': '',
              'magHeader': '',
              'totalVols': '',
              'noiseVols': '',
              }
        dictionary['totalVols'] = AcqNumber
        dictionary['noiseVols'] = noise
     
        echo = i + 1
        
        if nii['MP'] == 'M':
            magHeader = subID2 + 'ses-' + str(ses) + '_task-' + task + 'ME' + '_run-' + run + '_echo-' + str(echo) + '_bold'
            #phaseHeader = subID2 + 'ses-' + str(ses) + '_task-' + task + 'MEph' + '_run-' + run + '_echo-' + str(echo) + '_bold'
            trimHeader = subID2 + 'ses-' + str(ses) + '_task-' + task + 'MEt' + '_run-' + run + '_echo-' + str(echo) + '_bold'
            jsonHeader = subID2 + 'ses-' + str(ses) + '_task-' + task + 'ME' + '_run-' + run + '_echo-' + str(echo) + '_bold'
            jsonTrimHeader = subID2 + 'ses-' + str(ses) + '_task-' + task + 'MEt' + '_run-' + run + '_echo-' + str(echo) + '_bold'
            
            dictionary['jsonHeader'] = jsonHeader
            dictionary['jsonTrimHeader'] = jsonTrimHeader
            dictionary['trimHeader'] = trimHeader
            dictionary['magHeader'] = magHeader
            #dictionary['phaseHeader'] = phaseHeader
            magName = magHeader + '.nii.gz'
            if os.path.exists(os.path.join(funcDir,magName)): # and os.path.exists(os.path.join(funcDir,phName)):
                    anotherDict.append(dictionary)
            else:
                print(os.path.join(funcDir,magName))
                print('magName does not exist')

#print(anotherDict)

#%%
cmd_list = []
cmd_list2 = []
for m,mag in enumerate(anotherDict):
    magFile = anotherDict[m]['magHeader'] + '.nii.gz'
    magFilePath = os.path.join(funcDir,magFile)
    trimFile = anotherDict[m]['trimHeader'] + '.nii.gz'
    trimFilePath = os.path.join(funcDir,trimFile)

    noiseVols = anotherDict[m]['noiseVols']
    totalVols = anotherDict[m]['totalVols']
    keepVols = totalVols - noiseVols
    zero = 0
    if os.path.exists(magFilePath):
        pass
    else:
        print('file %s does not exist'%magFilePath)
    if totalVols == keepVols:
        print('no trimming needed, copying instead')
        cmd = 'cp %s %s'%(magFilePath,trimFilePath)
    else:
        cmd = 'fslroi %s %s %d %d'%(magFilePath,trimFilePath,zero,keepVols)
    cmd_list.append(cmd)
    #also rename json
for m,mag in enumerate(anotherDict):
    jsonFile = anotherDict[m]['jsonHeader'] +'.json'
    jsonTrimFile = anotherDict[m]['jsonTrimHeader'] +'.json'
    jsonFilePath = os.path.join(funcDir,jsonFile)
    jsonTrimFilePath = os.path.join(funcDir,jsonTrimFile)
    
    cmd = 'mv %s %s'%(jsonFilePath,jsonTrimFilePath)
    if not os.path.exists(jsonTrimFilePath):
        cmd_list.append(cmd)
        
for cmd in cmd_list:
    print(cmd)
    run_shell_cmd(cmd)
    