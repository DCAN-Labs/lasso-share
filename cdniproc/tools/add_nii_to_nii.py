#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 11:06:34 2025

@author: kweldon
"""

import nibabel as nb
import numpy as np
from nibabel.nifti1 import Nifti1Image
from tm_common.utilities.pathing import Path
from tm_common.utilities.rgba import normalize_nifti
from tm_common.utilities.nii2dcm import nii_to_dcm
import os

subject_id = "MSSM01"
series_num = 104
outputdir = "/scratch.global/kweldon/MSSM/derivatives/fmriprep25.2.2-xcpd0.12.0/MSSM01/reDICOM/dicom_output/"

#networks = ['SCANthresh2','SCAN','CO']
networks = ['SCAN']
for network in networks:
    print(network)
    series_num=series_num+1
    overlay_output_dir = os.path.join(outputdir,"pcm_%s_t1_overlay")%network
    description = "pcm_%s_t1_overlay"%network
    roifilename = "/scratch.global/kweldon/MSSM/derivatives/fmriprep25.2.2-xcpd0.12.0/MSSM01/reDICOM/sub-MSSM01_ses-01_desc-confidence_network-%s_space-native.nii.gz"%network

    t1w = nb.load("/scratch.global/kweldon/MSSM/derivatives/fmriprep-25.2.2/output/MSSM01/sub-MSSM01/ses-01/anat/sub-MSSM01_ses-01_desc-preproc_T1w.nii.gz")
    roi = nb.load(roifilename)
    #sub-MSSM01_ses-01_desc-confidence_network-SCANthresh2_space-native
    t1w_data = t1w.get_fdata()
    roi_data = roi.get_fdata()
    
    t1w_data = t1w_data / 2
    t1w_data[roi_data != 0] = 2 * np.max(t1w_data)
    
    t1w_out = nb.Nifti1Image(t1w_data, t1w.affine, t1w.header)
    filename="/scratch.global/kweldon/MSSM/derivatives/fmriprep25.2.2-xcpd0.12.0/MSSM01/reDICOM/pcm_%s_on_T1_space-native.nii.gz"%network
    t1w_out.to_filename(filename)
    
    roi_on_t1 = Path(filename)
    
    roi_on_t1_img = normalize_nifti(Nifti1Image.load(roi_on_t1))
    
    normfilename = "/scratch.global/kweldon/MSSM/derivatives/fmriprep25.2.2-xcpd0.12.0/MSSM01/reDICOM/pcm_%s_on_T1_space-nativenorm.nii.gz"%network
    
    roi_on_t1_img.to_filename(normfilename)
    
    # write out the T1w image
    print('writing out...')
    nii_to_dcm(roi_on_t1_img,overlay_output_dir,subject_id=subject_id,series_description=description,series_number=series_num+1)
    #nii_to_dcm(roi_on_t1,overlay_output_dir,subject_id=subject_id,series_description=description,series_number=series_num)


