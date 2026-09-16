#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  8 16:46:58 2025

@author: kweldon
"""

import argparse,json
import pandas as pd
import numpy as np
from pathlib import Path

parser = argparse.ArgumentParser(description="Convert JSONs to TSV.")
parser.add_argument("input_file", type=Path, help=".tsv file")

args = parser.parse_args()
filename = args.input_file.resolve()
jsonfilename = filename.with_suffix('.json')

df = pd.read_csv(filename,sep='\t',header=0)
print('reading from ... ', filename)
#get rid of nans
df = df.replace(np.nan, '', regex=True)

# Calculate sequential run number for series sharing the same BIDS keys
df['runNum'] = df.groupby(['label','EchoNumber','MP','PEdir','acq','inv']).cumcount().add(1)
df['runNum'] = np.where(df['label'] != '', df['runNum'], '')

df.to_csv(filename, sep='\t', index=False)

#%%
newDict = df.T.to_dict()
dicomList = []
for i in newDict:
    dicomList.append(newDict[i])

anatList = ["T1w", "T2w", "t1w", "t2w","qalas","QALAS", "mp2rage","unit1"]
fmapList = ["fmap","PErev","revPE", "fi", "fa", "magnitude", "phasediff", \
            'magnitude1', 'magnitude2', 'phase1', 'phase2','fmapDWI']
b1List = ['tb1tfl']

newDict = []
for i,dcm in enumerate(dicomList):
    if len(dcm['label'])>0:
        # Determine total echoes; default to 1 if empty or 0
        try:
            total_echoes = int(float(dcm['EchoNumber'])) if dcm['EchoNumber'] != '' else 1
        except ValueError:
            total_echoes = 1

        # Loop through each individual echo (1-indexed for BIDS)
        for e_idx in range(1, total_echoes + 1):
            bids_label = dcm['label']
            datatype = ''
            suffix = ''
            
            print(bids_label)
            # --- 1. Determine Datatype and Suffix ---
            if bids_label in anatList:
                print("anat")
                if bids_label == 'unit1':
                    suffix = 'UNIT1'
                elif bids_label == 'qalas':
                    suffix = 'QALAS'
                elif bids_label == 'mp2rage':
                    suffix = 'MP2RAGE'
                else:
                    suffix = bids_label.capitalize() # e.g., T1w
                datatype = 'anat'
            elif bids_label in fmapList:
                datatype = 'fmap'
                if bids_label == 'fmapDWI':
                    suffix = 'dwi'
                else:
                    suffix = 'epi'
            elif bids_label == 'dwi':
                datatype = 'dwi'
                suffix = 'dwi'
            elif bids_label in b1List:
                datatype = 'fmap'
                suffix = 'TB1TFL'
            else:
                suffix = 'bold'
                datatype = 'func'
                
            # --- 2. Populate the dictionary ---
            dictionary = {
                'datatype': datatype, 
                'suffix': suffix,
                'custom_entities': '', # This remains a placeholder for now
                'criteria': {
                    'SidecarFilename': str(dcm['filename'])[:3] + '_*', #dcm['filename']'', # Use the original JSON filename
                    'SeriesDescription': dcm['SeriesDescription'],
                    #'ImageTypeText': dcm['ImageTypeText'],
                    "EchoNumber": dcm['EchoNumber']
                }
            }
                
            # --- 3. Add Custom Entities  ---
            temp_entities = {}
            
            #task
            if datatype == 'func':
                temp_entities['task'] = dcm['label']
                
            #acq
            if dcm['acq']:
                temp_entities['acq'] = dcm['acq']
                
            #inv
            if dcm['inv']:
                temp_entities['inv'] = int(dcm['inv'])
                
            #pedir
            if datatype == "fmap" or datatype == 'dwi':
                temp_entities['dir'] = dcm['PEdir']

                        
            #run
            if dcm['runNum']:
                run_value = dcm['runNum']
                
                try:
                    # 1. Safely convert to float first (handles '1' and '1.0')
                    run_float = float(run_value)
                    
                    # 2. Convert to integer (truncating the .0 part: 1.0 -> 1)
                    run_int = int(run_float)
                    
                    # 3. Convert back to string and apply zero-padding (1 -> '01')
                    padded_run_num = str(run_int).zfill(2)
                    
                    temp_entities['run'] = padded_run_num
                    
                except ValueError:
                    # This handles non-numeric strings (e.g., '', 'a', or invalid floats)
                    # If conversion fails, we skip the assignment for the run number
                    pass
                
             
            #echo
            # This checks ImageTypeText first; if missing or empty, it checks ImageType.
            if 'TE' in dcm.get('ImageTypeText', dcm.get('ImageType', '')):
                dictionary['criteria']['EchoNumber'] = e_idx
                if datatype == 'func':
                    temp_entities['echo'] = e_idx
            else:
                dictionary['criteria'].pop('EchoNumber', None)
    
            # if dcm['ImageTypeText']:
            #     if 'TE' in dcm['ImageTypeText']:
            #         dictionary['criteria']['EchoNumber'] = e_idx
            #         if datatype == 'func': #also include echo in bids filename
            #             temp_entities['echo'] = e_idx
            #     else:
            #         del dictionary['criteria']['EchoNumber']
            # else:
            #     if 'TE' in dcm['ImageType']:
            #             dictionary['criteria']['EchoNumber'] = e_idx
            #     if datatype == 'func': #also include echo in bids filename
            #         temp_entities['echo'] = e_idx
            #     else:
            #         del dictionary['criteria']['EchoNumber']
                                 
            #mag/phase
            
            if datatype == 'func' and dcm['MP']:
                if dcm['MP'] == 'M':
                    temp_entities['part'] = 'mag'
                elif dcm['MP']== 'P':
                    temp_entities['part'] = 'phase'
                    
            custom_entity_list = []
            for key, value in temp_entities.items():
                custom_entity_list.append(f'{key}-{value}')
                
            # Join the list with underscores
            concatenated_entity_string = '_'.join(custom_entity_list)
            
            # Assign the resulting string to the dictionary key
            dictionary['custom_entities'] = concatenated_entity_string
            
            try:
                x = dictionary['criteria']['EchoNumber']
            except KeyError:
                newDict.append(dictionary)
            else:
                if dictionary['datatype'] == 'fmap' and dictionary['criteria']['EchoNumber'] > 1:
                    pass
                else:
                    newDict.append(dictionary)
           
        
print(newDict)
jsonString = json.dumps(newDict, indent=4)
print('writing....',jsonfilename)
output_data = {"descriptions": newDict}
with open(jsonfilename, "w") as outfile:
    json.dump(output_data, outfile, indent=4)
outfile.close()
