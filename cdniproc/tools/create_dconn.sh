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
#TASK=concatenated
FD=0.2
BOLD=denoised #options: 'denoised' or 'denoisedSmoothed' 'interpolated'
S_KERNEL=2.25

DERIVATIVES=/projects/standard/nardosr/shared/projects/uuiplus/derivatives/fmriprep-24.0.1-xcpd-0.10.7
#DERIVATIVES=/projects/standard/nardosr/shared/projects/uuiplus/derivatives/fmriprep-24.0.1-xcpd-0.10.7/01s1/analysis_input_files/
in_dir=${DERIVATIVES}/${SUB}/analysis_input_files
out_dir=/scratch.global/kweldon/uuiplus/dconns/
work_dir=/tmp/${SUB}/${SES}/${TASK}/

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

DTSERIESEXT=space-fsLR_den-91k_desc-${BOLD}_bold_spatially_interpolated.dtseries.nii
dtseries_in=${in_dir}/sub-${SUB}_ses-${SES}_task-${TASK}_${DTSERIESEXT}
surf_L=(${in_dir}/sub-${SUB}_*hemi-L_*desc-hcp_midthickness.surf.gii)
surf_R=(${in_dir}/sub-${SUB}_*hemi-R_*desc-hcp_midthickness.surf.gii)
motion_file=(${in_dir}/sub-${SUB}_ses-${SES}_task-${TASK}_desc-abcc_qc_power_2014_FD_only.mat)

# Make sure all inputs exists and exit script if any of them are missing 
if [ ! -f ${dtseries_in} ]; then
    echo "This dtseries doesn't exist:" ${dtseries_in}
    exit 1
fi
if [ ! -f ${surf_L} ]; then
    echo "This surface file doesn't exist:" ${surf_L}
    exit 1
fi
if [ ! -f ${surf_R} ]; then
    echo "This surface file doesn't exist:" ${surf_R}
    exit 1
fi
if [ ! -f ${motion_file} ]; then
    echo "This motion file doesn't exist:" ${motion_file}
    exit 1
fi

echo "all files exist! continuing...."
#exit 0

TR=$(wb_command -file-information ${dtseries_in} -only-step-interval) 

#run cifti-con for half1 part of data
python3 /projects/standard/faird/shared/code/internal/utilities/cifti_connectivity/cifti_conn_wrapper.py \
--motion ${motion_file} \
--mre-dir ${MRE_DIR} \
--left ${surf_L} \
--right ${surf_R} \
--wb-command ${WB_CMD} --fd-threshold ${FD} --smoothing-kernel ${S_KERNEL} --remove-outliers \
${dtseries_in} \
${TR} ${out_dir} matrix;

