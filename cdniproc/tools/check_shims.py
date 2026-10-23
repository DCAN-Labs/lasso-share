#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:36:57 2022

@author: kweldon
"""

"""
INTENDED FOR PARTICIPANTS > 1 YR

"""
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
mainDir = '/projects/standard/nardosr/shared/projects/sandbox/'
#subID = '1000101'
#sess = '1'
#filename = os.path.join(mainDir,'summaries',subID + '-ses' + sess + '.tsv')
bids = 'derivatives/nordic'
#%%

# parser = argparse.ArgumentParser()
# argcomplete.autocomplete(parser)

# parser.add_argument("-f", "--fileToParse", type=str, help="the .tsv")
# parser.add_argument("-b", "--bidsDirectory" type=str, help="bids directory to check")

# args = parser.parse_args()
# if args.fileToParse:
#     filename = args.fileToParse
# else:
#     print('I need a config file if you want to run dcm2bids on a dataset!')

#%%
filename = os.path.join(mainDir, 'check_shims.txt')
bids_path = os.path.join(mainDir, bids)
sub_list = sorted(glob.glob(os.path.join(bids_path,'*')))

if os.path.exists(filename):
    os.remove(filename)
for sub in sub_list: 
    subID = os.path.split(sub)[1].split('-')[1]
    session_list = sorted(glob.glob(os.path.join(sub,'*')))
    for session in session_list:
        session_path = session
    
        
    #if "ses" in filename:
        #subID = os.path.split(filename)[1].split('-')[0]
        #sessionNum = os.path.split(filename)[1].split('-')[1].split('.')[0][3:]
        #session_path = os.path.join(mainDir, 'derivatives/nordic/', 'sub-' + subID, 'ses-' + sessionNum)
        sessionNum = os.path.split(session)[1]
        #df_info = pd.DataFrame()
        #df = pd.read_csv(filename,sep='\t',header=0)
        #print('reading from ... ', session)
        #get rid of nans
        #df = df.replace(np.nan, '', regex=True)
        #df['ShimSetting'] = ''
        
        
        func_list = sorted(glob.glob(os.path.join(session_path, 'func/*bold.json')))
        func_list = func_list * 2
        match_list = []
        orphan_list = []
        for fmap in sorted(glob.glob(os.path.join(session_path,'fmap/*.json'))):
            #change fmap file permissions to allow write access
            #os.system("chmod 660 " + fmap)
            with open(fmap, 'r') as f:
                fmap_json = json.load(f)
                f.close()
            shim_fmap = fmap_json["ShimSetting"]
            #print(os.path.split(fmap)[1])
            #print(shim_fmap)
            for func in sorted(glob.glob(os.path.join(session_path, 'func/*bold.json'))):
                with open(func, 'r') as g:
                    func_json = json.load(g)
                    shim_func = func_json["ShimSetting"]
                    #patient_pos_func = func_json["ImageOrientationPatientDICOM"]
                    #acquisition_time_func = func_json["AcquisitionTime"]
                    g.close()
                if shim_fmap == shim_func:
                    match_list.append(func)
                else:
                    orphan_list.append(func)
                    
        unique_to_orphan = list(set(orphan_list) - set(match_list))
        unique_to_orphan.sort()

        if len(unique_to_orphan) == 0:
            pass
            print('all func matched in ' + subID + sessionNum)
        else:
            for item in unique_to_orphan:
                print(item)
                #print("orphan func files:", unique_to_orphan)
                  
    
        #print('writing....',filename)
        with open(filename, "a") as outfile:
            if len(unique_to_orphan) == 0:                
                outfile.write('all func matched in ' + subID + sessionNum + '\n')
            else:
                for item in unique_to_orphan:
                    outfile.write(item + '\n')
outfile.close()
