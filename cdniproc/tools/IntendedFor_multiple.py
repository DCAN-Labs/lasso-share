#!/usr/bin/env python3
import json
import os
from glob import glob
import argparse

"""
This script is designed to determine which field maps apply to discrete fMRI scans
Author - Timothy J Hendrickson - Modified by Bene and rae to include multiple fmaps in the same session 
"""

parser = argparse.ArgumentParser()
parser.add_argument("--ses", help="path/to/bids/subj/ses")

args = parser.parse_args()

try:
    if args.ses:
        subject_path = args.ses
        try:
            if not os.path.isabs(subject_path):
                raise ValueError("I won't work without a full path")
        except ValueError as e:
            print(e)
            exit(1)
except Exception as e:
    print('I need a directory!')
    exit(1)

def setup(subject_path):
    if "ses" in os.listdir(subject_path)[0]:
        for item in os.listdir(subject_path):
            session_path = os.path.join(subject_path, item)
            IntendedFor(session_path)
    else:
        IntendedFor(subject_path)

def IntendedFor(data_path):
    fmap_files = sorted(glob(data_path + '/fmap/*.json'))
    func_files = sorted(glob(data_path + '/func/*bold.json'))

    # Group func files by ShimSetting
    func_groups = {}
    for func in func_files:
        with open(func, 'r') as g:
            func_json = json.load(g)
            shim_func = tuple(func_json["ShimSetting"])  # Convert ShimSetting to a tuple
            if shim_func not in func_groups:
                func_groups[shim_func] = []
            func_groups[shim_func].append((func, func_json))
    
    assigned_funcs = set()
    current_fmap_idx = 0
    
    for fmap in fmap_files:
        with open(fmap, 'r') as f:
            fmap_json = json.load(f)
        
        if "IntendedFor" in fmap_json:
            del fmap_json["IntendedFor"]
        
        shim_fmap = tuple(fmap_json["ShimSetting"])  # Convert ShimSetting to a tuple
        series_fmap = fmap_json["SeriesNumber"]
        time_fmap = fmap_json["AcquisitionTime"]
        dir_label = fmap_json.get("PhaseEncodingDirection", "")  # Get direction label (dir-AP, dir-PA)

        func_list = []
        if shim_fmap in func_groups:
            funcs = func_groups[shim_fmap]
            for func, func_json in funcs:
                if (func, dir_label) in assigned_funcs:
                    continue

                series_func = func_json["SeriesNumber"]
                time_func = func_json["AcquisitionTime"]

                # Check SeriesNumber and AcquisitionTime within the same ShimSetting
                if current_fmap_idx + 1 < len(fmap_files):
                    next_fmap_json = json.load(open(fmap_files[current_fmap_idx + 1], 'r'))
                    next_shim_fmap = tuple(next_fmap_json["ShimSetting"])  # Convert ShimSetting to a tuple
                    series_next_fmap = next_fmap_json["SeriesNumber"]
                    time_next_fmap = next_fmap_json["AcquisitionTime"]
                    next_dir_label = next_fmap_json.get("PhaseEncodingDirection", "")  # Get next direction label

                    # Ensure we only add funcs that belong to the current fmap by SeriesNumber and AcquisitionTime
                    if next_shim_fmap == shim_fmap and next_dir_label == dir_label and series_func >= series_next_fmap and time_func >= time_next_fmap:
                        break

                func_nii = glob(data_path + '/func/' + func.split('/')[-1].split('.')[0] + ".nii*")[0]
                if "ses" in data_path:
                    func_nii = "/".join(func_nii.split("/")[-3:])
                else:
                    func_nii = "/".join(func_nii.split("/")[-2:])
                func_list.append(func_nii)
                assigned_funcs.add((func, dir_label))  # Mark this func and direction as assigned
        
        fmap_json["IntendedFor"] = func_list
        with open(fmap, 'w') as f:
            json.dump(fmap_json, f, indent=4)
        
        current_fmap_idx += 1

setup(subject_path)


#almost works, does the run 1 through 5 for first fmap 
# #!/usr/bin/env python3
# import json
# import os
# from glob import glob
# import argparse

# """
# This script is designed to determine which field maps apply to discrete fMRI scans
# Author - Timothy J Hendrickson - Modified by Bene to include multiple fmaps in the same session
# """

# parser = argparse.ArgumentParser()
# parser.add_argument("--ses", help="path/to/bids/subj/ses")

# args = parser.parse_args()

# try:
#     if args.ses:
#         subject_path = args.ses
#         try:
#             if not os.path.isabs(subject_path):
#                 raise ValueError("I won't work without a full path")
#         except ValueError as e:
#             print(e)
#             exit(1)
# except Exception as e:
#     print('I need a directory!')
#     exit(1)

# def setup(subject_path):
#     if "ses" in os.listdir(subject_path)[0]:
#         for item in os.listdir(subject_path):
#             session_path = os.path.join(subject_path, item)
#             IntendedFor(session_path)
#     else:
#         IntendedFor(subject_path)

# def IntendedFor(data_path):
#     fmap_files = sorted(glob(data_path + '/fmap/*.json'))
#     func_files = sorted(glob(data_path + '/func/*bold.json'))

#     # Group func files by ShimSetting
#     func_groups = {}
#     for func in func_files:
#         with open(func, 'r') as g:
#             func_json = json.load(g)
#             shim_func = tuple(func_json["ShimSetting"])  # Convert ShimSetting to a tuple
#             if shim_func not in func_groups:
#                 func_groups[shim_func] = []
#             func_groups[shim_func].append((func, func_json))
    
#     current_fmap_idx = 0
    
#     for fmap in fmap_files:
#         with open(fmap, 'r') as f:
#             fmap_json = json.load(f)
        
#         if "IntendedFor" in fmap_json:
#             del fmap_json["IntendedFor"]
        
#         shim_fmap = tuple(fmap_json["ShimSetting"])  # Convert ShimSetting to a tuple
#         series_fmap = fmap_json["SeriesNumber"]
#         time_fmap = fmap_json["AcquisitionTime"]
#         modality = fmap_json.get("Modality", "")  # Get modality if it exists
#         dir_label = fmap_json.get("PhaseEncodingDirection", "")  # Get direction label (dir-AP, dir-PA)

#         func_list = []
#         if shim_fmap in func_groups:
#             funcs = func_groups[shim_fmap]
#             for func, func_json in funcs:
#                 series_func = func_json["SeriesNumber"]
#                 time_func = func_json["AcquisitionTime"]

#                 # Check SeriesNumber and AcquisitionTime within the same ShimSetting
#                 if current_fmap_idx + 1 < len(fmap_files):
#                     next_fmap_json = json.load(open(fmap_files[current_fmap_idx + 1], 'r'))
#                     next_shim_fmap = tuple(next_fmap_json["ShimSetting"])  # Convert ShimSetting to a tuple
#                     series_next_fmap = next_fmap_json["SeriesNumber"]
#                     time_next_fmap = next_fmap_json["AcquisitionTime"]
#                     next_modality = next_fmap_json.get("Modality", "")  # Get next modality if it exists
#                     next_dir_label = next_fmap_json.get("PhaseEncodingDirection", "")  # Get next direction label

#                     # Ensure we only add funcs that belong to the current fmap by SeriesNumber and AcquisitionTime
#                     if next_shim_fmap == shim_fmap and next_dir_label == dir_label and series_func >= series_next_fmap and time_func >= time_next_fmap:
#                         break

#                 func_nii = glob(data_path + '/func/' + func.split('/')[-1].split('.')[0] + ".nii*")[0]
#                 if "ses" in data_path:
#                     func_nii = "/".join(func_nii.split("/")[-3:])
#                 else:
#                     func_nii = "/".join(func_nii.split("/")[-2:])
#                 func_list.append(func_nii)
        
#         fmap_json["IntendedFor"] = func_list
#         with open(fmap, 'w') as f:
#             json.dump(fmap_json, f, indent=4)
        
#         current_fmap_idx += 1

# setup(subject_path)

# ## works but only does it for dir-AP not dir-PA
# #!/usr/bin/env python3
# import json
# import os
# from glob import glob
# import argparse

# """
# This script is designed to determine which field maps apply to discrete fMRI scans
# Author - Timothy J Hendrickson
# """

# parser = argparse.ArgumentParser()
# parser.add_argument("--ses", help="path/to/bids/subj/ses")

# args = parser.parse_args()

# try:
#     if args.ses:
#         subject_path = args.ses
#         try:
#             if not os.path.isabs(subject_path):
#                 raise ValueError("I won't work without a full path")
#         except ValueError as e:
#             print(e)
#             exit(1)
# except Exception as e:
#     print('I need a directory!')
#     exit(1)

# def setup(subject_path):
#     if "ses" in os.listdir(subject_path)[0]:
#         for item in os.listdir(subject_path):
#             session_path = os.path.join(subject_path, item)
#             IntendedFor(session_path)
#     else:
#         IntendedFor(subject_path)

# def IntendedFor(data_path):
#     fmap_files = sorted(glob(data_path + '/fmap/*.json'))
#     func_files = sorted(glob(data_path + '/func/*bold.json'))
    
#     # Group func files by ShimSetting
#     func_groups = {}
#     for func in func_files:
#         with open(func, 'r') as g:
#             func_json = json.load(g)
#             shim_func = tuple(func_json["ShimSetting"])  # Convert ShimSetting to a tuple
#             if shim_func not in func_groups:
#                 func_groups[shim_func] = []
#             func_groups[shim_func].append((func, func_json))
    
#     assigned_funcs = set()
#     current_fmap_idx = 0
    
#     for fmap in fmap_files:
#         with open(fmap, 'r') as f:
#             fmap_json = json.load(f)
        
#         if "IntendedFor" in fmap_json:
#             del fmap_json["IntendedFor"]
        
#         shim_fmap = tuple(fmap_json["ShimSetting"])  # Convert ShimSetting to a tuple
#         series_fmap = fmap_json["SeriesNumber"]
#         time_fmap = fmap_json["AcquisitionTime"]

#         func_list = []
#         if shim_fmap in func_groups:
#             funcs = func_groups[shim_fmap]
#             for func, func_json in funcs:
#                 if func in assigned_funcs:
#                     continue

#                 series_func = func_json["SeriesNumber"]
#                 time_func = func_json["AcquisitionTime"]

#                 # Check SeriesNumber and AcquisitionTime within the same ShimSetting
#                 if current_fmap_idx + 1 < len(fmap_files):
#                     next_fmap_json = json.load(open(fmap_files[current_fmap_idx + 1], 'r'))
#                     next_shim_fmap = tuple(next_fmap_json["ShimSetting"])  # Convert ShimSetting to a tuple
#                     series_next_fmap = next_fmap_json["SeriesNumber"]
#                     time_next_fmap = next_fmap_json["AcquisitionTime"]

#                     # Ensure we only add funcs that belong to the current fmap by SeriesNumber and AcquisitionTime
#                     if next_shim_fmap == shim_fmap and series_func >= series_next_fmap and time_func >= time_next_fmap:
#                         break

#                 func_nii = glob(data_path + '/func/' + func.split('/')[-1].split('.')[0] + ".nii*")[0]
#                 if "ses" in data_path:
#                     func_nii = "/".join(func_nii.split("/")[-3:])
#                 else:
#                     func_nii = "/".join(func_nii.split("/")[-2:])
#                 func_list.append(func_nii)
#                 assigned_funcs.add(func)  # Mark this func as assigned
        
#         fmap_json["IntendedFor"] = func_list
#         with open(fmap, 'w') as f:
#             json.dump(fmap_json, f, indent=4)
        
#         current_fmap_idx += 1

# setup(subject_path)


## this version almost worked, just didn't acount for the fact that acquisition time and series number could be different in cases of different sessions combined into one. 
# #!/usr/bin/env python3
# import json
# import os
# from glob import glob
# import argparse

# """
# This script is designed to determine which field maps apply to discrete fMRI scans
# Author - Timothy J Hendrickson
# """

# parser = argparse.ArgumentParser()
# parser.add_argument("--ses", help="path/to/bids/subj/ses")

# args = parser.parse_args()

# try:
#     if args.ses:
#         subject_path = args.ses
#         try:
#             if not os.path.isabs(subject_path):
#                 raise ValueError("I won't work without a full path")
#         except ValueError as e:
#             print(e)
#             exit(1)
# except Exception as e:
#     print('I need a directory!')
#     exit(1)

# def setup(subject_path):
#     if "ses" in os.listdir(subject_path)[0]:
#         for item in os.listdir(subject_path):
#             session_path = os.path.join(subject_path, item)
#             IntendedFor(session_path)
#     else:
#         IntendedFor(subject_path)

# def IntendedFor(data_path):
#     fmap_files = sorted(glob(data_path + '/fmap/*.json'))
#     func_files = sorted(glob(data_path + '/func/*bold.json'))

#     assigned_funcs = set()
#     current_fmap_idx = 0

#     for fmap in fmap_files:
#         with open(fmap, 'r') as f:
#             fmap_json = json.load(f)
        
#         if "IntendedFor" in fmap_json:
#             del fmap_json["IntendedFor"]
        
#         shim_fmap = fmap_json["ShimSetting"]
#         series_fmap = fmap_json["SeriesNumber"]
#         time_fmap = fmap_json["AcquisitionTime"]

#         func_list = []
#         for func in func_files:
#             if func in assigned_funcs:
#                 continue

#             with open(func, 'r') as g:
#                 func_json = json.load(g)
#                 shim_func = func_json["ShimSetting"]
#                 series_func = func_json["SeriesNumber"]
#                 time_func = func_json["AcquisitionTime"]
            
#             # Check ShimSetting first, then SeriesNumber, then AcquisitionTime
#             if shim_fmap == shim_func:
#                 if current_fmap_idx + 1 < len(fmap_files):
#                     next_fmap_json = json.load(open(fmap_files[current_fmap_idx + 1], 'r'))
#                     series_next_fmap = next_fmap_json["SeriesNumber"]
#                     time_next_fmap = next_fmap_json["AcquisitionTime"]

#                     if series_func >= series_next_fmap and time_func >= time_next_fmap:
#                         break

#                 func_nii = glob(data_path + '/func/' + func.split('/')[-1].split('.')[0] + ".nii*")[0]
#                 if "ses" in data_path:
#                     func_nii = "/".join(func_nii.split("/")[-3:])
#                 else:
#                     func_nii = "/".join(func_nii.split("/")[-2:])
#                 func_list.append(func_nii)
#                 assigned_funcs.add(func)  # Mark this func as assigned
        
#         fmap_json["IntendedFor"] = func_list
#         with open(fmap, 'w') as f:
#             json.dump(fmap_json, f, indent=4)
        
#         current_fmap_idx += 1

# setup(subject_path)




# #!/usr/bin/env python3
# import json
# import os
# from glob import glob
# import argparse

# """
# This script is designed to determine which field maps apply to discrete fMRI scans
# Author - Timothy J Hendrickson
# """

# parser = argparse.ArgumentParser()
# parser.add_argument("--ses", help="path/to/bids/subj/ses")

# args = parser.parse_args()

# try:
#     if args.ses:
#         subject_path = args.ses
#         try:
#             if not os.path.isabs(subject_path):
#                 raise ValueError("I won't work without a full path")
#         except:
#             print('I need a directory!')
# except:
#     print('I need a directory!')

# def setup(subject_path):
#     if "ses" in os.listdir(subject_path)[0]:
#         for item in (os.listdir(subject_path)):
#             session_path = subject_path + '/' + item
#             IntendedFor(session_path)
#     IntendedFor(subject_path)

# def IntendedFor(data_path):
#     fmap_files = sorted(glob(data_path+'/fmap/*.json'))
#     func_files = sorted(glob(data_path+'/func/*bold.json'))
    
#     for fmap in fmap_files:
#         with open(fmap, 'r') as f:
#             fmap_json = json.load(f)
        
#         if "IntendedFor" in fmap_json:
#             del fmap_json["IntendedFor"]
        
#         shim_fmap = fmap_json["ShimSetting"]
#         series_fmap = fmap_json["SeriesNumber"]
#         time_fmap = fmap_json["AcquisitionTime"]

#         func_list = []
#         for func in func_files:
#             with open(func, 'r') as g:
#                 func_json = json.load(g)
#                 shim_func = func_json["ShimSetting"]
#                 series_func = func_json["SeriesNumber"]
#                 time_func = func_json["AcquisitionTime"]
            
#             # Check ShimSetting first, then SeriesNumber, then AcquisitionTime
#             if shim_fmap == shim_func:
#                 if series_fmap <= series_func:
#                     if time_fmap <= time_func:
#                         func_nii = glob(data_path+'/func/' + func.split('/')[-1].split('.')[0] + ".nii*")[0]
#                         if "ses" in data_path:
#                             func_nii = "/".join(func_nii.split("/")[-3:])
#                         else:
#                             func_nii = "/".join(func_nii.split("/")[-2:])
#                         func_list.append(func_nii)
        
#         fmap_json["IntendedFor"] = func_list
#         with open(fmap, 'w') as f:
#             json.dump(fmap_json, f, indent=4)

# setup(subject_path)
