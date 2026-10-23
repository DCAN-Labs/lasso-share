#!/bin/bash -l

#SBATCH -J proc2
#SBATCH -c 24
#SBATCH --mem=500G
#SBATCH -t 12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kweldon@umn.edu
#SBATCH -p ag2tb,agsmall,aglarge
#SBATCH -o output_logs/proc2_%A_%a.out
#SBATCH -e output_logs/proc2_%A_%a.err
#SBATCH -A maxwe128

singularity=`which singularity`
module load matlab/R2019a

SUB=${1}
SES=${2}

#set up directories
PARENT=/scratch.global/kweldon/subpoptest
dcm_s3_dir=s3://subpop/dicoms/${SUB}-ses${SES}/
dcm_scratch_dir=${PARENT}/dicoms/${SUB}-ses${SES}/
rawbids_dir=${PARENT}/bids
fmriprep_in_dir=${PARENT}/derivatives/nordic
fmriprep_out_dir=${PARENT}/derivatives/fmriprep/output/${SUB}
fmriprep_work_dir=${PARENT}/derivatives/fmriprep/work/${SUB}
xcpd_in_dir=${fmriprep_out_dir}
xcpd_out_dir=${PARENT}/derivatives/xcpd/output/${SUB}
xcpd_work_dir=${PARENT}/derivatives/xcpd/work/${SUB}


#make fmriprep dirs
if [ ! -d ${fmriprep_work_dir} ]; then
  mkdir -p ${fmriprep_work_dir}
fi  

if [ ! -d ${fmriprep_out_dir} ]; then
	mkdir -p ${fmriprep_out_dir}
fi

singularity=`which singularity`

#Nibabies
env -i ${singularity} run --cleanenv \
-B ${in_dir}:/data:ro \
-B ${out_dir}/:/out \
-B ${work_dir}/:/work \
-B ${bibsnet_dir}/:/bibsnet \
-B /projects/standard/faird/shared/code/external/utilities/freesurfer_license/license.txt:/opt/freesurfer/license.txt \
/projects/standard/faird/shared/code/external/pipelines/nibabies/nibabies_25.0.1.sif /data /out participant --participant-label ${SUB} \
--derivatives /bibsnet \
--fs-license-file /opt/freesurfer/license.txt \
--cifti-output 91k \
--use-syn-sdc \
--omp-nthreads 8 \
--nprocs 8 \
--multi-step-reg \
--norm-csf \
--project-goodvoxels \
--surface-recon-method mcribs \
--fd-radius 45 \
--age-months ${MONTHS} \
-vv \
-w /work \
--output-spaces MNI152NLin6Asym:res-2:res-native

#make xcpd dirs
if [ ! -d ${xcpd_work_dir} ]; then
  mkdir -p ${xcpd_work_dir}
fi  

if [ ! -d ${xcpd_out_dir} ]; then
	mkdir -p ${xcpd_out_dir}
fi

#xcpd command
env -i ${singularity} run --cleanenv \
-B /projects/standard/faird/shared/code/external/pipelines/xcp_d_test_binds/0105_concat_single_run/base.py:/usr/local/miniconda/lib/python3.10/site-packages/xcp_d/workflows/base.py \
-B /projects/standard/faird/shared/code/external/utilities/freesurfer_license/license.txt:/opt/freesurfer/license.txt \
-B ${xcpd_in_dir}:/data:ro \
-B ${xcpd_out_dir}:/out \
-B ${xcpd_work_dir}:/work \
/projects/standard/faird/shared/code/external/pipelines/xcp_d/xcp_d_0.10.5.sif \
--mode abcd \
--participant-label ${SUB} \
--band-stop-min 12 --band-stop-max 18 --motion-filter-type notch \
--omp-nthreads 3 \
--motion-filter-order 4 \
-vv \
-w /work \
/data /out participant

#convert motion hdf5 to .mat
echo matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/internal/utilities/xcpd2dcanmotion')); hdf5_files=dir('${FUNCDIR}/*.hdf5'); for i = 1:length(hdf5_files); xcpd2dcanmotion(fullfile(hdf5_files(i).folder, hdf5_files(i).name), hdf5_files(i).folder); end; exit"
matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/internal/utilities/xcpd2dcanmotion')); hdf5_files=dir('${FUNCDIR}/*.hdf5'); for i = 1:length(hdf5_files); xcpd2dcanmotion(fullfile(hdf5_files(i).folder, hdf5_files(i).name), hdf5_files(i).folder); end; exit"

#convert motion hdf5 to tsv
python /projects/standard/faird/shared/code/internal/utilities/xcpd2dcanmotion/convert_motion_hdf5_to_tsv.py ${xcpd_out_dir}

#interpolate
for FILE in ${FUNCDIR}/*denoised_bold.dtseries.nii; do
echo "spatially interpolating $FILE"
matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/internal/utilities/interpolate_noise_for_timeseries')); addpath(genpath('/projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks/')); cii_save_name=interpolate_noise_for_timeseries('${FILE}','/projects/standard/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command',0); exit"
done

#copy input files to template matching directory
python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/tools/copy_files_to_temp.py ${xcpd_out_dir}
