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
#import argcomplete

def run_shell_cmd(cmd):
    import subprocess as sub
    pipe = sub.Popen(cmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE,close_fds=True)
    o,e = pipe.communicate()
    return


def check_private_tag(ds,element):
    #print('check private tag', element)
    if element == 'ReceiveCoilActiveElements':
        tag1 = "0021, 114F"
        tag2 = "0021,114F"
        lookfor = 'LO: '
    elif element == 'ReceiveCoilName':
        tag1 = "0018, 1250"
        tag2 = "0018,1250"
        lookfor = 'SH: '
    elif element == 'CoilString':
        tag1 = "0051, 100F"
        tag2 = "0051,100F"
        lookfor = 'LO: '
    elif element == "ImageTypeText":
        tag1 = "0021, 1175"
        tag2 = "0021, 1075"
        tag3 = "0021,1175"
        lookfor = '['
        lookfor2 = ']'
    
    string = str(ds)# writing to file
    string = string.split('\n')
    #print(string)
    if element == 'ImageTypeText':
        for line in string:
            if tag1 in line:
                for item in line:
                    if item == lookfor:
                        startIndex = line.index(item)
                    if item == lookfor2:
                        endIndex = line.index(item) + 1
                        value = line[startIndex:endIndex]
                        break
            elif tag2 in line:
                #print('line', line)
                for item in line:
                    if item == lookfor:
                        startIndex = line.index(item)
                        endIndex = line.index(item) + 1
                        value = line[startIndex:]
                        break
            elif tag3 in line:
                #print('line', line)
                for item in line:
                    if item == lookfor:
                        startIndex = line.index(item)
                        endIndex = line.index(item) + 1
                        value = line[startIndex:]
                        break
    else:
        for line in string:
            if tag1 in line: 
                #print('line', line)
                startIndex = line.find(lookfor) + 5
                value = line[startIndex:-1]
                break    
            elif tag2 in line:
                #print('line', line)
                startIndex = line.find(lookfor) + 5
                value = line[startIndex:-1]
                break    
    
    try:
        value
    except:
        value = ''

    #print(value)
    return value


#%%
# mainDir = '/scratch.global/kweldon/subpoptest'
# dicoms = '1019402-ses1'
# dicom_dir = os.path.join(mainDir,'dicoms',dicoms)
# subID = '1019402'
# sess = 1
# bids = 'bids'
# # # heuristic = os.path.join(mainDir,'heuristic.csv')
# h = 0
# jsononly = 0
# coilcheck = 0
#%%

parser = argparse.ArgumentParser()
#argcomplete.autocomplete(parser)

parser.add_argument("-d", "--dicomDir", help="Dicom directory path. Do not include the trailing /")
parser.add_argument("-p", "--participantID", type=str, help="subID")
parser.add_argument("-s", "--sess", type=str, help="session number")
parser.add_argument("--coilcheck", action='store_true', help="do you want me to check coil elements(fragile)")
parser.add_argument("--heuristic", type=str, help="use heuristic")
parser.add_argument("--jsononly", action='store_true', help="remake json from csv")

mainDir = os.getcwd()
print(mainDir)
splitPath = mainDir.split('/')
for i in splitPath:
    try:
        int(i)
        mainDir = '/home' + mainDir[mainDir.index(i)+len(i):]
    except:
        pass

args = parser.parse_args()

if args.participantID:
    subID = args.participantID
else:
    subID = ''
    
if args.sess:
    sess = str(args.sess)
else:
    sess = ''

if args.heuristic:
    h = 1
    #print(args.heuristic)
    heuristic = args.heuristic
else:
    h = 0

try: 
    jsononly = args.jsononly
except:
    jsononly = 0
    
try: 
    coilcheck = args.coilcheck
except:
    coilcheck = 0

bids = 'bids'

discard = ''
dicom_dir = args.dicomDir

#make agnostic to trailing slash on dicomPath
if dicom_dir[-1] == '/':
    dicom_dir = dicom_dir[:-1]

if subID not in dicom_dir.split("/")[-1]:
    raise Exception("subID string needs to match at least part of the dicom directory name.")

#%%
sessName = os.path.split(dicom_dir)[1] + '.tsv'

sessNameHead = os.path.split(dicom_dir)[1]
jsonName = sessNameHead + '.json'

print('Reading from dicom dir: ', dicom_dir)
print('Creating (or overwriting) ', sessName, ' summary in ', mainDir)

filename = os.path.join(mainDir,sessName)
jsonfilename = os.path.join(mainDir,jsonName)

df_info = pd.DataFrame()

#%%
if jsononly:
    pass
else:    
    #figure out which datasets we're working on
    dcmlist = []
    if os.path.exists(dicom_dir):
        print('Raw data dir: ', dicom_dir)
        files = os.listdir(dicom_dir)
        files.sort()
        # first, get a list of directories that actually have dicom files
        for iF in range(len(files)):
            subdir = os.path.join(dicom_dir, files[iF])
            #if "Physio" not in os.path.split(subdir)[1]:
            if os.path.isdir(subdir) and os.path.split(subdir)[1].startswith('MR-SE0') and \
                "Physio" not in os.path.split(subdir)[1]:
                dcm = []
                print(os.path.split(subdir)[1])
                subdir_contents = glob.glob(os.path.join(subdir, '*.dcm'))
                subdir_contents.sort()
                lastDcmPath = subdir_contents[-1]
                lastDcm = os.path.split(subdir_contents[-1])[1]
                ds = dcmread(lastDcmPath)
                
                #get basic elements
                StudyYear = int(ds.StudyDate[:4])
                BirthYear = int(ds.PatientBirthDate[:4])
                subAge = str(StudyYear-BirthYear) + "Y"
                subSex = ds.PatientSex
                software = ds.SoftwareVersions
                dicomRoot = os.path.split(dicom_dir)[1]
                
                #get elements
                if 'XA' in ds.SoftwareVersions:
                    #try:
                    #    ReceiveCoilName = ds.ReceiveCoilName
                    #except:
                    #    ReceiveCoilName = 'none'
                    ReceiveCoilActiveElements = check_private_tag(ds,"ReceiveCoilActiveElements")
                    ReceiveCoilName = check_private_tag(ds, "ReceiveCoilName")
                    ImageTypeText = check_private_tag(ds, "ImageTypeText")
                else:
                    ReceiveCoilActiveElements = check_private_tag(ds,"CoilString")
                    try:
                        ReceiveCoilName = ds.ReceiveCoilName
                    except:
                        ReceiveCoilName = 'none'
                    try:
                        ImageTypeText = ds.ImageTypeText
                    except:
                        try:
                            ImageTypeText = ds.ImageType
                        except:
                            ImageTypeText = ''
                    
                name = files[iF]
                seriesNum = name[5:8] + '*'
                SeriesDescription = ds.SeriesDescription
                nTRs = len(subdir_contents) #OR (0020, 0013) Instance Number ????
                
                try:
                    AcqNumber = ds.AcquisitionNumber
                except:
                    AcqNumber = 0
                try:
                    ExpectedTRs = ds.NumberOfTemporalPositions
                except:
                    ExpectedTRs = 0
                try:
                    ImageType = ds.ImageType
                except:
                    ImageType = ''
                
                dcm.append(str(nTRs))
                dcm.append(str(AcqNumber))
                dcm.append(str(ExpectedTRs))
                dcm.append(str(SeriesDescription))
                dcm.append(str(seriesNum))
                dcm.append(str(name))
                dcm.append(str(ImageType))
                dcm.append(str(ImageTypeText))
                dcm.append(str(ReceiveCoilName))
                dcm.append(str(ReceiveCoilActiveElements))
                dcmlist.append(dcm)
    
    #%%# convert the list into dataframe row
    #warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    df = pd.DataFrame()
    cols = ['nTRs', 'AcqNumber','ExpectedTRs','SeriesDesc','SeriesNum','Name','ImageType','ImageTypeText','RCName','RCActive']
    df = df.reindex(df.columns.union(cols), axis=1)  
    print(df)
    for i in range(len(dcmlist)):
        df.loc[i] = dcmlist[i]
    df.insert(0, "SubID", subID, True)
    df.insert(1, "Session", sess, True)
    df.insert(2, "SubAge", subAge, True)
    df.insert(3, "SubSex", subSex, True)
    software = software.replace(" ", "") #remove spaces from text
    df.insert(4, "System", software, True)
    df.insert(5, "dicomDir", dicomRoot, True)
    
    #%%
    #make columns of nans
    df['label'] = ''
    df['PEdir'] = ''
    df['MP'] = ''
    df['acq'] = ''
    #df['noise'] = ''
    df['complete'] = ''
    #label full rest scans
    if h: #use a heuristic
        df_h = pd.read_csv(heuristic)
        hdict = df_h.T.to_dict()
        funcList = []
        for i in hdict:
            funcList.append(hdict[i])
        print('*****',funcList)
        #print(funcList)
        for i,func in enumerate(funcList):
            lookfor = func['lookfor']
            taskname = func['taskname']
            isNan = float(func['nTRs'])
            #check for correct number of volumes
            if math.isnan(isNan):
                print('labeling all runs')
                command = df['Name'].str.contains(lookfor) & \
                    ~df['Name'].str.contains('SBRef')  
            else:
                print('checking for expectedTRS ', str(func['nTRs']))
                expected = str(int(func['nTRs']))
                command = df['Name'].str.contains(lookfor) & \
                        ~df['Name'].str.contains('SBRef') & \
                        df['nTRs'].str.contains(expected)
                        
            df['label'] = np.where(command,taskname,df['label'])
            completeseq = df['label']
            if math.isnan(isNan):
                print('labeling all runs')
                command = df['Name'].str.contains(lookfor) & \
                    ~df['Name'].str.contains('SBRef')  
            else:
                print('checking for expectedTRS ', str(func['nTRs']))
                expected = str(int(func['nTRs']))
                command = df['Name'].str.contains(lookfor) & \
                        ~df['Name'].str.contains('SBRef') & \
                        df['AcqNumber'].str.contains(expected)
            
    else:
        rest1 = df['Name'].str.contains('rest') & \
                ~df['Name'].str.contains('SBRef')# & \
                #(df['RCActive'].str.fullmatch('HEA;HEP') | \
                # df['RCActive'].str.fullmatch('HC1-7;NC1,2'))
                #df['nTRs'].str.contains('2200') #| \
        rest2 = df['Name'].str.contains('rest') & \
                ~df['Name'].str.contains('SBRef') #& \
                #(df['RCActive'].str.fullmatch('HEA;HEP') | \
                # df['RCActive'].str.fullmatch('HC1-7;NC1,2'))
                #df['nTRs'].str.contains('1360')
        df['label'] = np.where(rest1,'rest',df['label'])
        df['label'] = np.where(rest2,'rest',df['label'])
        #incomplete
        completeseq = df['AcqNumber'] == df['ExpectedTRs']
    
    
        
    dropsbref = (df['Name'].str.contains('SBRef') | \
            df['Name'].str.contains('setter'))
    if 'XA' in software:
        df['complete'] = np.where(completeseq,'1','0')
        df['complete'] = np.where(dropsbref,'1',df['complete'])
    
    # #label dwi scans
    if 'XA' in software:
        dwi1 = (df['ImageTypeText'].str.contains("'DIFFUSION', 'NONE', 'MB'") & \
            df['Name'].str.contains('AP')) & \
            ~df['Name'].str.contains('Physio') & \
            ~df['Name'].str.contains('_Pha') & \
            df['complete'].str.match('1') 
        dwi2 = (df['ImageTypeText'].str.contains("'DIFFUSION', 'NONE', 'MB'") & \
                  df['Name'].str.contains('PA')) & \
                  ~df['Name'].str.contains('Physio') & \
                  ~df['Name'].str.contains('_Pha') & \
                      df['complete'].str.match('1') 
    else:
        dwi1 = (df['ImageTypeText'].str.contains("'DIFFUSION', 'NONE', 'MB'") & \
            df['Name'].str.contains('AP')) & \
            ~df['Name'].str.contains('Physio') & \
            ~df['Name'].str.contains('_Pha')
        dwi2 = (df['ImageTypeText'].str.contains("'DIFFUSION', 'NONE', 'MB'") & \
                  df['Name'].str.contains('PA')) & \
                  ~df['Name'].str.contains('Physio') & \
                  ~df['Name'].str.contains('_Pha')
    df['label'] = np.where(dwi1,'dwi',df['label'])
    df['PEdir'] = np.where(dwi1,'AP',df['PEdir'])
    df['label'] = np.where(dwi2,'dwi',df['label'])
    df['PEdir'] = np.where(dwi2,'PA',df['PEdir'])
    
    
    #label fmap scans
    fmap1 = (df['Name'].str.contains('FieldMap') & \
              df['Name'].str.contains('AP') & \
            ~df['Name'].str.contains('Physio') & \
            df['ImageTypeText'].str.contains("'M'")) #& \
            #(df['RCActive'].str.fullmatch('HEA;HEP') | \
            # df['RCActive'].str.fullmatch('HC1-7;NC1,2')))
    fmap2 = (df['Name'].str.contains('FieldMap') & \
              df['Name'].str.contains('PA') & \
            ~df['Name'].str.contains('Physio') & \
                df['ImageTypeText'].str.contains("'M'"))# & \
               # (df['RCActive'].str.fullmatch('HEA;HEP') | \
               #  df['RCActive'].str.fullmatch('HC1-7;NC1,2')))
    df['label'] = np.where(fmap1,'fmap',df['label'])
    df['PEdir'] = np.where(fmap1,'AP',df['PEdir'])
    df['label'] = np.where(fmap2,'fmap',df['label'])
    df['PEdir'] = np.where(fmap2,'PA',df['PEdir'])
    
    #label fmap scans
    fmap1 = (df['Name'].str.contains('fmap') & \
              df['Name'].str.contains('AP') & \
            ~df['Name'].str.contains('Physio') & \
            ~df['Name'].str.contains('Pha'))# & \
            #(df['RCActive'].str.fullmatch('HEA;HEP') | \
            # df['RCActive'].str.fullmatch('HC1-7;NC1,2')))
    fmap2 = (df['Name'].str.contains('fmap') & \
              df['Name'].str.contains('PA') & \
            ~df['Name'].str.contains('Physio') & \
            ~df['Name'].str.contains('Pha'))#& \
               # df['ImageTypeText'].str.contains("'M'")) #& \
            #(df['RCActive'].str.fullmatch('HEA;HEP') | \
            # df['RCActive'].str.fullmatch('HC1-7;NC1,2')))
    df['label'] = np.where(fmap1,'fmap',df['label'])
    df['PEdir'] = np.where(fmap1,'AP',df['PEdir'])
    df['label'] = np.where(fmap2,'fmap',df['label'])
    df['PEdir'] = np.where(fmap2,'PA',df['PEdir'])
    
    #label dwi fmap scans
    fmap1 = (df['Name'].str.contains('DistortionMap') & \
              df['Name'].str.contains('AP') & \
            ~df['Name'].str.contains('Physio'))
    fmap2 = (df['Name'].str.contains('DistortionMap') & \
              df['Name'].str.contains('PA') & \
            ~df['Name'].str.contains('Physio')) 
    df['label'] = np.where(fmap1,'fmap',df['label'])
    df['PEdir'] = np.where(fmap1,'AP',df['PEdir'])
    df['label'] = np.where(fmap2,'fmap',df['label'])
    df['PEdir'] = np.where(fmap2,'PA',df['PEdir'])
    
    
    #label fmap tb1 scans
    fmap1 = (df['Name'].str.contains('TB1TFL') & \
            ~df['Name'].str.contains('Physio') & \
                df['ImageTypeText'].str.contains("'M'"))
    fmap2 = (df['Name'].str.contains('TB1TFL') & \
            ~df['Name'].str.contains('Physio') & \
                df['ImageTypeText'].str.contains("'FLIP ANGLE MAP'"))
    df['label'] = np.where(fmap1,'fmap',df['label'])
    df['acq'] = np.where(fmap1,'anat',df['acq'])
    df['label'] = np.where(fmap2,'fmap',df['label'])
    df['acq'] = np.where(fmap2,'fmap',df['acq'])

    #label revPE scans
    revPE1 = (df['Name'].str.contains('rev', case=False) & \
              df['Name'].str.contains('AP')) & \
            ~df['Name'].str.contains('Physio') & \
            ~df['Name'].str.contains('SBRef') & \
                df['ImageTypeText'].str.contains("'M'")
    revPE2 = (df['Name'].str.contains('rev', case=False) & \
              df['Name'].str.contains('PA')) & \
                ~df['Name'].str.contains('Physio') & \
                ~df['Name'].str.contains('SBRef') & \
                df['ImageTypeText'].str.contains("'M'")
    df['label'] = np.where(revPE1,'fmap',df['label'])
    df['PEdir'] = np.where(revPE1,'AP',df['PEdir'])
    df['label'] = np.where(revPE2,'fmap',df['label'])
    df['PEdir'] = np.where(revPE2,'PA',df['PEdir'])
    
    #label structural scans
    struct1 = ((df['Name'].str.contains('T1', case=False) & \
              (df['ImageTypeText'].str.contains("'NORM'") | \
                df['ImageTypeText'].str.contains("'UNI'")))) 
    struct2 = ((df['Name'].str.contains('T2', case=False) & \
              (df['ImageTypeText'].str.contains("'NORM'"))))
    df['label'] = np.where(struct1, 'T1w',df['label'])
    df['label'] = np.where(struct2, 'T2w',df['label'])
    
    struct3 = ((df['Name'].str.contains('qalas', case=False)) & \
              (df['ImageTypeText'].str.contains("'NORM'")))
    df['label'] = np.where(struct3, 'QALAS',df['label'])
    
    inv1 = df['Name'].str.contains('INV1')
    inv2 = df['Name'].str.contains('INV2')
    uni = ((df['Name'].str.contains('T1', case=False)) & \
              (df['ImageTypeText'].str.contains("'UNI'")))
    df['label'] = np.where(inv1, 'T1w', df['label'])
    df['label'] = np.where(inv2, 'T1w', df['label'])
    df['acq'] = np.where(inv1, 'inv1', df['acq'])
    df['acq'] = np.where(inv2, 'inv2', df['acq'])
    df['acq'] = np.where(uni, 'uni', df['acq'])
    
    #make a column of nans
    #define runNums for mag and phase
    mptest1 = df['ImageTypeText'].str.contains("'M'") & df['label']
    mptest2 = df['ImageTypeText'].str.contains("'P'") & df['label']
    df['MP'] = np.where(mptest1,'M',df['MP'])
    df['MP'] = np.where(mptest2,'P',df['MP'])
    
    #add in runNum
    df['runNum'] = df.groupby(['label','MP','PEdir','acq']).cumcount().add(1)
    df['runNum'] = np.where(df['label'],df['runNum'],'')
    
    #find echo location
    df['echoLoc'] = df['ImageTypeText'].str.find("'TE")
    #take the first character after "TE"
    echoNum = df.apply(lambda x: x['ImageTypeText'][x['echoLoc']+3:x['echoLoc']+4],axis=1)
    #make nEc column
    df['nEc'] = np.where(df['ImageTypeText'].str.contains("'TE"),echoNum,'1')
    
    #add in noise scans for XA only (VE will have to be visually checked)
    # if 'XA' in software:
    #     notFunc = ['T1w','T2w','dwi','fmap','physio','']
    #     func = ~df['label'].isin(notFunc)
    #     ifcomplete = (func & df['complete'].str.contains('1'))
    #     ifincomplete = (func & df['complete'].str.contains('0'))
    #     df['noise'] = np.where(ifcomplete,'3',df['noise'])
    #     df['noise'] = np.where(ifincomplete,'0',df['noise'])
    
    df['comb'] = df['runNum']
    
    #delete unecessary
    df = df.drop('echoLoc', axis=1)
    #%%
    #write df to csv
    empty = ['']
    labeled = df[['SubID','Session','label','PEdir','acq','nTRs','AcqNumber','ExpectedTRs','complete','runNum','MP','RCActive']]#[~df['label'].isin(empty)]
    print(labeled)
    print('writing... ',filename)
    
    old_cols = df.columns.values 
    new_cols= ['SubID', 'Session', 'SubAge', 'SubSex', 'label','nTRs',
            'complete', 'PEdir', 'MP', 'acq',
            'runNum', 'comb','nEc',
            'AcqNumber', 'ExpectedTRs', 'SeriesDesc', 
            'SeriesNum', 'Name',
            'ImageType', 'ImageTypeText','System','dicomDir','RCName','RCActive']
    df = df.reindex(columns=new_cols)
    df.to_csv(filename, encoding='utf-8', index=False, sep="\t")
    
#%%
#build dictionary so we can make a json. I guess df -> json would be faster?
#but I'm not that good at df yet and the dict -> json was already written

if jsononly:
    df = pd.read_csv(filename,sep='\t',header=0)
    print('reading from ... ', filename)
    #get rid of nans
    df = df.replace(np.nan, '', regex=True)
    #add in new run nums
    mptest1 = df['ImageTypeText'].str.contains("'M'") & df['label']
    mptest2 = df['ImageTypeText'].str.contains("'P'") & df['label']
    df['MP'] = np.where(mptest1,'M',df['MP'])
    df['MP'] = np.where(mptest2,'P',df['MP'])
    
    df['runNum'] = df.groupby(['label','MP','PEdir','acq']).cumcount().add(1)
    df['runNum'] = np.where(df['label'],df['runNum'],'')
    
    completeseq = df['AcqNumber'] == df['ExpectedTRs']
    df['complete'] = np.where(completeseq,'1','0')

    
    notFunc = ['T1w','T2w','dwi','fmap','physio','']
    func = ~df['label'].isin(notFunc)
    ifcomplete = (func & df['complete'].str.contains('1'))
    ifincomplete = (func & df['complete'].str.contains('0'))
    #df['noise'] = np.where(ifcomplete,'3',df['noise'])
    #df['noise'] = np.where(ifincomplete,'0',df['noise'])
    
    df['comb'] = df['runNum']
    print('updating runs in csv...',filename)
    df.to_csv(filename, encoding='utf-8', index=False, sep="\t")
    df = pd.read_csv(filename,sep="\t")
    df = df.replace(np.nan, '', regex=True)
else:
    pass

newDict = df.T.to_dict()
dicomList = []
for i in newDict:
    dicomList.append(newDict[i])

anatList = ['T1w', 'T2w','qalas','QALAS']#, 'T1rho', 'T1map', 'T2map', 'T2star', 'FLAIR', 'FLASH']
fmapList = ['PErev', 'revPE', 'afi', 'fa', 'magnitude', 'phasediff', \
            'magnitude1', 'magnitude2', 'phase1', 'phase2']

newDict = []
for i,dcm in enumerate(dicomList):
    if len(dcm['label'])>0:
        #print(dcm['label'])
        for echo in range(int(dcm['nEc'])):
                echoN = echo +1
                dictionary = {
                      'datatype': '', 
                      'suffix': '',
                      'custom_entities': '',
                      'sidecar_changes': {
                            ''
#                          'ImageType': '',
                          },
                      'criteria': {
#                            'ReceiveCoilName': '',
                            'ReceiveCoilActiveElements': '',
                            'SidecarFilename': '',
                            'SeriesDescription': '',
                            'ImageType': ''
                          }
                      }           
    
                add = ''
                if dcm['label'] in anatList:
                    dictionary['datatype'] = 'anat'
                    dictionary['suffix'] = dcm['label']
                    if (dcm['runNum']) == '': 
                        run = ''
                    else:                        
                        if int(dcm['runNum']) > 9:
                            run = 'run-%s'%int(dcm['runNum'])
                        else:
                            run = 'run-0%s'%int(dcm['runNum'])
                    if dcm['acq'] == '':
                        acq = ''
                    else:
                        acq = 'acq-'+ dcm['acq']
            
                    
                    dictionary['custom_entities'] = '%s_%s'%(acq,run)
                    
                elif dcm['label'] in fmapList or dcm['label'] == 'fmap':
                    dictionary['datatype'] = 'fmap'
                    if 'DIFFUSION' in dcm['ImageType']:
                        #print('fmap dwi')
                        dictionary['suffix'] = 'dwi'
                        PEdir = 'dir-' + dcm['PEdir']
                    elif 'TB1TFL' in dcm['SeriesDesc']:
                        dictionary['suffix'] = 'TB1TFL'
                        PEdir = ''
                    else:
                        dictionary['suffix'] = 'epi'
                        PEdir = 'dir-' + dcm['PEdir']
                
                        
                    if (dcm['runNum']) == '': 
                        run = ''
                    else:                        
                        if int(dcm['runNum']) > 9:
                            run = 'run-%s'%int(dcm['runNum'])
                        else:
                            run = 'run-0%s'%int(dcm['runNum'])
                    
                    if dcm['acq'] == '':
                        acq = ''
                    else:
                        acq = 'acq-'+ dcm['acq']                    
                    if PEdir:
                        dictionary['custom_entities'] = '%s_%s_%s'%(acq,PEdir,run)
                    else:
                        dictionary['custom_entities'] = '%s_%s'%(acq,run)
                    
                elif dcm['label'] == 'dwi':
                    dictionary['datatype'] = 'dwi'
                    dictionary['suffix'] = 'dwi'
                    PEdir = 'dir-' + dcm['PEdir']                  
                    if dcm['acq'] == '':
                        acq = ''
                    else:
                        acq = '_acq-'+ dcm['acq']
                    #dictionary['custom_entities'] = '_%s'%(PEdir)
                    if (dcm['runNum']) == '':
                        run = ''
                    else:
                        if int(dcm['runNum']) > 9:
                            run = '_run-%s'%int(dcm['runNum'])
                        else:
                            run = '_run-0%s'%int(dcm['runNum'])
                    dictionary['custom_entities'] = '_%s%s%s'%(PEdir,acq,run)
                    
                else:
                    dictionary['datatype'] = 'func'
                    if 'SBRef' in dcm['Name']:
                        dictionary['suffix'] = 'sbref'
                        taskType = 'task-' + dcm['label']
                        #multiecho
                        if int(dcm['nEc']) > 1:
                            add = '_e%s.json'%(echoN)
                            dictionary['custom_entities'] = taskType +'ME_echo-%s'%echo
                                
                        #single echo
                        else:
                            dictionary['custom_entities'] = taskType +'SE'
                            add = '.json'
                            
                        ImageTypeChange = ["ORIGINAL","PRIMARY","FMRI","NONE"]
                        dictionary['sidecar_changes']['ImageType'] = ImageTypeChange
                        
                                
                    else:
                        dictionary['suffix'] = 'bold'
                        taskType = 'task-' + dcm['label']
                        #check for runs
                        if (dcm['runNum']) == '':
                            run = ''
                        else:
                            if int(dcm['runNum']) > 9:
                                run = 'run-%s'%int(dcm['runNum'])
                            else:
                                run = 'run-0%s'%int(dcm['runNum'])
                        
                        if dcm['acq'] == '':
                            acq = ''
                        else:
                            acq = 'acq-'+ dcm['acq']         

                        if 'P' in dcm['MP']:
                              if int(dcm['nEc']) > 1:
                                  add = 'e%s_ph.json'%echoN
                                  dictionary['custom_entities'] = taskType + '%s_%s_echo-%s_part-phase'%(acq, run, echoN) 
                              #single echo
                              else:
                                  add = '.json'
                                  dictionary['custom_entities'] = taskType + '%s_part-phase'%(run) 

                        elif 'M' in dcm['MP']:
                              #multiecho
                              if int(dcm['nEc']) > 1:
                                  add = '_e%s.json'%echoN
                                  dictionary['custom_entities'] = taskType +'%s_%s_echo-%s_part-mag'%(acq,run, echoN)
                              #single echo
                              else:
                                  add = '.json'
                                  dictionary['custom_entities'] = taskType + '%s_part-mag'%(run) 
                                     
                dictionary['criteria']['SidecarFilename'] = dcm['SeriesNum'] + add
                dictionary['criteria']['SeriesDescription'] = dcm['SeriesDesc']
                
                #dictionary['criteria']['ReceiveCoilName'] = dcm['RCName']
                dictionary['criteria']['ReceiveCoilActiveElements'] = dcm['RCActive']
                
                if not dictionary['suffix'] == 'sbref':
                    #make sure imagetype is a list otherwise dcm2bids won't work
                    if isinstance(dcm['ImageType'], str):
                        dictionary['criteria']['ImageType'] = eval(dcm['ImageType'])
                    else:
                        dictionary['criteria']['ImageType'] = dcm['ImageType']
                    
                    #trying this out    
#                    if isinstance(dcm['ImageTypeText'], str):
#                        dictionary['criteria']['ImageTypeText'] = eval(dcm['ImageTypeText'])
#                    else:
#                        dictionary['criteria']['ImageTypeText'] = dcm['ImageTypeText']
                
                if coilcheck == 0:
                   del dictionary['criteria']['ReceiveCoilActiveElements']
                if 'TE' in dcm['ImageTypeText']:
                    dictionary['criteria']['EchoNumber'] = echoN
                if dictionary['custom_entities'] == {''}:
                    del dictionary['custom_entities']
                if dictionary['sidecar_changes'] == {''}:
                    del dictionary['sidecar_changes']
                if dictionary['datatype'] == 'func':
                    del dictionary['criteria']['ImageType']
#                    del dictionary['criteria']['ImageTypeText']
                if dictionary['datatype'] == 'fmap':
                    del dictionary['criteria']['ImageType']
#                    del dictionary['criteria']['ImageTypeText']
#                if dictionary['datatype'] == 'anat':
#                    del dictionary['criteria']['ImageTypeText']
                #only print out the first echo for fmaps!!
                try:
                    x = dictionary['criteria']['EchoNumber']
                except KeyError:
                    newDict.append(dictionary)
                else:
                    if dictionary['datatype'] == 'fmap' and dictionary['criteria']['EchoNumber'] > 1:
                        pass
                    else:
                        newDict.append(dictionary)
                #print(dictionary)

#write out that dictionary as a json file! use this config file to run dcm2bids
#print(newDict)
jsonString = json.dumps(newDict, indent=4)
print('writing....',jsonfilename)
with open(jsonfilename, "w") as outfile:

    outfile.write('{\n')
    outfile.write('\t"descriptions":\n')
    outfile.write('\t')
    outfile.write(jsonString)
    outfile.write('\n')
    outfile.write('}')
outfile.close()