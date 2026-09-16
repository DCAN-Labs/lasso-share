#!/bin/bash -l

#SBATCH -J PIP_dataprep
#SBATCH -c 24
#SBATCH --mem=50G
#SBATCH -t 8:00:00
#SBATCH --mail-type=NONE
#SBATCH -p msismall
#SBATCH -o output_logs/PIP_dataprep_%A_%a.out
#SBATCH -e output_logs/PIP_dataprep_%A_%a.err
#SBATCH -A moser297

echo "Running data_prep.sh"
singularity=`which singularity`
source /projects/standard/faird/shared/code/external/envs/miniconda3/load_miniconda3.sh
conda activate py11
#run this to activate conda: /projects/standard/miran045/shared/code/external/envs/miniconda3/load_miniconda3.sh
#old source: /projects/standard/faird/shared/code/external/envs/miniconda3/load_miniconda3.sh

SUB=${1}
SES=${2}

#set up directories
#dcm_s3_dir=s3://subpop/dicoms/${SUB}-ses${SES}/
#dcm_scratch_dir=/scratch.global/kweldon/test/dicoms/${SUB}-ses${SES}/
dcm_dir=/projects/standard/moser297/shared/projects/PIP/data/DICOMs/${SUB}/${SUB}_ses${SES}/

#sync 1 dcm to make summary file
#echo /home/faird/shared/code/internal/utilities/MSI-utilities/s3_get_last_dicoms/s3_get_last_dicoms.sh -i ${dcm_s3_dir} -o ${dcm_scratch_dir}
#/home/faird/shared/code/internal/utilities/MSI-utilities/s3_get_last_dicoms/s3_get_last_dicoms.sh -i ${dcm_s3_dir} -o ${dcm_scratch_dir}

#run init
echo python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/init.py -p ${SUB} -s ${SES} -d ${dcm_dir}
python /projects/standard/faird/shared/code/internal/utilities/cdniproc_v2.0/init.py -p ${SUB} -s ${SES} -d ${dcm_dir}