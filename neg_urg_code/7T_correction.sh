#!/bin/bash

###############################################################################
# 7 T-specific processing  
# Originally created by Bene Ramirez 
# Slightly modified by rae McCollum to be made into a wrapper
###############################################################################

module load gcc/9.2.0
module load afni
module load fsl

project_dir='/projects/standard/lewi1538/shared/projects/neg_urg'
subid='NU001'
sesid='1' 

anat_dir="${project_dir}/bids/sub-${subid}/ses-${sesid}/anat"
bids_dir="${project_dir}/bids/" 
code_dir="${project_dir}/code"

############### 0.5) VERIFY PATHS ###########
if [ ! -d ${anat_dir} ]; then
	echo "Dir not found:" ${anat_dir}
fi

if [ ! -d ${bids_dir} ]; then
	echo "Dir not found:" ${bids_dir}
fi

if [ ! -d ${anat_dir} ]; then
	echo "Dir not found:" ${code_dir}
fi

############### 1) DENOISE + BIAS-FIELD-CORRECT THE ANATOMICALS ###########

echo "Running denoise + BFC..."

# Detect MP2RAGE files (with or without a run-label) ----------------------
INV1_FILE=$(ls ${anat_dir}/sub-${subid}_ses-${sesid}_acq-inv1*_T1w.nii.gz 2>/dev/null | head -n 1)
INV2_FILE=$(ls ${anat_dir}/sub-${subid}_ses-${sesid}_acq-inv2*_T1w.nii.gz 2>/dev/null | head -n 1)
UNI_FILE=$(ls  ${anat_dir}/sub-${subid}_ses-${sesid}_acq-uni*_T1w.nii.gz  2>/dev/null | head -n 1)

if [[ -z "$INV1_FILE" || -z "$INV2_FILE" || -z "$UNI_FILE" ]]; then
    echo "L  Could not find expected MP2RAGE files in ${anat_dir}.  Skipping denoise/BFC."
else
    # Determine whether a _run-?? label was present
    [[ "$INV1_FILE" == *"_run-"* ]] && RUN_SUFFIX="" || RUN_SUFFIX="_run-01"

    echo "='  MP2RAGE denoising via LayNii..."
    pushd /projects/standard/bart/shared/projects/7Tpiloting/anat_testing/scripts/LayNii  >/dev/null
    ./LN_MP2RAGE_DNOISE \
            -INV1  "$INV1_FILE" \
            -INV2  "$INV2_FILE" \
            -UNI   "$UNI_FILE" \
            -beta  0.5 \
            -output "${anat_dir}/sub-${subid}_ses-${sesid}_acq-unidenoised${RUN_SUFFIX}_T1w.nii.gz"
    popd >/dev/null

    echo "='  Bias-field correction..."
    sbatch "${code_dir}/start_bias_field_correction.sh" \
            "${anat_dir}/sub-${subid}_ses-${sesid}_acq-unidenoised${RUN_SUFFIX}_T1w.nii.gz" \
            "${anat_dir}/sub-${subid}_ses-${sesid}_acq-unidenoisedbfc${RUN_SUFFIX}_T1w.nii.gz" \
            "${code_dir}"
    cp "${UNI_FILE%.nii.gz}.json" \
        "${anat_dir}/sub-${subid}_ses-${sesid}_acq-unidenoisedbfc${RUN_SUFFIX}_T1w.json"

    # ---- Do the same for any T2w --------------------------------------------------
    T2W_FILE=$(ls ${anat_dir}/sub-${subid}_ses-${sesid}*_T2w.nii.gz 2>/dev/null | head -n 1)
    if [[ -n "$T2W_FILE" ]]; then
        [[ "$T2W_FILE" == *"_run-"* ]] && T2W_RUN_SUFFIX="" || T2W_RUN_SUFFIX="_run-01"
        sbatch "${code_dir}/start_bias_field_correction.sh" \
                "$T2W_FILE" \
                "${anat_dir}/sub-${subid}_ses-${sesid}_acq-bfc${T2W_RUN_SUFFIX}_T2w.nii.gz" \
                "${code_dir}"
        cp "${T2W_FILE%.nii.gz}.json" \
            "${anat_dir}/sub-${subid}_ses-${sesid}_acq-bfc${T2W_RUN_SUFFIX}_T2w.json"
    fi
fi

########### 2) GENERATE FAKE AP FMAP ###########

# echo "Running fake-forward-EPI creation..."

# python ${pCodePath}/IntendedFor_JSBR_prenordic.py ${bids_dir} --sub sub-${subid} --ses ${sesid} --assign-mode lookback --write
# python "${pCodePath}/generate_fake_ap.py" "${bids_dir}" "${subid}" ${sesid}
# python ${pCodePath}/IntendedFor_JSBR_prenordic.py ${bids_dir} --sub sub-${subid} --ses ${sesid} --assign-mode lookback --write

## Clean up Anat folder from for 7T 
# ${pCodePath}/cdniproc/cleanup_7T_anat.sh ${subid} --src-base ${PARENT}/summaries/bids --dst-base ${fmriprep_in_dir}
# project_dir="${fmriprep_in_dir}" 
# python ${pCodePath}/IntendedFor_JSBR_prenordic.py ${project_dir} --sub sub-${subid} --ses ${sesid} --assign-mode lookback --write
