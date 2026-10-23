#!/usr/bin/env python3
import json
import os
from glob import glob
import argparse
import numpy
import subprocess

"""
This script is designed to determine which field maps apply to discrete fMRI scans
Author - Timothy J Hendrickson
"""
parser = argparse.ArgumentParser()

parser.add_argument("--ses", help="path/to/bids/subj/ses")
#parser.add_argument("--noise", type=str, help="number of noise vols (typically 3")

args = parser.parse_args()

try:
    if args.ses:
        subject_path = args.ses
        try:
            os.path.isabs(subject_path)
        except:
            print('I wont work without a full path')
except:
    print('I need a directory!')

    
#%%    
def setup(subject_path):
	if "ses" in os.listdir(subject_path)[0]:
		for item in (os.listdir(subject_path)):
			session_path = subject_path + '/'+ item
			IntendedFor(session_path)
	IntendedFor(subject_path)

def IntendedFor(data_path):
    func_all = sorted(glob(data_path+'/func/*bold.json'))
    for fmap in sorted(glob(data_path+'/fmap/*.json')):
        # change fmap file permissions to allow write access
        #os.system("chmod 660 " + fmap)
        with open(fmap, 'r') as f:
            fmap_json = json.load(f)
            f.close()
        if "IntendedFor" in fmap_json:
            del fmap_json["IntendedFor"]
        shim_fmap = fmap_json["ShimSetting"]
        #print(fmap, shim_fmap)
        #patient_pos_fmap = fmap_json["ImageOrientationPatientDICOM"]
        #acquisition_time_fmap = fmap_json["AcquisitionTime"]
        func_list = []
        mismatch_list = []
        for func in sorted(glob(data_path+'/func/*bold.json')):
            with open(func, 'r') as g:
                func_json = json.load(g)
                shim_func = func_json["ShimSetting"]
                #patient_pos_func = func_json["ImageOrientationPatientDICOM"]
                #acquisition_time_func = func_json["AcquisitionTime"]
                g.close()
            if shim_fmap == shim_func:
                #print('matched ' + os.path.split(func)[1])
                if func in func_all:
                    func_all.remove(func)
                    #print(func_all)
                func_nii = glob(data_path+'/func/' +func.split('/')[-1].split('.')[0]+".nii*")[0]
                if "ses" in data_path:
                    func_nii = "/".join(func_nii.split("/")[-3:])
                    func_list.append(func_nii)
                else:
                    func_nii = "/".join(func_nii.split("/")[-2:])
                    func_list.append(func_nii)
            else:
                print('ERROR!!! no match for ' + os.path.split(func)[1])
                print('filling out fmaps anyway...')
                if func in func_all:
                    func_all.remove(func)
                    #print(func_all)
                func_nii = glob(data_path+'/func/' +func.split('/')[-1].split('.')[0]+".nii*")[0]
                if "ses" in data_path:
                    func_nii = "/".join(func_nii.split("/")[-3:])
                    mismatch_list.append(func_nii)
                else:
                    func_nii = "/".join(func_nii.split("/")[-2:])
                    mismatch_list.append(func_nii)
                
        print(func_list)
        print(mismatch_list)
        all_nii = func_list+mismatch_list
        entry = {"IntendedFor": func_list}
        fmap_json.update(entry)
        with open(fmap, 'w') as f:
            json.dump(fmap_json, f, indent = 4)
            #print(fmap_json)
            f.close()
        if len(func_all) == 0:
            'all func volumes matched'
        else:
            print('there was an ERROR')
            #for i in func_all:
            #    print(i)
        # change file permissions to read only
        #os.system("chmod 444 " + fmap)
        
setup(subject_path)