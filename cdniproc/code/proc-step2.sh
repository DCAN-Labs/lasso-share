#!/bin/bash -l

#SBATCH -J PCS04
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
PARENT=/scratch.global/kweldon/test
rawbids_dir=${PARENT}/bids
fmriprep_in_dir=${PARENT}/derivatives/nordic
fmriprep_out_dir=${PARENT}/derivatives/fmriprep-24.1.1/output/${SUB}
fmriprep_work_dir=${PARENT}/derivatives/fmriprep-24.1.1/work/${SUB}
xcpd_in_dir=${fmriprep_out_dir}
xcpd_out_dir=${PARENT}/derivatives/xcpd-0.10.7/output/${SUB}
xcpd_work_dir=${PARENT}/derivatives/xcpd-0.10.7/work/${SUB}
FUNCDIR=${xcpd_out_dir}/sub-${SUB}/ses-${SES}/func


#make fmriprep dirs
if [ ! -d ${fmriprep_work_dir} ]; then
  mkdir -p ${fmriprep_work_dir}
fi  

if [ ! -d ${fmriprep_out_dir} ]; then
	mkdir -p ${fmriprep_out_dir}
fi

singularity=`which singularity`

#fmriprep command  
env -i ${singularity} run --cleanenv \
  -B /tmp:/tmp \
  -B ${fmriprep_in_dir}:/bids_dir \
  -B ${fmriprep_out_dir}:/output_dir \
  -B ${fmriprep_work_dir}:/wd \
  -B /projects/standard/faird/shared/code/external/utilities/freesurfer_license/license.txt:/opt/freesurfer/license.txt \
  /projects/standard/faird/shared/code/external/pipelines/fmriprep/fmriprep_24.1.1.sif \
  --output-spaces MNI152NLin6Asym:res-2:res-native \
  --fs-license-file /opt/freesurfer/license.txt \
  --project-goodvoxels \
  --use-syn-sdc \
  --skull-strip-fixed-seed \
  --omp-nthreads 3 \
  --cifti-output 91k \
  --bold2anat-init auto \
  --participant-label ${SUB} \
  -vv \
  -w /wd \
/bids_dir /output_dir participant 

#make xcpd dirs
if [ ! -d ${xcpd_work_dir} ]; then
  mkdir -p ${xcpd_work_dir}
fi  

if [ ! -d ${xcpd_out_dir} ]; then
	mkdir -p ${xcpd_out_dir}
fi

#xcpd command
env -i ${singularity} run --cleanenv \
-B /projects/standard/faird/shared/code/external/utilities/freesurfer_license/license.txt:/opt/freesurfer/license.txt \
-B ${xcpd_in_dir}:/data:ro \
-B ${xcpd_out_dir}:/out \
-B ${xcpd_work_dir}:/work \
/projects/standard/faird/shared/code/external/pipelines/xcp_d/xcp_d_0.10.7.sif \
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
python /projects/standard/faird/shared/code/internal/utilities/xcpd2dcanmotion/convert_motion_hdf5_to_tsv.py ${FUNCDIR}

#interpolate
for FILE in ${FUNCDIR}/*denoised_bold.dtseries.nii; do
echo "spatially interpolating $FILE"
matlab -nodisplay -nosplash -r "addpath(genpath('/projects/standard/faird/shared/code/internal/utilities/interpolate_noise_for_timeseries')); addpath(genpath('/projects/standard/faird/shared/code/internal/analytics/compare_matrices_to_assign_networks/')); cii_save_name=interpolate_noise_for_timeseries('${FILE}','/projects/standard/faird/shared/code/external/utilities/workbench/1.4.2/workbench/bin_rh_linux64/wb_command',0); exit"
done

#copy input files
python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/tools/copy_input_files.py ${xcpd_out_dir}

#run_pcm
echo sbatch ${PARENT}/run_pcm.sh ${SUB} ${SES} ${PIPELINE}
sbatch ${PARENT}/run_pcm.sh ${SUB} ${SES} ${PIPELINE}
