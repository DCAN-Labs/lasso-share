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
#SBATCH -A lewi1538

singularity=`which singularity`

SUB=${1}
SES=${2}

#set up directories
dcm_dir=/home/lewi1538/shared/projects/neg_urg/dicoms/${SUB}/
heuristic=/home/lewi1538/shared/projects/neg_urg/code/heuristic.csv

#run init
echo python /home/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_dir} --heuristic ${heuristic}
python /home/faird/shared/code/internal/utilities/cdniproc/init_dev.py -p ${SUB} -s ${SES} -d ${dcm_dir} --heuristic ${heuristic}
