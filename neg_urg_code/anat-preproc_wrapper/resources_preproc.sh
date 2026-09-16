#!/bin/bash -l
#SBATCH -J anat_preproc
#SBATCH --mem=40gb
#SBATCH -t 03:00:00
#SBATCH --mail-user=lama0092@umn.edu
#SBATCH --mail-type=ALL
#SBATCH -p msismall
#SBATCH -o output_logs/anat_preproc_%A_%a.out
#SBATCH -e output_logs/anat_preproc_%A_%a.err
#SBATCH -A faird

cd run_files.preproc

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
