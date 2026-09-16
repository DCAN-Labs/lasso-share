#!/bin/bash -l
#SBATCH -J fmriprep
#SBATCH -c 24
#SBATCH --mem=400gb
#SBATCH -t 10:00:00
#SBATCH --mail-type=NONE
#SBATCH --tmp=500gb
#SBATCH -p msismall
#SBATCH -o output_logs/fmriprep_%A_%a.out
#SBATCH -e output_logs/fmriprep_%A_%a.err
#SBATCH -A faird

cd run_files.fmriprep

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
