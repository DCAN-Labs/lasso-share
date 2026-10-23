#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 19:32:12 2024

@author: kweldon
"""
import os
import argparse
import json
import pandas as pd

def intersection(lst1, lst2):
    lst3 = [value for value in lst2 if value in lst1]
    return lst3

tagstodrop = ['SeriesInstanceUID',
        'StudyInstanceUID',
        'ReferringPhysicianName',
        'StudyID',
        'PatientName',
        'PatientID',
        'AccessionNumber',
        'PatientBirthDate',
        'PatientWeight',
        'AcquisitionDateTime',
        'DeviceSerialNumber',
        'StationName',
        'SoftwareVersions',
        'ManufacturersModelName',
        'InstitutionName',
        'InstitutionalDepartmentName',
        'InstitutionAddress',
        'DeviceSerialNumber',
        'StationName',
        'PatientPosition',
        'ProcedureStepDescription',
        'SoftwareVersions',
        'SeriesDescription',
        'ProtocolName',
        'ScanningSequence',
        'SequenceVariant',
        'ScanOptions',
        'SequenceName',
        'ImageType',
        'AcquisitionNumber',
        ]

# %%
parser = argparse.ArgumentParser()
#parser.add_argument("-f", action='store_true', help="json file")
parser.add_argument("-f", help="file")
args = parser.parse_args()
file = args.f
mainDir = os.getcwd()
path = os.path.join(mainDir,file)

print(file)


# %%
#path = '/home/faird/kweldon/scratch/analysis/MBME_TEST/outdir/MR-SE011-ABCD_T1w_MPR_vNav_ABCD_T1w_MPR_vNav_20240130103136_11.json'
#
# %%
with open(path) as f:
    d = json.load(f)
    
keylist = []
valuelist = []
for key, value in d.items(): 
    keylist.append(key)
    if type(value)==str:
        valuelist.append(value)
    else:
        valuelist.append(str(value))

data = dict(zip(keylist, valuelist))
#types1 = [type(k) for k in data.values()]
df = pd.DataFrame(data, index=[0])
drop = intersection(keylist, tagstodrop)
df = df.drop(columns=drop)

#convert df to json
newDict = df.T.to_dict()
dicomList = []
for i in newDict:
    print(newDict[i])
    dicomList.append(newDict[i])

# #save out anonymized json
jsonString = json.dumps(newDict[0], indent=4)
print('writing....test.json')
with open('test.json', "w") as outfile:
    outfile.write(jsonString)
    outfile.write('\n')
outfile.close()