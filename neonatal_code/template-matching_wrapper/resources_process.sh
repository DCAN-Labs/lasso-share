#!/bin/bash -l
#SBATCH -J template_matching
#SBATCH --ntasks=4
#SBATCH --mem=200G
#SBATCH -t 04:00:00
#SBATCH -p agsmall,aglarge,ag2tb
#SBATCH --mail-type=NONE
#SBATCH --tmp=120gb
#SBATCH -o output_logs/abcd-temp-match_%A_%a.out
#SBATCH -e output_logs/abcd-temp-match_%A_%a.err
#SBATCH -A faird

cd run_files.tempmatch

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
