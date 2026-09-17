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

#fmriprep command  
env -i ${singularity} run --cleanenv \
  -B /tmp:/tmp \
  -B ${fmriprep_in_dir}:/bids_dir \
  -B ${fmriprep_out_dir}:/output_dir \
  -B ${fmriprep_work_dir}:/wd \
  -B /home/faird/shared/code/external/utilities/freesurfer_license/license.txt:/opt/freesurfer/license.txt \
  /home/faird/shared/code/external/pipelines/fmriprep/fmriprep_24.1.1.sif \
  --output-spaces MNI152NLin6Asym:res-2 \
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
-B /home/faird/shared/code/external/pipelines/xcp_d_test_binds/090_concat_single_run/base.py:/usr/local/miniconda/lib/python3.10/site-packages/xcp_d/workflows/base.py \
-B /home/faird/shared/code/external/utilities/freesurfer_license/license.txt:/opt/freesurfer/license.txt \
-B ${xcpd_in_dir}:/data:ro \
-B ${xcpd_out_dir}:/out \
-B ${xcpd_work_dir}:/work \
/home/faird/shared/code/external/pipelines/xcp_d/xcp_d_0.9.0.sif \
--mode abcd \
--participant-label ${SUB} \
--band-stop-min 12 --band-stop-max 18 --motion-filter-type notch \
--omp-nthreads 3 \
--motion-filter-order 4 \
-vv \
-w /work \
/data /out participant

#interpolate_and_convert

