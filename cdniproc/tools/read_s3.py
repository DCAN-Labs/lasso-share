#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 13:55:14 2024

@author: kweldon
"""

import os,glob

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return

#%%

mainDir = '/projects/standard/smnelson/shared/projects/subPop/'
miniDicomDir = os.path.join(mainDir,'mini_dicoms/')
get_minidicoms = '/projects/standard/faird/shared/code/internal/utilities/MSI-utilities/s3_get_last_dicoms/s3_get_last_dicoms.sh'
#mainDir = os.getcwd()
filepath = os.path.join(mainDir,'s3list.txt')
s3_list = []
if os.path.exists(filepath):
    print(filepath)

with open(filepath, 'r') as f:
    for line in f:
        line = line.strip()
        #dicomDir = line.split("/")
        dicomDir = line
        print(dicomDir)
        s3_list.append(dicomDir)
    f.close()

minidicom_list = glob.glob(os.path.join(miniDicomDir,'*/'))

for dicomDir in s3_list:
    s3dir = dicomDir.split("/")[4]
    for minidicom in minidicom_list:
        if s3dir in minidicom:
            print('found!!!!!', s3dir)
    else:
        output = os.path.join(miniDicomDir,s3dir)
        cmd = 'source %s -i %s -o %s'%(get_minidicoms,dicomDir,output)
        print(output)
        run_shell_cmd(cmd)
    
    

        