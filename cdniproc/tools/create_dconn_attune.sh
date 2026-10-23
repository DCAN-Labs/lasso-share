#!/bin/bash -l

#SBATCH -J dconn
#SBATCH --ntasks=4
#SBATCH --tmp=60gb
#SBATCH --mem=60gb
#SBATCH -t 02:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kweldon@umn.edu
#SBATCH -p msismall
#SBATCH -o output_logs/dconn_%A_%a.out
#SBATCH -e output_logs/dconn_%A_%a.err
#SBATCH -A yaco0006

SUB=${1}
SES=${2}
TASK=${3}
FD=0.2
BOLD=denoised #options: 'denoised' or 'denoisedSmoothed' 'interpolated'
S_KERNEL=2.25

work_dir=/tmp/${SUB}/${SES}/${TASK}/
in_dir=/scratch.global/kweldon/attune/derivatives/fmriprep-24.0.1-xcpd-0.10.7/${SUB}/analysis_input_files
out_dir=/scratch.global/kweldon/attune/derivatives/fmriprep-24.0.1-xcpd-0.10.7/${SUB}/dconn

MRE_DIR='/projects/standard/feczk001/shared/code/external/utilities/MATLAB_MCR/v91/'
WB_CMD='/projects/standard/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command'

if [ ! -d ${work_dir} ]; then
	mkdir -p ${work_dir}

fi

if [ ! -d ${out_dir} ]; then
	mkdir -p ${out_dir}

fi
module load workbench; 
module load matlab;     

TR=1.761
#TR=$(wb_command -file-information ${in_dir}/sub-${SUB}_ses-${SES}_task-${TASK}_space-fsLR_den-91k_desc-${BOLD}_bold_spatially_interpolated.dtseries.nii -only-step-interval) 

ANATL=$(ls ${in_dir}/*hemi-L_*desc-hcp_midthickness.surf.gii)
ANATR=$(ls ${in_dir}/*hemi-R_*desc-hcp_midthickness.surf.gii)


#run cifti-con 
python3 /projects/standard/faird/shared/code/internal/utilities/cifti_connectivity/cifti_conn_wrapper.py \
--motion ${in_dir}/sub-${SUB}_ses-${SES}_task-${TASK}_desc-abcc_qc_power_2014_FD_only.mat \
--mre-dir ${MRE_DIR} \
--left ${ANATL} \
--right ${ANATR} \
--wb-command ${WB_CMD} \
-fd ${FD} \
--smoothing-kernel ${S_KERNEL} \
--remove-outliers ${in_dir}/sub-${SUB}_ses-${SES}_task-${TASK}_space-fsLR_den-91k_desc-${BOLD}_bold_spatially_interpolated.dtseries.nii ${TR} ${out_dir} matrix;

