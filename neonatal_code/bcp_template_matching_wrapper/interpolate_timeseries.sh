#!/bin/bash

module load matlab/R2019a

derivs="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives/xcpd/bcp"

for dir in "${derivs}"/sub-* ; do
    folder=$(basename "$dir")
    subid=${folder%%_ses-*}
    sesid=${folder##*_}
    file="${dir}/${subid}/${sesid}/func/${subid}_${sesid}_task-rest_space-fsLR_den-91k_desc-denoised_bold.dtseries.nii"
    echo $file
    matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/internal/utilities/interpolate_noise_for_timeseries')); addpath(genpath('/projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks/')); cii_save_name=interpolate_noise_for_timeseries('${file}','/projects/standard/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command',0); exit"
done
