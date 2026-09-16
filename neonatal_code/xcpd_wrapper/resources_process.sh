#!/bin/bash -l
#SBATCH -J xcp-d
#SBATCH -c 4
#SBATCH --mem=100G
#SBATCH -t 10:00:00
#SBATCH -p agsmall,aglarge,ag2tb
#SBATCH --mail-type=NONE
#SBATCH --tmp=100gb
#SBATCH -o output_logs/xcp-d_%A_%a.out
#SBATCH -e output_logs/xcp_d_%A_%a.err
#SBATCH -A btervocl

cd run_files.xcpd

file=run${SLURM_ARRAY_TASK_ID}

bash ${file}
