#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 09:50:24 2023

@author: kweldon

Notes: 
    ds.private_creators(0x0021) returns private creator


"""

import os, argparse
from pydicom import dcmread
import glob
#import gdcm
#import nibabel.nicom.csareader as csareader

print(os.path.realpath('.'))

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return 

#%%    
parser = argparse.ArgumentParser()
#parser.add_argument("-f", "--file", help="Dicom file")
parser.add_argument("-d", "--directory", help="Dicom dir")
parser.add_argument("-e", "--element", help="Dicom file")
args = parser.parse_args()

#file = args.file
dicom_dir = args.directory
mainDir = os.getcwd()
element = args.element
#path = os.path.join(mainDir,file)
#file = 'MR-SE006-t1_mp2rage_sag_p3_0.70mm_INV1/MR-ST001-SE006-0001.dcm'
#path = '/projects/standard/bart/shared/projects/7Tpiloting/anat_testing/dicoms/s20231214_7T'
#path = '/projects/standard/smnelson/shared/projects/subPop/dicoms/1009401-ses2/MR-SE019-rest_ep2d_bold_4ME_16MIN_16bit_maton/MR-ST076-SE019-2200.dcm'
#%%
#print('mainDir: ', mainDir)
#print('file: ', file)
#print('path: ', path)

dicom_dir_path = os.path.join(mainDir,dicom_dir)

#%% scraps

if os.path.exists(dicom_dir_path):
    print('Raw data dir: ', dicom_dir_path)
    dicom_dir_contents = glob.glob(os.path.join(dicom_dir_path,'*','*.dcm'))
    dicom_dir_contents.sort()
    for dcm in dicom_dir_contents:
        print(dcm)
        ds = dcmread(dcm,force=True)
        tag = ds['%s'%element]
        
        new_name = tag.value.replace('[','')
        new_name = new_name.replace(']','')
        print('****old name****: ', tag.value)
        print('****new name****: ', new_name)
        
        tag.value = new_name
        print(ds['%s'%element].value)
        ds.save_as(dcm, write_like_original=False)
        
else:
    print('%s does not exist')%dicom_dir_path



#%% scraps
