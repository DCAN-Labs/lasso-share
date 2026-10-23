#!/bin/bash -l

#SBATCH -J fmriprep
#SBATCH -c 24
#SBATCH --mem=500G
#SBATCH -t 48:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=kweldon@umn.edu
#SBATCH -p ag2tb,agsmall,aglarge
#SBATCH -o output_logs/fmriprep_%A_%a.out
#SBATCH -e output_logs/fmriprep_%A_%a.err
#SBATCH -A maxwe128

singularity=`which singularity`

SUB=${1}
SES=${2}

#set up directories
dcm_s3_dir=s3://subpop/dicoms/${SUB}-ses${SES}/
dcm_scratch_dir=/scratch.global/kweldon/test/dicoms/${SUB}-ses${SES}/

#sync 1 dcm to make summary file
echo /projects/standard/faird/shared/code/internal/utilities/MSI-utilities/s3_get_last_dicoms/s3_get_last_dicoms.sh -i ${dcm_s3_dir} -o ${dcm_scratch_dir}
/projects/standard/faird/shared/code/internal/utilities/MSI-utilities/s3_get_last_dicoms/s3_get_last_dicoms.sh -i ${dcm_s3_dir} -o ${dcm_scratch_dir}

#run init
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_scratch_dir}
python /projects/standard/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_scratch_dir}
