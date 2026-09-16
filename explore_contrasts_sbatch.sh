#!/bin/bash -l
#SBATCH -J explore_contrasts
#SBATCH --mem=240gb
#SBATCH -t 01:00:00
#SBATCH -c 16
#SBATCH --mail-user=lama0092@umn.edu
#SBATCH --mail-type=NONE
#SBATCH -p msismall,msilarge,msibigmem
#SBATCH -o output_logs/explore_contrasts_%A_%a.out
#SBATCH -e output_logs/explore_contrasts_%A_%a.err
#SBATCH -A faird


source /projects/standard/faird/shared/code/external/envs/miniconda3/load_miniconda3.sh
conda activate CPAC_PipelineAgreement
export PYTHONNOUSERSITE=1
python /projects/standard/lewi1538/shared/projects/neg_urg/code/explore_contrasts.py -t /projects/standard/lewi1538/shared/projects/neg_urg/task_files/event_tsvs/ -d /projects/standard/lewi1538/shared/projects/neg_urg/derivatives/fmriprep/ -o /projects/standard/lewi1538/shared/projects/neg_urg/derivatives/task_analysis/21August_positive_minus_neutral_subs-01-70.nii.gz -c1 Positive -c2 Neutral
