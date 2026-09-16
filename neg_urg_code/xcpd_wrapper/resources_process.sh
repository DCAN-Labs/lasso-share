#!/bin/bash -l
#SBATCH -J xcp-d
#SBATCH -c 8
#SBATCH --mem=100G
#SBATCH -t 10:00:00
#SBATCH -p msismall
#SBATCH --mail-type=NONE
#SBATCH --tmp=100gb
#SBATCH -o output_logs/xcp-d_%A_%a.out
#SBATCH -e output_logs/xcp_d_%A_%a.err
#SBATCH -A faird

cd run_files.xcpd

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
