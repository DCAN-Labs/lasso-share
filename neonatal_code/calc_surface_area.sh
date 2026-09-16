#!/bin/bash
#SBATCH -J surface_area
#SBATCH -p msismall
#SBATCH --mem=100gb
#SBATCH -t 48:00:00
#SBATCH --mail-type=NONE
#SBATCH --tmp=100gb
#SBATCH -o output_logs/calc_surface_area_%A.out
#SBATCH -e output_logs/calc_surface_area_%A.err
#SBATCH -A darro015

module load matlab
module load workbench

subject_list="/projects/standard/csandova/shared/projects/rae_neonatal/code/bcp_template_matching_wrapper/7-Apr_successful_temp-match_bcp_subjects.csv"
derivs_dir="/projects/standard/csandova/shared/projects/rae_neonatal/derivatives"

while IFS=',' read -r subid ses age rest_of_line; do
    echo "Starting calculation for this sub/ses:" "${subid}" "${ses}"
    # Check if run-001 surface exists, if not, check if run-002, if not, assume there is no run number
    run="run-001_"
    L_midthickness="${derivs_dir}/xcpd/bcp/sub-${subid}_ses-${sesid}/sub-${subid}/ses-${sesid}/anat/sub-${subid}_ses-${sesid}_${run}hemi-L_space-fsLR_den-32k_desc-hcp_midthickness.surf.gii"
    if [[ ! -f "$L_midthickness" ]]; then
        run="run-002_"
        L_midthickness="${derivs_dir}/sub-${subid}_ses-${sesid}/sub-${subid}/ses-${sesid}/anat/sub-${subid}_ses-${sesid}_${run}hemi-L_space-fsLR_den-32k_desc-hcp_midthickness.surf.gii"
        if [[ ! -f "$L_midthickness" ]]; then
            run=""
        fi
    fi
	matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks/network_surface_area/')); surfaceareafromgreyordinates('${derivs_dir}/xcpd/bcp/sub-${subid}_ses-${ses}/sub-${subid}/ses-${ses}/anat/sub-${subid}_ses-${ses}_${run}hemi-L_space-fsLR_den-32k_desc-hcp_midthickness.surf.gii','${derivs_dir}/xcpd/bcp/sub-${subid}_ses-${ses}/sub-${subid}/ses-${ses}/anat/sub-${subid}_ses-${ses}_${run}hemi-R_space-fsLR_den-32k_desc-hcp_midthickness.surf.gii',1,'${derivs_dir}/bcp_template_matching/abcd/sub-${subid}/sub-${subid}_ses-${ses}_task-rest_space-fsLR_den-91k_desc-denoised_bold_spatially_interpolated_template_matched_Zscored_scanthresh3_recolored.dscalar.nii','sub-${subid}_ses-${ses}_surface_area','${derivs_dir}/bcp_template_matching/abcd/sub-${subid}/',1,0,0,''); exit"
done < "$subject_list"
